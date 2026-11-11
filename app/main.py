
from fastapi import FastAPI
from sqlalchemy import text

from app.database import Base, engine

from app.models.category import Category
from app.models.product import Product
from app.models.product_category import ProductCategory
from app.models.product_image import ProductImage
from app.models.product_attribute import ProductAttribute

from app.routers import categories, products
from app.routers import product_categories

from app.models.manufacturer import Manufacturer

from app.models.store import Store
from app.models.product_store import ProductStore



app = FastAPI(
    title="Shop API",
    description="API для управління товарами та категоріями",
    version="1.0.0"
)


# Create all tables
Base.metadata.create_all(bind=engine)




@app.get("/")
def root():
    return {
        "message": "Shop API is running!"
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "Server is healthy"
    }

@app.get("/db-check")
def db_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {"database": "connected"}


app.include_router(categories.router)
app.include_router(products.router)
app.include_router(product_categories.router)

