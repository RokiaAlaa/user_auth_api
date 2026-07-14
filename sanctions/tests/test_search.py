from django.test import TestCase
from ninja.testing import TestClient
from ..api import router, MIN_SIMILARITY
from ..models import SDNEntry, Alias

class SearchEndpointTests(TestCase):
    def setUp(self):
        entry1 = SDNEntry.objects.create(uid=1, name='ABBAS Abu', entity_type='individual', program='SDGT')
        entry2 = SDNEntry.objects.create(uid=2, name='GHANIMAT Abd Al-Rahman', entity_type='individual', program='SDGT')
        Alias.objects.create(entry=entry2, alias_type='aka', alias_name='AL-ZUMAR Abbud')
        
        self.client = TestClient(router)

    def test_exact_match(self):
        response = self.client.get('/search?name=ABBAS Abu')
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(response.json()[0]['similarity'], 1, places=1)

    def test_typo_match(self):
        response = self.client.get('/search?name=ABAS Abu')
        self.assertEqual(response.status_code, 200)
        self.assertLess(response.json()[0]['similarity'], 1)
        self.assertGreater(response.json()[0]['similarity'], MIN_SIMILARITY)
    
    def test_no_match(self):
        response = self.client.get('/search?name=Xyzabc Qwerty123')
        self.assertEqual(response.json(), [])

    def test_alias_match(self):
        response = self.client.get('/search?name=AL-ZUMAR Abbud')
        self.assertEqual(response.json()[0]['name'], 'GHANIMAT Abd Al-Rahman')
        self.assertEqual(response.json()[0]['matched_aliases'][0]['alias_name'], 'AL-ZUMAR Abbud')
