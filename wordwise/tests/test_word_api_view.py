from unittest.mock import Mock, patch

from django.test import TestCase

from wordwise.models import Definition, Example, TypeOf, Word
from wordwise.views import get_word


class APITest(TestCase):
    @patch("wordwise.views.api_view.requests.get")
    def setUp(self, mock_api):
        """Set up for testing"""
        # Create a mock response object to simulate the behavior of requests.get
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "word": "example",
            "results": [
                {
                    "definition": "a representative form or pattern",
                    "partOfSpeech": "noun",
                    "synonyms": ["model"],
                    "typeOf": ["representation", "internal representation", "mental representation"],
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
                    ],
                    "derivation": ["exemplify"],
                    "examples": ["I profited from his example"],
                },
                {
                    "definition": "something to be imitated",
                    "partOfSpeech": "noun",
                    "synonyms": ["exemplar", "good example", "model"],
                    "typeOf": ["ideal"],
                    "hasTypes": ["pacemaker", "pattern", "beauty", "prodigy", "beaut", "pacesetter"],
                    "derivation": ["exemplify", "exemplary"],
                },
                {
                    "definition": "an occurrence of something",
                    "partOfSpeech": "noun",
                    "synonyms": ["case", "instance"],
                    "typeOf": ["happening", "natural event", "occurrence", "occurrent"],
                    "hasTypes": ["clip", "mortification", "piece", "time", "humiliation", "bit"],
                    "derivation": ["exemplify"],
                    "examples": ["but there is always the famous example of the Smiths"],
                },
                {
                    "definition": "an item of information that is typical of a class or group",
                    "partOfSpeech": "noun",
                    "synonyms": ["illustration", "instance", "representative"],
                    "typeOf": ["information"],
                    "hasTypes": [
                        "excuse",
                        "apology",
                        "specimen",
                        "case in point",
                        "sample",
                        "exception",
                        "quintessence",
                        "precedent",
                    ],
                    "derivation": ["exemplify", "exemplary"],
                    "examples": [
                        "this patient provides a typical example of the syndrome",
                        "there is an example on page 10",
                    ],
                },
                {
                    "definition": "punishment intended as a warning to others",
                    "partOfSpeech": "noun",
                    "synonyms": ["deterrent example", "lesson", "object lesson"],
                    "typeOf": ["monition", "admonition", "word of advice", "warning"],
                    "derivation": ["exemplary"],
                    "examples": ["they decided to make an example of him"],
                },
                {
                    "definition": "a task performed or problem solved in order to develop skill or understanding",
                    "partOfSpeech": "noun",
                    "synonyms": ["exercise"],
                    "typeOf": ["lesson"],
                    "examples": ["you must work the examples at the end of each chapter in the textbook"],
                },
            ],
            "syllables": {"count": 3, "list": ["ex", "am", "ple"]},
            "pronunciation": {"all": "\u026a\u0261'z\u00e6mp\u0259l"},
            "frequency": 4.67,
        }

        # Configure the mock "mock.api" to return the mock response
        mock_api.return_value = mock_response
        # Call the view function that uses requests.get
        self.word_example = get_word("example")

    def test_creating_word_correct_ly(self):
        """Test word is created."""
        word = Word.objects.get(vocab="example")
        self.assertEqual(word, self.word_example)

    def test_creating_definition(self):
        """Test definition is created correctly, and link to the right word."""
        # test if the definition is created
        definition_all = Definition.objects.all()
        definition_list = [defi.definition for defi in definition_all]
        self.assertIn("a representative form or pattern", definition_list)
        self.assertIn("something to be imitated", definition_list)
        self.assertIn("an occurrence of something", definition_list)
        self.assertIn("an item of information that is typical of a class or group", definition_list)
        self.assertIn("punishment intended as a warning to others", definition_list)
        self.assertIn("a task performed or problem solved in order to develop skill or understanding", definition_list)
        # check if definition is link correctly
        for defi in definition_all:
            self.assertEqual(Word.objects.get(vocab="example"), defi.word)

    def test_creating_example(self):
        """Test example is created."""
        example_all = Example.objects.all()
        example_list = [sentence.example for sentence in example_all]
        self.assertIn("I profited from his example", example_list)
        self.assertIn("but there is always the famous example of the Smiths", example_list)
        self.assertIn("you must work the examples at the end of each chapter in the textbook", example_list)
        self.assertIn("they decided to make an example of him", example_list)
        self.assertIn("this patient provides a typical example of the syndrome", example_list)
        self.assertIn("there is an example on page 10", example_list)
        example_defi = [sentence.example_of for sentence in example_all]
        defi_list = [defi for defi in Definition.objects.filter(type_of=None)]
        for defi in defi_list:
            self.assertIn(defi, example_defi)

    def test_creating_type(self):
        """Test type is created"""
        type_list = [type_.type_of for type_ in TypeOf.objects.all()]
        self.assertIn("ideal", type_list)
        self.assertIn("representation", type_list)
        self.assertIn("ideal", type_list)
        self.assertIn("lesson", type_list)
        self.assertIn("occurrence", type_list)
