# Image Loading - Before & After Guide

## What Was Wrong ❌

### Symptoms:
1. **Brand List**: Logos showed as broken image icons or placeholder divs
2. **Category List**: Images showed as broken image icons or placeholder divs
3. **Browser Console**: 404 errors for `/media/brands/logo.png` or similar
4. **Direct Access**: Visiting `http://localhost:8000/media/brands/logo.png` returned 404

### Technical Cause:
- Django development server wasn't configured to serve files from `/media/` URL
- Templates couldn't access `{{ MEDIA_URL }}` variable

## What's Fixed Now ✅

### Expected Behavior After Fix:

#### 1. Brand Logo Display
**Location**: `http://localhost:8000/dashboard/brands/`

```
┌─────────────────────────────────────────────────────────┐
│  Brands                                  [Add Brand]    │
├─────────────────────────────────────────────────────────┤
│ Logo    Name        Slug      Products  Status          │
├─────────────────────────────────────────────────────────┤
│ [🏷️]   Brand A     brand-a      5      Active          │
│ [🏷️]   Brand B     brand-b      3      Active          │
│ [📦]   Brand C     brand-c      0      Inactive        │
└─────────────────────────────────────────────────────────┘

Legend:
🏷️ = Actual uploaded logo image displayed
📦 = No logo (shows placeholder icon)
```

#### 2. Category Image Display
**Location**: `http://localhost:8000/dashboard/categories/`

```
┌─────────────────────────────────────────────────────────┐
│  Categories                        [Add Category]       │
├─────────────────────────────────────────────────────────┤
│ Image   Name        Parent   Status   Display Order    │
├─────────────────────────────────────────────────────────┤
│ [🖼️]   Bikes       —        Active        1            │
│ [🖼️]   Parts       —        Active        2            │
│ [📁]   Helmets     —        Inactive      3            │
└─────────────────────────────────────────────────────────┘

Legend:
🖼️ = Actual uploaded image displayed
📁 = No image (shows placeholder icon)
```

#### 3. Edit Page Preview
**Location**: `http://localhost:8000/dashboard/brands/1/edit/`

```
┌─────────────────────────────────────┐
│  Edit Brand: Brand A                │
├─────────────────────────────────────┤
│                                     │
│  Brand Name: [Brand A          ]   │
│  Slug:       [brand-a          ]   │
│                                     │
│  Current Logo:                      │
│  ┌─────────────┐                    │
│  │             │                    │
│  │  [ACTUAL    │  ← Logo displays   │
│  │   LOGO]     │     here!         │
│  │             │                    │
│  └─────────────┘                    │
│                                     │
│  Change Logo: [Choose File]         │
│                                     │
│  [Update Brand] [Cancel]            │
└─────────────────────────────────────┘
```

## Testing Steps

### Step 1: Test Configuration
```bash
# Run the test script
python test_media_config.py
```

**Expected Output:**
```
============================================================
MEDIA CONFIGURATION TEST
============================================================

1. Checking MEDIA_URL...
   MEDIA_URL: /media/
   ✅ MEDIA_URL is correctly configured

2. Checking MEDIA_ROOT...
   MEDIA_ROOT: D:\Projects\bike_shop\media
   ✅ MEDIA_ROOT directory exists

3. Checking media subdirectories...
   ✅ brands/ exists
   ✅ categories/ exists
   ✅ products/ exists

4. Checking template context processors...
   ✅ Media context processor is enabled
   ✅ Static context processor is enabled

5. Checking DEBUG mode...
   DEBUG: True
   ✅ DEBUG is True (media serving enabled)

============================================================
TEST SUMMARY
============================================================
✅ All tests passed! Media files should work correctly.
```

### Step 2: Restart Server
```bash
# Stop current server (Ctrl+C if running)
python manage.py runserver
```

### Step 3: Test Brand Logo Upload

1. **Navigate to**: `http://localhost:8000/dashboard/brands/add/`

2. **Fill the form**:
   - Brand Name: `Test Brand`
   - Logo: Upload an image file (JPG, PNG)
   - Click "Save Brand"

3. **Check the list**: `http://localhost:8000/dashboard/brands/`
   - ✅ You should see the uploaded logo displayed
   - ❌ If you see a broken image, check browser console

4. **Edit the brand**: Click edit button
   - ✅ You should see "Current Logo" with the image displayed
   - ✅ Below that, option to "Change Logo"

### Step 4: Test Category Image Upload

1. **Navigate to**: `http://localhost:8000/dashboard/categories/add/`

2. **Fill the form**:
   - Category Name: `Test Category`
   - Image: Upload an image file
   - Click "Save Category"

3. **Check the list**: `http://localhost:8000/dashboard/categories/`
   - ✅ You should see the uploaded image displayed

4. **Edit the category**: Click edit button
   - ✅ You should see "Current Image" preview

### Step 5: Direct URL Test

After uploading, try accessing the image directly:

```
http://localhost:8000/media/brands/your-uploaded-logo.jpg
```

- ✅ **Should**: Display the image in browser
- ❌ **Should NOT**: Show 404 error

## Troubleshooting

### Problem: Images still not showing

**Solution 1: Hard Refresh Browser**
```
Chrome/Firefox: Ctrl + Shift + R (Windows) or Cmd + Shift + R (Mac)
```

**Solution 2: Clear Browser Cache**
```
Chrome: Settings → Privacy → Clear browsing data → Cached images
```

**Solution 3: Check Browser Console**
```
1. Press F12 to open Developer Tools
2. Go to "Console" tab
3. Look for red error messages
4. Check "Network" tab for failed image requests
```

**Solution 4: Verify File Exists**
```bash
# Windows PowerShell
dir media\brands\

# Should show your uploaded files
```

**Solution 5: Check File Permissions**
```bash
# Make sure media directory is writable
# Windows: Right-click folder → Properties → Security
# Ensure "Users" have "Write" permission
```

### Problem: Upload works but image is broken

**Possible Causes:**
1. File is corrupted
2. File extension not supported
3. File too large

**Solutions:**
- Try a different image file (JPG or PNG recommended)
- Check file size (should be < 2.5 MB by default)
- Verify image opens in image viewer before uploading

### Problem: 404 Error on image URL

**Check This:**
1. Server is running: `python manage.py runserver`
2. DEBUG = True in settings.py
3. URL configuration includes media serving code
4. File actually exists in media folder

## Files Changed Summary

### 1. bike_shop/urls.py
**Added:**
```python
# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

### 2. bike_shop/settings.py
**Added to context_processors:**
```python
'django.template.context_processors.media',
'django.template.context_processors.static',
```

### 3. Templates (No changes needed)
Templates already correctly use:
```django
{{ brand.logo.url }}
{{ category.image.url }}
```

## Success Checklist

- [ ] Ran `python test_media_config.py` - all tests passed
- [ ] Restarted Django server
- [ ] Uploaded a brand logo - logo displays in list
- [ ] Uploaded a category image - image displays in list
- [ ] Edited brand - logo preview shows
- [ ] Edited category - image preview shows
- [ ] Direct URL access works (e.g., `/media/brands/test.jpg`)
- [ ] No 404 errors in browser console
- [ ] No broken image icons

## Ready to Continue?

Once all checkboxes above are ✅, you're ready to proceed with:
- **Phase 4**: Product Management (with multiple images)
- **Phase 5**: Product Variant Management

---

*Guide Created: October 20, 2025*
