from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.config import settings
from app.models.product_model import Product
from app.models.inventory_model import InventoryTransaction
from app.schemas.inventory_schema import StockAdjustmentRequest, CurrentStockResponse

class InventoryService:
    @staticmethod
    def get_current_stock(db: Session, product_id: int) -> CurrentStockResponse:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {product_id} not found.")
        return CurrentStockResponse(
            product_id=product.id,
            product_name=product.name,
            sku=product.sku,
            stock_quantity=product.stock_quantity,
            is_active=product.is_active,
        )

    @staticmethod
    def stock_in(db: Session, product_id: int, payload: StockAdjustmentRequest) -> CurrentStockResponse:
        # Atomic lock using with_for_update to eliminate race conditions
        product = db.query(Product).filter(Product.id == product_id).with_for_update().first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {product_id} not found.")

        prev_stock = product.stock_quantity
        updated_stock = prev_stock + payload.quantity

        product.stock_quantity = updated_stock
        tx = InventoryTransaction(
            product_id=product.id,
            transaction_type="IN",
            quantity=payload.quantity,
            previous_stock=prev_stock,
            updated_stock=updated_stock,
            remarks=payload.remarks or "Stock In addition",
        )
        db.add(tx)
        db.commit()
        db.refresh(product)

        return CurrentStockResponse(
            product_id=product.id,
            product_name=product.name,
            sku=product.sku,
            stock_quantity=product.stock_quantity,
            is_active=product.is_active,
        )

    @staticmethod
    def stock_out(db: Session, product_id: int, payload: StockAdjustmentRequest) -> CurrentStockResponse:
        # Atomic lock using with_for_update to eliminate race conditions
        product = db.query(Product).filter(Product.id == product_id).with_for_update().first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {product_id} not found.")

        prev_stock = product.stock_quantity
        if prev_stock < payload.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Available: {prev_stock}, Requested deduction: {payload.quantity}.",
            )

        updated_stock = prev_stock - payload.quantity
        product.stock_quantity = updated_stock

        tx = InventoryTransaction(
            product_id=product.id,
            transaction_type="OUT",
            quantity=payload.quantity,
            previous_stock=prev_stock,
            updated_stock=updated_stock,
            remarks=payload.remarks or "Stock Out deduction",
        )
        db.add(tx)
        db.commit()
        db.refresh(product)

        return CurrentStockResponse(
            product_id=product.id,
            product_name=product.name,
            sku=product.sku,
            stock_quantity=product.stock_quantity,
            is_active=product.is_active,
        )

    @staticmethod
    def get_history(db: Session, product_id: int) -> List[InventoryTransaction]:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {product_id} not found.")
        return db.query(InventoryTransaction).filter(InventoryTransaction.product_id == product_id).order_by(InventoryTransaction.created_at.desc()).all()

    @staticmethod
    def get_low_stock_products(db: Session, threshold: int = None) -> List[CurrentStockResponse]:
        limit = threshold or settings.LOW_STOCK_THRESHOLD
        products = db.query(Product).filter(Product.stock_quantity <= limit, Product.is_active == True).all()
        return [
            CurrentStockResponse(
                product_id=p.id,
                product_name=p.name,
                sku=p.sku,
                stock_quantity=p.stock_quantity,
                is_active=p.is_active,
            )
            for p in products
        ]
