# SHOP-API

REST API для управління товарами та категоріями інтернет-магазину.

## Технології

- Python 3.13
- FastAPI
- SQLAlchemy
- MySQL 8.4
- Docker та Docker Compose
- phpMyAdmin
- Apache HTTP Server 2.4
- Pydantic
- Uvicorn

## Функціональність

### Category

- Перегляд списку категорій.
- Перегляд категорії за ID.
- Створення та редагування категорій.
- Рекурсивне видалення підкатегорій.
- Ієрархія категорій із повним шляхом.
- Пошук, фільтрація, сортування та пагінація.

### Product

- Перегляд списку товарів.
- Детальна інформація про товар.
- Створення товару разом із категоріями, зображеннями та характеристиками.
- Редагування та видалення товарів.
- Фільтрація за категорією та ціною.
- Сортування та пагінація.
- Управління додатковими зображеннями.
- Управління характеристиками товарів.
- Управління зв'язками товарів із категоріями.
- Отримання інформації про виробника та магазини товару.

## Структура бази даних

Основні таблиці:

- `categories` — категорії товарів.
- `products` — товари.
- `product_category` — зв'язок товарів із категоріями.
- `product_image` — додаткові зображення.
- `product_attribute` — характеристики товарів.
- `manufacturers` — виробники.
- `stores` — магазини.
- `product_store` — зв'язок товарів із магазинами.

## Встановлення та запуск

### 1. Клонування проєкту

```bash
git clone https://github.com/Irka-Bodnariuk/shop-api.git
cd shop-api
```

### 2. Створення віртуального середовища

```bash
python -m venv .venv
```

Активація у Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Встановлення залежностей

```bash
pip install -r requirements.txt
```

### 4. Запуск Docker-сервісів

```bash
docker compose up -d
```

Перевірка контейнерів:

```bash
docker compose ps
```

### 5. Запуск FastAPI

```bash
uvicorn app.main:app --reload
```

## Адреси сервісів

| Сервіс     | Адреса                      |
| ---------- | --------------------------- |
| FastAPI    | http://localhost:8000       |
| Swagger UI | http://localhost:8000/docs  |
| ReDoc      | http://localhost:8000/redoc |
| phpMyAdmin | http://localhost:8080       |
| Apache2    | http://localhost:8081       |

## Підключення до MySQL

- Host: `localhost`
- Port: `3306`
- Database: `shop_db`
- User: `shop_user`
- Password: значення `MYSQL_PASSWORD` у `docker-compose.yml`

Для phpMyAdmin як сервер бази даних використовується `db`.

## Тестування API

Для тестування API використовується Swagger UI.

Відкрий:

http://localhost:8000/docs

Swagger дозволяє виконувати GET, POST, PATCH та DELETE запити, переглядати параметри й отримувати відповіді API.

## Зупинка Docker

```bash
docker compose down
```

Дані MySQL зберігаються у Docker volume `mysql_data`.

Для зупинки контейнерів без видалення даних використовуйте `docker compose down`.

## Авторизація

Авторизація користувачів у межах поточної реалізації не передбачена.
