"""Product API endpoints with CRUD operations."""
from datetime import datetime
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from bson import ObjectId
from pymongo import DESCENDING
from pydantic import BaseModel, Field

from app.models.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductBase
)
from app.models.user import UserInDB
from app.core.security import get_current_active_user
from app.db.mongodb import MongoDB

router = APIRouter(prefix="/products", tags=["products"])


class StockUpdate(BaseModel):
    """Schema for updating stock in a specific warehouse."""
    items: float = Field(..., description="Number of items in stock")


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Create a new product (MVP fields only)."""
    db = MongoDB.get_db()
    products_collection = db.products
    
    # Check if ref already exists
    existing = await products_collection.find_one({"ref": product.ref, "deleted": False})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with ref '{product.ref}' already exists"
        )
    
    # Check if barcode already exists (if provided)
    if product.barcode:
        existing_barcode = await products_collection.find_one({
            "barcode": product.barcode,
            "deleted": False
        })
        if existing_barcode:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with barcode '{product.barcode}' already exists"
            )
    
    # Prepare product data
    product_dict = product.model_dump()
    product_dict["date_creation"] = datetime.utcnow()
    product_dict["date_modification"] = datetime.utcnow()
    
    # Insert into database
    result = await products_collection.insert_one(product_dict)
    
    # Fetch and return created product
    created_product = await products_collection.find_one({"_id": result.inserted_id})
    return ProductResponse(**created_product)


@router.get("", response_model=List[ProductResponse])
async def list_products(
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of products to return"),
    search: Optional[str] = Query(None, description="Search in product label"),
    type: Optional[str] = Query(None, description="Filter by product type (0=product, 1=service)"),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """List all non-deleted products with pagination and filtering."""
    db = MongoDB.get_db()
    products_collection = db.products
    
    # Build query
    query = {"deleted": False}
    
    if search:
        # Use regex for partial matching (case-insensitive)
        search_pattern = {"$regex": search, "$options": "i"}
        query["$or"] = [
            {"label": search_pattern},
            {"ref": search_pattern},
            {"barcode": search_pattern},
        ]
    
    if type is not None:
        query["type"] = type
    
    # Execute query with pagination
    cursor = products_collection.find(query).sort("date_creation", DESCENDING).skip(skip).limit(limit)
    products = await cursor.to_list(length=limit)
    
    return [ProductResponse(**product) for product in products]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get a product by MongoDB ObjectId."""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID format"
        )
    
    db = MongoDB.get_db()
    products_collection = db.products
    
    product = await products_collection.find_one({
        "_id": ObjectId(product_id),
        "deleted": False
    })
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return ProductResponse(**product)


@router.get("/ref/{ref}", response_model=ProductResponse)
async def get_product_by_ref(
    ref: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get a product by product reference number."""
    db = MongoDB.get_db()
    products_collection = db.products
    
    product = await products_collection.find_one({"ref": ref, "deleted": False})
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ref '{ref}' not found"
        )
    
    return ProductResponse(**product)


@router.get("/barcode/{barcode}", response_model=ProductResponse)
async def get_product_by_barcode(
    barcode: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get a product by barcode."""
    db = MongoDB.get_db()
    products_collection = db.products
    
    product = await products_collection.find_one({"barcode": barcode, "deleted": False})
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with barcode '{barcode}' not found"
        )
    
    return ProductResponse(**product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Update a product."""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID format"
        )
    
    db = MongoDB.get_db()
    products_collection = db.products
    
    # Check if product exists
    existing = await products_collection.find_one({
        "_id": ObjectId(product_id),
        "deleted": False
    })
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Prepare update data (only include fields that were actually set)
    update_data = product_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Check ref uniqueness if being updated
    if "ref" in update_data and update_data["ref"] != existing["ref"]:
        ref_exists = await products_collection.find_one({
            "ref": update_data["ref"],
            "deleted": False,
            "_id": {"$ne": ObjectId(product_id)}
        })
        if ref_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with ref '{update_data['ref']}' already exists"
            )
    
    # Check barcode uniqueness if being updated
    if "barcode" in update_data and update_data["barcode"]:
        barcode_exists = await products_collection.find_one({
            "barcode": update_data["barcode"],
            "deleted": False,
            "_id": {"$ne": ObjectId(product_id)}
        })
        if barcode_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with barcode '{update_data['barcode']}' already exists"
            )
    
    # Add modification timestamp
    update_data["date_modification"] = datetime.utcnow()
    
    # Update product
    await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": update_data}
    )
    
    # Fetch and return updated product
    updated_product = await products_collection.find_one({"_id": ObjectId(product_id)})
    return ProductResponse(**updated_product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Soft delete a product."""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID format"
        )
    
    db = MongoDB.get_db()
    products_collection = db.products
    
    # Check if product exists and is not already deleted
    existing = await products_collection.find_one({
        "_id": ObjectId(product_id),
        "deleted": False
    })
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Soft delete
    await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {
            "$set": {
                "deleted": True,
                "deleted_at": datetime.utcnow(),
                "date_modification": datetime.utcnow()
            }
        }
    )
    
    return None


