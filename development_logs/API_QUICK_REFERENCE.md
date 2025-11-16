# BikeShop API - Quick Reference

**Base URL:** `http://localhost:8000/api/`  
**Auth Header:** `Authorization: Bearer <token>`

---

## 🔐 Authentication (No Auth Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register/` | Register new user (returns token) |
| POST | `/auth/login/` | Login user (returns token) |

**Register/Login Request:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "password123"
}
```

**Response:**
```json
{
  "user": { "id": 1, "email": "...", "name": "..." },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 👤 User Profile (Auth Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/auth/profile/` | Get current user profile |
| PATCH | `/auth/profile/` | Update profile (name, phone) |
| POST | `/auth/change-password/` | Change password |

---

## 📍 Address Management (Auth Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/auth/addresses/` | List all user addresses |
| POST | `/auth/addresses/` | Create new address |
| PATCH | `/auth/addresses/{id}/` | Update address |
| DELETE | `/auth/addresses/{id}/` | Delete address |

---

## 🛍️ Products (Public)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products/` | List products (paginated) |
| GET | `/products/{slug}/` | Get product detail |

**Product Filters:**
```
?category=helmets           - Filter by category
?brand=giro                 - Filter by brand
?min_price=5000             - Minimum price
?max_price=15000            - Maximum price
?is_featured=true           - Featured products only
?on_sale=true              - On-sale products only
?search=helmet              - Search in title/description
?ordering=-price            - Sort by price (desc)
?ordering=created_at        - Sort by date (asc)
?page=2                     - Page number
?page_size=20               - Items per page
```

**Response Format:**
```json
{
  "data": [...],
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 5,
    "per_page": 20,
    "to": 20,
    "total": 95,
    "links": [...]
  }
}
```

---

## 📂 Categories (Public)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/categories/` | List all categories |
| GET | `/categories/{slug}/` | Get category with products |

---

## 🏷️ Brands (Public)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/brands/` | List all brands |
| GET | `/brands/{slug}/` | Get brand with products |

---

## 🛒 Cart (Public - Works for Both Guest & Authenticated)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cart/` | Get current cart |
| POST | `/cart/items/` | Add item to cart |
| PATCH | `/cart/items/{id}/` | Update item quantity |
| DELETE | `/cart/items/{id}/` | Remove item from cart |
| DELETE | `/cart/clear/` | Clear entire cart |

**Add to Cart Request:**
```json
{
  "variant_id": 1,
  "quantity": 2
}
```

**Update Cart Item Request:**
```json
{
  "quantity": 3
}
```

**Cart Response:**
```json
{
  "id": 1,
  "items": [
    {
      "id": 1,
      "variant": {
        "id": 1,
        "sku": "GIRO-SYNTAX-RED-M",
        "product": {
          "id": 1,
          "title": "Giro Helmet",
          "slug": "giro-helmet",
          "primary_image": "http://..."
        },
        "price": "12500.00",
        "sale_price": "10000.00",
        "attributes": [
          {"type": "Color", "value": "Red"},
          {"type": "Size", "value": "Medium"}
        ]
      },
      "quantity": 2,
      "price_snapshot": "10000.00",
      "total": "20000.00",
      "savings": "5000.00",
      "is_available": true
    }
  ],
  "total_items": 2,
  "subtotal": "20000.00",
  "total_savings": "5000.00"
}
```

---

## 🏠 Homepage (Public)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/homepage/` | Get banners and featured sections |

**Response:**
```json
{
  "banners": [
    {
      "id": 1,
      "title": "New Helmet Collection",
      "subtitle": "Premium protection",
      "image": "http://...",
      "image_mobile": "http://...",
      "link_product": {"id": 1, "title": "...", "slug": "..."},
      "button_text": "Shop Now",
      "display_order": 0
    }
  ],
  "featured_sections": [
    {
      "id": 1,
      "title": "New Arrivals",
      "subtitle": "Latest products",
      "section_type": "new",
      "products": [...]
    }
  ]
}
```

---

## 📊 Complete Endpoint List (21 Total)

### Authentication & User (5)
```
POST   /api/auth/register/
POST   /api/auth/login/
GET    /api/auth/profile/
PATCH  /api/auth/profile/
POST   /api/auth/change-password/
```

### Address Management (4)
```
GET    /api/auth/addresses/
POST   /api/auth/addresses/
PATCH  /api/auth/addresses/{id}/
DELETE /api/auth/addresses/{id}/
```

### Products (2)
```
GET    /api/products/
GET    /api/products/{slug}/
```

### Categories (2)
```
GET    /api/categories/
GET    /api/categories/{slug}/
```

### Brands (2)
```
GET    /api/brands/
GET    /api/brands/{slug}/
```

### Cart (5)
```
GET    /api/cart/
POST   /api/cart/items/
PATCH  /api/cart/items/{id}/
DELETE /api/cart/items/{id}/
DELETE /api/cart/clear/
```

### Homepage (1)
```
GET    /api/homepage/
```

---

## 🔧 Integration Example (React + Axios)

```javascript
// api/client.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  headers: { 'Content-Type': 'application/json' }
});

// Add token to all requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;

// Usage Examples
import api from './api/client';

// Register
const register = async (email, name, password) => {
  const { data } = await api.post('auth/register/', { email, name, password });
  localStorage.setItem('token', data.token);
  return data;
};

// Get Products
const getProducts = async (filters = {}) => {
  const { data } = await api.get('products/', { params: filters });
  return data;
};

// Add to Cart
const addToCart = async (variant_id, quantity) => {
  const { data } = await api.post('cart/items/', { variant_id, quantity });
  return data;
};

// Get Cart
const getCart = async () => {
  const { data } = await api.get('cart/');
  return data;
};
```

---

## ⚠️ Error Handling

### Status Codes
- `200 OK` - Success (GET, PATCH)
- `201 Created` - Success (POST)
- `204 No Content` - Success (DELETE)
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Auth required/invalid
- `404 Not Found` - Resource not found
- `500 Server Error` - Server error

### Error Response Format
```json
{
  "field_name": ["Error message"],
  "another_field": ["Another error"]
}
```

Or:
```json
{
  "detail": "Error message"
}
```

---

## 🎯 Key Features

✅ **JWT Authentication** - 7-day token validity, no refresh  
✅ **Guest Cart** - Works without authentication  
✅ **User Cart** - Persists across sessions  
✅ **Auto Cart Merge** - Guest cart merges on login  
✅ **Stock Validation** - Prevents overselling  
✅ **Price Snapshot** - Preserves prices in cart  
✅ **Laravel Pagination** - Standard pagination format  
✅ **Advanced Filtering** - Multiple filter options  
✅ **Full-Text Search** - Search products  
✅ **CORS Enabled** - Ready for frontend (localhost:3000)  

---

## 📚 More Documentation

- **`API_ENDPOINTS_LIST.md`** - Complete API documentation with examples
- **`API_TESTING_CHECKLIST.md`** - Testing guide and checklist
- **`REST_API_IMPLEMENTATION_LOG.md`** - Technical implementation details

---

**All 21 endpoints are ready for frontend integration! 🚀**
