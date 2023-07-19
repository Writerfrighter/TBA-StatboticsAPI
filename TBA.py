import requests

TBA_Api_Key = "XEgamR41nGmLtS6W2Own9kkz2CQxZY1NK6UNZsbpPUDWcus4ioeUH9lGSmfNmkgu"

def checkAPIStatus():
    """Checks The Blue Alliance API if it's down.
    Returns bool"""
    TBA_status = fetchAPIData("status")
    if TBA_status["is_datafeed_down"]: return True
    else: return False

def fetchEventsForTeam(teamNumber, season) -> list:
    team_data = fetchAPIData("team/frc{}/events/{}/simple".format(teamNumber, season))
    return [["{} ({})".format(event["name"], event["key"]), event["key"]] for event in team_data]

def fetchEventOprs(eventCode):
    team_data = fetchAPIData("event/{}/oprs".format(eventCode))
    return team_data
    
def fetchAPIData(url):
    """Helper function to fetch data from The Blue Alliance API."""
    API_return = requests.get("https://www.thebluealliance.com/api/v3/" + url, params = {"X-TBA-Auth-Key": TBA_Api_Key}).json()
    return API_return