@router.get("/deleted/list", response_model=List[ProductResponse])
async def list_deleted_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """List all deleted products (admin function)."""
    db = MongoDB.get_db()
    products_collection = db.products
    
    cursor = products_collection.find({"deleted": True}).sort("deleted_at", DESCENDING).skip(skip).limit(limit)
    products = await cursor.to_list(length=limit)
    
    return [ProductResponse(**product) for product in products]


@router.put("/{product_id}/stock/{warehouse_ref}", response_model=ProductResponse)
async def update_product_stock(
    product_id: str,
    warehouse_ref: str,
    stock_update: StockUpdate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Update stock quantity for a product in a specific warehouse."""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID format"
        )
    
    db = MongoDB.get_db()
    products_collection = db.products
    warehouses_collection = db.warehouses
    
    # Check if product exists
    product = await products_collection.find_one({
        "_id": ObjectId(product_id),
        "deleted": False
    })
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if warehouse exists
    warehouse = await warehouses_collection.find_one({
        "ref": warehouse_ref,
        "deleted": False
    })
    
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Warehouse with ref '{warehouse_ref}' not found"
        )
    
    # Check if stock_warehouse exists and is the right type
    stock_warehouse = product.get("stock_warehouse")
    if stock_warehouse is None or isinstance(stock_warehouse, list):
        # Initialize as empty dict if it's missing or an array
        await products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {"stock_warehouse": {}}}
        )
    
    # Update stock for this warehouse
    update_data = {
        f"stock_warehouse.{warehouse_ref}": stock_update.model_dump(),
        "date_modification": datetime.utcnow()
    }
    
    await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": update_data}
    )
    
    # Fetch and return updated product
    updated_product = await products_collection.find_one({"_id": ObjectId(product_id)})
    return ProductResponse(**updated_product)


@router.get("/{product_id}/stock", response_model=Dict[str, Dict[str, float]])
async def get_product_stock(
    product_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get all stock quantities for a product across all warehouses."""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID format"
        )
    
    db = MongoDB.get_db()
    products_collection = db.products
    
    product = await products_collection.find_one({
        "_id": ObjectId(product_id),
        "deleted": False
    })
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product.get("stock_warehouse", {})


@router.get("/{product_id}/stock/{warehouse_ref}", response_model=StockUpdate)
async def get_product_stock_in_warehouse(
    product_id: str,
    warehouse_ref: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get stock quantity for a product in a specific warehouse."""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID format"
        )
    
    db = MongoDB.get_db()
    products_collection = db.products
    
    product = await products_collection.find_one({
        "_id": ObjectId(product_id),
        "deleted": False
    })
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    stock_warehouse = product.get("stock_warehouse", {})
    
    if warehouse_ref not in stock_warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No stock data for warehouse '{warehouse_ref}'"
        )
    
    return StockUpdate(**stock_warehouse[warehouse_ref])


@router.delete("/{product_id}/stock/{warehouse_ref}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_stock_in_warehouse(
    product_id: str,
    warehouse_ref: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Remove stock data for a product in a specific warehouse."""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID format"
        )
    
    db = MongoDB.get_db()
    products_collection = db.products
    
    product = await products_collection.find_one({
        "_id": ObjectId(product_id),
        "deleted": False
    })
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Remove stock data for this warehouse
    await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {
            "$unset": {f"stock_warehouse.{warehouse_ref}": ""},
            "$set": {"date_modification": datetime.utcnow()}
        }
    )
    
    return None


# ============================================================================
# Photo Management Endpoints
# ============================================================================

@router.post("/{product_id}/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_photo_to_product(
    product_id: str,
    photo_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Add a photo reference to a product."""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID format"
        )
    
    if not ObjectId.is_valid(photo_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid photo ID format"
        )
    
    db = MongoDB.get_db()
    products_collection = db.products
    photos_collection = db.photos
    
    # Check if product exists
    product = await products_collection.find_one({
        "_id": ObjectId(product_id),
        "deleted": False
    })
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if photo exists
    photo = await photos_collection.find_one({"_id": ObjectId(photo_id)})
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )
    
    # Add photo ID to product's photos array (if not already present)
    await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {
            "$addToSet": {"photos": photo_id},
            "$set": {"date_modification": datetime.utcnow()}
        }
    )
    
    return None


@router.delete("/{product_id}/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_photo_from_product(
    product_id: str,
    photo_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Remove a photo reference from a product."""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID format"
        )
    
    db = MongoDB.get_db()
    products_collection = db.products
    
    product = await products_collection.find_one({
        "_id": ObjectId(product_id),
        "deleted": False
    })
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Remove photo ID from product's photos array
    await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {
            "$pull": {"photos": photo_id},
            "$set": {"date_modification": datetime.utcnow()}
        }
    )
    
    return None


@router.get("/{product_id}/photos", response_model=List[str])
async def get_product_photos(
    product_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get list of photo IDs for a product."""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID format"
        )
    
    db = MongoDB.get_db()
    products_collection = db.products
    
    product = await products_collection.find_one({
        "_id": ObjectId(product_id),
        "deleted": False
    })
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product.get("photos", [])
