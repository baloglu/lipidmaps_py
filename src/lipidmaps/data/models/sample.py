
import logging
from typing import Any, List, Dict, Optional, Union
import numpy as np
from .base import LipidmapsBaseModel
from pydantic import Field
from .reaction import ReactionData, CompoundComponent

logger = logging.getLogger(__name__)


class SampleMetadata(LipidmapsBaseModel):
    sample_id: str
    group: str  # e.g., "Control", "WT"
    label: Optional[str] = None  # e.g., "Fasted", "Fed"

    def mean_value_for_lipids(
        self,
        lipids: List[Union["QuantifiedLipid", str]],
        dataset: Optional["LipidDataset"] = None,
        skip_missing: bool = True,
    ) -> Optional[float]:
        """
        Compute the mean quantitation value for this sample across a list of lipids.

        Parameters:
        - lipids: list of `QuantifiedLipid` objects or lipid `input_name` strings.
        - dataset: optional `LipidDataset` used to resolve string names to lipid objects.
        - skip_missing: if True, missing values are ignored; if False, missing values are treated as NaN.

        Returns the mean as a float, or `None` if no valid numeric values were found.
        """
        if dataset is None:
            raise ValueError("dataset is required to resolve lipid names; call dataset.mean_value_for_lipids(...) instead")
        return dataset.mean_value_for_lipids(self, lipids, skip_missing=skip_missing)

class QuantifiedLipid(LipidmapsBaseModel):
    input_name: str
    values: Dict[str, float]  # sample_id -> value
    pathway_ids: Optional[List[str]] = None  # e.g., KEGG or Reactome IDs
    pathway_names: Optional[List[str]] = None  # Human-readable names
    enzyme_ids: Optional[List[str]] = None  
    # RefMet annotations
    standardized_name: Optional[str] = None
    standardized_by: Optional[str] = None # e.g., "RefMet"
    lm_id: Optional[str] = None
    lm_id_found_by: Optional[str] = None  # e.g., "LMSD", "RefMet"
    matched_field: Optional[str] = None
    generic_lm_id: Optional[str] = None
    sub_class: Optional[str] = None
    super_class: Optional[str] = None
    main_class: Optional[str] = None
    chebi_id: Optional[str] = None
    kegg_id: Optional[str] = None
    refmet_id: Optional[str] = None
    formula: Optional[str] = None
    mass: Optional[float] = None
    reactions: Optional[List[ReactionData]] = None # List of associated reactions
    weight: Optional[float] = None  # For species or class-level reaction

    def get_value_for_sample(self, sample: "SampleMetadata") -> Optional[float]:
        """
        Retrieve the quantitation value for a given SampleMetadata object.
        Returns None if not found.
        """
        return self.values.get(sample.sample_id)

    
    @property
    def recognized(self) -> bool:
        return self.standardized_name is not None
    
    def zscore(self) -> Dict[str, float]:
        vals = np.array(list(self.values.values()))
        mean = np.mean(vals)
        std = np.std(vals)
        return {
            k: (v - mean) / std if std != 0 else 0.0 for k, v in self.values.items()
        }

