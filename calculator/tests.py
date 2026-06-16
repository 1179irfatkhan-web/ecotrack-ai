from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch
from calculator.models import CarbonRecord
from calculator.services import CarbonService

class CalculatorTests(TestCase):
    def setUp(self):
        self.username = "eco_tester"
        self.password = "ecoPass123!"
        self.user = User.objects.create_user(
            username=self.username,
            email="tester@example.com",
            password=self.password
        )

    def test_calculator_login_required(self):
        """Test that calculator is protected and redirects anonymous users to login page."""
        response = self.client.get(reverse('calculator'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

    def test_calculator_view_get_authenticated(self):
        """Test authenticated user can access calculator form."""
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('calculator'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'calculator.html')

    @patch('calculator.views.get_ai_advice')
    def test_calculator_form_submission_success(self, mock_get_advice):
        """Test submitting the form with valid data saves the record and calls the AI advice."""
        mock_get_advice.return_value = "Mocked AI Advice for low footprint"
        
        self.client.login(username=self.username, password=self.password)
        post_data = {
            'transport_km': 100.0,      # CO2: 21.0
            'electricity_units': 100.0, # CO2: 82.0
            'meat_meals': 5,            # CO2: 16.5
            'waste_kg': 10.0            # CO2: 5.7
        }                               # Total expected = 21 + 82 + 16.5 + 5.7 = 125.2
        
        response = self.client.post(reverse('calculator'), post_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "125.2")
        self.assertContains(response, "Mocked AI Advice for low footprint")
        
        # Verify database insertion
        record = CarbonRecord.objects.filter(user=self.user).first()
        self.assertIsNotNone(record)
        self.assertEqual(record.transport_km, 100.0)
        self.assertEqual(record.electricity_units, 100.0)
        self.assertEqual(record.meat_meals, 5)
        self.assertEqual(record.waste_kg, 10.0)
        self.assertEqual(record.total_carbon, 125.2)

    def test_calculator_form_validation_negative_values(self):
        """Test that negative numbers fail form validation and do not insert into DB."""
        self.client.login(username=self.username, password=self.password)
        post_data = {
            'transport_km': -10.0,
            'electricity_units': 100.0,
            'meat_meals': 5,
            'waste_kg': 10.0
        }
        
        response = self.client.post(reverse('calculator'), post_data)
        self.assertEqual(response.status_code, 200)
        # Verify no record was created in the database
        self.assertEqual(CarbonRecord.objects.filter(user=self.user).count(), 0)

    def test_carbon_service_calculations(self):
        """Test the arithmetic in CarbonService directly."""
        test_data = {
            'transport_km': 50.0,       # 50 * 0.21 = 10.5
            'electricity_units': 120.0, # 120 * 0.82 = 98.4
            'meat_meals': 10,           # 10 * 3.3 = 33.0
            'waste_kg': 5.0             # 5 * 0.57 = 2.85
        }                               # Total = 144.75 -> rounded to 144.75
        result = CarbonService.calculate_carbon(test_data)
        self.assertEqual(result, 144.75)

    @patch('calculator.views.get_ai_advice')
    def test_calculator_form_submission_zero_values(self, mock_get_advice):
        """Test that submitting zero values is handled correctly and returns 0.0 total carbon."""
        mock_get_advice.return_value = "Mocked AI advice for zero carbon footprint"
        self.client.login(username=self.username, password=self.password)
        post_data = {
            'transport_km': 0,
            'electricity_units': 0,
            'meat_meals': 0,
            'waste_kg': 0
        }
        response = self.client.post(reverse('calculator'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "0.0")
        
        # Verify database insertion
        record = CarbonRecord.objects.filter(user=self.user, total_carbon=0.0).first()
        self.assertIsNotNone(record)
        self.assertEqual(record.total_carbon, 0.0)

