from django.core.management.base import BaseCommand
from leads.models import StageHistory


class Command(BaseCommand):
    help = 'Delete old stage history records with hardcoded "Sales stage updated" remarks'

    def handle(self, *args, **options):
        # Delete records with hardcoded message
        deleted_count, _ = StageHistory.objects.filter(notes='Sales stage updated').delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {deleted_count} old history records with hardcoded remarks'
            )
        )
