
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.category import Category

from app.models.product_category import ProductCategory
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListItem,
)

from app.models.product_image import ProductImage
from app.schemas.product_image import (
    ProductImageCreate,
    ProductImageUpdate,
    ProductImageResponse,
)

from app.models.product_attribute import ProductAttribute
from app.schemas.product_attribute import (
    ProductAttributeCreate,
    ProductAttributeUpdate,
    ProductAttributeResponse,
)

from app.models.product_store import ProductStore
from app.models.store import Store
from app.schemas.product_store import ProductStoreResponse


router = APIRouter(
    prefix="/product",
    tags=["Product"]
)


def build_category_paths(categories):
    """Формує повний шлях кожної категорії."""

    category_map = {
        category.category_id: category
        for category in categories
    }

    paths = {}

    def get_path(category_id, visited=None):
        if category_id in paths:
            return paths[category_id]

        if visited is None:
            visited = set()

        if category_id in visited:
            return "Помилка ієрархії"

        visited.add(category_id)
        category = category_map[category_id]

        if category.parent_category_id is None:
            path = category.name
        elif category.parent_category_id in category_map:
            path = (
                get_path(category.parent_category_id, visited)
                + " > "
                + category.name
            )
        else:
            path = category.name

        paths[category_id] = path
        return path

    for category in categories:
        get_path(category.category_id)

    return paths


def get_product_categories(db, product_id):
    """Отримує категорії конкретного товару."""

    links = db.query(ProductCategory).filter(
        ProductCategory.product_id == product_id
    ).all()

    categories = []

    for link in links:
        category = db.query(Category).filter(
            Category.category_id == link.category_id
        ).first()

        if category:
            categories.append(category)

    return categories


def prepare_product_response(product, db):
    """Формує повну відповідь із даними товару."""

    categories = get_product_categories(db, product.product_id)
    all_categories = db.query(Category).all()
    paths = build_category_paths(all_categories)

    result = {
        column.name: getattr(product, column.name)
        for column in Product.__table__.columns
    }

    # Категорії
    result["categories"] = [
        {
            "category_id": category.category_id,
            "name": category.name,
            "category_path": paths[category.category_id]
        }
        for category in categories
    ]

    # Зображення
    images = db.query(ProductImage).filter(
        ProductImage.product_id == product.product_id
    ).order_by(ProductImage.sort_order).all()

    result["images"] = images

    # Характеристики
    attributes = db.query(ProductAttribute).filter(
        ProductAttribute.product_id == product.product_id
    ).order_by(ProductAttribute.sort_order).all()

    result["attributes"] = attributes

    # Виробник
    if product.manufacturer:
        result["manufacturer"] = {
            "manufacturer_id": product.manufacturer.manufacturer_id,
            "name": product.manufacturer.name,
            "description": product.manufacturer.description
        }
    else:
        result["manufacturer"] = None

    # Магазини
    stores = db.query(ProductStore, Store).join(
        Store,
        ProductStore.store_id == Store.store_id
    ).filter(
        ProductStore.product_id == product.product_id
    ).all()

    result["stores"] = [
        {
            "product_store_id": link.product_store_id,
            "store_id": store.store_id,
            "store_name": store.name
        }
        for link, store in stores
    ]

    return result


def validate_category_ids(db, category_ids):
    """Перевіряє існування всіх переданих категорій."""

    unique_ids = set(category_ids)

    if len(unique_ids) != len(category_ids):
        raise HTTPException(
            status_code=400,
            detail="Duplicate category IDs are not allowed"
        )

    if not unique_ids:
        return

    existing_ids = {
        row[0]
        for row in db.query(Category.category_id).filter(
            Category.category_id.in_(unique_ids)
        ).all()
    }

    missing_ids = unique_ids - existing_ids

    if missing_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Categories not found: {sorted(missing_ids)}"
        )


def set_product_categories(db, product, category_ids):
    """Замінює прив'язки товару до категорій."""

    validate_category_ids(db, category_ids)

    db.query(ProductCategory).filter(
        ProductCategory.product_id == product.product_id
    ).delete(synchronize_session=False)

    for category_id in category_ids:
        db.add(
            ProductCategory(
                product_id=product.product_id,
                category_id=category_id
            )
        )



# CREATE — створення товару
@router.post("", response_model=ProductResponse, status_code=201)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db)
):
    data = product_data.model_dump(
        exclude={"category_ids", "images", "attributes"}
    )

    category_ids = product_data.category_ids

    # Перевіряємо категорії
    validate_category_ids(db, category_ids)

    # Створюємо товар
    product = Product(**data)
    db.add(product)
    db.flush()

    # Додаємо категорії
    set_product_categories(db, product, category_ids)

    # Додаємо зображення
    for image_data in product_data.images:
        image = ProductImage(
            product_id=product.product_id,
            **image_data.model_dump()
        )
        db.add(image)

    # Додаємо характеристики
    for attribute_data in product_data.attributes:
        attribute = ProductAttribute(
            product_id=product.product_id,
            **attribute_data.model_dump()
        )
        db.add(attribute)

    db.commit()
    db.refresh(product)

    return prepare_product_response(product, db)


