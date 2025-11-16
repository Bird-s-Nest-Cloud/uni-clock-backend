"""
Media Configuration Test Script
Run this to verify media files are configured correctly
"""

from django.conf import settings
import os

def test_media_configuration():
    print("=" * 60)
    print("MEDIA CONFIGURATION TEST")
    print("=" * 60)
    
    # Test 1: Check MEDIA_URL
    print("\n1. Checking MEDIA_URL...")
    print(f"   MEDIA_URL: {settings.MEDIA_URL}")
    if settings.MEDIA_URL == '/media/':
        print("   ✅ MEDIA_URL is correctly configured")
    else:
        print("   ❌ MEDIA_URL should be '/media/'")
    
    # Test 2: Check MEDIA_ROOT
    print("\n2. Checking MEDIA_ROOT...")
    print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
    if os.path.exists(settings.MEDIA_ROOT):
        print("   ✅ MEDIA_ROOT directory exists")
    else:
        print("   ❌ MEDIA_ROOT directory does not exist")
        print(f"   Creating directory: {settings.MEDIA_ROOT}")
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    
    # Test 3: Check subdirectories
    print("\n3. Checking media subdirectories...")
    subdirs = ['brands', 'categories', 'products']
    for subdir in subdirs:
        subdir_path = os.path.join(settings.MEDIA_ROOT, subdir)
        if os.path.exists(subdir_path):
            print(f"   ✅ {subdir}/ exists")
        else:
            print(f"   ⚠️  {subdir}/ does not exist, creating...")
            os.makedirs(subdir_path, exist_ok=True)
    
    # Test 4: Check context processors
    print("\n4. Checking template context processors...")
    context_processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']
    
    has_media = 'django.template.context_processors.media' in context_processors
    has_static = 'django.template.context_processors.static' in context_processors
    
    if has_media:
        print("   ✅ Media context processor is enabled")
    else:
        print("   ❌ Media context processor is missing")
    
    if has_static:
        print("   ✅ Static context processor is enabled")
    else:
        print("   ❌ Static context processor is missing")
    
    # Test 5: Check DEBUG mode
    print("\n5. Checking DEBUG mode...")
    print(f"   DEBUG: {settings.DEBUG}")
    if settings.DEBUG:
        print("   ✅ DEBUG is True (media serving enabled)")
    else:
        print("   ⚠️  DEBUG is False (media serving may not work)")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_good = (
        settings.MEDIA_URL == '/media/' and
        os.path.exists(settings.MEDIA_ROOT) and
        has_media and
        has_static and
        settings.DEBUG
    )
    
    if all_good:
        print("✅ All tests passed! Media files should work correctly.")
        print("\nNext steps:")
        print("1. Restart your Django server")
        print("2. Try uploading an image via the admin panel")
        print("3. Check if the image displays in the list view")
    else:
        print("⚠️  Some tests failed. Please check the configuration above.")
    
    print("=" * 60)

if __name__ == "__main__":
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bike_shop.settings')
    django.setup()
    test_media_configuration()
