import requests
from bs4 import BeautifulSoup
from constants import team_to_league

url = "https://www.baseballpress.com/lineups/"

#parsing uses mascot name, not full team name
__team_to_mascot = {
    'Boston Red Sox' : 'Red Sox',
    'New York Yankees' : 'Yankees',
    'Tampa Bay Rays' : 'Rays',
    'Toronto Blue Jays' : 'Blue Jays',
    'Baltimore Orioles' : 'Orioles',
    'Cleveland Indians' : 'Indians',
    'Minnesota Twins' : 'Twins',
    'Kansas City Royals' : 'Royals',
    'Chicago White Sox' : 'White Sox',
    'Detroit Tigers' : 'Tigers',
    'Houston Astros' : 'Astros',
    'Los Angeles Angels' : 'Angels',
    'Seattle Mariners' : 'Mariners',
    'Texas Rangers' : 'Rangers',
    'Oakland Athletics' : 'Athletics',

    'Washington Nationals' : 'Nationals',
    'Miami Marlins' : 'Marlins',
    'Atlanta Braves' : 'Braves',
    'New York Mets' : 'Mets',
    'Philadelphia Phillies' : 'Phillies',
    'Chicago Cubs' : 'Cubs',
    'Milwaukee Brewers' : 'Brewers',
    'St. Louis Cardinals' : 'Cardinals',
    'Pittsburgh Pirates' : 'Pirates',
    'Cincinnati Reds' : 'Reds',
    'Los Angeles Dodgers' : 'Dodgers',
    'Arizona Diamondbacks' : 'Diamondbacks',
    'Colorado Rockies' : 'Rockies',
    'San Diego Padres' : 'Padres',
    'San Francisco Giants' : 'Giants',
}

#returns dictionary of roster, pitcher first, batting in order
#away team must be listed first
#team mascots used
def get_lineups(date, away_team, home_team, double_header=False):
    away_team_mascot = __team_to_mascot[away_team]
    away_team_league = team_to_league[away_team]
    request_url = url + date
    r = requests.get(request_url)
    soup = BeautifulSoup(r.text,'lxml')
    players = []
    for item in soup.select("[data-league='{}']:-soup-contains('{}') .player > a.player-link".format(away_team_league, away_team_mascot)):
        player_name = item.get('data-razz').split("/")[-2].replace("+"," ")
        players.append(player_name)

    if len(players) < 20:
        players = []
        away_team_league = "AL" if away_team_league == "NL" else "NL"
        for item in soup.select("[data-league='{}']:-soup-contains('{}') .player > a.player-link".format(away_team_league, away_team_mascot)):
            player_name = item.get('data-razz').split("/")[-2].replace("+"," ")
            players.append(player_name)
        if len(players) < 20:
            raise Exception("Couldn't scrape roster for date={} teams={}, {}, rosters={}".format(date, away_team, home_team, players))

    if double_header and len(players) != 40:
        raise Exception("Couldn't scrape roster for double header on date={} teams={}, {}, rosters={}".format(date, away_team, home_team, players))
    #scrape returns both teams
    #players[0] = away team pitcher
    #players[1] = home team pitcher
    #pitchers[2-11] = away team roster
    #pitchers[12-20] = home team roster
    rosters = {}
    away_team_roster = []
    home_team_roster = []
    rosters[away_team] = away_team_roster
    rosters[home_team] = home_team_roster

    if not double_header:
        away_team_roster.append(players[0])
        home_team_roster.append(players[1])

        for i in range(2, 11):
            away_team_roster.append(players[i])

        for i in range(11, 20):
            home_team_roster.append(players[i])
    else:
        away_team_roster.append(players[20])
        home_team_roster.append(players[21])

        for i in range(22, 31):
            away_team_roster.append(players[i])

        for i in range(31, 40):
            home_team_roster.append(players[i])


    return rosters

# returns the starting pitcher from a roster as returned by get_lineups
#dict[team1] = [pitcher, batter1, ..., batter9]
def get_starting_pitcher(team, roster):
    return roster[team][0]

# returns the batting lineup from a roster as returned by get_lineups
#dict[team1] = [pitcher, batter1, ..., batter9]
def get_batting_lineup(team, roster):
    return roster[team][1:]

# print(get_lineups("2017-10-01", "Boston Red Sox", "Houston Astros"))
# print(get_starting_pitcher("Boston Red Sox", rosters))
# print(get_starting_pitcher("Miami Marlins", rosters))
# print(get_batting_lineup("Boston Red Sox", rosters))