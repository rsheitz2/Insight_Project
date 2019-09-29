#!/usr/local/bin/python3

import sys
sys.path.insert(1, 'Models')

from flaskapp import app

app.run(debug = True)

# insert at 1, 0 is the script path (or '' in REPL)



#app.run()
