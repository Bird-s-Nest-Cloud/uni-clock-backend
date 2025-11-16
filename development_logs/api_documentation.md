# Bike Shop E-commerce API Documentation

**Base URL:** `http://localhost:8000/api/`

**Authentication:** JWT tokens (valid for 7 days)

---

## Authentication

All authenticated endpoints require JWT token in header:
```
Authorization: Bearer <token>
```

Token expires after 7 days. User must login again after expiration.

---

## 1. Authentication APIs

### 1.1 Register
**POST** `/api/auth/register/`

Create new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securepass123"
}
```

**Response (201):**
```json
{
  "status": true,
  "status_code": 201,
  "message": "User registered successfully",
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "phone": null,
      "date_joined": "2025-10-25T10:30:00Z"
    },
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Validation:**
- Email must be valid and unique
- Password minimum 8 characters
- Name is required

**Errors (400):**
```json
{
  "status": false,
  "status_code": 400,
  "message": "Registration failed",
  "data": {
    "errors": {
      "email": ["User with this email already exists."],
      "password": ["Password must be at least 8 characters."]
    }
  }
}
```

---

### 1.2 Login
**POST** `/api/auth/login/`

Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response (200):**
```json
{
  "status": true,
  "status_code": 200,
  "message": "Login successful",
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "phone": "+8801712345678",
      "date_joined": "2025-10-20T10:30:00Z"
    },
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Errors (401):**
```json
{
  "status": false,
  "status_code": 401,
  "message": "Invalid credentials",
  "data": {
    "errors": {
      "email": ["Invalid email or password"]
    }
  }
}
```

---

### 1.3 Get Profile
**GET** `/api/auth/profile/`

Get current user profile with all addresses.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "status": true,
  "status_code": 200,
  "message": "Profile retrieved successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "phone": "+8801712345678",
    "date_joined": "2025-10-20T10:30:00Z",
    "addresses": [
      {
        "id": 1,
        "label": "Home",
        "street": "123 Main St",
        "city": "Dhaka",
        "state": "Dhaka Division",
        "postal_code": "1200",
        "country": "Bangladesh",
        "phone": "+8801712345678",
        "address_type": "billing",
        "is_default_billing": true,
        "is_default_shipping": false,
        "created_at": "2025-10-25T10:30:00Z"
      }
    ]
  }
}
```

---

### 1.4 Update Profile
**PATCH** `/api/auth/profile/`

Update user profile.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "name": "John Smith",
  "phone": "+8801712345678"
}
```

**Response (200):**
```json
{
  "status": true,
  "status_code": 200,
  "message": "Profile updated successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Smith",
    "phone": "+8801712345678",
    "date_joined": "2025-10-20T10:30:00Z",
    "addresses": [...]
  }
}
```

---

### 1.5 Change Password
**POST** `/api/auth/change-password/`

Change user password.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "old_password": "oldpass123",
  "new_password": "newpass456"
}
```

**Response (200):**
```json
{
  "status": true,
  "status_code": 200,
  "message": "Password changed successfully",
  "data": {}
}
```

**Errors (400):**
```json
{
  "status": false,
  "status_code": 400,
  "message": "Password change failed",
  "data": {
    "errors": {
      "old_password": ["Incorrect password"]
    }
  }
}
```

---

## 2. Address Management

### 2.1 List Addresses
**GET** `/api/auth/addresses/`

Get all user addresses.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "status": true,
  "status_code": 200,
  "message": "Addresses retrieved successfully",
  "data": [
    {
      "id": 1,
      "label": "Home",
      "street": "123 Main St",
      "city": "Dhaka",
      "state": "Dhaka Division",
      "postal_code": "1200",
      "country": "Bangladesh",
      "phone": "+8801712345678",
      "address_type": "billing",
      "is_default_billing": true,
      "is_default_shipping": false,
      "created_at": "2025-10-25T10:30:00Z"
    },
    {
      "id": 2,
      "label": "Office",
      "street": "456 Work Ave",
      "city": "Dhaka",
      "state": "Dhaka Division",
      "postal_code": "1200",
      "country": "Bangladesh",
      "phone": "+8801712345678",
      "address_type": "shipping",
      "is_default_billing": false,
      "is_default_shipping": true,
      "created_at": "2025-10-25T11:00:00Z"
    }
  ]
}
```

---

### 2.2 Create Address
**POST** `/api/auth/addresses/`

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "label": "Home",
  "street": "123 Main St",
  "city": "Dhaka",
  "state": "Dhaka Division",
  "postal_code": "1200",
  "country": "Bangladesh",
  "phone": "+8801712345678",
  "address_type": "billing",
  "is_default_billing": true,
  "is_default_shipping": false
}
```