# READ — список товарів із фільтрами та сортуванням
@router.get("", response_model=list[ProductListItem])
def get_products(
    category_id: int | None = Query(default=None, ge=1),
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    search: str | None = Query(default=None),
    sort: str = Query(
        default="name_asc",
        pattern="^(name_asc|name_desc|price_asc|price_desc|category_asc|category_desc)$"
    ),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Product)

    if category_id is not None:
        query = query.join(
            ProductCategory,
            Product.product_id == ProductCategory.product_id
        ).filter(
            ProductCategory.category_id == category_id
        )

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if min_price is not None and max_price is not None:
        if min_price > max_price:
            raise HTTPException(
                status_code=400,
                detail="min_price cannot be greater than max_price"
            )

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    products = query.distinct().all()

    all_categories = db.query(Category).all()
    paths = build_category_paths(all_categories)

    product_paths = {}

    for product in products:
        categories = get_product_categories(db, product.product_id)

        product_paths[product.product_id] = sorted(
            paths[category.category_id]
            for category in categories
            if category.category_id in paths
        )

    if sort == "name_asc":
        products.sort(key=lambda item: item.name.lower())

    elif sort == "name_desc":
        products.sort(
            key=lambda item: item.name.lower(),
            reverse=True
        )

    elif sort == "price_asc":
        products.sort(
            key=lambda item: (
                item.price is None,
                item.price if item.price is not None else Decimal("0")
            )
        )

    elif sort == "price_desc":
        products.sort(
            key=lambda item: (
                item.price is None,
                -(item.price if item.price is not None else Decimal("0"))
            )
        )

    elif sort == "category_asc":
        products.sort(
            key=lambda item: product_paths[item.product_id]
        )

    elif sort == "category_desc":
        products.sort(
            key=lambda item: product_paths[item.product_id],
            reverse=True
        )

    start = (page - 1) * limit
    paginated_products = products[start:start + limit]

    return [
        {
            "product_id": product.product_id,
            "name": product.name,
            "category_path": " | ".join(
                product_paths[product.product_id]
            ),
            "price": product.price,
            "status": product.status
        }
        for product in paginated_products
    ]


# READ — деталі одного товару
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return prepare_product_response(product, db)


# UPDATE — часткове оновлення товару
@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    update_data = product_data.model_dump(exclude_unset=True)

    category_ids = update_data.pop("category_ids", None)

    for field, value in update_data.items():
        setattr(product, field, value)

    if category_ids is not None:
        set_product_categories(db, product, category_ids)

    db.commit()
    db.refresh(product)

    return prepare_product_response(product, db)


# DELETE — видалення товару та його зв'язків
@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()

    return {
        "message": "Product and its category links deleted successfully"
    }



# ============ PRODUCT IMAGES ===============================


