from math import ceil
from typing import Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc
from fastapi import HTTPException, status
from app.models.category_model import Category
from app.models.product_model import Product
from app.models.inventory_model import InventoryTransaction
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductPatch, PaginatedProductsResponse, ProductResponse

class ProductService:
    @staticmethod
    def _validate_category(db: Session, category_id: int):
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with ID {category_id} does not exist.")
        return category

    @staticmethod
    def create_product(db: Session, payload: ProductCreate) -> Product:
        ProductService._validate_category(db, payload.category_id)
        if db.query(Product).filter(Product.sku == payload.sku).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Product with SKU '{payload.sku}' already exists.")
        if payload.discount_price and payload.discount_price > payload.price:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Discount price cannot exceed base price.")

        product = Product(
            category_id=payload.category_id,
            name=payload.name,
            description=payload.description,
            sku=payload.sku,
            price=payload.price,
            discount_price=payload.discount_price,
            stock_quantity=payload.stock_quantity,
            image_url=payload.image_url,
            brand=payload.brand,
            is_active=payload.is_active,
        )
        db.add(product)
        db.flush()

        # Record initial stock transaction if stock > 0
        if payload.stock_quantity > 0:
            initial_tx = InventoryTransaction(
                product_id=product.id,
                transaction_type="IN",
                quantity=payload.stock_quantity,
                previous_stock=0,
                updated_stock=payload.stock_quantity,
                remarks="Initial stock upon product creation",
            )
            db.add(initial_tx)

        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def get_product(db: Session, product_id: int, allow_inactive: bool = False) -> Product:
        q = db.query(Product).filter(Product.id == product_id)
        if not allow_inactive:
            q = q.filter(Product.is_active == True)
        product = q.first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with ID {product_id} not found.")
        return product

    @staticmethod
    def list_products(
        db: Session,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        is_active: Optional[bool] = True,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "id",
        sort_order: str = "asc",
    ) -> PaginatedProductsResponse:
        q = db.query(Product)
        if is_active is not None:
            q = q.filter(Product.is_active == is_active)
        if category_id:
            q = q.filter(Product.category_id == category_id)
        if search:
            pattern = f"%{search}%"
            q = q.filter(or_(Product.name.ilike(pattern), Product.sku.ilike(pattern), Product.brand.ilike(pattern)))
        if min_price is not None:
            q = q.filter(Product.price >= min_price)
        if max_price is not None:
            q = q.filter(Product.price <= max_price)

        total = q.count()

        # Sorting
        sort_column = getattr(Product, sort_by, Product.id)
        q = q.order_by(desc(sort_column) if sort_order.lower() == "desc" else asc(sort_column))

        # Pagination
        offset = (page - 1) * page_size
        items = q.offset(offset).limit(page_size).all()
        total_pages = ceil(total / page_size) if total > 0 else 0

        return PaginatedProductsResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            items=[ProductResponse.model_validate(p) for p in items],
        )

    @staticmethod
    def update_product(db: Session, product_id: int, payload: ProductUpdate) -> Product:
        product = ProductService.get_product(db, product_id, allow_inactive=True)
        ProductService._validate_category(db, payload.category_id)

        duplicate_sku = db.query(Product).filter(Product.sku == payload.sku, Product.id != product_id).first()
        if duplicate_sku:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"SKU '{payload.sku}' is already in use.")

        for key, val in payload.model_dump().items():
            setattr(product, key, val)

        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def patch_product(db: Session, product_id: int, payload: ProductPatch) -> Product:
        product = ProductService.get_product(db, product_id, allow_inactive=True)
        data = payload.model_dump(exclude_unset=True)

        if "category_id" in data and data["category_id"] is not None:
            ProductService._validate_category(db, data["category_id"])

        if "sku" in data and data["sku"] is not None:
            duplicate = db.query(Product).filter(Product.sku == data["sku"], Product.id != product_id).first()
            if duplicate:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"SKU '{data['sku']}' is already in use.")

        for key, val in data.items():
            setattr(product, key, val)

        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete_product(db: Session, product_id: int):
        product = ProductService.get_product(db, product_id, allow_inactive=True)
        db.delete(product)
        db.commit()
        return {"message": f"Product '{product.name}' and its inventory history deleted successfully."}
