from flask import Flask, render_template, request
from datetime import datetime
import numpy as np
import logging
import concurrent.futures
import createRankings
import TBA

app = Flask(__name__)

team_number = 492

logging.basicConfig(filename="main.log", format='%(asctime)s %(message)s', filemode='w')

# Creating a logging object
logger = logging.getLogger()
 
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.INFO)

def getTeamData(number):
	logging.info("Thread for team %s: Starting", number)
	info = TBA.fetchTeamInfo(number)
	teams.append({"images": TBA.fetchTeamMedia(number), "name": info["nickname"], "number": number, "location": "{}, {}".format(info["city"], info["state_prov"]), "website": info["website"]})
	logging.info("Thread for team %s: Finished", number)
	
@app.route('/')
def index():
	return render_template('index.html', current_event = True if TBA.fetchEventChannels(team_number) != "No current events" else False)

@app.route('/chat')
def chat():
	return render_template('chat.html')
@app.route('/scouting')
def scouting():
	return render_template('scouting.html', current_year = datetime.now().year, years = np.flip(np.arange(start=1992, stop=datetime.now().year)))

@app.route('/pit_scouting')
def pit_scouting():
	return render_template('pit-scouting.html')

@app.route('/game_scouting')
def game_scouting():
	return render_template('game-scouting.html')

@app.route('/testing')
def testing():
	global teams
	teams = []
	team_numbers = TBA.fetchTeamsForEvents("2023pncmp")
	with concurrent.futures.ThreadPoolExecutor(max_workers=len(team_numbers)) as executer: 
		executer.map(getTeamData, team_numbers)
	return render_template('testing.html', teams=teams)

@app.route('/team/<team>')
def team(team):
	return team

@app.route('/chat_response')
def chat_response():
	chat = request.args.get('chat')

	response = "In developmemt, please wait."
	# Magic Chat stuff Annand will make

	return response
@app.route('/get_events')
def get_events():
	season = request.args.get('season')
	team_number = request.args.get('team_number')
	return TBA.fetchEventsForTeam(team_number, season)

@app.route('/get_channels')
def get_channels():
	team = request.args.get('team')
	return TBA.fetchEventChannels(team)

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
app.run()