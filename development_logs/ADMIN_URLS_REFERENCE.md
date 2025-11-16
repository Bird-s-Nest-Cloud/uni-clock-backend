# Admin URLs Quick Reference

## Access All Admin Features

### Dashboard
```
http://localhost:8000/dashboard/
```

---

## Category Management
```
List:    http://localhost:8000/dashboard/categories/
Add:     http://localhost:8000/dashboard/categories/add/
Edit:    http://localhost:8000/dashboard/categories/<id>/edit/
Delete:  http://localhost:8000/dashboard/categories/<id>/delete/
```

**Features:**
- Parent-child hierarchy
- Image upload
- Search by name
- Filter by parent/status
- Display order

---

## Brand Management
```
List:    http://localhost:8000/dashboard/brands/
Add:     http://localhost:8000/dashboard/brands/add/
Edit:    http://localhost:8000/dashboard/brands/<id>/edit/
Delete:  http://localhost:8000/dashboard/brands/<id>/delete/
```

**Features:**
- Logo upload
- Website URL
- Search by name
- Filter by status

---

## Attribute Management

### Attribute Types
```
List:    http://localhost:8000/dashboard/attributes/
Add:     http://localhost:8000/dashboard/attributes/add/
Edit:    http://localhost:8000/dashboard/attributes/<id>/edit/
Delete:  http://localhost:8000/dashboard/attributes/<id>/delete/
```

### Attribute Values
```
List:    http://localhost:8000/dashboard/attributes/<type_id>/values/
Add:     http://localhost:8000/dashboard/attributes/<type_id>/values/add/
Edit:    http://localhost:8000/dashboard/attributes/values/<id>/edit/
Delete:  http://localhost:8000/dashboard/attributes/values/<id>/delete/
```

**Features:**
- Type-Value relationship
- Display order for both
- Search by name/value
- Value count display

**Example Attributes:**
- Color: Red, Blue, Green, Black
- Size: Small, Medium, Large, XL
- Material: Cotton, Polyester, Leather
- Frame Size: 48cm, 52cm, 56cm, 60cm

---

## Product Management
```
List:    http://localhost:8000/dashboard/products/
Add:     http://localhost:8000/dashboard/products/add/
Edit:    http://localhost:8000/dashboard/products/<id>/edit/
Delete:  http://localhost:8000/dashboard/products/<id>/delete/
```

**Features:**
- Multiple image upload
- Image deletion
- Price & sale price
- Stock tracking
- Physical dimensions
- SEO fields
- Search by title/description
- Filter by category/brand/status

---

## Product Variant Management
```
List:    http://localhost:8000/dashboard/products/<product_id>/variants/
Add:     http://localhost:8000/dashboard/products/<product_id>/variants/add/
Edit:    http://localhost:8000/dashboard/variants/<id>/edit/
Delete:  http://localhost:8000/dashboard/variants/<id>/delete/
```

**Features:**
- SKU management
- Attribute assignment (dynamic)
- Variant-specific pricing
- Individual stock tracking
- Search by SKU
- Filter by status

---

## Testing Workflow

### 1. Setup Attributes First
```
1. Create Attribute Type "Color"
   http://localhost:8000/dashboard/attributes/add/
   
2. Add Color Values: Red, Blue, Black
   http://localhost:8000/dashboard/attributes/1/values/add/
   
3. Create Attribute Type "Size"
   http://localhost:8000/dashboard/attributes/add/
   
4. Add Size Values: Small, Medium, Large
   http://localhost:8000/dashboard/attributes/2/values/add/
```

### 2. Create Categories
```
1. Create parent category "Bikes"
   http://localhost:8000/dashboard/categories/add/
   
2. Create child "Mountain Bikes" (parent: Bikes)
   http://localhost:8000/dashboard/categories/add/
   
3. Upload category image
```

### 3. Create Brands
```
1. Create brand "Trek"
   http://localhost:8000/dashboard/brands/add/
   
2. Upload brand logo
3. Add website URL
```

