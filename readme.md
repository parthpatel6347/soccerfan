# Soccer Fan

### CS50x Final Project

---

#### Video Demo: https://youtu.be/Z4QRs69_cmc

#### Description:

This is an application for following your favorite soccer teams and players.
It is made with Flask.

---

### The Database:

The database consists of 4 tables:

1. The first table stores the user's unique ID, username and hashed password.
2. The table stores the league names with correspong league id's on the API. (This is required while querying for players).
3. The third table stores User IDs and their favorite teams.
4. The fourth table stores User IDs and their favorite players.

---

### Index Page:

Once the user logs in, they are taken to the index page.
The index page has 2 tabs, where the user can see their favorite teams and players. The IDs of the user's favorite teams and players are extracted from the database and sent to the API to receive latest information for the team and the player via separate requests.

The team card has infomation like team logo, results of the previous fixture and details about the upcoming fixture.  
The player card has a player photo, player's team name and stats like appearences, goals, assists and average rating.

If the player doesn't already have any favorite teams or players, the index page has buttons that redirect to the respective search pages.

---

### Teams Page:

This page is where the user can search and add team to their favorites.

This page consists of a search bar where the user can query for a team. This request is sent to the API and if there are any matches the information is parsed and the user is shown a team card. This team card has team information like the one on the index page along with a button to add team to favorites.

If the user adds this team to their favorites, the team ID is stored in the database, and the user is redirected to the home page where they will be able to see this team card appear among their favorite teams.

---

### Players Page:

On this page the user can search for players and add to their favorites.

This page consists of a search bar for entering the player name, and a drop down menu of league names. Once the user searches for a player name within the desired league, the request is sent to the API and all matches are shown to the user in form of player cards with an add to favorites button.

If the user adds a player to their favorites, the players ID is saved to the database and the user is redirected to the index page where the newly added player will appear.
