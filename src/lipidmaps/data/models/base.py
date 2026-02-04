from pydantic import BaseModel, Field
import uuid

class LipidmapsBaseModel(BaseModel):
    """
    Base model for all LIPID MAPS data classes, providing a unique object id.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique object identifier (UUID4)")
