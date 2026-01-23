from typing import List, Any
import logging

from .base import LipidmapsBaseModel
from pydantic import field_validator

""" IN TEMPLATE PHASE"""

logger = logging.getLogger(__name__)


class Pathway(LipidmapsBaseModel):
    pathway_id: int
    pathway_name: str
    pathway_type: List[str]
    wikipathways_id: str
    wikipathways_description: str
    organism: str
    wikipathways_author: str
    reactions: List[Any]  # Replace Any with the actual Reaction type when defined

    @field_validator("pathway_name")
    def name_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("Pathway name must not be empty")
        return v

    def __init__(self, **data):
        super().__init__(**data)
        logger.info(f"Created Pathway: {self.pathway_name}")