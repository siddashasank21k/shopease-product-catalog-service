from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.security import require_admin
from app.schemas.inventory_schema import StockAdjustmentRequest, CurrentStockResponse, InventoryTransactionResponse
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/api/inventory", tags=["Inventory Management"])

@router.get("/low-stock", response_model=List[CurrentStockResponse])
def list_low_stock(threshold: Optional[int] = Query(None, ge=1), db: Session = Depends(get_db), claims: dict = Depends(require_admin)):
    return InventoryService.get_low_stock_products(db, threshold)

@router.get("/{product_id}", response_model=CurrentStockResponse)
def get_stock(product_id: int, db: Session = Depends(get_db), claims: dict = Depends(require_admin)):
    return InventoryService.get_current_stock(db, product_id)

@router.post("/{product_id}/stock-in", response_model=CurrentStockResponse)
def stock_in(product_id: int, payload: StockAdjustmentRequest, db: Session = Depends(get_db), claims: dict = Depends(require_admin)):
    return InventoryService.stock_in(db, product_id, payload)

@router.post("/{product_id}/stock-out", response_model=CurrentStockResponse)
def stock_out(product_id: int, payload: StockAdjustmentRequest, db: Session = Depends(get_db), claims: dict = Depends(require_admin)):
    return InventoryService.stock_out(db, product_id, payload)

@router.get("/{product_id}/history", response_model=List[InventoryTransactionResponse])
def get_inventory_history(product_id: int, db: Session = Depends(get_db), claims: dict = Depends(require_admin)):
    return InventoryService.get_history(db, product_id)
