import sys

sys.path.insert(1, 'Models')
from flask import Flask
app = Flask(__name__)
from flaskapp import views

