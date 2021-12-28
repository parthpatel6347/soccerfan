from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    get_flashed_messages,
)
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3


from helpers import (
    get_player,
    login_required,
    get_next_fixtures,
    get_last_fixtures,
    get_team_by_name,
    get_team_by_id,
    get_player_by_id,
    get_datetime,
    format_decimal,
    apology,
)


# configure app
app = Flask(__name__)

# set templates to auto-reload
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["dt"] = get_datetime
app.jinja_env.filters["decimal"] = format_decimal

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect to database
con = sqlite3.connect("soccer.db", check_same_thread=False)
con.row_factory = sqlite3.Row
cur = con.cursor()


@app.route("/")
@login_required
def index():

    ## Get user's ID
    userid = session["user_id"]

    ## Get user's favorite team id's from database
    cur.execute("SELECT team_id FROM userteams WHERE user_id = ?", (userid,))
    team_results = cur.fetchall()

    ## Construct team dictionary
    teams = []
    for row in team_results:
        teams.append(
            {
                "team": get_team_by_id(row["team_id"]),
                "next": get_next_fixtures(row["team_id"], 1),
                "last": get_last_fixtures(row["team_id"], 1),
            }
        )

    ## Get user's favorite player id's from database
    cur.execute("SELECT player_id FROM userplayers WHERE user_id = ?", (userid,))
    player_results = cur.fetchall()

    ## Construct player dictionary
    players = []
    for row in player_results:
        players.append(get_player_by_id(row["player_id"]))

    return render_template("index.html", teams=teams, players=players)


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget previous log in
    session.clear()

    # If user reaches route via POST method (trying to log in)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please enter a username.")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please enter a password.")
            return render_template("login.html")

        # Query database for username
        cur.execute(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
        )
        rows = cur.fetchall()
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("invalid username and/or password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please enter a username.")
            return render_template("register.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please enter a password.")
            return render_template("register.html")

        # Ensure password was submitted
        elif not request.form.get("confirmation"):
            flash("Please enter password confirmation.")
            return render_template("register.html")

        elif request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords do not match.")
            return render_template("register.html")

        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))

        ## Check if user already exists
        cur.execute("SELECT username FROM users WHERE username = ?", (username,))
        user_check = cur.fetchall()

        if not user_check:
            cur.execute(
                "INSERT INTO users (username, hash) VALUES(?, ?)",
                (
                    username,
                    password,
                ),
            )
            con.commit()

            return redirect("/")
        else:
            flash("Username already exists.")
            return render_template("register.html")

    else:
        return render_template("register.html")


@app.route("/teams", methods=["GET", "POST"])
@login_required
def teams():

    ## If user has searched for a team
    if request.method == "POST":

        ## Manage error
        if not request.form.get("team"):
            return apology("There was an error while trying fetch user input.", 400)

        team = get_team_by_name(request.form.get("team"))

        print(team)
        ## If the search returns an empty team array, we send it out to the template, where it will be managed
        if not team:
            return render_template("found-team.html", team=team)

        ## If a team matches the search, find its fixtures.
        next = get_next_fixtures(team["team_id"], 1)
        last = get_last_fixtures(team["team_id"], 1)

        return render_template("found-team.html", team=team, next=next, last=last)

    else:
        return render_template("teams.html")


## Add team to users favorites
@app.route("/addteam", methods=["POST"])
@login_required
def addteam():

    ## Manage error if no input
    if not request.form.get("team_id"):
        return apology("There was an error while trying fetch user input.", 400)

    userid = session["user_id"]
    teamid = request.form.get("team_id")

    ## Check if team already added to user's favorites
    cur.execute(
        "SELECT team_id FROM userteams WHERE user_id = ? AND team_id= ? ",
        (
            userid,
            teamid,
        ),
    )
    teamexists = cur.fetchall()

    ## add team id to users favorites if it doesn't already exist
    if not teamexists:
        cur.execute(
            "INSERT INTO userteams (user_id, team_id) VALUES(?, ?)",
            (
                userid,
                teamid,
            ),
        )
        con.commit()
    else:
        flash("Team already added to favorites.")
        return redirect("/")

    flash("Team added to favorites!")
    return redirect("/")


@app.route("/players", methods=["GET", "POST"])
@login_required
def players():

    ## Get league ids from the database.
    ## To search for a player by name, it is required by the API to select a league in which to search for.
    cur.execute(
        "SELECT id, name FROM leagueids",
    )
    leagues = cur.fetchall()

    ## If the user has searched for a player
    if request.method == "POST":
        if not request.form.get("name"):
            return apology("There was an error while trying fetch user input.", 400)

        if not request.form.get("league_id"):
            return apology("There was an error while trying fetch user input.", 400)

        name = request.form.get("name")
        league_id = request.form.get("league_id")

        ## Get Player data from API
        players = get_player(league_id, name)

        return render_template("found-player.html", players=players, leagues=leagues)

    else:
        return render_template("players.html", leagues=leagues)


## Add player to users favorites
@app.route("/addplayer", methods=["POST"])
@login_required
def add_player():

    if not request.form.get("player_id"):
        return apology("There was an error while trying fetch user input.", 400)

    userid = session["user_id"]
    playerid = request.form.get("player_id")

    ## Check if player is already in user's favorites, if not add to database
    cur.execute(
        "SELECT player_id FROM userplayers WHERE user_id = ? AND player_id= ? ",
        (
            userid,
            playerid,
        ),
    )
    playerexists = cur.fetchall()

    if not playerexists:
        cur.execute(
            "INSERT INTO userplayers (user_id, player_id) VALUES(?, ?)",
            (
                userid,
                playerid,
            ),
        )
        con.commit()
    else:
        flash("Player already added to favorites.")
        return redirect("/")

    flash("Player added to favorites")
    return redirect("/")


def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
