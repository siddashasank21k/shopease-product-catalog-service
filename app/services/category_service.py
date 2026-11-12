from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.category_model import Category
from app.models.product_model import Product
from app.schemas.category_schema import CategoryCreate, CategoryUpdate

class CategoryService:
    @staticmethod
    def create_category(db: Session, payload: CategoryCreate) -> Category:
        existing = db.query(Category).filter(Category.name == payload.name).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Category '{payload.name}' already exists.")
        category = Category(name=payload.name, description=payload.description, is_active=payload.is_active)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def list_categories(db: Session, active_only: bool = False) -> List[Category]:
        q = db.query(Category)
        if active_only:
            q = q.filter(Category.is_active == True)
        return q.all()

    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> Category:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with ID {category_id} not found.")
        return category

    @staticmethod
    def update_category(db: Session, category_id: int, payload: CategoryUpdate) -> Category:
        category = CategoryService.get_category_by_id(db, category_id)
        duplicate = db.query(Category).filter(Category.name == payload.name, Category.id != category_id).first()
        if duplicate:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Category name '{payload.name}' is already in use.")
        category.name = payload.name
        category.description = payload.description
        category.is_active = payload.is_active
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete_category(db: Session, category_id: int):
        category = CategoryService.get_category_by_id(db, category_id)
        product_count = db.query(Product).filter(Product.category_id == category_id).count()
        if product_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete category '{category.name}' because it contains {product_count} products. Reassign or delete the products first."
            )
        db.delete(category)
        db.commit()
        return {"message": f"Category '{category.name}' deleted successfully."}
