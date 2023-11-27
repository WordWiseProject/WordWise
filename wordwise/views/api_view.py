from pathlib import Path

import environ
import requests

from wordwise.models import Definition, Example, TypeOf, Word

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
env = environ.Env()
env.read_env(str(BASE_DIR / ".env"))
HEADERS = {"X-RapidAPI-Key": env("X_RAPIDAPI_KEY"), "X-RapidAPI-Host": env("X_RAPIDAPI_HOST")}


def get_word(word: str):
    url = f"https://wordsapiv1.p.rapidapi.com/words/{word}/"
    try:
        word = Word.objects.get(vocab=word.lower())
    except Word.DoesNotExist:
        response = requests.get(url, headers=HEADERS)
        print(response.status_code)
        if response.status_code == 404:
            return None
        word_json = response.json()
        if "results" not in word_json:
            return None
        word = Word(vocab=word_json["word"].lower())
        word.save()
        for results in word_json["results"]:
            defi = Definition(
                word=word,
                definition=results["definition"],
                part_of_speech=results["partOfSpeech"],
            )
            defi.save()
            if "typeOf" in results:
                for type_of in results["typeOf"]:
                    try:
                        get_type_of = TypeOf.objects.get(type_of=type_of)
                        defi.type_of.add(get_type_of)
                    except TypeOf.DoesNotExist:
                        get_type_of = TypeOf(type_of=type_of)
                        get_type_of.save()
                        defi.type_of.add(get_type_of)
            if "examples" in results:
                for example in results["examples"]:
                    example_sentence = Example(example=example, example_of=defi)
                    example_sentence.save()

    return word


def get_list_word_from_type_of(type):
    url = f"https://wordsapiv1.p.rapidapi.com/words/{type}/hasTypes"
    response = requests.get(url, headers=HEADERS)
    type_json = response.json()
    word_list = list(type_json["hasTypes"])
    return word_list
