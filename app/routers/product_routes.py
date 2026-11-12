from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.security import require_admin
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductPatch, ProductResponse, PaginatedProductsResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), claims: dict = Depends(require_admin)):
    return ProductService.create_product(db, payload)

@router.get("/", response_model=PaginatedProductsResponse)
def list_products(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    is_active: Optional[bool] = True,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("id", regex="^(id|name|price|created_at|stock_quantity)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    return ProductService.list_products(
        db, search, category_id, min_price, max_price, is_active, page, page_size, sort_by, sort_order
    )

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return ProductService.get_product(db, product_id, allow_inactive=False)

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db), claims: dict = Depends(require_admin)):
    return ProductService.update_product(db, product_id, payload)

@router.patch("/{product_id}", response_model=ProductResponse)
def patch_product(product_id: int, payload: ProductPatch, db: Session = Depends(get_db), claims: dict = Depends(require_admin)):
    return ProductService.patch_product(db, product_id, payload)

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), claims: dict = Depends(require_admin)):
    return ProductService.delete_product(db, product_id)
