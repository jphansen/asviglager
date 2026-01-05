"""Warehouse API endpoints with CRUD operations."""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from bson import ObjectId
from pymongo import DESCENDING

from app.models.warehouse import (
    WarehouseCreate,
    WarehouseUpdate,
    WarehouseResponse,
    WarehouseBase,
    WarehouseType,
    ContainerType
)
from app.models.user import UserInDB
from app.core.security import get_current_active_user
from app.db.mongodb import MongoDB

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


@router.post("", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    warehouse: WarehouseCreate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Create a new warehouse."""
    db = MongoDB.get_db()
    warehouses_collection = db.warehouses
    
    # Check if ref already exists
    existing = await warehouses_collection.find_one({"ref": warehouse.ref, "deleted": False})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Warehouse with ref '{warehouse.ref}' already exists"
        )
    
    # Prepare warehouse data
    warehouse_dict = warehouse.model_dump()
    warehouse_dict["date_creation"] = datetime.utcnow()
    warehouse_dict["date_modification"] = datetime.utcnow()
    
    # Insert into database
    result = await warehouses_collection.insert_one(warehouse_dict)
    
    # Fetch and return created warehouse
    created_warehouse = await warehouses_collection.find_one({"_id": result.inserted_id})
    return WarehouseResponse(**created_warehouse)


@router.get("", response_model=List[WarehouseResponse])
async def list_warehouses(
    skip: int = Query(0, ge=0, description="Number of warehouses to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of warehouses to return"),
    search: Optional[str] = Query(None, description="Search in warehouse label or description"),
    type: Optional[WarehouseType] = Query(None, description="Filter by type (warehouse, location, container)"),
    parent_id: Optional[str] = Query(None, description="Filter by parent ObjectId"),
    status: Optional[bool] = Query(None, description="Filter by status (true=enabled, false=disabled)"),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """List all non-deleted warehouses with pagination and filtering."""
    db = MongoDB.get_db()
    warehouses_collection = db.warehouses
    
    # Build query
    query = {"deleted": False}
    
    if search:
        # Use regex for partial matching (case-insensitive)
        search_pattern = {"$regex": search, "$options": "i"}
        query["$or"] = [
            {"label": search_pattern},
            {"ref": search_pattern},
            {"description": search_pattern},
        ]
    
    if type is not None:
        query["type"] = type.value
    
    if parent_id is not None:
        if not ObjectId.is_valid(parent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid parent_id format"
            )
        query["fk_parent"] = parent_id
    
    if status is not None:
        query["status"] = status
    
    # Execute query with pagination
    cursor = warehouses_collection.find(query).sort("date_creation", DESCENDING).skip(skip).limit(limit)
    warehouses = await cursor.to_list(length=limit)
    
    return [WarehouseResponse(**warehouse) for warehouse in warehouses]


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get a warehouse by MongoDB ObjectId."""
    if not ObjectId.is_valid(warehouse_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid warehouse ID format"
        )
    
    db = MongoDB.get_db()
    warehouses_collection = db.warehouses
    
    warehouse = await warehouses_collection.find_one({
        "_id": ObjectId(warehouse_id),
        "deleted": False
    })
    
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    
    return WarehouseResponse(**warehouse)


@router.get("/ref/{ref}", response_model=WarehouseResponse)
async def get_warehouse_by_ref(
    ref: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get a warehouse by reference code."""
    db = MongoDB.get_db()
    warehouses_collection = db.warehouses
    
    warehouse = await warehouses_collection.find_one({"ref": ref, "deleted": False})
    
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Warehouse with ref '{ref}' not found"
        )
    
    return WarehouseResponse(**warehouse)


@router.put("/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(
    warehouse_id: str,
    warehouse_update: WarehouseUpdate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Update a warehouse."""
    if not ObjectId.is_valid(warehouse_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid warehouse ID format"
        )
    
    db = MongoDB.get_db()
    warehouses_collection = db.warehouses
    
    # Check if warehouse exists
    existing = await warehouses_collection.find_one({
        "_id": ObjectId(warehouse_id),
        "deleted": False
    })
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    
    # Prepare update data (only include fields that were actually set)
    update_data = warehouse_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Check ref uniqueness if being updated
    if "ref" in update_data and update_data["ref"] != existing["ref"]:
        ref_exists = await warehouses_collection.find_one({
            "ref": update_data["ref"],
            "deleted": False
        })
        if ref_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Warehouse with ref '{update_data['ref']}' already exists"
            )
    
    # Add modification timestamp
    update_data["date_modification"] = datetime.utcnow()
    
    # Update warehouse
    await warehouses_collection.update_one(
        {"_id": ObjectId(warehouse_id)},
        {"$set": update_data}
    )
    
    # Fetch and return updated warehouse
    updated_warehouse = await warehouses_collection.find_one({"_id": ObjectId(warehouse_id)})
    return WarehouseResponse(**updated_warehouse)


@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_warehouse(
    warehouse_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Soft delete a warehouse."""
    if not ObjectId.is_valid(warehouse_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid warehouse ID format"
        )
    
    db = MongoDB.get_db()
    warehouses_collection = db.warehouses
    
    # Check if warehouse exists
    existing = await warehouses_collection.find_one({
        "_id": ObjectId(warehouse_id),
        "deleted": False
    })
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    
    # Soft delete the warehouse
    await warehouses_collection.update_one(
        {"_id": ObjectId(warehouse_id)},
        {
            "$set": {
                "deleted": True,
                "deleted_at": datetime.utcnow(),
                "date_modification": datetime.utcnow()
            }
        }
    )
    
    return None


@router.get("/type/{type}", response_model=List[WarehouseResponse])
async def list_by_type(
    type: WarehouseType,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get all items of a specific type (warehouse, location, or container)."""
    db = MongoDB.get_db()
    warehouses_collection = db.warehouses
    
    query = {"deleted": False, "type": type.value}
    
    cursor = warehouses_collection.find(query).sort("label", 1).skip(skip).limit(limit)
    items = await cursor.to_list(length=limit)
    
    return [WarehouseResponse(**item) for item in items]


@router.get("/{warehouse_id}/children", response_model=List[WarehouseResponse])
async def get_children(
    warehouse_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get all child items (locations under warehouse, or containers under location)."""
    if not ObjectId.is_valid(warehouse_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid warehouse ID format"
        )
    
    db = MongoDB.get_db()
    warehouses_collection = db.warehouses
    
    # Check parent exists
    parent = await warehouses_collection.find_one({
        "_id": ObjectId(warehouse_id),
        "deleted": False
    })
    
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent not found"
        )
    
    # Get children
    cursor = warehouses_collection.find({
        "fk_parent": warehouse_id,
        "deleted": False
    }).sort("label", 1)
    
    children = await cursor.to_list(length=None)
    
    return [WarehouseResponse(**child) for child in children]


@router.get("/{warehouse_id}/path", response_model=List[WarehouseResponse])
async def get_hierarchy_path(
    warehouse_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get full hierarchy path from warehouse down to this item (e.g., [warehouse, location, container])."""
    if not ObjectId.is_valid(warehouse_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid warehouse ID format"
        )
    
    db = MongoDB.get_db()
    warehouses_collection = db.warehouses
    
    # Get the item
    item = await warehouses_collection.find_one({
        "_id": ObjectId(warehouse_id),
        "deleted": False
    })
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Build path by traversing up the hierarchy
    path = [WarehouseResponse(**item)]
    
    current_parent_id = item.get("fk_parent")
    while current_parent_id:
        if not ObjectId.is_valid(current_parent_id):
            break
            
        parent = await warehouses_collection.find_one({
            "_id": ObjectId(current_parent_id),
            "deleted": False
        })
        
        if not parent:
            break
        
        path.insert(0, WarehouseResponse(**parent))
        current_parent_id = parent.get("fk_parent")
    
    return path


@router.get("/container-types/list", response_model=List[str])
async def list_container_types(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get list of all container types (predefined enum values)."""
    return [ct.value for ct in ContainerType]