### 4. Create Products
```
1. Create product "Mountain Bike X1"
   http://localhost:8000/dashboard/products/add/
   
2. Assign category: Mountain Bikes
3. Assign brand: Trek
4. Upload multiple images
5. Set price: $999
6. Set sale price: $799
7. Add stock: 50
8. Fill SEO fields
```

### 5. Create Variants
```
1. Access variants for "Mountain Bike X1"
   http://localhost:8000/dashboard/products/1/variants/
   
2. Add variant with SKU "BIKE-RED-M"
   - Color: Red
   - Size: Medium
   - Price: $999
   - Stock: 10
   
3. Add variant with SKU "BIKE-BLUE-L"
   - Color: Blue
   - Size: Large
   - Price: $1099
   - Stock: 5
```

---

## Common Tasks

### Upload Images
**Category/Brand:**
- Single image upload
- Formats: JPG, PNG, GIF
- Stored in: media/categories/ or media/brands/

**Products:**
- Multiple images supported
- Select multiple files at once
- Stored in: media/products/YYYY/MM/
- Delete via checkboxes in edit page

### Manage Hierarchy
**Categories:**
- Select parent when creating/editing
- Visual hierarchy in list view
- Prevent circular references

**Attributes:**
- Navigate from types to values
- Breadcrumb navigation
- Back to type link in values

### Search & Filter
**All List Views:**
- Search bar at top
- Filter dropdowns
- Click "Filter" to apply
- Clear by removing text/selection

### Delete Items
**All Delete Pages:**
- Shows item details
- Lists related data
- Requires confirmation checkbox
- Suggests alternatives
- Cannot undo!

---

## Admin Access

### Login Required
```
http://localhost:8000/accounts/login/
```

### Requirements
- User must have `is_staff = True`
- Checked by `@user_passes_test(admin_required)` decorator

### Check User Status
```python
# In Django shell
python manage.py shell

from django.contrib.auth import get_user_model
User = get_user_model()

# Make user staff
user = User.objects.get(username='your_username')
user.is_staff = True
user.save()
```

---

## Sidebar Navigation

All features accessible from sidebar:
- Dashboard
- Categories
- Brands  
- Attributes
- Products
- (Variants accessed via Products)

---

## Tips & Best Practices

### SKU Naming Convention
- Use consistent format
- Include product identifier
- Include variant attributes
- Examples:
  - BIKE-MTN-RED-M
  - HELM-ROAD-BLK-L
  - TIRE-700C-25MM

### Image Guidelines
- Use high-quality images
- Consistent dimensions recommended
- First image = thumbnail
- Multiple angles for products
- Logos should be square/transparent

### Pricing Strategy
- Set base price on product
- Variants can override
- Use sale_price for promotions
- Sale price must be less than regular

### Stock Management
- Track at variant level
- Product stock is summary
- Set low_stock_threshold
- Monitor stock badges

### SEO Best Practices
- Unique meta titles
- Descriptive meta descriptions
- Include keywords naturally
- Keep titles under 60 chars
- Keep descriptions under 160 chars

---

## Troubleshooting

### Images Not Showing
✅ Fixed! Media configuration updated in:
- `bike_shop/urls.py` - Added static() helper
- `bike_shop/settings.py` - Added context processors

### Cannot Access Admin
- Check `is_staff = True`
- Verify login credentials
- Check URL is /dashboard/

### Variant Attributes Not Saving
- Create AttributeTypes first
- Add AttributeValues to types
- Select from dropdowns in variant form

### SKU Duplicate Error
- SKUs must be unique across all variants
- Change SKU to something unique
- Follow naming convention

---

## Quick Commands

### Run Development Server
```powershell
python manage.py runserver
```

### Create Superuser
```powershell
python manage.py createsuperuser
```

### Make Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Collect Static Files
```powershell
python manage.py collectstatic
```

### Django Shell
```powershell
python manage.py shell
```

---

## API Endpoints Reference

All views use function-based views with GET/POST methods:

- **GET** = Display form/list
- **POST** = Submit form/delete

Forms include CSRF protection automatically.

---

*Last Updated: October 20, 2025*  
*BikeShop Custom Admin - All Features Implemented ✅*
