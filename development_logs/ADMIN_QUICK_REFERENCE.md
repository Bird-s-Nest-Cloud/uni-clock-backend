# Admin Dashboard Quick Reference Guide

**BikeShop E-commerce Platform**  
**Date:** October 20, 2025

---

## 🔐 Admin Access

### Login URL
```
http://localhost:8000/admin/login/
```

### Requirements
- Must be a **staff user** (`is_staff=True`)
- Valid email and password
- Active account (`is_active=True`)

### Creating Admin User
```bash
python manage.py createsuperuser
```

---

## 📋 Admin Dashboard URLs

### Main Dashboard
```
/admin/                     # Dashboard home
/admin/home/                # Alternative dashboard URL
```

### User Management
```
/admin/users/               # List all users
/admin/users/add/           # Add new user
/admin/users/<id>/edit/     # Edit user
/admin/users/<id>/delete/   # Delete user
```

### Order Management
```
/admin/orders/              # List all orders
/admin/orders/<id>/         # View order details
/admin/orders/<id>/status/  # Update order status (POST)
```

### Catalog Management
```
# Categories
/admin/categories/          # List categories
/admin/categories/add/      # Add category
/admin/categories/<id>/edit/    # Edit category
/admin/categories/<id>/delete/  # Delete category

# Brands
/admin/brands/              # List brands
/admin/brands/add/          # Add brand
/admin/brands/<id>/edit/    # Edit brand
/admin/brands/<id>/delete/  # Delete brand

# Products
/admin/products/            # List products
/admin/products/add/        # Add product
/admin/products/<id>/edit/  # Edit product
/admin/products/<id>/delete/    # Delete product

# Product Variants
/admin/products/<product_id>/variants/  # List variants
/admin/products/<product_id>/variants/add/  # Add variant
/admin/variants/<id>/edit/  # Edit variant
/admin/variants/<id>/delete/    # Delete variant

# Attributes
/admin/attributes/          # List attribute types
/admin/attributes/add/      # Add attribute type
/admin/attributes/<id>/edit/    # Edit attribute type
/admin/attributes/<id>/delete/  # Delete attribute type

# Attribute Values
/admin/attributes/<attr_id>/values/ # List values
/admin/attributes/<attr_id>/values/add/ # Add value
/admin/attribute-values/<id>/edit/  # Edit value
/admin/attribute-values/<id>/delete/    # Delete value
```

### Content Management
```
# Banners
/admin/banners/             # List banners
/admin/banners/add/         # Add banner
/admin/banners/<id>/edit/   # Edit banner
/admin/banners/<id>/delete/ # Delete banner
/admin/banners/<id>/toggle-status/  # Toggle active status (AJAX)

# Featured Sections
/admin/featured-sections/   # List sections
/admin/featured-sections/add/   # Add section
/admin/featured-sections/<id>/edit/ # Edit section
/admin/featured-sections/<id>/delete/   # Delete section
/admin/featured-sections/<id>/toggle-status/    # Toggle status (AJAX)
/admin/featured-sections/<id>/preview/  # Preview products (AJAX)
```

---

## 👥 User Management

### User List Features
- **Search:** By name, email, or phone
- **Filters:**
  - Staff status (All/Staff Only/Customers Only)
  - Active status (All/Active/Inactive)
- **Columns:** ID, Name, Email, Phone, Role, Status, Joined Date, Actions

### User Roles
- **Super Admin** (Red badge): `is_superuser=True`
- **Staff** (Yellow badge): `is_staff=True`
- **Customer** (Blue badge): Regular user

### User Status
- **Active** (Green badge): Can login
- **Inactive** (Red badge): Cannot login

### Adding a User
1. Click "Add User" button
2. Fill required fields:
   - Full Name (required)
   - Email (required, unique)
   - Password (required, min 8 chars)
   - Phone (optional)
3. Toggle staff/active status
4. Click "Create User"

### Editing a User
1. Click edit icon (pencil) in Actions column
2. Modify user details
3. Optionally update password (leave blank to keep current)
4. Click "Update User"

### Deleting a User
1. Click delete icon (trash) in Actions column
2. Review user details
3. Click "Yes, Delete User" to confirm
4. Note: Cannot delete your own account

---

## 📦 Order Management

