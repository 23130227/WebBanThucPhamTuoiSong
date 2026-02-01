import os
import cloudinary
import cloudinary.uploader
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import Product
from pages.models import HomeSlide
from blog.models import Post


class Command(BaseCommand):
    help = 'Migrate local media files to Cloudinary'

    def handle(self, *args, **options):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
        )

        # Upload vào folder "media/xxx" để khớp với cloudinary_storage
        self.migrate_model(Product, 'image', 'media/products', 'products')
        self.migrate_model(HomeSlide, 'background_image', 'media/home_slides', 'home_slides')
        self.migrate_model(Post, 'image', 'media/blog', 'blog')

        self.stdout.write(self.style.SUCCESS('\n✅ Migration completed!'))

    def migrate_model(self, model_class, image_field, cloudinary_folder, local_folder):
        self.stdout.write(f'\nMigrating {model_class.__name__}...')

        # Lấy danh sách file thực tế trong folder local
        local_folder_path = os.path.join(settings.MEDIA_ROOT, local_folder)

        if not os.path.exists(local_folder_path):
            self.stdout.write(
                self.style.WARNING(f'  ⚠ Folder not found: {local_folder_path}')
            )
            return

        # Tạo dict: tên file không extension -> tên file đầy đủ
        actual_files = {}
        for f in os.listdir(local_folder_path):
            name_without_ext = os.path.splitext(f)[0]
            actual_files[name_without_ext] = f

        count = 0
        for obj in model_class.objects.all():
            image = getattr(obj, image_field, None)

            if not image:
                continue

            # Lấy tên file từ database (có thể thiếu extension)
            db_filename = os.path.basename(image.name)
            db_name_without_ext = os.path.splitext(db_filename)[0]

            # Tìm file thực tế khớp với tên trong database
            if db_name_without_ext in actual_files:
                actual_filename = actual_files[db_name_without_ext]
            elif db_filename in actual_files.values():
                actual_filename = db_filename
            else:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ No matching file for: {image.name}')
                )
                continue

            local_path = os.path.join(local_folder_path, actual_filename)

            if not os.path.exists(local_path):
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ File not found: {local_path}')
                )
                continue

            try:
                # Lấy tên file không có extension để làm public_id
                filename_without_ext = os.path.splitext(actual_filename)[0]

                # Upload lên Cloudinary
                result = cloudinary.uploader.upload(
                    local_path,
                    folder=cloudinary_folder,  # media/products, media/home_slide, etc.
                    public_id=filename_without_ext,
                    overwrite=True,
                    resource_type="image"
                )

                # Lưu đường dẫn theo format của cloudinary_storage
                # Format: local_folder/filename (KHÔNG có "media/" prefix, KHÔNG có extension)
                new_path = f"{local_folder}/{filename_without_ext}"

                setattr(obj, image_field, new_path)
                obj.save()

                count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ {actual_filename} -> {new_path}')
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Error: {actual_filename} - {str(e)}')
                )

        self.stdout.write(f'  📊 Total {model_class.__name__}: {count} images migrated')