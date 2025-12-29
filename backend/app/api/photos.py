"""Photo API endpoints for managing product images."""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from app.models.photo import PhotoCreate, PhotoResponse, PhotoMetadata
from app.models.user import UserInDB
from app.core.security import get_current_active_user
from app.db.mongodb import MongoDB

router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    photo: PhotoCreate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Upload a new photo."""
    db = MongoDB.get_db()
    photos_collection = db.photos
    
    # Calculate file size from base64 data
    file_size = len(photo.data.encode('utf-8'))
    
    # Prepare photo data
    photo_dict = photo.model_dump()
    photo_dict["date_creation"] = datetime.utcnow()
    photo_dict["file_size"] = file_size
    photo_dict["uploaded_by"] = current_user.username
    
    # Insert into database
    result = await photos_collection.insert_one(photo_dict)
    
    # Fetch and return created photo
    created_photo = await photos_collection.find_one({"_id": result.inserted_id})
    return PhotoResponse(**created_photo)


@router.get("", response_model=List[PhotoMetadata])
async def list_photos(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """List all photos (metadata only, without image data)."""
    db = MongoDB.get_db()
    photos_collection = db.photos
    
    # Fetch photos without the data field to save bandwidth
    cursor = photos_collection.find(
        {},
        {"data": 0}  # Exclude the large data field
    ).sort("date_creation", -1)
    
    photos = await cursor.to_list(length=1000)
    return [PhotoMetadata(**photo) for photo in photos]


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(
    photo_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get a specific photo by ID (includes image data)."""
    if not ObjectId.is_valid(photo_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid photo ID format"
        )
    
    db = MongoDB.get_db()
    photos_collection = db.photos
    
    photo = await photos_collection.find_one({"_id": ObjectId(photo_id)})
    
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )
    
    return PhotoResponse(**photo)


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Delete a photo."""
    if not ObjectId.is_valid(photo_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid photo ID format"
        )
    
    db = MongoDB.get_db()
    photos_collection = db.photos
    
    result = await photos_collection.delete_one({"_id": ObjectId(photo_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )
    
    return None
