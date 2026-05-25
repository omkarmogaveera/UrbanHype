import os
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Category, Item
from django.utils.text import slugify
import random


class Command(BaseCommand):
    help = 'Seed Items from files in MEDIA_ROOT'

    def handle(self, *args, **options):
        media = settings.MEDIA_ROOT
        if not os.path.isdir(media):
            self.stdout.write(self.style.ERROR(
                f'MEDIA_ROOT not found: {media}'))
            return
        files = [f for f in os.listdir(media) if os.path.isfile(os.path.join(
            media, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        if not files:
            self.stdout.write('No image files found in MEDIA_ROOT')
            return
        cat, created = Category.objects.get_or_create(title='Imported', slug='imported', defaults={
                                                      'description': 'Imported from advanced repo', 'is_active': True})
        created_count = 0
        for fn in files:
            # skip files that look like UI banners
            if fn.lower().startswith('banner') or fn.lower().startswith('add'):
                continue
            name = os.path.splitext(fn)[0]
            slug = slugify(name)[:50]
            if Item.objects.filter(slug=slug).exists():
                continue
            item = Item()
            item.title = name.replace('-', ' ').replace('_', ' ').title()
            item.price = round(random.uniform(12, 120), 2)
            item.discount_price = None
            item.category = cat
            item.label = 'N'
            item.slug = slug
            item.stock_no = str(random.randint(1000, 9999))
            item.description_short = item.title
            item.description_long = item.title + ' — imported sample product.'
            # set image name relative to MEDIA_ROOT
            item.image.name = fn
            item.is_active = True
            item.save()
            created_count += 1
        self.stdout.write(self.style.SUCCESS(
            f'Created {created_count} items in category "{cat.title}"'))
