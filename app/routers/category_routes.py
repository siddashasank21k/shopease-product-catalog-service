from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.security import require_admin
from app.schemas.category_schema import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.category_service import CategoryService

router = APIRouter(prefix="/api/categories", tags=["Categories"])

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), claims: dict = Depends(require_admin)):
    return CategoryService.create_category(db, payload)

@router.get("/", response_model=List[CategoryResponse])
def list_categories(active_only: bool = True, db: Session = Depends(get_db)):
    return CategoryService.list_categories(db, active_only=active_only)

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return CategoryService.get_category_by_id(db, category_id)

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db), claims: dict = Depends(require_admin)):
    return CategoryService.update_category(db, category_id, payload)

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), claims: dict = Depends(require_admin)):
    return CategoryService.delete_category(db, category_id)
