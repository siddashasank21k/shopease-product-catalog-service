import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.database.connection import engine, Base
from app.models.category_model import Category
from app.models.product_model import Product
from app.models.inventory_model import InventoryTransaction
from app.routers import category_routes, product_routes, inventory_routes

logger = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Safe startup retry handler to prevent cold container handshake issues
    for attempt in range(1, 16):
        try:
            logger.info(f"Connecting to MySQL database (attempt {attempt}/15)...")
            Base.metadata.create_all(bind=engine)
            logger.info("Product Catalog database connected and schema initialized.")
            break
        except Exception as e:
            logger.warning(f"Database connection waiting: {e}. Retrying in 2 seconds...")
            time.sleep(2)
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Independent microservice handling categories, products, inventory controls, and stock audits.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(category_routes.router)
app.include_router(product_routes.router)
app.include_router(inventory_routes.router)

@app.get("/health", tags=["Health"])
def health():
    return JSONResponse(status_code=200, content={"status": "healthy", "service": settings.APP_NAME})
