import unittest
from lipidmaps.data.data_manager import DataManager
from lipidmaps.data.models.sample import QuantifiedLipid, LipidDataset, SampleMetadata
from lipidmaps.data.models.reaction import ReactionChecker, ReactionData, CompoundComponent
# from lipidmaps.data.reaction_checker import ReactionChecker, ReactionData, CompoundComponent

class TestAnnotateLipidsWithReactions(unittest.TestCase):
    def setUp(self):
        # Create mock lipids
        self.lipids = [
            QuantifiedLipid(input_name="PC(16:0/18:1)", values={"S1": 1.0}, lm_id="LMGP01010001"),
            QuantifiedLipid(input_name="LPC(16:0)", values={"S1": 2.0}, lm_id="LMGP02010001"),
        ]
        self.samples = [SampleMetadata(sample_id="S1", group="Control")]
        self.dataset = LipidDataset(samples=self.samples, lipids=self.lipids)
        self.manager = DataManager()
        self.manager.dataset = self.dataset

        # Create mock CompoundComponent objects
        reactant1 = CompoundComponent(compound_type="lm_main", compound_lm_id="LMGP01010001", compound_name="PC(16:0/18:1)")
        product1 = CompoundComponent(compound_type="lm_main", compound_lm_id="LMGP02010001", compound_name="LPC(16:0)")
        reactant2 = CompoundComponent(compound_type="lm_main",compound_lm_id="LMGP02010001", compound_name="LPC(16:0)")
        product2 = CompoundComponent(compound_type="lm_main", compound_lm_id="LMGP01010001", compound_name="PC(16:0/18:1)")

        # Create mock reactions using CompoundComponent
        self.reactions = [
            ReactionData(
                reaction_id=1,
                reaction_name="PC to LPC",
                reactants=[reactant1],
                products=[product1],
                reaction_type="class-level"
            ),
            ReactionData(
                reaction_id=2,
                reaction_name="LPC to PC",
                reactants=[reactant2],
                products=[product2],
                reaction_type="class-level"
            ),
        ]

    # ignore this test
    # @unittest.skip("Skipping test_annotate_lipids_with_reactions")
    def test_annotate_lipids_with_reactions(self):
        self.manager.annotate_lipids_with_reactions(self.dataset, self.reactions)
        # Check that each lipid has reactions
        for lipid in self.dataset.lipids:
            self.assertIsInstance(lipid.reactions, list)
            self.assertGreaterEqual(len(lipid.reactions), 1)
            # Check that the reaction_id is present in the reactions

            reaction_ids = [int(r.reaction_id) for r in lipid.reactions]
            self.assertTrue(any(rid in [1, 2] for rid in reaction_ids))

if __name__ == "__main__":
    unittest.main()