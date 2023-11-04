from django.test import TestCase

from wordwise.models import Definition, Example, Word


class ExampleTest(TestCase):
    def test_censor_of_example(self):
        word = Word(vocab="test")
        defi = Definition(word=word, definition="test", part_of_speech="test")
        exam = Example(example_of=defi, example="We are testing")
        self.assertEqual(exam.censor(), "We are ____ing")

        exam = Example(example_of=defi, example="We are done tested")
        self.assertEqual(exam.censor(), "We are done ____ed")

        exam = Example(example_of=defi, example="Testing")
        self.assertEqual(exam.censor(), "____ing")

        word2 = Word(vocab="example")
        defi2 = Definition(word=word2, definition="test", part_of_speech="test")
        exam = Example(
            example_of=defi2, example="In the classroom, the teacher was exampling a new concept to the students."
        )
        self.assertEqual(exam.censor(), "In the classroom, the teacher was ______ing a new concept to the students.")

        exam = Example(example_of=defi2, example="I profited from his example")
        self.assertEqual(exam.censor(), "I profited from his _______")
