# ShopEase Product Catalog & Inventory Microservice

An independent FastAPI microservice responsible for managing product categories, products, pricing, search/filtering, and concurrency-safe inventory operations within the ShopEase e-commerce platform.

## Architecture & Tech Stack
- **Framework:** FastAPI (Python 3.11)
- **Database:** MySQL 8.0 (\shopease_product_catalog_db\)
- **ORM:** SQLAlchemy 2.0 (Row-level pessimistic locking via \with_for_update()\)
- **Migrations:** Alembic (Baseline revision: \eb2eecfc89a8\)
- **Authentication & RBAC:** Stateless JWT validation with Role-Based Access Control (\dmin\ vs \customer\)
- **Containerization:** Docker & Docker Compose

## Port Mappings
- **Product Catalog Service:** \http://localhost:8003\ (Swagger Docs: \http://localhost:8003/docs\)
- **Catalog MySQL Database:** \localhost:3311\ (mapped from internal port \3306\)

## Folder Structure
\\\	ext
shopease-product-catalog-service/
├── app/
│   ├── main.py
│   ├── routers/
│   │   ├── category_routes.py
│   │   ├── product_routes.py
│   │   └── inventory_routes.py
│   ├── models/
│   │   ├── category_model.py
│   │   ├── product_model.py
│   │   └── inventory_model.py
│   ├── schemas/
│   │   ├── category_schema.py
│   │   ├── product_schema.py
│   │   └── inventory_schema.py
│   ├── services/
│   │   ├── category_service.py
│   │   ├── product_service.py
│   │   └── inventory_service.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   └── database/
│       └── connection.py
├── alembic/
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
├── .gitignore
└── README.md
\\\

## Environment Configuration
Configure via \.env\ (excluded from version control):
\\\env
APP_NAME=ShopEase Product Catalog Service
ENVIRONMENT=development
PORT=8003
DATABASE_URL=mysql+pymysql://shopease_catalog_user:catalog_secure_password_2026@catalog_mysql:3306/shopease_product_catalog_db
SECRET_KEY=shopease_super_secret_jwt_key_2026_secure
ALGORITHM=HS256
LOW_STOCK_THRESHOLD=10
\\\

## API Endpoints Matrix

### 1. Category Management (\/api/categories\)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| **POST** | \/api/categories/\ | Admin | Create a new unique category |
| **GET** | \/api/categories/\ | Public | List active categories |
| **GET** | \/api/categories/{id}\ | Public | Get category details |
| **PUT** | \/api/categories/{id}\ | Admin | Update category name/status |
| **DELETE** | \/api/categories/{id}\ | Admin | Delete category (blocked if products are linked) |

### 2. Product Management (\/api/products\)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| **POST** | \/api/products/\ | Admin | Create product (validates category & unique SKU) |
| **GET** | \/api/products/\ | Public | Search, filter, sort, and paginate active products |
| **GET** | \/api/products/{id}\ | Public | Retrieve single active product details |
| **PUT** | \/api/products/{id}\ | Admin | Full product update |
| **PATCH** | \/api/products/{id}\ | Admin | Partial product update / activation toggle |
| **DELETE** | \/api/products/{id}\ | Admin | Delete product and cascade inventory history |

### 3. Inventory Management (\/api/inventory\)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| **GET** | \/api/inventory/{product_id}\ | Admin | Check current stock level |
| **POST** | \/api/inventory/{product_id}/stock-in\ | Admin | Atomic stock increase + audit transaction |
| **POST** | \/api/inventory/{product_id}/stock-out\ | Admin | Atomic stock decrease (prevents negative stock) |
| **GET** | \/api/inventory/{product_id}/history\ | Admin | View chronological stock movement audit log |
| **GET** | \/api/inventory/low-stock\ | Admin | List active products at or below threshold |

## Search, Filtering & Pagination Examples
\\\ash
# Search by name/SKU/brand with price boundaries
GET /api/products/?search=Galaxy&min_price=50000&max_price=90000

# Filter by category with descending price sort and pagination
GET /api/products/?category_id=1&page=1&page_size=10&sort_by=price&sort_order=desc
\\\

## Docker Setup & Alembic Migrations
\\\ash
# Launch service and MySQL containers
docker compose up -d --build

# Generate and apply database migrations
docker compose exec catalog_service alembic revision --autogenerate -m "create categories products and inventory tables"
docker compose exec catalog_service alembic upgrade head
\\\

## Automated Verification Summary (20/20 Passed)
- **Category & Product Validation:** Verified unique category names, unique SKUs, invalid category rejection (\404\), and negative price rejection (\422\).
- **Query Engine:** Verified keyword search, price range filtering, pagination, and multi-column sorting.
- **Inventory & Concurrency:** Verified \stock-in\, \stock-out\, negative stock prevention (\400\), transaction audit logs, low-stock alerts, and row-level locking across 5 simultaneous stock updates.
- **Security & RBAC:** Verified \401 Unauthorized\ for missing/invalid tokens and \403 Forbidden\ when customer tokens access admin routes.
