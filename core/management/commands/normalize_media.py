import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Item


class Command(BaseCommand):
    help = 'Normalize Item image filenames to media_root/images/{slug}{ext} and update DB entries.'

    def handle(self, *args, **options):
        media = settings.MEDIA_ROOT
        images_dir = os.path.join(media, 'images')
        if not os.path.isdir(images_dir):
            self.stdout.write(self.style.ERROR(
                'media_root/images does not exist. Run organize_media first.'))
            return
        updated = 0
        for item in Item.objects.all():
            if not item.image:
                continue
            try:
                cur_path = item.image.path
            except Exception:
                # ImageField may store name only
                cur_path = os.path.join(media, item.image.name)
            if not os.path.exists(cur_path):
                self.stdout.write(self.style.WARNING(
                    f'File not found for item {item.slug}: {cur_path}'))
                continue
            _, ext = os.path.splitext(cur_path)
            base = item.slug or item.title.replace(' ', '-').lower()
            safe_name = f"{base}{ext}"
            dest = os.path.join(images_dir, safe_name)
            i = 1
            while os.path.exists(dest):
                dest = os.path.join(images_dir, f"{base}-{i}{ext}")
                i += 1
            shutil.copy2(cur_path, dest)
            item.image.name = os.path.join(
                'images', os.path.basename(dest)).replace('\\', '/')
            item.save()
            updated += 1
        self.stdout.write(self.style.SUCCESS(
            f'Updated {updated} Item image paths.'))
