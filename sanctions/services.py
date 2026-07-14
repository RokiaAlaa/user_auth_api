import requests
from .models import SDNEntry, Alias, SyncLog
import csv
import io


SDN_URL = 'https://www.treasury.gov/ofac/downloads/sdn.csv'
ALT_URL = 'https://www.treasury.gov/ofac/downloads/alt.csv'

def sync_sdn_data(sdn_text=None, alt_text=None):

    if sdn_text is None:
        response = requests.get(SDN_URL)
        response.raise_for_status()
        sdn_text = response.text

    existing_uids_before = set(SDNEntry.objects.values_list('uid', flat=True))

    reader = csv.reader(io.StringIO(sdn_text))
    entries_to_create = []
    parsed_uids = set()

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

        parsed_uids.add(uid)
        entry = SDNEntry(uid=uid, name=name, entity_type=entity_type, program=program)
        entries_to_create.append(entry)

    parsed_entries = len(entries_to_create)

    before = SDNEntry.objects.count()
    SDNEntry.objects.bulk_create(entries_to_create, ignore_conflicts=True)
    after = SDNEntry.objects.count()
    
    new_entries = after - before

    removed_uids = existing_uids_before - parsed_uids
    SDNEntry.objects.filter(uid__in=removed_uids).delete()
    removed_count = len(removed_uids)


    
    if alt_text is None:
        response = requests.get(ALT_URL)
        response.raise_for_status()
        alt_text = response.text

    entries_map = {entry.uid: entry for entry in SDNEntry.objects.all()}

    reader = csv.reader(io.StringIO(alt_text))
    aliases_to_create = []

    for row in reader:

        if len(row) < 4:
            continue

        entnum = row[1]

        try:
            entnum = int(entnum)
        except ValueError:
            continue

        if entnum not in entries_map:
            continue

        entry = entries_map[entnum]
        alias = Alias(entry=entry, alias_type=row[2].strip(), alias_name=row[3].strip())

        aliases_to_create.append(alias)

    before = Alias.objects.count()
    Alias.objects.bulk_create(aliases_to_create, ignore_conflicts=True)
    after = Alias.objects.count()
    
    created_aliases = after - before

    SyncLog.objects.create(
        parsed_entries=parsed_entries,
        new_entries=new_entries,
        removed_entries=removed_count,
        new_aliases=created_aliases

    )

    return {'parsed_entries' : parsed_entries, 'new_entries': new_entries, 'removed_entries': removed_count, 'created_aliases': created_aliases}