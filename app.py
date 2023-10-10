from flask import Flask, render_template, request, send_file, jsonify, flash, redirect
from werkzeug.utils import secure_filename
from datetime import datetime
import numpy as np
import logging
import concurrent.futures
import createRankings
import TBA
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "scouting_data"
app.secret_key = "no"

allowed_extensions = ["csv", "xlsx", "png"]  # Extensions parsable by the data reader.
team_number = 492

# Setting logging config
logging.basicConfig(filename="main.log", format="%(asctime)s %(message)s", filemode="w")
logger = logging.getLogger()

logger.setLevel(logging.INFO)


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
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


@app.route("/")
def index():
    currentEvent = TBA.fetchCurrentEvent(team_number)

    if currentEvent != "No current events":
        return render_template(
            "index.html",
            current_event=currentEvent["webcasts"][0]["channel"],
            matches=TBA.fetchMatchesForEvent(team_number, currentEvent["event_code"]),
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
                    "game-scouting.html", message="File(s) is an unsupported extension"
                )

        for file in files:
            file.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"], secure_filename(file.filename)
                )
            )
        return render_template("game-scouting.html", success = True)
    else:
        return render_template("game-scouting.html")


@app.route("/team_list")
def team_list():
    global teams
    teams = []
    team_numbers = TBA.fetchTeamsForEvents(
        "2023brd"
    )  # ToDo: Make event UI configurable
    # Initailize a multi-threaded fetch of all team data
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(team_numbers)
    ) as executer:
        executer.map(getTeamData, team_numbers)
    return render_template("team-list.html", teams=teams)


@app.route("/team/<team>")
def team(team):
    return team


@app.route("/chat_response")
def chat_response():
    chat = request.args.get("chat")

    response = "This chat is in developmemt, please wait."
    # Magic Chat stuff Annand will make

    return response


@app.route("/get_events")
def get_events():
    season = request.args.get("season")
    team_number = request.args.get("team_number")
    return TBA.fetchEventsForTeam(team_number, season)


@app.route("/get_channels")
def get_channels():
    team = request.args.get("team")
    return TBA.fetchEventChannels(team)


@app.route("/get_rankings")
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


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    list = []
    if request.method == "POST":
        json = request.get_json()
        if json["message_type"] == "verification":
            list.append(json)
            return jsonify(success=True)
        elif json["message_type"] == "broadcast":
            list.append(json)
            return jsonify(success=True)
        elif json["message_type"] == "ping":
            list.append(json)
            return jsonify(success=True)
        else:
            list.append(json)
            return jsonify(success=True)

    else:
        return list


if __name__ == "__main__":
    app.run()
