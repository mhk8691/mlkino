from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from .models import PropertyRecord, AgencyExpertLink


class SupplementaryPropertySearchTests(TestCase):
    def setUp(self):
        users = get_user_model()
        self.admin = users.objects.create_superuser('09123004001', 'test-password')
        self.agency = users.objects.create_user('09123004002', role='agency')
        self.expert = users.objects.create_user('09123004003', role='expert')
        self.outside = users.objects.create_user('09123004004', role='expert')
        AgencyExpertLink.objects.create(agency=self.agency, expert=self.expert)
        self.data = dict(city='قم', province='قم', district='منطقه ۳', neighborhood='امام خمینی', propertyType='آپارتمان', contractType='فروش', area=120, totalPrice=500, roomCount=3, floor=2, buildYear=1402, status='فعال', amenities=['پارکینگ', 'آسانسور'])
        self.match = PropertyRecord.objects.create(kind='file', created_by=self.expert, data=self.data)
        self.other = PropertyRecord.objects.create(kind='file', created_by=self.outside, data={**self.data, 'floor': 4, 'amenities': ['پارکینگ']})
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_combined_filters_agree_between_results_and_dashboard(self):
        query = dict(neighborhood='امام خمینی', areaFrom='۱۰۰', areaTo='۱۳۰', priceFrom='400', priceTo='600', roomCount='۳', floor='۲', buildYear='۱۴۰۲', creatorRoles='expert', amenities='پارکینگ|آسانسور')
        result = self.client.get('/panel/files/', query)
        self.assertEqual(result.status_code, 200, result.data)
        self.assertEqual([r['id'] for r in result.data['data']['results']], [self.match.pk])
        dashboard = self.client.get('/panel/dashboard/estate-overview/', query)
        self.assertEqual(dashboard.status_code, 200, dashboard.data)
        self.assertEqual(dashboard.data['data']['matching_files'], 1)

    def test_roles_and_identifier_respect_visibility(self):
        self.assertEqual(self.client.get('/panel/files/', {'creatorRoles': 'agency|user'}).data['data']['total_results'], 0)
        self.assertEqual(self.client.get('/panel/files/', {'recordId': self.match.pk}).data['data']['total_results'], 1)
        self.client.force_authenticate(self.agency)
        self.assertEqual(self.client.get('/panel/files/', {'recordId': self.other.pk}).data['data']['total_results'], 0)

    def test_invalid_filters_rejected_for_both_endpoints(self):
        for path in ('/panel/files/', '/panel/dashboard/estate-overview/'):
            for query in ({'areaFrom': 200, 'areaTo': 100}, {'floor': 'NaN'}, {'roomCount': '-1'}, {'creatorRoles': 'superadmin'}, {'buildYear': '1400.5'}):
                response = self.client.get(path, query)
                self.assertEqual(response.status_code, 400, (path, query, response.data))

    def test_all_selected_amenities_are_required_and_ordering_works(self):
        self.assertEqual(self.client.get('/panel/files/', {'amenities': 'آسانسور'}).data['data']['total_results'], 1)
        rows = self.client.get('/panel/files/', {'ordering': 'created_at'}).data['data']['results']
        self.assertEqual([r['id'] for r in rows], [self.match.pk, self.other.pk])
        rental = PropertyRecord.objects.create(kind='file', created_by=self.expert, data={**self.data, 'contractType': 'رهن و اجاره', 'mortgagePrice': 700})
        rows = self.client.get('/panel/files/', {'contractType': 'رهن و اجاره', 'priceFrom': 650, 'priceTo': 750}).data['data']['results']
        self.assertEqual([r['id'] for r in rows], [rental.pk])
