from django.test import TestCase
from ..services import sync_sdn_data, sync_un_data
from ..models import SDNEntry, Alias
from .fixtures import sample_un_xml, sample_un_xml_removed

class SyncIdempotencyOFACTest(TestCase):
    def test_running_sync_data_does_not_duplicate_data(self):
        sample_sdn_text = (
            '4107,"RODRIGUEZ OREJUELA, Gilberto Jose","individual","SDNT"\n'
            '4108,"RODRIGUEZ OREJUELA, Miguel Angel","individual","SDNT"\n'
        )
        sample_alt_text = (
            '36,4107,"aka","AERO-CARIBBEAN"\n'
        )
    
        response1 = sync_sdn_data(sdn_text=sample_sdn_text, alt_text=sample_alt_text)
        response2 = sync_sdn_data(sdn_text=sample_sdn_text, alt_text=sample_alt_text)

        self.assertEqual(SDNEntry.objects.count(), 2)
        self.assertEqual(Alias.objects.count(), 1)

        self.assertEqual(response2, {'parsed_entries' : 2, 'new_entries': 0, 'removed_entries': 0, 'created_aliases': 0})

    def test_sync_removes_entries_not_in_new_data(self):
        sample_sdn_text = (
            '4107,"RODRIGUEZ OREJUELA, Gilberto Jose","individual","SDNT"\n'
            '4108,"RODRIGUEZ OREJUELA, Miguel Angel","individual","SDNT"\n'
        )
        sample_sdn_text_removed = (
            '4107,"RODRIGUEZ OREJUELA, Gilberto Jose","individual","SDNT"\n'
        )

        sample_alt_text = (
        '36,4108,"aka","AERO-CARIBBEAN"\n'
        )
        
        response1 = sync_sdn_data(sdn_text=sample_sdn_text, alt_text=sample_alt_text)
        response2 = sync_sdn_data(sdn_text=sample_sdn_text_removed, alt_text=sample_alt_text)

        self.assertEqual(SDNEntry.objects.count(), 1)
        self.assertEqual(Alias.objects.count(), 0)
        self.assertEqual(SDNEntry.objects.filter(uid=4108).exists(), False)
        self.assertEqual(response2['removed_entries'], 1)

class SyncIdempotencyUNTest(TestCase):
    def test_running_sync_data_does_not_duplicate_data(self):
        response1 = sync_un_data(xml_text=sample_un_xml)
        response2 = sync_un_data(xml_text=sample_un_xml)

        self.assertEqual(SDNEntry.objects.filter(source='UN').count(), 2)
        self.assertEqual(response2, {'parsed_entries' : 2, 'new_entries': 0, 'removed_entries': 0, 'created_aliases': 0})


    def test_sync_removes_entries_not_in_new_data(self):
        
        response1 = sync_un_data(xml_text=sample_un_xml)
        response2 = sync_un_data(xml_text=sample_un_xml_removed)

        self.assertEqual(SDNEntry.objects.filter(source='UN').count(), 1)
        self.assertEqual(SDNEntry.objects.filter(uid=6908000, source='UN').exists(), False)
        self.assertEqual(Alias.objects.count(), 0)
        self.assertEqual(response2['removed_entries'], 1)