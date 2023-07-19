from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import numpy as np

import createRankings
import TBA

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/scouting')
def scouting():
	return render_template('scouting.html', current_year = datetime.now().year, years = np.flip(np.arange(start=1992, stop=datetime.now().year)))

@app.route('/get_events')
def get_events():
	season = request.args.get('season')
	team_number = request.args.get('team_number')
	return TBA.fetchEventsForTeam(team_number, season)

@app.route('/get_rankings')
def get_rankings():
	event = request.args.get('event')
	
app.run(host='0.0.0.0', port=8080, debug=True)