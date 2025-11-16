# REST API Testing Checklist

**Project:** BikeShop E-commerce Platform  
**Date:** October 20, 2025  
**Base URL:** `http://localhost:8000/api/`

---

## 🧪 Testing Tools

You can use any of these tools to test the API:
- **Postman** (Recommended)
- **Thunder Client** (VS Code Extension)
- **Insomnia**
- **cURL** (Command line)
- **HTTPie** (Command line)

---

## ✅ Testing Checklist

### Phase 1: Authentication & User Management

#### 1.1 User Registration
- [ ] **POST** `/api/auth/register/`
  - [ ] Valid registration (email, name, password)
  - [ ] Returns user object and JWT token
  - [ ] Duplicate email validation
  - [ ] Password length validation (min 8 chars)
  - [ ] Invalid email format validation

#### 1.2 User Login
- [ ] **POST** `/api/auth/login/`
  - [ ] Valid login (email, password)
  - [ ] Returns user object and JWT token
  - [ ] Invalid credentials error (401)
  - [ ] Non-existent user error

#### 1.3 User Profile
- [ ] **GET** `/api/auth/profile/`
  - [ ] Returns current user profile (with token)
  - [ ] Unauthorized error without token (401)
- [ ] **PATCH** `/api/auth/profile/`
  - [ ] Update name successfully
  - [ ] Update phone successfully
  - [ ] Partial update works (only name or only phone)

#### 1.4 Change Password
- [ ] **POST** `/api/auth/change-password/`
  - [ ] Successful password change
  - [ ] Incorrect old password error (400)
  - [ ] New password validation (min 8 chars)

---

### Phase 2: Address Management

#### 2.1 Address CRUD
- [ ] **GET** `/api/auth/addresses/`
  - [ ] Returns empty array initially
  - [ ] Returns user's addresses only
- [ ] **POST** `/api/auth/addresses/`
  - [ ] Create new address successfully
  - [ ] Set as default address
  - [ ] Required fields validation
- [ ] **PATCH** `/api/auth/addresses/{id}/`
  - [ ] Update address successfully
  - [ ] Can only update own addresses
- [ ] **DELETE** `/api/auth/addresses/{id}/`
  - [ ] Delete address successfully (204)
  - [ ] Can only delete own addresses
  - [ ] Cannot access other users' addresses

---

### Phase 3: Products

#### 3.1 Product List
- [ ] **GET** `/api/products/`
  - [ ] Returns paginated product list
  - [ ] Pagination meta data is correct
  - [ ] Returns 20 items per page by default
  - [ ] Can change page size with `?page_size=10`
  - [ ] Navigate to next page with `?page=2`

#### 3.2 Product Filtering
- [ ] Filter by category: `?category=helmets`
- [ ] Filter by brand: `?brand=giro`
- [ ] Filter by price range: `?min_price=5000&max_price=15000`
- [ ] Filter featured products: `?is_featured=true`
- [ ] Filter on-sale products: `?on_sale=true`
- [ ] Combine multiple filters

#### 3.3 Product Search & Ordering
- [ ] Search: `?search=helmet`
- [ ] Order by price ascending: `?ordering=price`
- [ ] Order by price descending: `?ordering=-price`
- [ ] Order by date ascending: `?ordering=created_at`
- [ ] Order by date descending: `?ordering=-created_at`

#### 3.4 Product Detail
- [ ] **GET** `/api/products/{slug}/`
  - [ ] Returns full product details
  - [ ] Includes variants array
  - [ ] Includes images array
  - [ ] Includes category and brand info
  - [ ] Returns 404 for non-existent product

---

### Phase 4: Categories

#### 4.1 Category List
- [ ] **GET** `/api/categories/`
  - [ ] Returns all active categories
  - [ ] No pagination (returns all)
  - [ ] Includes product_count

#### 4.2 Category Detail
- [ ] **GET** `/api/categories/{slug}/`
  - [ ] Returns category with products
  - [ ] Products array populated
  - [ ] Returns 404 for non-existent category

---

### Phase 5: Brands

#### 5.1 Brand List
- [ ] **GET** `/api/brands/`
  - [ ] Returns all active brands
  - [ ] No pagination (returns all)
  - [ ] Includes product_count
  - [ ] Includes logo URLs

#### 5.2 Brand Detail
- [ ] **GET** `/api/brands/{slug}/`
  - [ ] Returns brand with products
  - [ ] Products array populated
  - [ ] Returns 404 for non-existent brand

---

### Phase 6: Cart Management (Guest)

#### 6.1 Guest Cart
- [ ] **GET** `/api/cart/`
  - [ ] Returns empty cart initially
  - [ ] Works without authentication
- [ ] **POST** `/api/cart/items/`
  - [ ] Add item to cart (variant_id, quantity)
  - [ ] Returns cart item with details
  - [ ] Increments quantity if item already in cart
  - [ ] Stock validation (cannot exceed stock)
  - [ ] Invalid variant_id error (400)
