"""Warehouse data models with flexible schema support."""
from datetime import datetime
from typing import Optional, Any, Dict, Annotated
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


class WarehouseBase(BaseModel):
    """
    Base warehouse model with MVP fields.
    These are the minimum required fields for warehouse management.
    """
    
    # Required fields
    ref: str = Field(..., description="Warehouse reference/code (unique)")
    label: str = Field(..., description="Warehouse name/label")
    
    # Optional core fields
    description: Optional[str] = Field(default=None, description="Warehouse description")
    lieu: Optional[str] = Field(default=None, description="Location code")
    address: Optional[str] = Field(default=None, description="Street address")
    zip: Optional[str] = Field(default=None, description="Postal code")
    town: Optional[str] = Field(default=None, description="City/town")
    phone: Optional[str] = Field(default=None, description="Phone number")
    fax: Optional[str] = Field(default=None, description="Fax number")
    statut: str = Field(default="1", description="Warehouse status: 0=disabled, 1=enabled")
    fk_parent: Optional[str] = Field(default=None, description="Parent warehouse ID")
    
    # Soft delete fields
    deleted: bool = Field(default=False, description="Soft delete flag")
    deleted_at: Optional[datetime] = Field(default=None, description="Deletion timestamp")
    
    # Timestamps
    date_creation: Optional[datetime] = Field(default_factory=datetime.utcnow)
    date_modification: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


class WarehouseFull(WarehouseBase):
    """
    Full warehouse model including all Dolibarr fields.
    Used for importing existing Dolibarr warehouses.
    All additional fields are optional to allow flexibility.
    """
    
    # MongoDB ID
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    
    # Dolibarr ID fields
    dolibarr_id: Optional[str] = Field(default=None, description="Original Dolibarr ID")
    entity: Optional[str] = Field(default=None)
    import_key: Optional[str] = Field(default=None)
    ref_ext: Optional[str] = Field(default=None, description="External reference")
    
    # Status fields
    status: Optional[str] = Field(default=None)
    
    # Location fields
    country_id: Optional[str] = Field(default=None)
    country_code: Optional[str] = Field(default=None)
    state_id: Optional[str] = Field(default=None)
    region_id: Optional[str] = Field(default=None)
    
    # Barcode fields
    barcode_type: Optional[str] = Field(default=None)
    barcode_type_coder: Optional[str] = Field(default=None)
    
    # Financial fields
    mode_reglement_id: Optional[str] = Field(default=None)
    cond_reglement_id: Optional[str] = Field(default=None)
    fk_account: Optional[str] = Field(default=None)
    
    # Shipping fields
    demand_reason_id: Optional[str] = Field(default=None)
    transport_mode_id: Optional[str] = Field(default=None)
    shipping_method_id: Optional[str] = Field(default=None)
    shipping_method: Optional[str] = Field(default=None)
    
    # Multi-currency fields
    fk_multicurrency: Optional[str] = Field(default=None)
    multicurrency_code: Optional[str] = Field(default=None)
    multicurrency_tx: Optional[float] = Field(default=None)
    multicurrency_total_ht: Optional[float] = Field(default=None)
    multicurrency_total_tva: Optional[float] = Field(default=None)
    multicurrency_total_ttc: Optional[float] = Field(default=None)
    multicurrency_total_localtax1: Optional[float] = Field(default=None)
    multicurrency_total_localtax2: Optional[float] = Field(default=None)
    
    # Notes
    note_public: Optional[str] = Field(default=None)
    note_private: Optional[str] = Field(default=None)
    
    # Totals
    total_ht: Optional[float] = Field(default=None)
    total_tva: Optional[float] = Field(default=None)
    total_localtax1: Optional[float] = Field(default=None)
    total_localtax2: Optional[float] = Field(default=None)
    total_ttc: Optional[float] = Field(default=None)
    totalpaid: Optional[float] = Field(default=None)
    
    # User fields
    user_author: Optional[str] = Field(default=None)
    user_creation: Optional[str] = Field(default=None)
    user_creation_id: Optional[str] = Field(default=None)
    user_valid: Optional[str] = Field(default=None)
    user_validation: Optional[str] = Field(default=None)
    user_validation_id: Optional[str] = Field(default=None)
    user_closing_id: Optional[str] = Field(default=None)
    user_modification: Optional[str] = Field(default=None)
    user_modification_id: Optional[str] = Field(default=None)
    fk_user_creat: Optional[str] = Field(default=None)
    fk_user_modif: Optional[str] = Field(default=None)
    
    # Date fields
    date_validation: Optional[datetime] = Field(default=None)
    date_cloture: Optional[datetime] = Field(default=None)
    tms: Optional[datetime] = Field(default=None)
    
    # Other fields
    warehouse_id: Optional[str] = Field(default=None)
    warehouse_usage: Optional[str] = Field(default=None)
    fk_project: Optional[str] = Field(default=None)
    contact_id: Optional[str] = Field(default=None)
    user: Optional[str] = Field(default=None)
    origin_type: Optional[str] = Field(default=None)
    origin_id: Optional[str] = Field(default=None)
    last_main_doc: Optional[str] = Field(default=None)
    specimen: Optional[int] = Field(default=0)
    deposit_percent: Optional[float] = Field(default=None)
    retained_warranty_fk_cond_reglement: Optional[str] = Field(default=None)
    cond_reglement_supplier_id: Optional[str] = Field(default=None)
    
    # Name fields (if person-related)
    name: Optional[str] = Field(default=None)
    lastname: Optional[str] = Field(default=None)
    firstname: Optional[str] = Field(default=None)
    civility_id: Optional[str] = Field(default=None)
    libelle: Optional[str] = Field(default=None)
    
    # Miscellaneous Dolibarr fields (store as dict for flexibility)
    array_options: Optional[list] = Field(default_factory=list)
    array_languages: Optional[Any] = Field(default=None)
    contacts_ids: Optional[Any] = Field(default=None)
    linkedObjectsIds: Optional[Any] = Field(default=None)
    extraparams: Optional[list] = Field(default_factory=list)
    lines: Optional[Any] = Field(default=None)
    canvas: Optional[str] = Field(default=None)
    actiontypecode: Optional[str] = Field(default=None)
    product: Optional[Any] = Field(default=None)
    module: Optional[str] = Field(default=None)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


class WarehouseCreate(WarehouseBase):
    """Schema for creating a new warehouse (MVP fields)."""
    pass


class WarehouseUpdate(BaseModel):
    """Schema for updating a warehouse. All fields are optional."""
    ref: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    lieu: Optional[str] = None
    address: Optional[str] = None
    zip: Optional[str] = None
    town: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    statut: Optional[str] = None
    fk_parent: Optional[str] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )


class WarehouseResponse(WarehouseBase):
    """Schema for warehouse responses with MongoDB ID."""
    id: PyObjectId = Field(alias="_id")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
