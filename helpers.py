from flask import redirect, render_template, request, session
from functools import wraps
import requests
import os
from datetime import datetime

## Render error msg
def apology(message, code=400):
    return render_template("apology.html", message=message), code


# Decorate routes to require login.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


## format date time
def get_datetime(input):
    dt = datetime.fromisoformat(input)
    date = dt.strftime("%m-%d-%y")
    time = dt.strftime("%I:%M %p")
    return f"{date} {time}"


## format number to have only 2 decimal places
def format_decimal(input):
    d = float(input)
    return f"{d:,.2f}"


### TEAMS HELPER FUNCTIONS
def get_team_by_name(team_name):
    try:
        url = f"https://v3.football.api-sports.io/teams?name={team_name}"

        payload = {}
        headers = {
            "x-rapidapi-key": os.environ.get("API_KEY"),
            "x-rapidapi-host": "v3.football.api-sports.io",
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if not response.json()["results"]:
            return None
    except requests.RequestException:
        return None

    # parse data
    try:
        team_data = response.json()["response"][0]["team"]
        return {
            "team_id": team_data["id"],
            "team_logo": team_data["logo"],
            "name": team_data["name"],
        }
    except (KeyError, TypeError, ValueError, IndexError):
        return None


def get_team_by_id(team_id):
    try:
        url = f"https://v3.football.api-sports.io/teams?id={team_id}"

        payload = {}
        headers = {
            "x-rapidapi-key": os.environ.get("API_KEY"),
            "x-rapidapi-host": "v3.football.api-sports.io",
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if not response.json()["results"]:
            return None
    except requests.RequestException:
        return None

    # parse data
    try:
        team_data = response.json()["response"][0]["team"]
        return {
            "team_id": team_data["id"],
            "team_logo": team_data["logo"],
            "name": team_data["name"],
        }
    except (KeyError, TypeError, ValueError, IndexError):
        return None


def get_next_fixtures(team_id, fixtures):

    # Request from API
    try:
        url = (
            f"https://v3.football.api-sports.io/fixtures?team={team_id}&next={fixtures}"
        )

        payload = {}
        headers = {
            "x-rapidapi-key": os.environ.get("API_KEY"),
            "x-rapidapi-host": "v3.football.api-sports.io",
        }

        response = requests.request("GET", url, headers=headers, data=payload)
    except requests.RequestException:
        return None

    # parse data
    try:
        fixture_data = response.json()["response"]
        fixture_list = []
        for fixture in fixture_data:
            fixture_list.append(
                {
                    "home": fixture["teams"]["home"],
                    "away": fixture["teams"]["away"],
                    "date": fixture["fixture"]["date"],
                }
            )
            # print(fixture_list)
        return fixture_list
    except (KeyError, TypeError, ValueError, IndexError):
        return None


def get_last_fixtures(team_id, fixtures):

    # Request from API
    try:
        url = (
            f"https://v3.football.api-sports.io/fixtures?team={team_id}&last={fixtures}"
        )

        payload = {}
        headers = {
            "x-rapidapi-key": os.environ.get("API_KEY"),
            "x-rapidapi-host": "v3.football.api-sports.io",
        }

        response = requests.request("GET", url, headers=headers, data=payload)
    except requests.RequestException:
        return None

    # parse data
    try:
        fixture_data = response.json()["response"]
        fixture_list = []
        for fixture in fixture_data:
            fixture_list.append(
                {
                    "home": fixture["teams"]["home"],
                    "away": fixture["teams"]["away"],
                    "date": fixture["fixture"]["date"],
                    "score": fixture["score"]["fulltime"],
                }
            )
            # print(fixture_list)
        return fixture_list
    except (KeyError, TypeError, ValueError, IndexError):
        return None


### PLAYERS HELPER FUNCTIONS
def get_player(league_id, name):
    try:
        url = f"https://v3.football.api-sports.io/players?search={name}&league={league_id}&season=2021"

        payload = {}
        headers = {
            "x-rapidapi-key": os.environ.get("API_KEY"),
            "x-rapidapi-host": "v3.football.api-sports.io",
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        print("GOT RESPONSE")
    except requests.RequestException:
        return None

    # parse data
    try:
        player_list = []
        for p in response.json()["response"]:
            player_list.append(
                {
                    "id": p["player"]["id"],
                    "name": p["player"]["name"],
                    "photo": p["player"]["photo"],
                    "team": p["statistics"][0]["team"]["name"],
                    "appearences": p["statistics"][0]["games"]["appearences"],
                    "goals": p["statistics"][0]["goals"]["total"],
                    "assists": p["statistics"][0]["goals"]["assists"],
                    "rating": p["statistics"][0]["games"]["rating"],
                }
            )
        return player_list
    except (KeyError, TypeError, ValueError, IndexError):
        return None


def get_player_by_id(id):
    try:
        url = f"https://v3.football.api-sports.io/players?id={id}&&season=2021"

        payload = {}
        headers = {
            "x-rapidapi-key": os.environ.get("API_KEY"),
            "x-rapidapi-host": "v3.football.api-sports.io",
        }

        response = requests.request("GET", url, headers=headers, data=payload)
    except requests.RequestException:
        return None

    # parse data
    try:
        p = response.json()["response"][0]
        player = {
            "id": p["player"]["id"],
            "name": p["player"]["name"],
            "photo": p["player"]["photo"],
            "team": p["statistics"][0]["team"]["name"],
            "appearences": p["statistics"][0]["games"]["appearences"],
            "goals": p["statistics"][0]["goals"]["total"],
            "assists": p["statistics"][0]["goals"]["assists"],
            "rating": p["statistics"][0]["games"]["rating"],
        }
        return player
    except (KeyError, TypeError, ValueError, IndexError):
        return None
