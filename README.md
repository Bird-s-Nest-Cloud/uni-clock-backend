# BikeShop E-Commerce Platform

A comprehensive e-commerce platform built with Django 5.2.7 for managing bike products, variants, and attributes.

## 🚀 Features

### Custom Admin Panel
Complete custom admin implementation with full CRUD operations for:
- **Categories** - Hierarchical product categorization with images
- **Brands** - Brand management with logos and descriptions
- **Attributes** - Flexible attribute system (Color, Size, Material, etc.)
- **Products** - Multi-image product management with SEO fields
- **Product Variants** - SKU-based variants with attribute assignment

### Key Capabilities
- ✅ Multi-image upload and management
- ✅ Search and advanced filtering
- ✅ Stock management with alerts
- ✅ Pricing with sale price support
- ✅ Parent-child hierarchies
- ✅ SEO optimization fields
- ✅ Responsive Bootstrap 5 UI
- ✅ Secure authentication and authorization

## 📚 Documentation

All comprehensive documentation is available in the [`development_logs/`](development_logs/) folder:

### Quick Start
- **[README](development_logs/README.md)** - Documentation overview
- **[Complete Summary](development_logs/COMPLETE_IMPLEMENTATION_SUMMARY.md)** - Full project details
- **[URLs Reference](development_logs/ADMIN_URLS_REFERENCE.md)** - Testing guide with all URLs

### Technical Guides
- **[Implementation Log](development_logs/ADMIN_IMPLEMENTATION_LOG.md)** - Phase-by-phase development log
- **[Quick Reference](development_logs/QUICK_REFERENCE.md)** - Commands and shortcuts
- **[Image Loading Guide](development_logs/IMAGE_LOADING_GUIDE.md)** - Image upload handling

### Troubleshooting
- **[ApexCharts & Form Fixes](development_logs/APEXCHARTS_ERROR_FIX.md)** - Common issues and solutions
- **[Image Fix Documentation](development_logs/IMAGE_FIX_DOCUMENTATION.md)** - Media configuration fixes

## 🛠️ Technology Stack

- **Framework:** Django 5.2.7
- **Database:** MySQL
- **Frontend:** Bootstrap 5, Iconoir Icons
- **Template Engine:** Django Templates
- **Python:** 3.x

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Bird-s-Nest-Cloud/be-ecomm-affiliate.git
   cd be-ecomm-affiliate
   ```

2. **Install dependencies**
   ```bash
   pipenv install
   pipenv shell
   ```

3. **Configure database**
   - Update `bike_shop/settings.py` with your MySQL credentials

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Access admin panel**
   ```
   http://localhost:8000/dashboard/
   ```

## 🎯 Admin Access

### Requirements
- User must have `is_staff = True`
- Login at: `http://localhost:8000/accounts/login/`

### Make User Staff
```python
python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='your_username')
user.is_staff = True
user.save()
```

## 📊 Project Status

**Status:** ✅ Production Ready

### Completed Features
- [x] Phase 1: Category Management
- [x] Phase 2: Brand Management
- [x] Phase 3: Attribute Management
- [x] Phase 4: Product Management
- [x] Phase 5: Product Variant Management
- [x] All bug fixes and optimizations

### Statistics
- **24 Templates** created
- **24 View Functions** implemented
- **6 Form Classes** with validation
- **8 Documentation Files** comprehensive guides
- **0 Errors** - clean codebase

## 🔐 Security

- CSRF protection on all forms
- User authentication with `@user_passes_test` decorator
- File upload validation
- SQL injection prevention via Django ORM
- Secure media file handling

## 🤝 Contributing

This is a private repository. For questions or contributions, please contact the project maintainers.

## 📝 License

Proprietary - All rights reserved

## 📧 Contact

- **Organization:** Bird's Nest Cloud
- **Repository:** be-ecomm-affiliate
- **Branch:** main

---

*Last Updated: October 20, 2025*
```
