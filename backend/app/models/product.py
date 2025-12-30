"""Product data models with flexible schema support."""
from datetime import datetime
from typing import Optional, Any, Dict, List, Annotated
from pydantic import BaseModel, Field, field_validator, ConfigDict, BeforeValidator
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


class ProductBase(BaseModel):
    """
    Base product model with MVP fields for creating new products.
    These are the minimum required fields for product management.
    """
    
    # Required fields
    ref: str = Field(..., description="Product reference number (unique)")
    label: str = Field(..., description="Product name/label")
    price: float = Field(..., description="Sale price", ge=0)
    
    # Optional core fields
    type: str = Field(default="0", description="Product type: 0=product, 1=service")
    barcode: Optional[str] = Field(default=None, description="Product barcode (EAN-13)")
    cost_price: Optional[float] = Field(default=None, description="Cost/purchase price", ge=0)
    description: Optional[str] = Field(default=None, description="Product description")
    status: str = Field(default="1", description="Product status: 0=disabled, 1=enabled")
    status_buy: str = Field(default="1", description="Can be purchased: 0=no, 1=yes")
    
    # Soft delete fields
    deleted: bool = Field(default=False, description="Soft delete flag")
    deleted_at: Optional[datetime] = Field(default=None, description="Deletion timestamp")
    
    # Stock tracking per warehouse
    stock_warehouse: Optional[Dict[str, Dict[str, float]]] = Field(
        default_factory=dict,
        description="Stock quantities per warehouse. Key is warehouse ref, value contains stock data"
    )
    
    # Photo references (list of photo IDs)
    photos: Optional[List[str]] = Field(
        default_factory=list,
        description="List of photo IDs associated with this product"
    )
    
    # Timestamps
    date_creation: Optional[datetime] = Field(default_factory=datetime.utcnow)
    date_modification: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    @field_validator("barcode")
    @classmethod
    def validate_barcode(cls, v):
        """Normalize barcode if provided."""
        if v is not None and v != "":
            # Remove whitespace
            v = v.strip()
        return v
    
    @field_validator("stock_warehouse", mode="before")
    @classmethod
    def validate_stock_warehouse(cls, v):
        """Ensure stock_warehouse is a dict, convert empty list to dict."""
        if v is None or v == [] or v == "":
            return {}
        if isinstance(v, dict):
            return v
        return {}
    
    @field_validator("price", "cost_price")
    @classmethod
    def validate_positive(cls, v):
        """Ensure prices are positive."""
        if v is not None and v < 0:
            raise ValueError("Price must be positive")
        return v


