from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class StockAdjustmentRequest(BaseModel):
    quantity: int = Field(..., gt=0, description="Quantity must be greater than zero")
    remarks: Optional[str] = Field(None, max_length=255)

class CurrentStockResponse(BaseModel):
    product_id: int
    product_name: str
    sku: str
    stock_quantity: int
    is_active: bool

class InventoryTransactionResponse(BaseModel):
    id: int
    product_id: int
    transaction_type: str
    quantity: int
    previous_stock: int
    updated_stock: int
    remarks: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