# GET — список зображень товару
@router.get(
    "/{product_id}/image",
    response_model=list[ProductImageResponse]
)
def get_product_images(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return db.query(ProductImage).filter(
        ProductImage.product_id == product_id
    ).order_by(ProductImage.sort_order).all()


# GET — одне зображення товару
@router.get(
    "/{product_id}/image/{product_image_id}",
    response_model=ProductImageResponse
)
def get_product_image(
    product_id: int,
    product_image_id: int,
    db: Session = Depends(get_db)
):
    image = db.query(ProductImage).filter(
        ProductImage.product_id == product_id,
        ProductImage.product_image_id == product_image_id
    ).first()

    if not image:
        raise HTTPException(
            status_code=404,
            detail="Product image not found"
        )

    return image


# POST — додавання зображення
@router.post(
    "/{product_id}/image",
    response_model=ProductImageResponse,
    status_code=201
)
def create_product_image(
    product_id: int,
    image_data: ProductImageCreate,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    image = ProductImage(
        product_id=product_id,
        image=image_data.image,
        sort_order=image_data.sort_order
    )

    db.add(image)
    db.commit()
    db.refresh(image)

    return image


# PATCH — зміна порядку зображення
@router.patch(
    "/{product_id}/image/{product_image_id}",
    response_model=ProductImageResponse
)
def update_product_image(
    product_id: int,
    product_image_id: int,
    image_data: ProductImageUpdate,
    db: Session = Depends(get_db)
):
    image = db.query(ProductImage).filter(
        ProductImage.product_id == product_id,
        ProductImage.product_image_id == product_image_id
    ).first()

    if not image:
        raise HTTPException(
            status_code=404,
            detail="Product image not found"
        )

    image.sort_order = image_data.sort_order

    db.commit()
    db.refresh(image)

    return image


# DELETE — видалення зображення
@router.delete(
    "/{product_id}/image/{product_image_id}"
)
def delete_product_image(
    product_id: int,
    product_image_id: int,
    db: Session = Depends(get_db)
):
    image = db.query(ProductImage).filter(
        ProductImage.product_id == product_id,
        ProductImage.product_image_id == product_image_id
    ).first()

    if not image:
        raise HTTPException(
            status_code=404,
            detail="Product image not found"
        )

    db.delete(image)
    db.commit()

    return {
        "message": "Product image deleted successfully"
    }


# ================ PRODUCT ATTRIBUTES ==================================


# GET — список атрибутів товару
@router.get(
    "/{product_id}/attribute",
    response_model=list[ProductAttributeResponse]
)
def get_product_attributes(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return db.query(ProductAttribute).filter(
        ProductAttribute.product_id == product_id
    ).order_by(ProductAttribute.sort_order).all()


# GET — один атрибут
@router.get(
    "/{product_id}/attribute/{product_attribute_id}",
    response_model=ProductAttributeResponse
)
def get_product_attribute(
    product_id: int,
    product_attribute_id: int,
    db: Session = Depends(get_db)
):
    attribute = db.query(ProductAttribute).filter(
        ProductAttribute.product_id == product_id,
        ProductAttribute.product_attribute_id == product_attribute_id
    ).first()

    if not attribute:
        raise HTTPException(
            status_code=404,
            detail="Product attribute not found"
        )

    return attribute


# POST — створення атрибута
@router.post(
    "/{product_id}/attribute",
    response_model=ProductAttributeResponse,
    status_code=201
)
def create_product_attribute(
    product_id: int,
    attribute_data: ProductAttributeCreate,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    attribute = ProductAttribute(
        product_id=product_id,
        **attribute_data.model_dump()
    )

    db.add(attribute)
    db.commit()
    db.refresh(attribute)

    return attribute


# PATCH — оновлення атрибута
@router.patch(
    "/{product_id}/attribute/{product_attribute_id}",
    response_model=ProductAttributeResponse
)
def update_product_attribute(
    product_id: int,
    product_attribute_id: int,
    attribute_data: ProductAttributeUpdate,
    db: Session = Depends(get_db)
):
    attribute = db.query(ProductAttribute).filter(
        ProductAttribute.product_id == product_id,
        ProductAttribute.product_attribute_id == product_attribute_id
    ).first()

    if not attribute:
        raise HTTPException(
            status_code=404,
            detail="Product attribute not found"
        )

    update_data = attribute_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(attribute, field, value)

    db.commit()
    db.refresh(attribute)

    return attribute


# DELETE — видалення атрибута
@router.delete(
    "/{product_id}/attribute/{product_attribute_id}"
)
def delete_product_attribute(
    product_id: int,
    product_attribute_id: int,
    db: Session = Depends(get_db)
):
    attribute = db.query(ProductAttribute).filter(
        ProductAttribute.product_id == product_id,
        ProductAttribute.product_attribute_id == product_attribute_id
    ).first()

    if not attribute:
        raise HTTPException(
            status_code=404,
            detail="Product attribute not found"
        )

    db.delete(attribute)
    db.commit()

    return {
        "message": "Product attribute deleted successfully"
    }

# ================ PRODUCT STORES ==================================

# GET — усі магазини товару
@router.get("/{product_id}/store")
def get_product_stores(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    stores = db.query(ProductStore, Store).join(
        Store,
        ProductStore.store_id == Store.store_id
    ).filter(
        ProductStore.product_id == product_id
    ).all()

    return [
        {
            "product_store_id": link.product_store_id,
            "product_id": link.product_id,
            "store_id": store.store_id,
            "store_name": store.name
        }
        for link, store in stores
    ]


# GET — конкретний магазин товару
@router.get("/{product_id}/store/{product_store_id}")
def get_product_store(
    product_id: int,
    product_store_id: int,
    db: Session = Depends(get_db)
):
    result = db.query(ProductStore, Store).join(
        Store,
        ProductStore.store_id == Store.store_id
    ).filter(
        ProductStore.product_id == product_id,
        ProductStore.product_store_id == product_store_id
    ).first()

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Product store not found"
        )

    link, store = result

    return {
        "product_store_id": link.product_store_id,
        "product_id": link.product_id,
        "store_id": store.store_id,
        "store_name": store.name
    }
