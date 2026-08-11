# StockSwap-backend REST API

**StockSwap** is a peer-to-peer e-commerce marketplace API built with Django 5 and Django REST Framework (DRF). Every registered user acts as both a buyer and a seller, managing their own shop, listing products, and purchasing products from other shops across the marketplace.

---

## 🚀 Key Features & Architectural Rules

1. **Dual Role Architecture**: Every user has exactly one shop (`Shop` model, 1:1 relationship with `User`). Users can create product listings for their shop and buy items from other users' shops.
2. **Self-Purchase Prevention**: Enforced at the database transaction level—a user cannot buy products from their own shop.
3. **Stock Safety & Atomic Transactions**: Purchases use database row locks (`select_for_update()`) inside atomic transactions. Stock (`quantity`) is decremented safely and can never drop below zero.
4. **Historical Price Protection**: `Order` objects record `price_at_purchase` when an order is created, preserving historical financial records even if the seller updates product pricing later.
5. **Stock Visibility**: Out-of-stock products (`quantity = 0`) are hidden from marketplace browsing/search endpoints (`/api/product/` and `/api/product/category/<category>/`), but remain visible in the seller's own listings (`/api/product/user/<user>/`) and in past order histories.
6. **Token Authentication**: Header `Authorization: Token <token>` required for all protected endpoints.

---

## ⚙️ Environment Variables

The project reads settings from environment variables with sensible defaults for local development:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `SECRET_KEY` | Secret key for Django cryptographic signing | `django-insecure-stockswap-default-secret-key-2026` |
| `DEBUG` | Enable/disable debug mode (`True`/`False`) | `True` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hostnames | `localhost,127.0.0.1,0.0.0.0,*` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated list of allowed frontend origins | `http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173` |
| `CORS_ALLOW_ALL_ORIGINS` | Allow all origins in development (`True`/`False`) | `True` |

---

## 🛠️ Quickstart & Local Setup

```bash
# 1. Clone the repository
cd StockSwap-backend

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply database migrations
python manage.py makemigrations
python manage.py migrate

# 5. Seed demo users, shops, and products
python manage.py seed_demo

# 6. Start the local server
python manage.py runserver 0.0.0.0:8000
```

---

## 🔑 Demo Credentials

After running `python manage.py seed_demo`, the following accounts are pre-populated:

| Email | Password | Shop Name | Role / Focus |
| :--- | :--- | :--- | :--- |
| `techstore@stockswap.com` | `pass1234` | **TechVault Electronics** | Electronics seller (Headphones, Keyboards, SSDs) |
| `apparelhub@stockswap.com` | `pass1234` | **Urban Threads Boutique** | Apparel seller (Hoodies, Leather Bags) |
| `homegoods@stockswap.com` | `pass1234` | **Cornerstone Living** | Home & Kitchen seller (Espresso Cups, Desk Trays) |

---

## 📡 API Contract & Route Reference

### 1. Authentication Routes

#### POST `/api/auth/register/`
Create a new user account and shop.
- **Auth Required**: No
- **Request Body**:
```json
{
  "name": "Sarah Connor",
  "email": "sarah@cyberdyne.com",
  "password": "SecurePassword123!",
  "shop_name": "Resistance Supply",
  "phone": "+1-555-0199",
  "address": "42 Tech Way, Los Angeles, CA"
}
```
- **Response** (`201 Created`):
```json
{
  "token": "a1b2c3d4e5f67890123456789abcdef012345678",
  "user": {
    "id": 4,
    "username": "sarah@cyberdyne.com",
    "email": "sarah@cyberdyne.com",
    "name": "Sarah Connor",
    "shop": {
      "id": 4,
      "shop_name": "Resistance Supply",
      "phone": "+1-555-0199",
      "address": "42 Tech Way, Los Angeles, CA",
      "created_at": "2026-08-11T00:30:00Z"
    }
  }
}
```

#### POST `/api/auth/login/`
Authenticate with email and password.
- **Auth Required**: No
- **Request Body**:
```json
{
  "email": "techstore@stockswap.com",
  "password": "pass1234"
}
```
- **Response** (`200 OK`):
```json
{
  "token": "f9e8d7c6b5a43210987654321fedcba098765432",
  "user": {
    "id": 1,
    "username": "techstore@stockswap.com",
    "email": "techstore@stockswap.com",
    "name": "Alex Rivera",
    "shop": {
      "id": 1,
      "shop_name": "TechVault Electronics",
      "phone": "+1-555-0192",
      "address": "101 Silicon Way, San Jose, CA",
      "created_at": "2026-08-11T00:00:00Z"
    }
  }
}
```

#### POST `/api/auth/logout/`
Invalidate current auth token.
- **Auth Required**: Yes (`Authorization: Token <token>`)
- **Response** (`200 OK`):
```json
{
  "detail": "Successfully logged out."
}
```

