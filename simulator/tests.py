from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

class SimulatorTests(TestCase):
    def setUp(self):
        self.username = "sim_tester"
        self.password = "simPass123!"
        self.user = User.objects.create_user(
            username=self.username,
            email="sim@example.com",
            password=self.password
        )

    def test_simulator_login_required(self):
        """Test simulator view is protected by login."""
        response = self.client.get(reverse('simulator'))
        self.assertEqual(response.status_code, 302)

    def test_simulator_view_get_authenticated(self):
        """Test authenticated user can load simulator form."""
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('simulator'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'simulator.html')

    def test_simulator_math_calculations_post(self):
        """Test simulator form post calculates and returns correct reduction values."""
        self.client.login(username=self.username, password=self.password)
        
        # Current: 100km transport (21), 100kWh elec (82), 5 meat meals (16.5), 10kg waste (5.7) = 125.2 kg
        # Future: 50km transport (10.5), 50kWh elec (41), 2 meat meals (6.6), 5kg waste (2.85) = 60.95 kg
        # Savings: 125.2 - 60.95 = 64.25 kg
        # Percentage reduction: 64.25 / 125.2 * 100 = 51.32%
        post_data = {
            'current_transport': 100.0,
            'current_electricity': 100.0,
            'current_meat': 5,
            'current_waste': 10.0,
            'future_transport': 50.0,
            'future_electricity': 50.0,
            'future_meat': 2,
            'future_waste': 5.0
        }
        
        response = self.client.post(reverse('simulator'), post_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "125.2")
        self.assertContains(response, "60.95")
        self.assertContains(response, "64.25")
        self.assertContains(response, "51.32%")