- [ ] **PATCH** `/api/cart/items/{id}/`
  - [ ] Update quantity successfully
  - [ ] Stock validation works
  - [ ] Cannot update other users' cart items
- [ ] **DELETE** `/api/cart/items/{id}/`
  - [ ] Remove item successfully (204)
  - [ ] Cannot remove other users' cart items
- [ ] **DELETE** `/api/cart/clear/`
  - [ ] Clear all items from cart
  - [ ] Returns success message

---

### Phase 7: Cart Management (Authenticated)

#### 7.1 User Cart
- [ ] **GET** `/api/cart/` (with token)
  - [ ] Returns user's cart
  - [ ] Cart persists across sessions
- [ ] **POST** `/api/cart/items/` (with token)
  - [ ] Add item to user cart
  - [ ] Linked to user account

#### 7.2 Cart Merging
- [ ] Add items to guest cart
- [ ] Login with user credentials
- [ ] **GET** `/api/cart/` should show merged cart
- [ ] Guest cart items merged into user cart
- [ ] Quantities added if same variant exists
- [ ] Guest cart deleted after merge

---

### Phase 8: Homepage

#### 8.1 Homepage Data
- [ ] **GET** `/api/homepage/`
  - [ ] Returns banners array
  - [ ] Returns featured_sections array
  - [ ] Only active banners shown
  - [ ] Only currently valid banners (date range)
  - [ ] Images return full URLs
  - [ ] Linked products populated

---

## 📝 Sample Test Data

### Register User
```json
POST /api/auth/register/
{
  "email": "test@example.com",
  "name": "Test User",
  "password": "password123"
}
```

### Login
```json
POST /api/auth/login/
{
  "email": "test@example.com",
  "password": "password123"
}
```

### Add to Cart
```json
POST /api/cart/items/
{
  "variant_id": 1,
  "quantity": 2
}
```

### Update Cart Item
```json
PATCH /api/cart/items/1/
{
  "quantity": 3
}
```

### Create Address
```json
POST /api/auth/addresses/
{
  "label": "Home",
  "street": "123 Main St",
  "city": "Dhaka",
  "state": "Dhaka Division",
  "postal_code": "1200",
  "country": "Bangladesh",
  "phone": "+8801712345678",
  "is_default": true
}
```

---

## 🔍 What to Check

### Response Structure
- [ ] Status codes are correct (200, 201, 204, 400, 401, 404)
- [ ] Response format matches documentation
- [ ] Error messages are clear and helpful
- [ ] Timestamps are in ISO 8601 format
- [ ] Image URLs are absolute and accessible

### Data Integrity
- [ ] Prices are correctly formatted (2 decimal places)
- [ ] Stock levels are accurate
- [ ] Discount calculations are correct
- [ ] Cart totals are accurate
- [ ] Savings calculations are correct

### Security
- [ ] Cannot access other users' data
- [ ] JWT token validation works
- [ ] Expired tokens are rejected
- [ ] Unauthorized requests return 401
- [ ] Protected endpoints require authentication

### Performance
- [ ] Queries are optimized (no N+1 queries)
- [ ] Response times are acceptable
- [ ] Pagination works smoothly
- [ ] Image URLs load correctly

---

## 🐛 Common Issues to Check

1. **CORS Issues**
   - If testing from React app on localhost:3000
   - Check CORS headers in response
   - Verify CORS_ALLOWED_ORIGINS in settings

2. **Image URLs**
   - Should be absolute URLs
   - Should include domain (http://localhost:8000)
   - Should be accessible when opened in browser

3. **Session Management**
   - Guest cart should work without auth
   - Session should persist across requests
   - Cart should merge on login

4. **Stock Validation**
   - Cannot add more than available stock
   - Error message should show available stock

5. **Pagination**
   - Links should include query parameters
   - Page numbers should be correct
   - Total count should match actual records

---

## ✅ Success Criteria

All tests pass and API is ready for production when:

- ✅ All endpoints return correct status codes
- ✅ All validations work as expected
- ✅ Authentication and authorization work correctly
- ✅ Cart system works for both guest and users
- ✅ Cart merging works on login
- ✅ Stock validation prevents overselling
- ✅ Pagination works correctly
- ✅ Filtering and search work as expected
- ✅ Image URLs are accessible
- ✅ Error messages are helpful
- ✅ No security vulnerabilities
- ✅ Performance is acceptable

---

## 📚 Next Steps After Testing

1. **Production Deployment**
   - Switch to production database (PostgreSQL/MySQL)
   - Configure production settings
   - Set up environment variables
   - Enable HTTPS

2. **Performance Optimization**
   - Add caching (Redis)
   - Optimize database queries
   - Add database indexes
   - Enable compression

3. **Security Hardening**
   - Add rate limiting
   - Add request throttling
   - Enable security middleware
   - Regular security audits

4. **Monitoring**
   - Add error tracking (Sentry)
   - Add performance monitoring
   - Set up logging
   - Monitor API usage

---

**Happy Testing! 🚀**
