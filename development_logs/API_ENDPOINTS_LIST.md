# BikeShop E-commerce REST API - Complete Endpoints List

**Base URL:** `http://localhost:8000/api/`  
**Authentication:** JWT Bearer Token (7-day validity)  
**Date:** October 20, 2025

---

## 📋 Table of Contents

1. [Authentication & User Management](#authentication--user-management)
2. [Address Management](#address-management)
3. [Products](#products)
4. [Categories](#categories)
5. [Brands](#brands)
6. [Cart Management](#cart-management)
7. [Homepage Content](#homepage-content)
8. [Response Formats](#response-formats)
9. [Error Handling](#error-handling)

---

## 🔐 Authentication & User Management

### 1. Register New User
- **Endpoint:** `POST /api/auth/register/`
- **Auth Required:** No
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "name": "John Doe",
    "password": "securepass123"
  }
  ```
- **Success Response (201):**
  ```json
  {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "phone": null
    },
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
  ```

### 2. Login
- **Endpoint:** `POST /api/auth/login/`
- **Auth Required:** No
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "securepass123"
  }
  ```
- **Success Response (200):**
  ```json
  {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "phone": "+8801712345678"
    },
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
  ```

### 3. Get User Profile
- **Endpoint:** `GET /api/auth/profile/`
- **Auth Required:** Yes
- **Headers:** `Authorization: Bearer <token>`
- **Success Response (200):**
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "phone": "+8801712345678",
    "date_joined": "2025-10-20T10:30:00Z"
  }
  ```

### 4. Update User Profile
- **Endpoint:** `PATCH /api/auth/profile/`
- **Auth Required:** Yes
- **Headers:** `Authorization: Bearer <token>`
- **Request Body:**
  ```json
  {
    "name": "John Smith",
    "phone": "+8801712345678"
  }
  ```
- **Success Response (200):**
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "name": "John Smith",
    "phone": "+8801712345678"
  }
  ```

### 5. Change Password
- **Endpoint:** `POST /api/auth/change-password/`
- **Auth Required:** Yes
- **Headers:** `Authorization: Bearer <token>`
- **Request Body:**
  ```json
  {
    "old_password": "oldpass123",
    "new_password": "newpass456"
  }
  ```
- **Success Response (200):**
  ```json
  {
    "message": "Password changed successfully"
  }
  ```

---

## 📍 Address Management

### 6. List User Addresses
- **Endpoint:** `GET /api/auth/addresses/`
- **Auth Required:** Yes
- **Headers:** `Authorization: Bearer <token>`
- **Success Response (200):**
  ```json
  [
    {
      "id": 1,
      "label": "Home",
      "street": "123 Main St",
      "city": "Dhaka",
      "state": "Dhaka Division",
      "postal_code": "1200",
      "country": "Bangladesh",
      "phone": "+8801712345678",
      "is_default": true
    }
  ]
  ```

### 7. Create Address
- **Endpoint:** `POST /api/auth/addresses/`
- **Auth Required:** Yes
- **Headers:** `Authorization: Bearer <token>`
- **Request Body:**
  ```json
  {
    "label": "Office",
    "street": "456 Work Ave",
    "city": "Dhaka",
    "state": "Dhaka Division",
    "postal_code": "1200",
    "country": "Bangladesh",
    "phone": "+8801712345678",
    "is_default": false
  }
  ```

### 8. Update Address
- **Endpoint:** `PATCH /api/auth/addresses/{id}/`
- **Auth Required:** Yes
- **Headers:** `Authorization: Bearer <token>`
- **Request Body:** (Same as create, all fields optional)

### 9. Delete Address
- **Endpoint:** `DELETE /api/auth/addresses/{id}/`
- **Auth Required:** Yes
- **Headers:** `Authorization: Bearer <token>`
- **Success Response:** 204 No Content

---

## 🛍️ Products

### 10. List Products (with Filters)
- **Endpoint:** `GET /api/products/`
- **Auth Required:** No
- **Query Parameters:**
  - `page` - Page number (default: 1)
  - `page_size` - Items per page (default: 20, max: 100)
  - `category` - Filter by category slug (e.g., `helmets`)
  - `brand` - Filter by brand slug (e.g., `giro`)
  - `min_price` - Minimum price (e.g., `5000`)
  - `max_price` - Maximum price (e.g., `15000`)
  - `search` - Search in title/description (e.g., `helmet`)
  - `is_featured` - Filter featured products (`true`/`false`)
  - `on_sale` - Filter sale products (`true`/`false`)
  - `ordering` - Sort by: `price`, `-price`, `created_at`, `-created_at`, `name`, `-name`

- **Example Request:**
  ```
  GET /api/products/?category=helmets&min_price=5000&max_price=15000&ordering=-created_at
  ```

- **Success Response (200):**
  ```json
  {
    "data": [
      {
        "id": 1,
        "title": "Giro Syntax MIPS Helmet",
        "slug": "giro-syntax-mips-helmet",
        "category": {
          "id": 1,
          "name": "Helmets",
          "slug": "helmets"
        },
        "brand": {
          "id": 1,
          "name": "Giro",
          "slug": "giro"
        },
        "price": "12500.00",
        "sale_price": null,
        "min_price": "10000.00",
        "max_price": "12500.00",
        "is_on_sale": true,
        "discount_percentage": 20,
        "is_featured": true,
        "stock": 16,
        "primary_image": "http://localhost:8000/media/products/helmet.jpg",
        "variant_count": 4
      }
    ],
    "meta": {
      "current_page": 1,
      "from": 1,
      "last_page": 3,
      "links": [...],
      "path": "http://localhost:8000/api/products/",
      "per_page": 20,
      "to": 20,
      "total": 45
    }
  }
  ```

### 11. Get Product Detail
- **Endpoint:** `GET /api/products/{slug}/`
- **Auth Required:** No
- **Success Response (200):**
  ```json
  {
    "id": 1,
    "title": "Giro Syntax MIPS Helmet",
    "slug": "giro-syntax-mips-helmet",
    "description": "Premium road cycling helmet...",
    "category": {
      "id": 1,
      "name": "Helmets",
      "slug": "helmets"
    },
    "brand": {
      "id": 1,
      "name": "Giro",
      "slug": "giro",
      "logo": "http://localhost:8000/media/brands/giro.png"
    },
    "price": "12500.00",
    "sale_price": null,
    "stock": 16,
    "weight": "280.00",
    "is_featured": true,
    "images": [
      {
        "id": 1,
        "image": "http://localhost:8000/media/products/helmet-1.jpg",
        "alt_text": "Front view",
        "position": 0
      }
    ],
    "variants": [
      {
        "id": 1,
        "sku": "GIRO-SYNTAX-RED-M",
        "price": "12500.00",
        "sale_price": "10000.00",
        "stock": 5,
        "is_on_sale": true,
        "discount_percentage": 20,
        "is_in_stock": true,
        "attributes": [
          {
            "type": "Color",
            "value": "Red"
          },
          {
            "type": "Size",
            "value": "Medium"
          }
        ]
      }
    ]
  }
  ```

---

## 📂 Categories

### 12. List All Categories
- **Endpoint:** `GET /api/categories/`
- **Auth Required:** No
- **Success Response (200):**
  ```json
  [
    {
      "id": 1,
      "name": "Helmets",
      "slug": "helmets",
      "description": "Safety helmets for bike riders",
      "image": "http://localhost:8000/media/categories/helmets.jpg",
      "product_count": 12
    }
  ]
  ```

### 13. Get Category Detail
- **Endpoint:** `GET /api/categories/{slug}/`
- **Auth Required:** No
- **Success Response (200):**
  ```json
  {
    "id": 1,
    "name": "Helmets",
    "slug": "helmets",
    "description": "Safety helmets for bike riders",
    "image": "http://localhost:8000/media/categories/helmets.jpg",
    "product_count": 12,
    "products": [
      {
        "id": 1,
        "title": "Giro Helmet",
        "slug": "giro-helmet",
        "price": "12500.00",
        "primary_image": "...",
        "is_on_sale": true
      }
    ]
  }
  ```

---

## 🏷️ Brands

### 14. List All Brands
- **Endpoint:** `GET /api/brands/`
- **Auth Required:** No
- **Success Response (200):**
  ```json
  [
    {
      "id": 1,
      "name": "Giro",
      "slug": "giro",
      "description": "Premium cycling gear",
      "logo": "http://localhost:8000/media/brands/giro.png",
      "product_count": 8
    }
  ]
  ```

### 15. Get Brand Detail
- **Endpoint:** `GET /api/brands/{slug}/`
- **Auth Required:** No
- **Success Response (200):**
  ```json
  {
    "id": 1,
    "name": "Giro",
    "slug": "giro",
    "description": "Premium cycling gear manufacturer",
    "logo": "http://localhost:8000/media/brands/giro.png",
    "website": "https://www.giro.com",
    "product_count": 8,
    "products": [...]
  }
  ```

---

## 🛒 Cart Management

### 16. Get Cart
- **Endpoint:** `GET /api/cart/`
- **Auth Required:** No (works for both guest and authenticated users)
- **Headers (Optional):** `Authorization: Bearer <token>`
- **Success Response (200):**
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
            "primary_image": "http://localhost:8000/media/products/helmet.jpg"
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

### 17. Add Item to Cart
- **Endpoint:** `POST /api/cart/items/`
- **Auth Required:** No
- **Headers (Optional):** `Authorization: Bearer <token>`
- **Request Body:**
  ```json
  {
    "variant_id": 1,
    "quantity": 2
  }
  ```
- **Success Response (201):**
  ```json
  {
    "id": 1,
    "variant": {...},
    "quantity": 2,
    "total": "20000.00",
    "message": "Item added to cart"
  }
  ```

### 18. Update Cart Item Quantity
- **Endpoint:** `PATCH /api/cart/items/{id}/`
- **Auth Required:** No
- **Headers (Optional):** `Authorization: Bearer <token>`
- **Request Body:**
  ```json
  {
    "quantity": 3
  }
  ```
- **Success Response (200):**
  ```json
  {
    "id": 1,
    "quantity": 3,
    "total": "30000.00"
  }
  ```

### 19. Remove Cart Item
- **Endpoint:** `DELETE /api/cart/items/{id}/`
- **Auth Required:** No
- **Headers (Optional):** `Authorization: Bearer <token>`
- **Success Response:** 204 No Content

### 20. Clear Cart
- **Endpoint:** `DELETE /api/cart/clear/`
- **Auth Required:** No
- **Headers (Optional):** `Authorization: Bearer <token>`
- **Success Response (200):**
  ```json
  {
    "message": "Cart cleared successfully"
  }
  ```

---

## 🏠 Homepage Content

### 21. Get Homepage Data
- **Endpoint:** `GET /api/homepage/`
- **Auth Required:** No
- **Description:** Get all homepage content including banners, featured sections, categories, and brands
- **Success Response (200):**
  ```json
  {
    "banners": [
      {
        "id": 1,
        "title": "New Helmet Collection",
        "subtitle": "Premium protection for every ride",
        "image": "http://localhost:8000/media/banners/hero.jpg",
        "image_mobile": "http://localhost:8000/media/banners/mobile/hero.jpg",
        "link_product": {
          "id": 1,
          "title": "Giro Helmet",
          "slug": "giro-helmet"
        },
        "button_text": "Shop Now",
        "display_order": 0
      }
    ],
    "featured_sections": [
      {
        "id": 1,
        "title": "New Arrivals",
        "subtitle": "Check out our latest products",
        "section_type": "new",
        "products": [
          {
            "id": 1,
            "title": "Mountain Bike Helmet",
            "slug": "mountain-bike-helmet",
            "price": "5999.00",
            "sale_price": "4999.00",
            "primary_image": "http://localhost:8000/media/products/helmet.jpg",
            "is_on_sale": true
          }
        ]
      }
    ],
    "categories": [
      {
        "id": 1,
        "name": "Helmets",
        "slug": "helmets",
        "description": "Safety helmets for all riding styles",
        "image_url": "http://localhost:8000/media/categories/helmets.jpg",
        "product_count": 25
      },
      {
        "id": 2,
        "name": "Bikes",
        "slug": "bikes",
        "description": "Premium bikes for every terrain",
        "image_url": "http://localhost:8000/media/categories/bikes.jpg",
        "product_count": 45
      }
    ],
    "brands": [
      {
        "id": 1,
        "name": "Giro",
        "slug": "giro",
        "description": "Premium cycling gear",
        "logo_url": "http://localhost:8000/media/brands/giro.png",
        "website": "https://www.giro.com",
        "product_count": 15
      },
      {
        "id": 2,
        "name": "Specialized",
        "slug": "specialized",
        "description": "Innovation in cycling",
        "logo_url": "http://localhost:8000/media/brands/specialized.png",
        "website": "https://www.specialized.com",
        "product_count": 30
      }
    ]
  }
  ```
- **Notes:**
  - Returns up to 20 active categories
  - Returns up to 20 active brands
  - All URLs are absolute (full domain included)
  - Product counts are for active products only
  - Categories and brands are ordered by name
  - Images return `null` if not set

---

## 📊 Response Formats

### Laravel-Style Pagination (for Products)

```json
{
  "data": [...],
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 5,
    "links": [
      {
        "url": null,
        "label": "&laquo; Previous",
        "page": null,
        "active": false
      },
      {
        "url": "http://localhost:8000/api/products/?page=1",
        "label": "1",
        "page": 1,
        "active": true
      },
      {
        "url": "http://localhost:8000/api/products/?page=2",
        "label": "2",
        "page": 2,
        "active": false
      },
      {
        "url": "http://localhost:8000/api/products/?page=2",
        "label": "Next &raquo;",
        "page": 2,
        "active": false
      }
    ],
    "path": "http://localhost:8000/api/products/",
    "per_page": 20,
    "to": 20,
    "total": 95
  }
}
```

---

## ⚠️ Error Handling

### HTTP Status Codes

- **200 OK** - Successful GET/PATCH/POST
- **201 Created** - Successful resource creation
- **204 No Content** - Successful DELETE
- **400 Bad Request** - Validation errors
- **401 Unauthorized** - Authentication required or invalid token
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Server error

### Error Response Format

**Validation Errors (400):**
```json
{
  "email": ["User with this email already exists."],
  "password": ["Password must be at least 8 characters."]
}
```

**Authentication Error (401):**
```json
{
  "detail": "Invalid email or password"
}
```

**Not Found (404):**
```json
{
  "detail": "Not found."
}
```

---

## 🔑 Authentication Notes

1. **Token Lifetime:** JWT tokens are valid for 7 days
2. **Token Format:** `Authorization: Bearer <your_token_here>`
3. **No Refresh Token:** System uses access token only
4. **Token Generation:** Tokens are generated on registration and login
5. **After Expiry:** User must login again to get a new token

---

## 🛒 Cart System Notes

1. **Guest Cart:** Works without authentication using session
2. **User Cart:** Linked to authenticated user account
3. **Cart Merging:** When guest logs in, their cart automatically merges with user cart
4. **Stock Validation:** System prevents adding more items than available stock
5. **Price Snapshot:** Prices are preserved at the time of adding to cart

---

## 📝 Additional Notes

- **Currency:** All prices in BDT (Bangladeshi Taka)
- **Timestamps:** All dates in ISO 8601 format (UTC)
- **Images:** All image fields return full absolute URLs
- **Pagination:** Only applied to product listings
- **CORS:** Configured for `localhost:3000` (React frontend)

---

## 🚀 Quick Integration Guide

### 1. Setup Axios Instance (React Example)

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### 2. Example API Calls

```javascript
// Register
const register = async (email, name, password) => {
  const response = await api.post('auth/register/', { email, name, password });
  localStorage.setItem('token', response.data.token);
  return response.data;
};

// Get Products
const getProducts = async (filters = {}) => {
  const response = await api.get('products/', { params: filters });
  return response.data;
};

// Add to Cart
const addToCart = async (variant_id, quantity) => {
  const response = await api.post('cart/items/', { variant_id, quantity });
  return response.data;
};
```

---

## ✅ API Implementation Status

All endpoints are **COMPLETED** and ready for frontend integration:

✅ Authentication (Register, Login, Profile, Password Change)  
✅ Address Management (CRUD)  
✅ Products (List with filters, Detail)  
✅ Categories (List, Detail)  
✅ Brands (List, Detail)  
✅ Cart (Get, Add, Update, Remove, Clear)  
✅ Homepage (Banners, Featured Sections)  
✅ JWT Authentication (7-day tokens)  
✅ Laravel-style Pagination  
✅ Guest Cart Support  
✅ Cart Merging on Login  
✅ Stock Validation  

---

**Ready for Testing and Integration! 🎉**
