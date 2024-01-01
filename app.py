# External Imports
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from pretty_html_table import build_table
from datetime import datetime
import pandas as pd
import numpy as np
import logging
import concurrent.futures
import glob
import os

# Local Imports
import createRankings
import TBA
import params

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = params.upload_folder
app.secret_key = "no"

# Setting logging config
logging.basicConfig(filename="main.log", format="%(asctime)s %(message)s", filemode="w")
logger = logging.getLogger()

logger.setLevel(logging.DEBUG)


def getTeamData(number):
    logging.info("Thread for team %s: Starting", number)
    info = TBA.fetchTeamInfo(number)
    teams.append(
        {
            "images": TBA.fetchTeamMedia(number),
            "name": info["nickname"],
            "number": number,
            "location": "{}, {}".format(info["city"], info["state_prov"]),
            "website": info["website"],
        }
    )
    logging.info("Thread for team %s: Finished", number)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in params.allowed_file_extensions
    )


@app.route("/")
def index():
    currentEvent = TBA.fetchCurrentEvent(params.team_number)

    if currentEvent != "No current events":
        return render_template(
            "index.html",
            current_event=currentEvent["webcasts"][0]["channel"],
            matches=TBA.fetchTeamMatchesForEvent(
                params.team_number, currentEvent["event_code"]
            ),
        )
    else:
        return render_template(
            "index.html",
            current_event=False,
        )


@app.route("/chat")
def chat():
    return render_template("chat.html")


@app.route("/scouting")
def scouting():
    return render_template(
        "scouting.html",
        current_year=datetime.now().year,
        years=np.flip(np.arange(start=1992, stop=datetime.now().year)),
    )


@app.route("/pit_scouting")
def pit_scouting():
    return render_template("pit-scouting.html")


@app.route("/game_scouting", methods=["GET", "POST"])
def game_scouting():
    if request.method == "POST":
        if "file" not in request.files:
            return render_template("game-scouting.html", message="No file attached")

        files = request.files.getlist("file")
        for file in files:
            if file.filename == "":
                return render_template("game-scouting.html", message="No file attached")
            elif not allowed_file(file.filename):
                return render_template(
                    "game-scouting.html",
                    message="File(s) is an unsupported extension",
                    table=build_table(
                        pd.read_excel(
                            os.path.join(
                                params.download_folder,
                                os.listdir(params.download_folder)[0],
                            )
                        ),
                        "blue_light",
                    ),
                )

        for file in files:
            file.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"], secure_filename(file.filename)
                )
            )
        return render_template(
            "game-scouting.html",
            success=True,
            table=build_table(
                pd.read_excel(
                    os.path.join(
                        params.download_folder, os.listdir(params.download_folder)[0]
                    )
                ),
                "blue_light",
            ),
        )
    else:
        return render_template(
            "game-scouting.html",
            table=build_table(
                pd.read_excel(
                    os.path.join(
                        params.download_folder, os.listdir(params.download_folder)[0]
                    )
                ),
                "blue_light",
            ),
        )


@app.route("/team_list")
def team_list():
    global teams
    teams = []
    params.team_numbers = TBA.fetchTeamsForEvents(
        "2023brd"
    )  # ToDo: Make event UI configurable
    # Initailize a multi-threaded fetch of all team data
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(params.team_numbers)
    ) as executer:
        executer.map(getTeamData, params.team_numbers)
    return render_template("team-list.html", teams=teams)


@app.route("/team/<team>")
def team(team):
    return team


@app.route("/api/chat_response")
def chat_response():
    chat = request.args.get("chat")

    response = "This chat is in developmemt, please wait."
    # Magic Chat stuff Annand will make

    return response


@app.route("/api/get_events")
def get_events():
    season = request.args.get("season")
    team_number = request.args.get("team_number")
    return TBA.fetchEventsForTeam(team_number, season)


@app.route("/api/get_channels")
def get_channels():
    team = request.args.get("team")
    return TBA.fetchEventChannels(team)


@app.route("/api/get_rankings")
def get_rankings():
    event = request.args.get("event")
    use_OPR = True if request.args.get("OPR") == "True" else False
    use_CCWMS = True if request.args.get("CCWMS") == "True" else False
    use_overall_EPA = True if request.args.get("Overall") == "True" else False
    use_auto_EPA = True if request.args.get("Auto") == "True" else False
    use_teleop_EPA = True if request.args.get("Teleop") == "True" else False
    use_endgame_EPA = True if request.args.get("Endgame") == "True" else False
    # print(use_OPR, use_CCWMS,use_overall_EPA, use_auto_EPA, use_teleop_EPA, use_endgame_EPA)
    return createRankings.createRankings(
        event,
        use_OPR,
        use_CCWMS,
        use_overall_EPA,
        use_auto_EPA,
        use_teleop_EPA,
        use_endgame_EPA,
    )


@app.route("/api/search_team/<str>")
def search_team(str):
    pass


@app.route("/download_data/<id>")
def download_data(id):
    try:
        id = int(id)
    except:
        return "ID is not a valid integer"
    if len(os.listdir(params.download_folder)) <= 0:
        return "There are currently no available downloads."
    elif len(os.listdir(params.download_folder)) < id or id < 0:
        return "Invalid ID range."
    else:
        files = list(filter(os.path.isfile, glob.glob(params.download_folder + "\*")))
        files.sort(key=os.path.getctime)
        return send_file(files[0])


if __name__ == "__main__":
    app.run()
