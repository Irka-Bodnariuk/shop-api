
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.category import Category
from app.models.product_category import ProductCategory


router = APIRouter(
    prefix="/product/{product_id}/category",
    tags=["Product Category"]
)


def check_product(db: Session, product_id: int):
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )


# GET — список категорій товару
@router.get("")
def get_product_categories(
    product_id: int,
    db: Session = Depends(get_db)
):
    check_product(db, product_id)

    links = db.query(ProductCategory).filter(
        ProductCategory.product_id == product_id
    ).all()

    result = []

    for link in links:
        category = db.query(Category).filter(
            Category.category_id == link.category_id
        ).first()

        if category:
            result.append({
                "product_category_id": link.product_category_id,
                "product_id": link.product_id,
                "category_id": category.category_id,
                "category_name": category.name
            })

    return result


# GET — одна прив'язка категорії
@router.get("/{product_category_id}")
def get_product_category(
    product_id: int,
    product_category_id: int,
    db: Session = Depends(get_db)
):
    check_product(db, product_id)

    link = db.query(ProductCategory).filter(
        ProductCategory.product_category_id == product_category_id,
        ProductCategory.product_id == product_id
    ).first()

    if not link:
        raise HTTPException(
            status_code=404,
            detail="Product category link not found"
        )

    category = db.query(Category).filter(
        Category.category_id == link.category_id
    ).first()

    return {
        "product_category_id": link.product_category_id,
        "product_id": link.product_id,
        "category_id": link.category_id,
        "category_name": category.name if category else None
    }


# POST — додати категорію товару
@router.post("", status_code=201)
def create_product_category(
    product_id: int,
    category_id: int,
    db: Session = Depends(get_db)
):
    check_product(db, product_id)

    category = db.query(Category).filter(
        Category.category_id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    existing = db.query(ProductCategory).filter(
        ProductCategory.product_id == product_id,
        ProductCategory.category_id == category_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Category is already assigned to this product"
        )

    link = ProductCategory(
        product_id=product_id,
        category_id=category_id
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    return {
        "product_category_id": link.product_category_id,
        "product_id": link.product_id,
        "category_id": link.category_id,
        "category_name": category.name
    }


# DELETE — видалити прив'язку категорії
@router.delete("/{product_category_id}")
def delete_product_category(
    product_id: int,
    product_category_id: int,
    db: Session = Depends(get_db)
):
    check_product(db, product_id)

    link = db.query(ProductCategory).filter(
        ProductCategory.product_category_id == product_category_id,
        ProductCategory.product_id == product_id
    ).first()

    if not link:
        raise HTTPException(
            status_code=404,
            detail="Product category link not found"
        )

    db.delete(link)
    db.commit()

    return {
        "message": "Product category link deleted successfully"
    }
