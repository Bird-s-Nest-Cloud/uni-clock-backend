# Quick Reference Guide - Custom Admin

## Access URLs

### Dashboard
- Main Dashboard: `http://localhost:8000/dashboard/`
- Login: `http://localhost:8000/dashboard/login/`

### Categories
- List: `http://localhost:8000/dashboard/categories/`
- Add: `http://localhost:8000/dashboard/categories/add/`
- Edit: `http://localhost:8000/dashboard/categories/<id>/edit/`
- Delete: `http://localhost:8000/dashboard/categories/<id>/delete/`

### Brands
- List: `http://localhost:8000/dashboard/brands/`
- Add: `http://localhost:8000/dashboard/brands/add/`
- Edit: `http://localhost:8000/dashboard/brands/<id>/edit/`
- Delete: `http://localhost:8000/dashboard/brands/<id>/delete/`

### Attributes
- List Types: `http://localhost:8000/dashboard/attributes/`
- Add Type: `http://localhost:8000/dashboard/attributes/add/`
- Edit Type: `http://localhost:8000/dashboard/attributes/<id>/edit/`
- Delete Type: `http://localhost:8000/dashboard/attributes/<id>/delete/`
- List Values: `http://localhost:8000/dashboard/attributes/<id>/values/`
- Add Value: `http://localhost:8000/dashboard/attributes/<id>/values/add/`
- Edit Value: `http://localhost:8000/dashboard/attribute-values/<id>/edit/`
- Delete Value: `http://localhost:8000/dashboard/attribute-values/<id>/delete/`

---

## File Locations

### Forms
`apps/catalog/forms.py`
- CategoryForm
- BrandForm
- AttributeTypeForm
- AttributeValueForm
- ProductForm (ready)
- ProductVariantForm (ready)

### Views
`apps/dashboard/views.py`
- Category: list, add, edit, delete ✅
- Brand: list, add, edit, delete ✅
- Attribute: list, add, edit, delete ✅
- AttributeValue: list, add, edit, delete ✅
- Product: views exist, need full implementation
- Variant: views exist, need full implementation

### Templates
```
templates/admin/modules/
├── categories/
│   ├── list.html ✅
│   ├── add.html ✅
│   ├── edit.html ✅
│   └── delete.html ✅
├── brands/
│   ├── list.html ✅
│   ├── add.html ✅
│   ├── edit.html ✅
│   └── delete.html ✅
├── attributes/
│   ├── list.html ✅
│   ├── add.html ✅
│   ├── edit.html ✅
│   └── delete.html ✅
└── attribute_values/
    ├── list.html ✅
    ├── add.html ✅
    ├── edit.html ✅
    └── delete.html ✅
```

---

## Testing Commands

### Test Media Configuration (IMPORTANT - Run First!)
```bash
python test_media_config.py
```
**Expected**: All tests should pass ✅

### Run Server
```bash
python manage.py runserver
```

### Create Superuser (if needed)
```bash
python manage.py createsuperuser
```

### Run Migrations (if needed)
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Image Upload Testing

### Verify Images Load Correctly
1. **Restart server** after applying media fixes
2. **Upload a brand logo**:
   - Go to Dashboard → Brands → Add Brand
   - Upload an image file
   - Save and check if logo displays in list
3. **Upload category image**:
   - Go to Dashboard → Categories → Add Category
   - Upload an image file
   - Save and check if image displays in list
4. **Direct URL test**:
   - Try accessing: `http://localhost:8000/media/brands/<filename>`
   - Should display the image, not 404

### If Images Don't Load:
- See `IMAGE_LOADING_GUIDE.md` for detailed troubleshooting
- Hard refresh browser (Ctrl+Shift+R)
- Check browser console for errors
- Verify `test_media_config.py` passes all tests

---

## Common Tasks

### Add New Category
1. Go to Dashboard → Catalog → Categories
2. Click "Add Category"
3. Fill in: Name, Parent (optional), Description, Image
4. Set Display Order and Active status
5. Click "Save Category"

### Add Brand
1. Go to Dashboard → Catalog → Brands
2. Click "Add Brand"
3. Fill in: Name, Description, Logo, Website
4. Set Active status
5. Click "Save Brand"

### Add Attribute with Values
1. Go to Dashboard → Catalog → Attributes
2. Click "Add Attribute Type"
3. Enter name (e.g., "Color")
4. Click "Save Attribute Type"
5. Click on the newly created attribute
6. Click "Add Value"
7. Enter value (e.g., "Red")
8. Repeat for more values

---

## Navigation Flow

```
Dashboard
└── Catalog (sidebar)
    ├── Categories
    │   ├── List (search, filter)
    │   ├── Add
    │   └── Edit/Delete
    ├── Brands
    │   ├── List (search, filter)
    │   ├── Add
    │   └── Edit/Delete
    ├── Products (not fully implemented yet)
    └── Attributes
        ├── List Types (search)
        ├── Add Type
        ├── Edit/Delete Type
        └── Manage Values
            ├── List Values
            ├── Add Value
            └── Edit/Delete Value
```

---

## Features Overview

### Completed ✅
- **Categories**: Full CRUD with parent-child relationships
- **Brands**: Full CRUD with logo upload
- **Attributes**: Full CRUD for types and values
- **Search**: Available on all list views
- **Filters**: Status filters, parent filters
- **Images**: Upload and preview for categories and brands
- **Validation**: Form validation with error messages
- **Messages**: Success/error notifications
- **Confirmations**: Delete confirmations with warnings

### Pending ⏳
- **Products**: Need full implementation
- **Variants**: Need full implementation
- **Pagination**: To be added if needed
- **Bulk Actions**: Future enhancement

---

## Important Notes

### File Uploads
- Categories: Upload to `media/categories/`
- Brands: Upload to `media/brands/`
- Products: Upload to `media/products/%Y/%m/`

### Permissions
All views require:
- User to be authenticated
- User to have `is_staff=True`

### Auto-Generation
Slugs are auto-generated from names if left empty

### Cascade Behavior
- Deleting category: Deletes children categories
- Deleting brand: Keeps products, removes brand association
- Deleting attribute type: Deletes all its values

---

## Troubleshooting

### "Permission Denied"
→ Make sure user has `is_staff=True`

### "404 Not Found"
→ Check URL pattern in `apps/dashboard/urls.py`
→ Ensure app_name='dashboard' is set

### "Image not displaying"
→ Check MEDIA_URL and MEDIA_ROOT in settings
→ Ensure static files are configured properly

### "Form not saving"
→ Check form validation errors
→ Ensure all required fields are filled

---

## Next Steps

1. **Test Everything**
   ```bash
   python manage.py runserver
   ```
   Navigate to: http://localhost:8000/dashboard/

2. **Create Sample Data**
   - Add 2-3 categories
   - Add 2-3 brands
   - Add 2 attribute types with values each

3. **Continue to Phase 4**
   - Product management implementation
   - Or let me know if you need any adjustments!

---

*Quick Reference Guide - Last Updated: October 20, 2025*
