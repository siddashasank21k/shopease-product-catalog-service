from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    category_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    sku: str = Field(..., min_length=3, max_length=100)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    discount_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    stock_quantity: int = Field(0, ge=0)
    image_url: Optional[str] = Field(None, max_length=500)
    brand: Optional[str] = Field(None, max_length=100)
    is_active: bool = True

class ProductUpdate(BaseModel):
    category_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    sku: str = Field(..., min_length=3, max_length=100)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    discount_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    image_url: Optional[str] = Field(None, max_length=500)
    brand: Optional[str] = Field(None, max_length=100)
    is_active: bool = True

class ProductPatch(BaseModel):
    category_id: Optional[int] = Field(None, gt=0)
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    sku: Optional[str] = Field(None, min_length=3, max_length=100)
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    discount_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    image_url: Optional[str] = Field(None, max_length=500)
    brand: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

class ProductResponse(BaseModel):
    id: int
    category_id: int
    name: str
    description: Optional[str]
    sku: str
    price: Decimal
    discount_price: Optional[Decimal]
    stock_quantity: int
    image_url: Optional[str]
    brand: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaginatedProductsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[ProductResponse]
