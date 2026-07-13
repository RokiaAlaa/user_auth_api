import requests
from django.core.management.base import BaseCommand
from sanctions.models import SDNEntry, Alias
import csv
import io


SDN_URL = 'https://www.treasury.gov/ofac/downloads/sdn.csv'
ALT_URL = 'https://www.treasury.gov/ofac/downloads/alt.csv'

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Downloading SDN data...')

        response = requests.get(SDN_URL)
        response.raise_for_status()
        sdn_text = response.text

        reader = csv.reader(io.StringIO(sdn_text))

        entries_to_create = []

        for row in reader:
            
            if len(row) < 4:
                continue

            uid = row[0]
            name = row[1].strip()
            entity_type = row[2].strip()
            program = row[3].strip()

            if entity_type != 'individual':
                continue

            try:
                uid = int(uid)
            except ValueError:
                continue

            entry = SDNEntry(uid=uid, name=name, entity_type=entity_type, program=program)

            entries_to_create.append(entry)

        self.stdout.write(f'Parsed {len(entries_to_create)} individual entries')

        before = SDNEntry.objects.count()
        SDNEntry.objects.bulk_create(entries_to_create, ignore_conflicts=True)
        after = SDNEntry.objects.count()
        self.stdout.write(f'Saved {after - before} new entries')