class LipidDataset(LipidmapsBaseModel):
    samples: List[SampleMetadata]
    lipids: List[QuantifiedLipid]
    column_info: Optional[Dict[str, Any]] = None  # Metadata about CSV columns
    reactions: List[ReactionData] = Field(default_factory=list)  # All reactions in dataset

    def list_samples(self) -> List[str]:
        return [s.sample_id for s in self.samples]

    def list_lipids(self) -> List[str]:
        return [l.input_name for l in self.lipids]
    
    def list_reactions(self) -> Optional[List[str]]:
        return [f"{r.reaction_name} {r.reaction_id}" for r in (self.reactions)]
    
    def list_lipids_with_lmid(self) -> List[str]:
        return [l.input_name for l in self.lipids if l.lm_id is not None]
    
    def list_lm_ids(self) -> List[str]:
        # Collect lm_ids, skip missing values, and preserve original order
        lm_ids = [l.lm_id for l in self.lipids if l.lm_id is not None]
        seen = set()
        unique = []
        for lid in lm_ids:
            if lid not in seen:
                seen.add(lid)
                unique.append(lid)
        return unique

    def list_lipids_with_reactions(self) -> List[str]:
        return [l.input_name for l in self.lipids if l.reactions is not None and len(l.reactions) > 0]
    
    def get_lipids_with_reactions(self) -> List[QuantifiedLipid]:
        return [l for l in self.lipids if l.reactions is not None and len(l.reactions) > 0]

    def get_lipids_for_component(self, component: CompoundComponent) -> List[QuantifiedLipid]:
        """
        Return all QuantifiedLipid objects where the component matches lm_id (case-insensitive).
        """
        comp_names = set()

        if hasattr(component, "compound_lm_id") and component.compound_lm_id:
            comp_names.add(component.compound_lm_id.lower())

        return [
            l for l in self.lipids
            if (l.lm_id and l.lm_id.lower() in comp_names)
            or (l.generic_lm_id and l.generic_lm_id.lower() in comp_names)
        ]

    def find_lipids(self, query: str) -> List[QuantifiedLipid]:
        q = query.lower()
        return [
            l for l in self.lipids
            if q in (l.input_name or "").lower() or (l.standardized_name and q in l.standardized_name.lower())
        ]

    def fill_missing_lm_ids_from_headgroups(self) -> int:
        """
        Fill missing lm_id fields on QuantifiedLipid objects using headgroup mapping from headgroups.py.
        Returns:
            Number of lipids updated with an lm_id.
        """
        import re
        from ..utils.headgroups import lipidmaps_headgroups
        updated = 0
        for lipid in self.lipids:
            if not getattr(lipid, "generic_lm_id", None):
                match = re.match(r"^([A-Za-z0-9\-]+)", lipid.input_name)
                if match:
                    headgroup = match.group(1)
                    lm_ids = lipidmaps_headgroups.get(headgroup)
                    if lm_ids and lm_ids[0]:
                        lipid.generic_lm_id = lm_ids[0]
                        lipid.lm_id_found_by = "headgroup"
                        updated += 1
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Updated {updated} generic_lm_id fields using headgroup mapping (via LipidDataset)")
        return updated

    def get_value(self, sample: "SampleMetadata", lipid: "QuantifiedLipid") -> Optional[float]:
        """
        Retrieve the quantitation value for a given sample and lipid object.
        Returns None if not found.
        """
        return lipid.values.get(sample.sample_id)

    def mean_value_for_lipids(
        self,
        sample: Union["SampleMetadata", str],
        lipids: List[Union["QuantifiedLipid", str]],
        skip_missing: bool = True,
    ) -> Optional[float]:
        """
        Compute the mean quantitation value for `sample` across a list of lipids.

        Parameters:
        - sample: `SampleMetadata` or sample_id string.
        - lipids: list of `QuantifiedLipid` objects or lipid `input_name` strings.
        - skip_missing: if True, missing values are ignored; if False, missing values are treated as NaN.

        Returns the mean as a float, or `None` if no valid numeric values were found.
        """
        # resolve sample id
        sample_id = sample.sample_id if hasattr(sample, "sample_id") else sample

        collected_values: List[float] = []
        for item in lipids:
            lipid_obj = None
            if isinstance(item, str):
                name_lc = item.lower()
                lipid_obj = next(
                    (
                        l
                        for l in self.lipids
                        if (l.input_name or "").lower() == name_lc
                        or (l.standardized_name and l.standardized_name.lower() == name_lc)
                    ),
                    None,
                )
                if lipid_obj is None:
                    continue
            else:
                lipid_obj = item

            value = lipid_obj.values.get(sample_id)
            if value is None:
                if skip_missing:
                    continue
                collected_values.append(np.nan)
            else:
                collected_values.append(value)

        if not collected_values:
            return None
        return float(np.nanmean(collected_values))

    def get_values(self, lipid_name: str) -> Optional[Dict[str, float]]:
        """
        Return the values dict for a lipid, matching input_name case-insensitively.
        Returns None if not found.
        """
        name_lc = lipid_name.lower()
        for l in self.lipids:
            if (l.input_name or '').lower() == name_lc:
                return l.values
        return None
        
    def get_grouped_data(self) -> Dict[str, List[QuantifiedLipid]]:
        grouped = {}
        for sample in self.samples:
            grouped.setdefault(sample.group, []).append(sample.sample_id)
        result = {}
        for group, sample_ids in grouped.items():
            result[group] = [
                QuantifiedLipid(
                    input_name=lipid.input_name,
                    values={
                        sid: lipid.values[sid]
                        for sid in sample_ids
                        if sid in lipid.values
                    },
                )
                for lipid in self.lipids
            ]
        return result
    
    def get_lipids_by_generic_lm_id(self, generic_lm_id: str) -> List[QuantifiedLipid]:
        """Return all QuantifiedLipid objects with the given generic lm_id."""
        return [l for l in self.lipids if l.generic_lm_id == generic_lm_id]

    def get_lipid_values_for_samples(self, sample_id: str) -> List[Dict[str, Optional[float]]]:
        """
        Return a list of objects for a given `sample_id` where each object contains:
            - `input_name`: the lipid's input name
            - `value`: the quantitation value for the provided sample_id (or None)

        This is useful for building per-sample plots or tables.
        """
        # maintain backward compatibility: accept either a sample_id string or a SampleMetadata object
        if hasattr(sample_id, "sample_id"):
            sid = sample_id.sample_id
        else:
            sid = sample_id

        return [
            {"input_name": l.input_name, "value": l.values.get(sid)}
            for l in self.lipids
        ]

    def get_lipids_for_reaction(self, reaction_or_id, role: str = "reactant") -> List[QuantifiedLipid]:
        """
        Return QuantifiedLipid objects that are reactants or products in a given reaction.
        Accepts either a ReactionData object or a reaction_id (str).
        role: "reactant" or "product"
        """
        # Determine if input is a ReactionData object or an id
        if isinstance(reaction_or_id, ReactionData):
            reaction = reaction_or_id
        else:
            reaction = next((r for r in self.reactions if getattr(r, 'reaction_id', None) == reaction_or_id), None)
        if not reaction:
            return []
        lm_ids = getattr(reaction, 'reactant_lm_ids', []) if role == "reactant" else getattr(reaction, 'product_lm_ids', [])
        # If reaction uses CompoundComponent, adjust accordingly
        if not lm_ids and hasattr(reaction, 'reactants') and role == "reactant":
            lm_ids = [c.compound_lm_id for c in getattr(reaction, 'reactants', []) if hasattr(c, 'compound_lm_id')]
        if not lm_ids and hasattr(reaction, 'products') and role == "product":
            lm_ids = [c.compound_lm_id for c in getattr(reaction, 'products', []) if hasattr(c, 'compound_lm_id')]
        return [l for l in self.lipids if l.lm_id in lm_ids]



class Quantitation(LipidmapsBaseModel):
    lipid: "QuantifiedLipid"  # Reference to a QuantifiedLipid object
    sample_values: Dict[str, float]  # sample_id -> value
    method: Optional[str] = None  # e.g., 'LC-MS', 'GC-MS'
    unit: Optional[str] = None  # e.g., 'pmol', 'ng'
    notes: Optional[str] = None
    # Add more fields as needed

    def get_value_for_sample(self, sample_id: str) -> Optional[float]:
        return self.sample_values.get(sample_id)
    
if __name__ == "__main__":

    lipid = QuantifiedLipid(
        input_name="PC(16:0/18:1)",
        values={"Sample1": 10.2, "Sample2": 11.3, "Sample3": 9.8},
    )
    zscores = lipid.zscore()
    print(f"Z-scores: {zscores} {lipid}")
