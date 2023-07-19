from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import numpy as np
app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/scouting')
def scouting():
	return render_template('scouting.html', current_year = datetime.now().year, years = np.flip(np.arange(start=1992, stop=datetime.now().year)))
app.run(host='0.0.0.0', port=8080, debug=True) 