### Order List Features
- **Search:** By order number, customer name, or email
- **Filters:**
  - Order Status (Pending/Processing/Shipped/Delivered/Cancelled)
  - Payment Status (Unpaid/Paid/Failed/Refunded)
- **Columns:** Order #, Customer, Items, Total, Status, Payment, Date, Actions

### Order Statuses
- **Pending** (Yellow badge): New order
- **Processing** (Blue badge): Being prepared
- **Shipped** (Purple badge): Out for delivery
- **Delivered** (Green badge): Completed
- **Cancelled** (Red badge): Cancelled

### Payment Statuses
- **Unpaid** (Yellow badge): Payment pending
- **Paid** (Green badge): Payment received
- **Failed** (Red badge): Payment failed
- **Refunded** (Blue badge): Refunded to customer

### Viewing Order Details
1. Click on order number or view icon
2. View sections:
   - **Order Items:** Products with images, SKU, price, quantity
   - **Order Totals:** Subtotal, discount, shipping, total
   - **Customer Info:** Name, email, phone
   - **Shipping Address:** Full address details
   - **Payment Info:** Method, transaction ID, paid date
   - **Order Notes:** Internal admin notes

### Updating Order Status
1. Open order detail page
2. In the right sidebar:
   - Select new order status
   - Select new payment status
   - Add/update admin notes
3. Click "Update Order"
4. Success message will appear

---

## 🎨 Dashboard Overview

### Statistics Cards
- Total Products
- Total Orders
- Total Users
- Other key metrics

### Recent Orders
- Last 5 orders
- Quick view of order status

### Low Stock Alert
- Products with stock ≤ 5 units
- Helps manage inventory

---

## 🔍 Search and Filter Tips

### Search
- Type keywords in search box
- Works on multiple fields (name, email, phone, order #, etc.)
- Case-insensitive search
- Press Enter or click Filter button

### Filters
- Use dropdown menus to filter by specific criteria
- Multiple filters can be combined
- Click Filter button to apply
- Clear search box and select "All" in dropdowns to reset

---

## 💡 Best Practices

### User Management
1. Always use strong passwords (min 8 characters)
2. Use staff status only for admin users
3. Deactivate users instead of deleting when possible
4. Keep user emails unique and valid
5. Add phone numbers for better communication

### Order Management
1. Update order status regularly
2. Add admin notes for order tracking
3. Verify payment status before shipping
4. Update shipping status promptly
5. Keep customer informed (external to admin)

### General
1. Use search before browsing large lists
2. Filter by status to find specific items
3. Double-check before deleting
4. Keep admin notes for reference
5. Regular backup of data

---

## 🚨 Important Notes

### Security
- Never share admin credentials
- Logout when finished (`/admin/logout/`)
- Change password regularly
- Monitor user creation/deletion activities

### Data Integrity
- Cannot delete yourself (self-deletion prevention)
- Deleting categories/brands may affect related products
- Deleting products may affect orders (consider deactivating instead)
- Order data is preserved even if user is deleted

### Performance
- Queries are optimized with `select_related` and `prefetch_related`
- Use filters to reduce data load on large datasets
- Product images may take time to load depending on size

---

## 🛠️ Troubleshooting

### Cannot Login
- Verify you are a staff user (`is_staff=True`)
- Check if account is active (`is_active=True`)
- Ensure correct email and password
- Contact superadmin if locked out

### Page Not Found
- Check URL structure
- Ensure you're logged in
- Verify item ID exists
- Check if item was deleted

### Cannot Delete Item
- Check for related dependencies
- Some items cannot be deleted if referenced by others
- Consider deactivating instead

### Images Not Loading
- Verify MEDIA_ROOT and MEDIA_URL in settings
- Check if media files exist in media folder
- Ensure proper file permissions
- Check web server configuration

---

## 📞 Support

For technical issues or questions:
1. Check development logs in `development_logs/` folder
2. Review implementation documentation
3. Contact system administrator
4. Check Django error logs

---

## 📚 Additional Documentation

- `ADMIN_MODULES_IMPLEMENTATION_STATUS.md` - Full implementation details
- `API_ENDPOINTS_LIST.md` - Complete API documentation
- `API_QUICK_REFERENCE.md` - API quick reference
- `REST_API_IMPLEMENTATION_LOG.md` - API implementation log

---

**Last Updated:** October 20, 2025  
**Version:** 1.0.0
