import requests
from datetime import datetime

TBA_Api_Key = "XEgamR41nGmLtS6W2Own9kkz2CQxZY1NK6UNZsbpPUDWcus4ioeUH9lGSmfNmkgu"

def checkAPIStatus():
    """Checks The Blue Alliance API if it's down.
    Returns bool"""
    TBA_status = fetchAPIData("status")
    if TBA_status["is_datafeed_down"]: return True
    else: return False

def fetchEventsForTeam(teamNumber, season) -> list:
    team_data = fetchAPIData("team/frc{}/events/{}/simple".format(teamNumber, season))
    response = ""
    for event in team_data:
        response += "~{}~{}~".format(event["name"], event["key"])
    return response

def fetchEventOprs(eventCode):
    team_data = fetchAPIData("event/{}/oprs".format(eventCode))
    return team_data

def fetchEventChannels(team):
    date = datetime.now()
    resp = fetchAPIData("team/frc{}/events/{}".format(team, date.year))
    for event in resp:
        if event["start_date"] < str(date)[:11:] and event["end_date"] > str(date)[:11:]:
            return event["webcasts"][0]["channel"]
    return "No current events"

def fetchTeamInfo(team):
    resp = fetchAPIData("/team/frc{}")
    return resp
def fetchTeamMedia(team):
    images = []
    resp = fetchAPIData("team/frc{}/media/{}".format(team, datetime.now().year))
    for item in resp:
        if item["type"] == "imgur": images.append(item["direct_url"])
    if len(images) == 0: images = "No Images"

    return images

def fetchAPIData(url):
    """Helper function to fetch data from The Blue Alliance API."""
    API_return = requests.get("https://www.thebluealliance.com/api/v3/" + url, params = {"X-TBA-Auth-Key": TBA_Api_Key}).json()
    return API_return