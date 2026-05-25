import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Item

IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.webp', '.gif')


class Command(BaseCommand):
    help = 'Move loose images in MEDIA_ROOT into MEDIA_ROOT/images and update Item.image paths.'

    def handle(self, *args, **options):
        media = settings.MEDIA_ROOT
        images_dir = os.path.join(media, 'images')
        if not os.path.isdir(media):
            self.stdout.write(self.style.ERROR(
                f'MEDIA_ROOT does not exist: {media}'))
            return
        os.makedirs(images_dir, exist_ok=True)
        moved = 0
        updated = 0
        for fname in os.listdir(media):
            fpath = os.path.join(media, fname)
            if os.path.isdir(fpath):
                continue
            if not fname.lower().endswith(IMAGE_EXTS):
                continue
            # skip if already inside images (shouldn't be)
            if os.path.dirname(fpath).endswith('images'):
                continue
            dest = os.path.join(images_dir, fname)
            # avoid overwrite by renaming if exists
            if os.path.exists(dest):
                base, ext = os.path.splitext(fname)
                i = 1
                while True:
                    newname = f"{base}-{i}{ext}"
                    dest = os.path.join(images_dir, newname)
                    if not os.path.exists(dest):
                        fname = newname
                        break
                    i += 1
            shutil.move(fpath, dest)
            moved += 1
            # update any Item using the old filename (basename match)
            for item in Item.objects.filter(image__icontains=os.path.basename(fpath)):
                item.image.name = os.path.join(
                    'images', os.path.basename(dest)).replace('\\', '/')
                item.save()
                updated += 1
        self.stdout.write(self.style.SUCCESS(
            f'Moved {moved} files and updated {updated} Item records.'))
