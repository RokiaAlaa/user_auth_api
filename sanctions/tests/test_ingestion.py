from django.test import TestCase
from ..services import sync_sdn_data
from ..models import SDNEntry, Alias

class SyncSdnDataTests(TestCase):
    def test_parses_and_saves_individual_entries(self):
        
        sample_sdn_text = ('4107,"RODRIGUEZ OREJUELA, Gilberto Jose","individual","SDNT"\n'
                           '4108,"RODRIGUEZ OREJUELA, Miguel Angel","individual","SDNT"\n'
                           '4238,"MAR AZUL", "vessel", "CUBA"\n')

        sample_alt_text = ('36,4107,"aka","AERO-CARIBBEAN"\n'
                           '173,4108,"aka","AVIA IMPORT"\n')
        
        result = sync_sdn_data(sdn_text=sample_sdn_text, alt_text=sample_alt_text)

        self.assertEqual(SDNEntry.objects.count(), 2)
        self.assertEqual(Alias.objects.count(), 2)
        self.assertEqual(result, {'parsed_entries' : 2, 'new_entries': 2, 'removed_entries': 0, 'created_aliases': 2})