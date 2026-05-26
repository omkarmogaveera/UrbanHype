# UrbanHype

A full-featured e-commerce web application built with Django. Browse products across multiple categories, filter and sort by price, add items to your cart, and manage your order — all without a payment system, keeping the focus on the shopping experience.

**Built with:** Django 2.2 · Python 3.10 · PostgreSQL (Neon) · Bootstrap 4 · django-allauth

---

## Pages

**Home**
![Home Page](screenshots/home.png)

**Shop**
![Shop Page](screenshots/shop.png)

**Category**
![Category Page](screenshots/category.png)

**Product Detail**
![Product Detail](screenshots/product-detail.png)

**Sign In**
![Sign In](screenshots/sign-up.png)

---

## Features

- Browse 50+ products across categories: Beauty, Books, Clothings, Furniture, Laptops, Mobiles
- Filter by price range and sort by name or price (ascending/descending)
- Add / remove items from cart with quantity control
- User authentication — register, login, logout (django-allauth)
- Django admin panel for managing products, categories, and orders
- Environment-based settings — safe for deployment with no secrets hardcoded

---

## Local Setup

```bash
git clone https://github.com/your-username/UrbanHype.git
cd UrbanHype
```

**Create and activate a virtual environment:**

```bash
# Windows
python -m venv env
env\Scripts\activate

# Mac / Linux
python -m venv env
source env/bin/activate
```

**Install dependencies:**

```bash
pip install -r requirements-advanced.txt
```

**Run migrations and start the server:**

```bash
python manage.py migrate --settings=app.local_test_settings
python manage.py runserver --settings=app.local_test_settings
```

Visit `http://127.0.0.1:8000`

---

## Admin Access

```bash
python manage.py createsuperuser --settings=app.local_test_settings
```

Then go to `http://127.0.0.1:8000/admin/`

---

## Deployment

Copy `.env.example` to `.env` and fill in your values, or set them as environment variables in your hosting dashboard (Railway, Render, etc.):

```
DJANGO_SECRET_KEY=your-generated-secret-key
DJANGO_DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
```

Generate a secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---