class ProductFull(ProductBase):
    """
    Full product model supporting all Dolibarr fields.
    Used for importing existing Dolibarr products.
    All additional fields are optional to allow flexibility.
    """
    
    # MongoDB ID
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    
    # Dolibarr ID fields
    dolibarr_id: Optional[str] = Field(default=None, description="Original Dolibarr ID")
    entity: Optional[str] = Field(default=None)
    ref_ext: Optional[str] = Field(default=None, description="External reference")
    
    # Status fields
    finished: Optional[str] = Field(default=None)
    status_batch: Optional[str] = Field(default=None)
    specimen: Optional[int] = Field(default=None)
    
    # Pricing fields (detailed)
    price_ttc: Optional[float] = Field(default=None, description="Price including tax")
    price_base_type: Optional[str] = Field(default=None)
    price_min: Optional[float] = Field(default=None)
    price_min_ttc: Optional[float] = Field(default=None)
    pmp: Optional[float] = Field(default=None, description="Weighted average price")
    
    # Tax fields
    tva_tx: Optional[float] = Field(default=None, description="VAT rate")
    localtax1_tx: Optional[float] = Field(default=None)
    localtax2_tx: Optional[float] = Field(default=None)
    localtax1_type: Optional[str] = Field(default=None)
    localtax2_type: Optional[str] = Field(default=None)
    default_vat_code: Optional[str] = Field(default=None)
    
    # Barcode fields
    barcode_type: Optional[str] = Field(default=None)
    barcode_type_coder: Optional[str] = Field(default=None)
    
    # Stock fields
    stock_reel: Optional[int] = Field(default=None, description="Real stock")
    stock_theorique: Optional[int] = Field(default=None, description="Theoretical stock")
    seuil_stock_alerte: Optional[int] = Field(default=None, description="Stock alert threshold")
    desiredstock: Optional[int] = Field(default=None)
    
    # Batch/lot tracking
    sell_or_eat_by_mandatory: Optional[str] = Field(default=None)
    batch_mask: Optional[str] = Field(default=None)
    mandatory_period: Optional[str] = Field(default=None)
    
    # Physical dimensions
    weight: Optional[float] = Field(default=None)
    weight_units: Optional[str] = Field(default=None)
    length: Optional[float] = Field(default=None)
    length_units: Optional[str] = Field(default=None)
    width: Optional[float] = Field(default=None)
    width_units: Optional[str] = Field(default=None)
    height: Optional[float] = Field(default=None)
    height_units: Optional[str] = Field(default=None)
    surface: Optional[float] = Field(default=None)
    surface_units: Optional[str] = Field(default=None)
    volume: Optional[float] = Field(default=None)
    volume_units: Optional[str] = Field(default=None)
    
    # Location fields
    country_id: Optional[str] = Field(default=None)
    country_code: Optional[str] = Field(default=None)
    state_id: Optional[str] = Field(default=None)
    region_id: Optional[str] = Field(default=None)
    warehouse_id: Optional[str] = Field(default=None)
    fk_default_warehouse: Optional[str] = Field(default=None)
    
    # Custom code
    customcode: Optional[str] = Field(default=None)
    
    # Miscellaneous Dolibarr fields (store as dict for flexibility)
    extra_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @classmethod
    def from_dolibarr(cls, dolibarr_data: dict) -> "ProductFull":
        """
        Create ProductFull from Dolibarr API data.
        Handles type conversions and field mappings.
        """
        # Convert Unix timestamps to datetime
        if "date_creation" in dolibarr_data and isinstance(dolibarr_data["date_creation"], int):
            dolibarr_data["date_creation"] = datetime.fromtimestamp(dolibarr_data["date_creation"])
        
        if "date_modification" in dolibarr_data and isinstance(dolibarr_data["date_modification"], int):
            dolibarr_data["date_modification"] = datetime.fromtimestamp(dolibarr_data["date_modification"])
        
        # Store original Dolibarr ID
        if "id" in dolibarr_data:
            dolibarr_data["dolibarr_id"] = str(dolibarr_data["id"])
            del dolibarr_data["id"]  # Remove to avoid conflict with MongoDB _id
        
        # Convert price strings to Decimal
        price_fields = ["price", "price_ttc", "price_min", "price_min_ttc", "cost_price", "pmp",
                       "tva_tx", "localtax1_tx", "localtax2_tx"]
        for field in price_fields:
            if field in dolibarr_data and dolibarr_data[field]:
                try:
                    if isinstance(dolibarr_data[field], str):
                        dolibarr_data[field] = Decimal(dolibarr_data[field])
                    elif isinstance(dolibarr_data[field], (int, float)):
                        dolibarr_data[field] = Decimal(str(dolibarr_data[field]))
                except:
                    pass
        
        # Convert dimension fields
        dimension_fields = ["weight", "length", "width", "height", "surface", "volume"]
        for field in dimension_fields:
            if field in dolibarr_data and dolibarr_data[field]:
                try:
                    dolibarr_data[field] = Decimal(str(dolibarr_data[field]))
                except:
                    pass
        
        # Handle empty strings vs None
        for key, value in list(dolibarr_data.items()):
            if value == "":
                dolibarr_data[key] = None
        
        # Add soft delete fields
        dolibarr_data["deleted"] = False
        dolibarr_data["deleted_at"] = None
        
        return cls(**dolibarr_data)


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product. All fields are optional."""
    ref: Optional[str] = None
    label: Optional[str] = None
    price: Optional[float] = None
    type: Optional[str] = None
    barcode: Optional[str] = None
    cost_price: Optional[float] = None
    description: Optional[str] = None
    status: Optional[str] = None
    status_buy: Optional[str] = None
    stock_warehouse: Optional[Dict[str, Dict[str, float]]] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )


class ProductResponse(ProductBase):
    """Schema for product responses with MongoDB ID."""
    id: PyObjectId = Field(alias="_id")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    @field_validator("stock_warehouse", mode="before")
    @classmethod
    def validate_stock_warehouse_response(cls, v):
        """Ensure stock_warehouse is a dict, convert empty list to dict."""
        if v is None or v == [] or v == "":
            return {}
        if isinstance(v, dict):
            return v
        return {}
