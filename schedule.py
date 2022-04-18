import pandas

__team_to_abbreviation = {
    'Boston Red Sox' : 'BOS',
    'New York Yankees' : 'NYY',
    'Tampa Bay Rays' : 'TB',
    'Toronto Blue Jays' : 'TOR',
    'Baltimore Orioles' : 'BAL',
    'Cleveland Indians' : 'CLE',
    'Minnesota Twins' : 'MIN',
    'Kansas City Royals' : 'KC',
    'Chicago White Sox' : 'CHW',
    'Detroit Tigers' : 'DET',
    'Houston Astros' : 'HOU',
    'Los Angeles Angels' : 'LAA',
    'Seattle Mariners' : 'SEA',
    'Texas Rangers' : 'TEX',
    'Oakland Athletics' : 'OAK',

    'Washington Nationals' : 'WSN',
    'Miami Marlins' : 'MIA',
    'Atlanta Braves' : 'ATL',
    'New York Mets' : 'NYM',
    'Philadelphia Phillies' : 'PHI',
    'Chicago Cubs' : 'CHC',
    'Milwaukee Brewers' : 'MIL',
    'St. Louis Cardinals' : 'STL',
    'Pittsburgh Pirates' : 'PIT',
    'Cincinnati Reds' : 'CIN',
    'Los Angeles Dodgers' : 'LAD',
    'Arizona Diamondbacks' : 'ARI',
    'Colorado Rockies' : 'COL',
    'San Diego Padres' : 'SD',
    'San Francisco Giants' : 'SF',
}
__abbreviation_to_team = {v: k for k, v in __team_to_abbreviation.items()}
#for some reason this data source has multiple mappings for the same teams...
__abbreviation_to_team["SFG"] = 'San Francisco Giants'
__abbreviation_to_team["SDP"] = 'San Diego Padres'
__abbreviation_to_team["KCR"] = 'Kansas City Royals'
__abbreviation_to_team["TBR"] = 'Tampa Bay Rays'

abbreviations = ["ARI",
                 "ATL",
                 "BAL",
                 "BOS",
                 "CHW",
                 "CHC",
                 "CIN",
                 "CLE",
                 "COL",
                 "DET",
                 "HOU",
                 "KC",
                 "LAA",
                 "LAD",
                 "MIA",
                 "MIL",
                 "MIN",
                 "NYM",
                 "NYY",
                 "OAK",
                 "PHI",
                 "PIT",
                 "SD",
                 "SF",
                 "SEA",
                 "STL",
                 "TB",
                 "TEX",
                 "TOR",
                 "WSN"]

__schedule_directory = "/Users/devonallison/code/Monopoly/src/main/thesis/data/schedules/"

def get_away_and_home_team(date, team1, team2):
    team1_abbrev = __team_to_abbreviation[team1]
    team1_schedule = pandas.read_pickle(__schedule_directory + team1_abbrev + "2.pkl")
    home_away = team1_schedule.loc[team1_schedule["Date"] == date]["Home_Away"].iloc[0]
    if home_away == "Home":
        return {"Home" : team1, "Away" : team2}
    else:
        return {"Home" : team2, "Away" : team1}

#returns date and opponent of the next game after input date
def get_next_game(date, team):
    team_abbrev = __team_to_abbreviation[team]
    team_schedule = pandas.read_pickle(__schedule_directory + team_abbrev + "2.pkl")
    schedule_after_date = team_schedule.loc[team_schedule["Date"] > date]
    if len(schedule_after_date) < 1:
        return None

    opponent = schedule_after_date["Opp"].iloc[0]
    opponent_full_team_name = __abbreviation_to_team[opponent]
    game_date = schedule_after_date["Date"].iloc[0]
    home_away = schedule_after_date["Home_Away"].iloc[0]
    actual_score = {team : schedule_after_date["R"].iloc[0], opponent_full_team_name : schedule_after_date["RA"].iloc[0]}
    if home_away == "Home":
        home_team = team
        away_team = opponent_full_team_name
    else:
        home_team = opponent_full_team_name
        away_team = team

    return {"Date" : game_date, "Home" : home_team, "Away" : away_team, "Score" : actual_score}
