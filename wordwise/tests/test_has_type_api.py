from unittest.mock import Mock, patch

from django.test import TestCase

from wordwise.views.api_view import get_list_word_from_type_of


class Test(TestCase):
    @patch("wordwise.views.api_view.requests.get")
    def setUp(self, mock_api):
        """Set up for testing"""
        # Create a mock response object to simulate the behavior of requests.get
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "word": "example",
            "hasTypes": [
                "prefiguration",
                "archetype",
                "epitome",
                "guide",
                "holotype",
                "image",
                "loadstar",
                "lodestar",
                "microcosm",
                "original",
                "paradigm",
                "pilot",
                "prototype",
                "template",
                "templet",
                "type specimen",
                "pacemaker",
                "pattern",
                "beauty",
                "prodigy",
                "beaut",
                "pacesetter",
                "clip",
                "mortification",
                "piece",
                "time",
                "humiliation",
                "bit",
                "excuse",
                "apology",
                "specimen",
                "case in point",
                "sample",
                "exception",
                "quintessence",
                "precedent",
            ],
        }
        # Configure the mock "mock.api" to return the mock response
        mock_api.return_value = mock_response
        self.num = len(mock_response.json.return_value["hasTypes"])
        # Call the view function that uses requests.get
        self.result = get_list_word_from_type_of("example")

    def test_get_list_word_from_type_of(self):
        self.assertEqual(len(self.result), self.num)
