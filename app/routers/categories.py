
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListItem,
)


router = APIRouter(
    prefix="/category",
    tags=["Category"]
)


def build_category_paths(categories):
    """Створює повний ієрархічний шлях для кожної категорії."""

    category_map = {category.category_id: category for category in categories}
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
            parent_path = get_path(category.parent_category_id, visited)
            path = f"{parent_path} > {category.name}"
        else:
            path = category.name

        paths[category_id] = path
        return path

    for category in categories:
        get_path(category.category_id)

    return paths


def get_tree_order(categories):
    """Повертає категорії в порядку дерева: батько, потім нащадки."""

    children = {}

    for category in categories:
        children.setdefault(category.parent_category_id, []).append(category)

    for items in children.values():
        items.sort(key=lambda item: item.name.lower())

    result = []

    def add_children(parent_id):
        for category in children.get(parent_id, []):
            result.append(category)
            add_children(category.category_id)

    add_children(None)

    return result


def validate_parent(db, parent_id, category_id=None):
    """Перевіряє існування батьківської категорії та відсутність циклу."""

    if parent_id in (None, 0):
        return

    parent = db.query(Category).filter(
        Category.category_id == parent_id
    ).first()

    if not parent:
        raise HTTPException(
            status_code=404,
            detail="Parent category not found"
        )

    if category_id is None:
        return

    if parent_id == category_id:
        raise HTTPException(
            status_code=400,
            detail="Category cannot be its own parent"
        )

    current_id = parent_id

    while current_id is not None:
        if current_id == category_id:
            raise HTTPException(
                status_code=400,
                detail="Cannot move category into its own descendants"
            )

        current = db.query(Category).filter(
            Category.category_id == current_id
        ).first()

        if not current:
            break

        current_id = current.parent_category_id


# CREATE
@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db)
):
    validate_parent(db, category_data.parent_category_id)

    data = category_data.model_dump()

    if data["parent_category_id"] == 0:
        data["parent_category_id"] = None

    category = Category(**data)

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


# READ — список категорій, пошук, фільтри, сортування, пагінація
@router.get("", response_model=list[CategoryListItem])
def get_categories(
    category_id: int | None = Query(default=None, ge=1),
    search: str | None = Query(default=None),
    status: int | None = Query(default=None, ge=0, le=1),
    sort: str = Query(
        default="tree",
        pattern="^(tree|name_asc|name_desc|path_asc|path_desc|id_asc|id_desc)$"
    ),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Category)

    if category_id is not None:
        query = query.filter(Category.category_id == category_id)

    if search:
        query = query.filter(Category.name.ilike(f"%{search}%"))

    if status is not None:
        query = query.filter(Category.status == status)

    all_categories = db.query(Category).all()
    paths = build_category_paths(all_categories)

    categories = query.all()

    if sort == "tree":
        ordered_ids = [
            item.category_id for item in get_tree_order(all_categories)
        ]
        order_map = {category_id: index for index, category_id in enumerate(ordered_ids)}
        categories.sort(key=lambda item: order_map.get(item.category_id, 999999))   
    elif sort == "name_asc":
        categories.sort(key=lambda item: item.name.lower())
    elif sort == "name_desc":
        categories.sort(key=lambda item: item.name.lower(), reverse=True)
    elif sort == "path_asc":
        categories.sort(key=lambda item: paths[item.category_id].lower())
    elif sort == "path_desc":
        categories.sort(
            key=lambda item: paths[item.category_id].lower(),
            reverse=True
        )
    elif sort == "id_asc":
        categories.sort(key=lambda item: item.category_id)
    elif sort == "id_desc":
        categories.sort(key=lambda item: item.category_id, reverse=True)

    start = (page - 1) * limit
    paginated_categories = categories[start:start + limit]

    return [
        {
            "category_id": category.category_id,
            "name": category.name,
            "category_path": paths[category.category_id],
            "status": category.status,
            "status_label": (
                "Enabled" if category.status == 1 else "Disabled"
            )
        }
        for category in paginated_categories
    ]


# READ — одна категорія з усіма полями
@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.category_id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category


# UPDATE — часткове оновлення
@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.category_id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    update_data = category_data.model_dump(exclude_unset=True)

    if update_data.get("parent_category_id") == 0:
        update_data["parent_category_id"] = None

    if "parent_category_id" in update_data:
        validate_parent(
            db,
            update_data["parent_category_id"],
            category_id
        )

    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)

    return category


# DELETE — видалення категорії разом із дочірніми
@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.category_id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    db.delete(category)
    db.commit()

    return {
        "message": "Category and its child categories deleted successfully"
    }
