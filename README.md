# WordWise

***Discover the World, One Word at a Time.***

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)

License: MIT

## What is WordWise

"WordWise" is a web app that aids in memorizing English words and meanings
through flashcards. Users can generate random words or create own flashcards.
Designed for all ages, the app supports traditional flashcard use or
interactive games.

## Installation

1. Clone the repository.
    ```sh
   git clone https://github.com/WordWiseProject/WordWise.git
   ```
2. Change directory to the project directory.
    ```sh
   cd WordWise
   ```

3. Create virtual environment.
    ```sh
   python -m venv venv
   ```

4. Activate virtual environment.
    * MacOS/Linux:
   ```sh
   . venv/bin/activate
   ```
   * Windows:
   ```sh
   . venv\Scripts\activate.bat
   ```

5. Install the required packages.
    ```sh
   pip install -r requirements/local.txt
   ```

6. Create a file named `.env` using sample.env and edit the value inside.
    ```sh
   cp sample.env .env
   ```

   List of environment variables:

   |     Variable      |                                                   Example                                                   |
   |:-----------------:|:-----------------------------------------------------------------------------------------------------------:|
   |  `DATABASE_URL`   |                              postgres://postgres:2882@127.0.0.1:5432/wordwise                               |
   | `X_RAPIDAPI_KEY`  | WORDSAPI key, you can have it easily by going to this [site](https://rapidapi.com/dpventures/api/wordsapi). |
   | `X_RAPIDAPI_HOST` |                                          wordsapiv1.p.rapidapi.com                                          |
   |     `SITE_ID`     |                                                      3                                                      |

7. Migrate database
    ```sh
   python manage.py migrate
   ```
   **(Optional)** Create an admin account in the application.
   ```sh
   python manage.py createsuperuser
   ```

8. Run Server
    ```sh
   python manage.py runserver
   ```

## Deployment

This project demo has been deployed via Heroku at [Wordwise](https://wordwise-project-c6b7ee2f234f.herokuapp.com).

# Project Documents
[Wiki Home with all Documents](https://github.com/WordWiseProject/WordWise/wiki)
