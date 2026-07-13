import requests
from django.core.management.base import BaseCommand
from sanctions.models import SDNEntry, Alias
import csv
import io
from sanctions.services import sync_sdn_data


class Command(BaseCommand):
    def handle(self, *args, **options):
        result = sync_sdn_data()

        self.stdout.write(f'Parsed {result['parsed_entries']} individual entries')
        self.stdout.write(f'Saved {result['new_entries']} new entries')
        self.stdout.write(f'Saved {result['created_aliases']} aliases')