#### GET `/api/auth/me/`
Fetch current user profile and shop.
- **Auth Required**: Yes (`Authorization: Token <token>`)
- **Response** (`200 OK`):
```json
{
  "id": 1,
  "username": "techstore@stockswap.com",
  "email": "techstore@stockswap.com",
  "name": "Alex Rivera",
  "shop": {
    "id": 1,
    "shop_name": "TechVault Electronics",
    "phone": "+1-555-0192",
    "address": "101 Silicon Way, San Jose, CA",
    "created_at": "2026-08-11T00:00:00Z"
  }
}
```

---

### 2. Product Marketplace Routes

#### GET `/api/product/`
List in-stock products (`quantity > 0`). Optional search query `?search=<keyword>`.
- **Auth Required**: No
- **Response** (`200 OK`):
```json
[
  {
    "id": 1,
    "name": "Wireless Noise-Canceling Headphones",
    "description": "Studio headphones with active noise cancellation.",
    "category": "Electronics",
    "price": "149.99",
    "quantity": 15,
    "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600",
    "created_at": "2026-08-11T00:00:00Z",
    "shop_name": "TechVault Electronics",
    "seller_username": "techstore@stockswap.com",
    "owner_id": 1
  }
]
```

#### POST `/api/product/`
Create a new product listing for logged-in user's shop.
- **Auth Required**: Yes (`Authorization: Token <token>`)
- **Request Body**:
```json
{
  "name": "Smart Fitness Watch V2",
  "description": "Waterproof AMOLED GPS fitness tracker.",
  "category": "Electronics",
  "price": 199.00,
  "quantity": 10,
  "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600"
}
```
- **Response** (`201 Created`):
```json
{
  "id": 8,
  "name": "Smart Fitness Watch V2",
  "description": "Waterproof AMOLED GPS fitness tracker.",
  "category": "Electronics",
  "price": "199.00",
  "quantity": 10,
  "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600",
  "created_at": "2026-08-11T00:35:00Z",
  "shop_name": "TechVault Electronics",
  "seller_username": "techstore@stockswap.com",
  "owner_id": 1
}
```

#### GET `/api/product/category/<category>/`
Filter products by category (case-insensitive, `quantity > 0`).
- **Example**: `/api/product/category/Apparel/`
- **Response** (`200 OK`): Array of matching Product objects.

#### GET `/api/product/<id>/`
Retrieve detail of a specific product.
- **Example**: `/api/product/1/`
- **Response** (`200 OK`): Product object.

#### PATCH `/api/product/<id>/`
Update a product listing (Owner only).
- **Auth Required**: Yes (`Authorization: Token <token>`)
- **Request Body**:
```json
{
  "price": 139.99,
  "quantity": 25
}
```
- **Response** (`200 OK`): Updated Product object.
- **Non-Owner Response** (`403 Forbidden`):
```json
{
  "detail": "You do not have permission to edit this product."
}
```

#### DELETE `/api/product/<id>/`
Delete a product listing (Owner only).
- **Auth Required**: Yes (`Authorization: Token <token>`)
- **Response** (`200 OK`):
```json
{
  "detail": "Product deleted successfully."
}
```

#### GET `/api/product/user/<user>/`
List all products owned by a shop (including out-of-stock `quantity = 0`). `<user>` accepts user ID or email/username.
- **Example**: `/api/product/user/techstore@stockswap.com/`
- **Response** (`200 OK`): Array of Product objects.

---

### 3. Checkout & Order Routes

#### POST `/api/product/checkout/`
Purchase a product. Immediately marks order as `paid` and decrements product stock inside a database transaction lock.
- **Auth Required**: Yes (`Authorization: Token <token>`)
- **Request Body**:
```json
{
  "product_id": 4,
  "quantity": 2
}
```
- **Response** (`201 Created`):
```json
{
  "id": 2,
  "product": 4,
  "product_name": "Organic Cotton Oversized Hoodie",
  "buyer": 1,
  "buyer_username": "techstore@stockswap.com",
  "buyer_shop_name": "TechVault Electronics",
  "seller": 2,
  "seller_username": "apparelhub@stockswap.com",
  "seller_shop_name": "Urban Threads Boutique",
  "quantity": 2,
  "price_at_purchase": "65.00",
  "total_amount": "130.00",
  "status": "paid",
  "created_at": "2026-08-11T00:36:00Z"
}
```
- **Self-Purchase Error** (`400 Bad Request`):
```json
{
  "detail": "A user cannot buy their own product."
}
```
- **Insufficient Stock Error** (`400 Bad Request`):
```json
{
  "detail": "Requested quantity (50) exceeds available stock (18)."
}
```

#### GET `/api/purchase/`
List sales sold from the logged-in user's shop ("My Sales").
- **Auth Required**: Yes (`Authorization: Token <token>`)
- **Response** (`200 OK`): Array of Order objects where `seller == request.user`.

#### GET `/api/purchase/user/`
List orders bought by the logged-in user ("My Purchases").
- **Auth Required**: Yes (`Authorization: Token <token>`)
- **Response** (`200 OK`): Array of Order objects where `buyer == request.user`.

---

## 🖼️ Media Files in Production

In development, media files are served directly by Django at `/media/`. For production deployments (e.g. Render, Railway, AWS Cloud Run), configure an S3 bucket or persistent volume:
```python
# settings.py production example
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```
