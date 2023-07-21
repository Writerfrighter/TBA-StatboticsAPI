from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import numpy as np

import createRankings
import TBA

app = Flask(__name__)

team = 492

@app.route('/')
def index():
	return render_template('index.html', current_event = True if TBA.eventChannels(492) != "No current events" else False)

@app.route('/scouting')
def scouting():
	return render_template('scouting.html', current_year = datetime.now().year, years = np.flip(np.arange(start=1992, stop=datetime.now().year)))

@app.route('/team/n')
def teams():
	team = request.args.get('team')
@app.route('/get_events')
def get_events():
	season = request.args.get('season')
	team_number = request.args.get('team_number')
	return TBA.fetchEventsForTeam(team_number, season)

@app.route('/get_channels')
def get_channels():
	team = request.args.get('team')
	return TBA.eventChannels(team)

@app.route('/get_rankings')
def get_rankings():
	event = request.args.get('event')
	use_OPR = True if request.args.get('OPR') == 'True' else False
	use_CCWMS = True if request.args.get('CCWMS') == 'True' else False
	use_overall_EPA = True if request.args.get('Overall') == 'True' else False
	use_auto_EPA = True if request.args.get('Auto')  == 'True' else False
	use_teleop_EPA = True if request.args.get('Teleop')  == 'True' else False
	use_endgame_EPA = True if request.args.get('Endgame')  == 'True' else False
	# print(use_OPR, use_CCWMS,use_overall_EPA, use_auto_EPA, use_teleop_EPA, use_endgame_EPA)
	return createRankings.createRankings(event, use_OPR, use_CCWMS, use_overall_EPA, use_auto_EPA, use_teleop_EPA, use_endgame_EPA)
app.run(host='0.0.0.0', port=8080, debug=True)