**Note:** 
- `address_type` must be either `"billing"` or `"shipping"` (not both)
- Set `is_default_billing: true` to make it the default billing address
- Set `is_default_shipping: true` to make it the default shipping address
- A user can have only one default billing and one default shipping address
- Setting a new default will automatically unset the previous default of the same type

**Response (201):**
```json
{
  "status": true,
  "status_code": 201,
  "message": "Address created successfully",
  "data": {
    "id": 3,
    "label": "Home",
    "street": "123 Main St",
    "city": "Dhaka",
    "state": "Dhaka Division",
    "postal_code": "1200",
    "country": "Bangladesh",
    "phone": "+8801712345678",
    "address_type": "billing",
    "is_default_billing": true,
    "is_default_shipping": false,
    "created_at": "2025-10-25T12:00:00Z"
  }
}
```

---

### 2.3 Update Address
**PATCH** `/api/auth/addresses/{id}/`

Update an existing address.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "label": "Home Updated",
  "is_default_shipping": true
}
```

**Response (200):**
```json
{
  "status": true,
  "status_code": 200,
  "message": "Address updated successfully",
  "data": {
    "id": 1,
    "label": "Home Updated",
    "street": "123 Main St",
    "city": "Dhaka",
    "state": "Dhaka Division",
    "postal_code": "1200",
    "country": "Bangladesh",
    "phone": "+8801712345678",
    "address_type": "billing",
    "is_default_billing": true,
    "is_default_shipping": true,
    "created_at": "2025-10-25T10:30:00Z"
  }
}
```

---

### 2.4 Delete Address
**DELETE** `/api/auth/addresses/{id}/`

Delete an address.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "status": true,
  "status_code": 200,
  "message": "Address deleted successfully",
  "data": {}
}
```

---

## 3. Products

### 3.1 List Products
**GET** `/api/products/`

Get paginated product list with filters.

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)
- `category` - Filter by category slug (e.g., `helmets`)
- `brand` - Filter by brand slug (e.g., `giro`)
- `min_price` - Minimum price (e.g., `5000`)
- `max_price` - Maximum price (e.g., `15000`)
- `search` - Search in title/description (e.g., `helmet`)
- `is_featured` - Filter featured products (`true`/`false`)
- `on_sale` - Filter sale products (`true`/`false`)
- `ordering` - Sort by: `price`, `-price`, `created_at`, `-created_at`

**Example:**
```
GET /api/products/?category=helmets&min_price=5000&max_price=15000&ordering=-created_at
```

**Response (200):**
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
      "primary_image": "http://localhost:8000/media/products/2025/10/helmet.jpg",
      "variant_count": 4
    }
  ],
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 3,
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
        "label": "Next &raquo;",
        "page": 2,
        "active": false
      }
    ],
    "path": "http://localhost:8000/api/products/",
    "per_page": 20,
    "to": 20,
    "total": 45
  }
}
```

---

### 3.2 Get Product Detail
**GET** `/api/products/{slug}/`

Get single product with full details including variants.

**Response (200):**
```json
{
  "id": 1,
  "title": "Giro Syntax MIPS Helmet",
  "slug": "giro-syntax-mips-helmet",
  "description": "Premium road cycling helmet with MIPS protection for enhanced safety...",
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
      "image": "http://localhost:8000/media/products/2025/10/helmet-1.jpg",
      "alt_text": "Front view",
      "position": 0
    },
    {
      "id": 2,
      "image": "http://localhost:8000/media/products/2025/10/helmet-2.jpg",
      "alt_text": "Side view",
      "position": 1
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
    },
    {
      "id": 2,
      "sku": "GIRO-SYNTAX-BLUE-L",
      "price": "12000.00",
      "sale_price": null,
      "stock": 3,
      "is_on_sale": false,
      "is_in_stock": true,
      "attributes": [
        {
          "type": "Color",
          "value": "Blue"
        },
        {
          "type": "Size",
          "value": "Large"
        }
      ]
    }
  ]
}
```

---

## 4. Categories

### 4.1 List Categories
**GET** `/api/categories/`

Get all active categories.

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Helmets",
    "slug": "helmets",
    "description": "Safety helmets for bike riders",
    "image": "http://localhost:8000/media/categories/helmets.jpg",
    "product_count": 12
  },
  {
    "id": 2,
    "name": "Lights",
    "slug": "lights",
    "product_count": 8
  }
]
```

