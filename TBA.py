import requests
from datetime import datetime
import json

TBA_Api_Key = "XEgamR41nGmLtS6W2Own9kkz2CQxZY1NK6UNZsbpPUDWcus4ioeUH9lGSmfNmkgu"


def checkAPIStatus():
    TBA_status = fetchAPIData("status")
    if TBA_status["is_datafeed_down"]:
        return True
    else:
        return False


def fetchEventsForTeam(teamNumber, season):
    team_data = fetchAPIData("team/frc{}/events/{}/simple".format(teamNumber, season))
    response = []
    for event in team_data:
        response.append([event["name"], event["key"]])
    return json.dumps(response)


def fetchTeamsForEvents(event):
    response = fetchAPIData("event/{}/teams/simple".format(event))
    return [team["team_number"] for team in response]


def fetchEventOprs(eventCode):
    team_data = fetchAPIData("event/{}/oprs".format(eventCode))
    return team_data


def fetchCurrentEvent(team):
    date = datetime.now()
    resp = fetchAPIData("team/frc{}/events/{}".format(team, date.year))
    for event in resp:
        if (
            event["start_date"] < str(date)[:11:]
            and event["end_date"] > str(date)[:11:]
        ):
            return event
    return "No current events"


def fetchEventDate(eventCode):
    resp = fetchAPIData("event/{}/simple".format(eventCode))
    return resp["start_date"] + " " + resp["end_date"]


def fetchTeamMatchesForEvent(team, eventCode):
    resp = fetchAPIData(
        "team/frc{}/event/{}/matches/simple".format(
            team, str(datetime.now().year) + eventCode
        )
    )
    return resp


def fetchTeamInfo(team):
    resp = fetchAPIData("/team/frc{}".format(team))
    return resp


def fetchTeamMedia(team):
    images = []
    resp = fetchAPIData("team/frc{}/media/{}".format(team, datetime.now().year))
    for item in resp:
        if item["type"] == "imgur" and item["preferred"]:
            images.insert(0, item["direct_url"])
        elif item["type"] == "imgur":
            images.append(item["direct_url"])

        if len(images) >= 3:
            break
    if len(images) == 0:
        images = "No Images"

    return images


def fetchEventMatches(eventCode):
    resp = fetchAPIData("event/{}/matches".format(eventCode))

    return [i for i in resp if i["comp_level"] == "qm"]


def fetchMatchData(matchKey):
    resp = fetchAPIData("match/{}/simple".format(matchKey))
    return resp


def fetchAPIData(url):
    """Helper function to fetch data from The Blue Alliance API."""
    API_return = requests.get(
        "https://www.thebluealliance.com/api/v3/" + url,
        params={"X-TBA-Auth-Key": TBA_Api_Key},
    ).json()
    return API_return
