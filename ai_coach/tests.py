from django.test import TestCase
from unittest.mock import patch, MagicMock
import os
from ai_coach.gemini_service import get_ai_advice

class AICoachTests(TestCase):
    @patch.dict(os.environ, {"GEMINI_API_KEY": ""})
    def test_get_ai_advice_fallback(self):
        """Test that get_ai_advice returns fallback rule-based advice if API key is missing."""
        data = {
            "transport_km": 100.0,
            "electricity_units": 120.0,
            "meat_meals": 8,
            "waste_kg": 12.0,
            "total_carbon": 150.0
        }
        advice = get_ai_advice(data)
        self.assertIn("Carbon Analysis", advice)
        self.assertIn("Total Carbon Footprint:\n150.0 kg CO₂", advice)
        self.assertIn("Sustainability Score:\n20/100", advice)

    @patch('google.genai.Client')
    @patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
    def test_get_ai_advice_gemini(self, mock_client_class):
        """Test that get_ai_advice calls google.genai.Client and returns the generated content."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "This is live mock advice from Gemini!"
        mock_client.models.generate_content.return_value = mock_response

        data = {
            "transport_km": 10.0,
            "electricity_units": 10.0,
            "meat_meals": 1,
            "waste_kg": 1.0,
            "total_carbon": 10.0
        }
        advice = get_ai_advice(data)
        self.assertEqual(advice, "This is live mock advice from Gemini!")
        mock_client.models.generate_content.assert_called_once()
