import os
import urllib.request
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.text import slugify
from core.models import Category, Item, OrderItem, Order, Slide

GITHUB_RAW = "https://raw.githubusercontent.com/seebham/ecommerce-dummy-data/main/images/"
DATA_URL = "https://raw.githubusercontent.com/seebham/ecommerce-dummy-data/main/data.json"

CATEGORY_DESCRIPTIONS = {
    "Mobiles":    "The latest smartphones from top brands — Apple, Samsung, OnePlus and more.",
    "Books":      "Bestsellers, classics and regional titles across fiction, history and poetry.",
    "Clothings":  "Casual wear, formal shirts, kurtas and kids apparel for every occasion.",
    "Beauty":     "Skincare, hair care, fragrances and makeup from trusted brands.",
    "Furniture":  "Desks, sofas, beds and wardrobes to furnish your space in style.",
    "Laptops":    "Student, gaming and professional laptops from HP, Dell, Asus, Apple and more.",
}

CATEGORY_IMAGES = {
    "Mobiles":   "iphone12M1.jpg",
    "Books":     "monksoldhisferrari.jpg",
    "Clothings": "shirt.jpg",
    "Beauty":    "roseShowerGel.jpg",
    "Furniture": "desk.jpg",
    "Laptops":   "gamingLaptop1.jpg",
}


class Command(BaseCommand):
    help = "Clear old products & seed 50 fresh products from the GitHub dummy-data repo"

    def handle(self, *args, **kwargs):
        import json
        import urllib.request as req

        if Item.objects.exists():
            self.stdout.write(self.style.SUCCESS(
                'Database already seeded — skipping.'))
            return

        self.stdout.write("Fetching product data from GitHub...")
        with req.urlopen(DATA_URL, timeout=30) as r:
            data = json.loads(r.read().decode())

        products = data["products"]
        self.stdout.write(f"  Found {len(products)} products")

        # ------------------------------------------------------------------
        # 1. Delete old items (and dependent OrderItems / Orders / Categories)
        # ------------------------------------------------------------------
        self.stdout.write("Deleting old order items and orders...")
        OrderItem.objects.all().delete()
        Order.objects.all().delete()

        self.stdout.write("Deleting old products, categories and slides...")
        Item.objects.all().delete()
        Category.objects.all().delete()
        Slide.objects.all().delete()

        # ------------------------------------------------------------------
        # 2. Ensure media/images folder exists
        # ------------------------------------------------------------------
        img_dir = os.path.join(settings.MEDIA_ROOT, "images")
        os.makedirs(img_dir, exist_ok=True)

        # ------------------------------------------------------------------
        # 3. Create 6 categories (download one representative image each)
        # ------------------------------------------------------------------
        self.stdout.write("Creating categories...")
        cat_map = {}
        for name, desc in CATEGORY_DESCRIPTIONS.items():
            slug = slugify(name)
            img_filename = CATEGORY_IMAGES[name]
            local_path = os.path.join(img_dir, img_filename)
            if not os.path.exists(local_path):
                self._download(GITHUB_RAW + img_filename, local_path)
            cat = Category.objects.create(
                title=name,
                slug=slug,
                description=desc,
                image=f"images/{img_filename}",
                is_active=True,
            )
            cat_map[name] = cat
            self.stdout.write(f"  + Category: {name}")

        # ------------------------------------------------------------------
        # 4. Create items
        # ------------------------------------------------------------------
        self.stdout.write("Creating products...")
        created = 0
        for p in products:
            cat_name = p.get("category", "")
            cat = cat_map.get(cat_name)
            if not cat:
                self.stdout.write(self.style.WARNING(
                    f"  Skipping {p['title']} — unknown category '{cat_name}'"))
                continue

            # image
            imgs = p.get("imgs", [])
            img_filename = None
            if imgs:
                raw_url = imgs[0]
                # normalise: could be gitcdn or github raw
                fname = raw_url.split("/")[-1]
                local_path = os.path.join(img_dir, fname)
                if not os.path.exists(local_path):
                    # try GitHub raw first, fall back to original URL
                    github_url = GITHUB_RAW + fname
                    downloaded = self._download(github_url, local_path)
                    if not downloaded:
                        downloaded = self._download(raw_url, local_path)
                img_filename = f"images/{fname}" if os.path.exists(
                    local_path) else ""

            # specs → description_long
            specs = p.get("specs", "")
            if isinstance(specs, list):
                desc_long = " | ".join(specs)
            else:
                desc_long = str(specs)

            # label
            label = "P" if p.get("popular") else "N"

            # price — ensure it's a valid float
            price = float(p.get("price", 0) or 0)
            if price == 0:
                price = 9.99

            # slug — must be unique
            base_slug = slugify(p["title"])[:45]
            slug = base_slug
            counter = 1
            while Item.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            Item.objects.create(
                title=p["title"][:100],
                price=price,
                discount_price=None,
                category=cat,
                label=label,
                slug=slug,
                stock_no=p.get("id", slug[:10]),
                description_short=p["title"][:50],
                description_long=desc_long[:1000],
                image=img_filename or "",
                is_active=True,
            )
            created += 1
            self.stdout.write(f"  + [{created:02d}] {p['title'][:60]}")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. {created} products created across {len(cat_map)} categories."))

        # ------------------------------------------------------------------
        # 5. Create hero slides using banner images from static_in_env
        # ------------------------------------------------------------------
        import shutil
        banners_src = os.path.join(
            settings.BASE_DIR, 'static_in_env', 'images')
        banners_dst = os.path.join(settings.MEDIA_ROOT, 'banners')
        os.makedirs(banners_dst, exist_ok=True)

        SLIDES = [
            ("New Arrivals",     "Shop The Latest Collection",
             "/shop/",               "hero-01.jpg"),
            ("Top Electronics",  "Mobiles & Laptops On Sale",
             "/category/mobiles/",   "hero-02.jpg"),
            ("Home & Furniture", "Style Your Space",
             "/category/furniture/", "hero-03.jpg"),
        ]
        self.stdout.write("Creating slides...")
        for caption1, caption2, link, fname in SLIDES:
            src = os.path.join(banners_src, fname)
            dst = os.path.join(banners_dst, fname)
            if os.path.exists(src) and not os.path.exists(dst):
                shutil.copy2(src, dst)
            Slide.objects.create(
                caption1=caption1,
                caption2=caption2,
                link=link,
                image=f"banners/{fname}" if os.path.exists(dst) else "",
                is_active=True,
            )
        self.stdout.write(self.style.SUCCESS(f"Created {len(SLIDES)} slides."))

    def _download(self, url, dest):
        try:
            urllib.request.urlretrieve(url, dest)
            return True
        except Exception as e:
            self.stdout.write(self.style.WARNING(
                f"    Could not download {url}: {e}"))
            return False
