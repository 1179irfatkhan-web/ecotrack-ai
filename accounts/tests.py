from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

class AccountsTests(TestCase):
    def setUp(self):
        self.username = "sustain_user"
        self.email = "sustain@example.com"
        self.password = "Secr3tP@ssw0rd!"
        # Create a user for login testing
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )

    def test_registration_view_get(self):
        """Test registration page renders correctly."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_registration_submission_success(self):
        """Test registering a new user is successful and redirects to dashboard."""
        response = self.client.post(reverse('register'), {
            'username': 'new_eco_user',
            'email': 'neweco@example.com',
            'password1': 'NewS3cretP@ss!',
            'password2': 'NewS3cretP@ss!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/dashboard/')
        self.assertTrue(User.objects.filter(username='new_eco_user').exists())

    def test_registration_submission_password_mismatch(self):
        """Test registration fails when passwords do not match."""
        response = self.client.post(reverse('register'), {
            'username': 'mismatch_user',
            'email': 'mismatch@example.com',
            'password1': 'Password123!',
            'password2': 'Password1234!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='mismatch_user').exists())

    def test_login_view_get(self):
        """Test login page renders correctly."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_success(self):
        """Test successful login redirects to dashboard."""
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.status_code, 302)
        # LoginRedirectUrl in settings.py is /dashboard/
        self.assertRedirects(response, '/dashboard/')

    def test_login_invalid_credentials(self):
        """Test login fails with invalid credentials."""
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200) # Re-renders page with errors
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_logout(self):
        """Test logout clears the session and redirects to index/root page."""
        self.client.login(username=self.username, password=self.password)
        self.assertTrue('_auth_user_id' in self.client.session)
        response = self.client.post(reverse('logout')) # Django 5.x uses POST for logout by default
        if response.status_code == 405: # In case GET logout is enabled fallback
            response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)
