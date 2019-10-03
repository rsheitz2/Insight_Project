#!/usr/local/bin/python3

import sys
sys.path.insert(1, 'Models')

from flaskapp import app
app.run(debug = True)
