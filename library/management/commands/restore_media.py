import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Restore media files from media_source/ into media/'

    def handle(self, *args, **options):
        source_dir = Path(settings.BASE_DIR) / 'media_source'
        target_dir = Path(settings.MEDIA_ROOT)

        if not source_dir.exists():
            self.stdout.write(self.style.WARNING('media_source/ không tồn tại, bỏ qua.'))
            return

        count = 0
        for item in source_dir.rglob('*'):
            if item.is_file():
                relative_path = item.relative_to(source_dir)
                dest_path = target_dir / relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                if not dest_path.exists():
                    shutil.copy2(item, dest_path)
                    count += 1
        self.stdout.write(self.style.SUCCESS(f'Đã khôi phục {count} file media.'))