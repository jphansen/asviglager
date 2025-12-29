"""Photo data models for storing product images."""
from datetime import datetime
from typing import Optional, Any, Annotated
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator
from bson import ObjectId


def validate_object_id(v: Any) -> str:
    """Validate and convert ObjectId to string."""
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, str):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return v
    raise ValueError("Invalid ObjectId type")


# Create an annotated type for MongoDB ObjectId
PyObjectId = Annotated[str, BeforeValidator(validate_object_id)]


class PhotoBase(BaseModel):
    """Base photo model for uploading."""
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type (e.g., image/jpeg)")
    data: str = Field(..., description="Base64 encoded image data")
    description: Optional[str] = Field(default=None, description="Photo description")


class PhotoCreate(PhotoBase):
    """Schema for creating a new photo."""
    pass


class PhotoResponse(BaseModel):
    """Response model for photo data."""
    id: PyObjectId = Field(alias="_id", description="Photo ID")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type")
    data: str = Field(..., description="Base64 encoded image data")
    description: Optional[str] = Field(default=None, description="Photo description")
    file_size: int = Field(..., description="File size in bytes")
    date_creation: datetime = Field(..., description="Upload timestamp")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


class PhotoMetadata(BaseModel):
    """Photo metadata without the actual image data (for listings)."""
    id: PyObjectId = Field(alias="_id", description="Photo ID")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type")
    description: Optional[str] = Field(default=None, description="Photo description")
    file_size: int = Field(..., description="File size in bytes")
    date_creation: datetime = Field(..., description="Upload timestamp")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
