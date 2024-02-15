# NOTAM SORT

Notam Sort is a webpage that takes the input from the user for a departure and arrival airport and using the FAA api retrieve the NOTAMS relevant to the projected path.

## Requirements

Python 3.11.3
## Installing Dependencies
If you import a new module into your script, you will need to run the following command so that everyone else can easily install the new dependencies:
```
pip freeze > requirements.txt
```
If python tells you it can't find certain modules, run the below script to install them:
```
pip install -r requirements.txt
```
## Running Flask
1. Make sure to run ```pip install -r requirements.txt``` to install everything need for Flask.
2. In the directory containing `app.py`, run the following command in your python environment: ```python -m flask run``` You'll see something like this: 
> (.venv) C:\\...\\Flask_Frontend>python -m flask run
>  * Debug mode: off
> WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
>  * Running on http://127.0.0.1:5000
> Press CTRL+C to quit
4. `Ctrl-click` the URL http://127.0.0.1:5000 to open the Flask webpage.

## Creating .env file

For purposes of having using FAA API, users must utilize their own API keys in a seperate .env file </br>
This can be done by creating a .env file in the root directory </br>
Inside the file place the following script: </br>

```
client_id = "[insert client ID]"
client_secret = "[insert client Secret]"
```