---

### 4.2 Get Category Detail
**GET** `/api/categories/{slug}/`

Get category with products.

**Response (200):**
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

## 5. Brands

### 5.1 List Brands
**GET** `/api/brands/`

**Response (200):**
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

---

### 5.2 Get Brand Detail
**GET** `/api/brands/{slug}/`

**Response (200):**
```json
{
  "id": 1,
  "name": "Giro",
  "slug": "giro",
  "description": "Premium cycling gear manufacturer",
  "logo": "http://localhost:8000/media/brands/giro.png",
  "website": "https://www.giro.com",
  "product_count": 8,
  "products": [
    {
      "id": 1,
      "title": "Giro Helmet",
      "slug": "giro-helmet",
      "price": "12500.00"
    }
  ]
}
```

---

## 6. Cart Management

### 6.1 Get Cart
**GET** `/api/cart/`

Get current user's cart. For guests, uses session-based cart.

**Headers (optional):** `Authorization: Bearer <token>`

**Response (200):**
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

---

### 6.2 Add Item to Cart
**POST** `/api/cart/items/`

Add product variant to cart.

**Headers (optional):** `Authorization: Bearer <token>`

**Request:**
```json
{
  "variant_id": 1,
  "quantity": 2
}
```

**Response (201):**
```json
{
  "id": 1,
  "variant": {
    "id": 1,
    "sku": "GIRO-SYNTAX-RED-M",
    "product": {
      "title": "Giro Helmet"
    }
  },
  "quantity": 2,
  "total": "20000.00",
  "message": "Item added to cart"
}
```

**Validation Errors (400):**
```json
{
  "variant_id": ["Variant not found"],
  "quantity": ["Quantity must be at least 1"],
  "stock": ["Only 3 items available in stock"]
}
```

---

### 6.3 Update Cart Item
**PATCH** `/api/cart/items/{id}/`

Update item quantity.

**Headers (optional):** `Authorization: Bearer <token>`

**Request:**
```json
{
  "quantity": 3
}
```

**Response (200):**
```json
{
  "id": 1,
  "quantity": 3,
  "total": "30000.00"
}
```

---

### 6.4 Remove Cart Item
**DELETE** `/api/cart/items/{id}/`

Remove item from cart.

**Headers (optional):** `Authorization: Bearer <token>`

**Response (204):** No content

---

### 6.5 Clear Cart
**DELETE** `/api/cart/clear/`

Remove all items from cart.

**Headers (optional):** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "message": "Cart cleared successfully"
}
```

---

## 7. Homepage

### 7.1 Get Homepage Data
**GET** `/api/homepage/`

Get banners and featured sections for homepage.

**Response (200):**
```json
{
  "banners": [
    {
      "id": 1,
      "title": "New Helmet Collection",
      "subtitle": "Premium protection for every ride",
      "image": "http://localhost:8000/media/banners/2025/10/hero.jpg",
      "image_mobile": "http://localhost:8000/media/banners/2025/10/mobile/hero.jpg",
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
          "title": "Giro Helmet",
          "slug": "giro-helmet",
          "price": "12500.00",
          "sale_price": "10000.00",
          "primary_image": "http://localhost:8000/media/products/helmet.jpg",
          "is_on_sale": true
        }
      ]
    }
  ]
}
```

---

## Error Responses

### 400 Bad Request
Validation errors.
```json
{
  "email": ["This field is required."],
  "password": ["Password must be at least 8 characters."]
}
```

### 401 Unauthorized
Missing or invalid token.
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
Resource not found.
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
Server error.
```json
{
  "detail": "A server error occurred."
}
```

---

## Notes

- **Token Lifetime:** 7 days. After expiration, user must login again.
- **Pagination:** All list endpoints support `page` and `page_size` parameters.
- **Guest Cart:** Cart works without authentication using session. On login, guest cart merges with user cart.
- **Image URLs:** All image fields return full absolute URLs.
- **Timestamps:** All dates in ISO 8601 format (UTC).
- **Currency:** All prices in BDT (Bangladeshi Taka).
