import random
import pickle
from baseball_scraper import *
from roster import *
from constants import *
from schedule import *

debug = True

#whether to cache player stats
cache = False
pitcher_cache = {}
batter_cache = {}

__url = "https://www.baseballpress.com/lineups/"
__base_list = [single, double, triple, home_run]

#for debug
__n_innings = 9
__n_batters = 9

__pitcher_suffix = "_p"
__batter_suffix = "_b"

__output_dir = "/Users/devonallison/code/Monopoly/src/main/thesis/data/results/20220414/"

def save_dict(file, dict):
    debug_logging("Saving dict to file {}".format(file))

    with open('{}{}.pkl'.format(__output_dir, file), 'wb') as f:
        pickle.dump(dict, f)

#found via script calc_averages.py
__league_averages = {
    strike : 0.19695532194871276,
    foul : 0.1934050788200313,
    ball : 0.39814586532720636,
    field_out : 0.13257389656411794,
    single : 0.051659126756630716,
    double : 0.015899457304702467,
    triple : 0.0018636400091488863,
    home_run : 0.009497613269449551
}

def get_league(team):
    return team_to_league[team]

# print(df.head(2))
import sys
# print(df['events'].unique())
# print(df['description'].unique())

def get_player_id(fname, lname):
    debug_logging("Getting player id for {} {}".format(fname, lname))
    player_id_data = playerid_lookup(lname, fname)
    id = player_id_data["key_mlbam"]

    if id is None or len(id) < 1:
        return -1

    debug_logging("Got id {}".format(id[0]))
    if len(id) > 1:
        debug_logging("Found more than one row for {} {}".format(fname, lname))
    return id[0]

def get_pitcher_stats(start_dt, end_dt, id):
    return statcast_pitcher(start_dt, end_dt, id)

def get_batter_stats(start_dt, end_dt, id):
    return statcast_batter(start_dt, end_dt, id)

def calculate_stats(start_dt, end_dt, player_name, is_pitcher):
    if cache:
        if is_pitcher and player_name in pitcher_cache:
            debug_logging("Found pitcher {} in pitcher cache; using cached data".format(player_name))
            return pitcher_cache[player_name]
        elif not is_pitcher and player_name in batter_cache:
            debug_logging("Found batter {} in batter cache; using cached data".format(player_name))
            return batter_cache[player_name]

    name = player_name.split()
    id = get_player_id(name[0], name[1])

    debug_logging("Calculating stats for id {}, is pitcher? {}".format(id, is_pitcher))

    #statcast can throw exceptions, even partway through a simulation; gotta protect ourselves
    try:
        if id < 0: # if we couldn't find the player, return the league averages
            if is_pitcher:
                pitcher_cache[player_name] = __league_averages
            else:
                batter_cache[player_name] = __league_averages
            return __league_averages

        if is_pitcher:
            stats = get_pitcher_stats(start_dt, end_dt, id)
        else:
            stats = get_batter_stats(start_dt, end_dt, id)

        num_pitches = len(stats)
        if num_pitches == 0: # if no data for given date range, return the league averages
            if is_pitcher:
                pitcher_cache[player_name] = __league_averages
            else:
                batter_cache[player_name] = __league_averages
            return __league_averages

        df = {}
        df[strike] = len(stats.loc[stats["description"] == strike]) / num_pitches
        df[foul] = len(stats.loc[stats["description"] == foul]) / num_pitches
        df[ball] = len(stats.loc[stats["description"] == ball]) / num_pitches
        df_hit = stats.loc[stats["description"] == hit]
        df[single] = len(df_hit.loc[df_hit["events"] == single]) / num_pitches
        df[double] = len(df_hit.loc[df_hit["events"] == double]) / num_pitches
        df[triple] = len(df_hit.loc[df_hit["events"] == triple]) / num_pitches
        df[home_run] = len(df_hit.loc[df_hit["events"] == home_run]) / num_pitches
        df[field_out] = len(df_hit.loc[df_hit["events"] == field_out]) / num_pitches

        if sum(df.values()) == 0:
            df = __league_averages

        debug_logging("Done calculating stats for id {} {}".format(id, df))

        if is_pitcher:
            pitcher_cache[player_name] = df
        else:
            batter_cache[player_name] = df

        return df
    except Exception as e:
        return __league_averages


#get the stats for a game from before the given game
def get_starting_lineup_stats(date, team1, team2, rosters):
    return {
        team1 : get_pregame_stats(date, team1, rosters),
        team2 : get_pregame_stats(date, team2, rosters)
    }

def start(date, team1, team2, num_iterations=10):
    teams = get_away_and_home_team(date, team1, team2)
    away_team = teams["Away"]
    home_team = teams["Home"]
    simulate_game(date, home_team, away_team, num_iterations=num_iterations)

def simulate_game(date, home_team, away_team, double_header=False, num_iterations=10):
    debug_logging("Simulating game: home team = {}, away team = {}, date = {}, num_iterations = {}".format(home_team, away_team, date, num_iterations))

    lineups = get_lineups(date, away_team, home_team, double_header)
    debug_logging("Lineups = {}".format(lineups))

    starting_lineup_stats = get_starting_lineup_stats(date, home_team, away_team, lineups)
    debug_logging("Finished getting starting lineup stats = {}".format(starting_lineup_stats))

    team1_pitcher_stats = starting_lineup_stats[home_team]["{}{}".format(home_team, __pitcher_suffix)]
    team1_batter_stats = starting_lineup_stats[home_team]["{}{}".format(home_team, __batter_suffix)]
    team2_pitcher_stats = starting_lineup_stats[away_team]["{}{}".format(away_team, __pitcher_suffix)]
    team2_batter_stats = starting_lineup_stats[away_team]["{}{}".format(away_team, __batter_suffix)]

    debug_logging("team1_pitcher_stats = {}".format(team1_pitcher_stats))
    debug_logging("team1_batter_stats = {}".format(team1_batter_stats))
    debug_logging("team2_pitcher_stats = {}".format(team2_pitcher_stats))
    debug_logging("team2_batter_stats = {}".format(team2_batter_stats))

    wins = {}
    wins[home_team] = 0
    wins[away_team] = 0
    num_runs = []
    for i in range(0, num_iterations):
        score = run_simulation(home_team, away_team, team1_pitcher_stats, team1_batter_stats, team2_pitcher_stats, team2_batter_stats)

        if score[home_team] > score[away_team]:
            wins[home_team] = wins[home_team] + 1
        else:
            wins[away_team] = wins[away_team] + 1

        num_runs.append(score[home_team] + score[away_team])

    post_report(date, home_team, away_team, num_iterations, wins, num_runs)

    return {"wins" : wins, "runs" : num_runs}

def post_report(date, team1, team2, num_iterations, wins, num_runs):
    print("Simulated {} vs {} on {} {} times.".format(team1, team2, date, num_iterations))
    print("Of these, {} won {}, and {} won {}".format(team1, wins[team1], team2, wins[team2]))

    total_runs = sum(num_runs)
    print("The total number of runs was {}, giving an average number of {}".format(total_runs, total_runs / len(num_runs)))

def simulate_2017_season(team, num_runs=1, use_cache=True):
    for i in range(1, num_runs):
        next_game = get_next_game("2017-01-01", team)
        global cache
        cache = use_cache
        odds_to_results = {}
        simulated_runs_vs_actual = {"sim" : [], "actual" : []}
        prevDate = None
        while next_game:
            game_date = next_game["Date"]
            home_team = next_game["Home"]
            away_team = next_game["Away"]
            actual_score = next_game["Score"]
            opponent = away_team if home_team == team else home_team
            double_header = prevDate == game_date

            try:
                simulated_game = simulate_game(game_date, home_team, away_team, double_header)
            except Exception as e:
                print("Failed to simulated game {}. Skipping".format(next_game))
                print(e)
                next_game = get_next_game(game_date, team)
                prevDate = game_date
                continue

            sim_wins = simulated_game["wins"]
            sim_runs = simulated_game["runs"]
            sim_odds = sim_wins[team] / (sim_wins[team] + sim_wins[opponent])
            actual_team_won = actual_score[team] > actual_score[opponent]
            actual_winner = team if actual_team_won else opponent

            debug_logging("Finished simulating game {}".format(simulated_game))
            debug_logging("Sim odds {}".format(sim_odds))
            debug_logging("Sim runs {}".format(sim_runs))
            debug_logging("Actual winner {}".format(actual_winner))
            debug_logging("Actual score {}".format(actual_score))

            if sim_odds not in odds_to_results:
                odds_to_results[sim_odds] = {"wins" : 0, "losses" : 0, "draws" : 0, "actual_wins" : 0, "actual_losses" : 0}

            if sim_odds > 0.50:
                odds_to_results[sim_odds]["wins"] = odds_to_results[sim_odds]["wins"] + 1
            elif sim_odds < 0.5:
                odds_to_results[sim_odds]["losses"] = odds_to_results[sim_odds]["losses"] + 1
            else:
                if random.randrange(0,2) == 0: #simulation was a push- randomly pick winner
                    odds_to_results[sim_odds]["losses"] = odds_to_results[sim_odds]["losses"] + 1
                else:
                    odds_to_results[sim_odds]["wins"] = odds_to_results[sim_odds]["wins"] + 1

            if actual_team_won:
                odds_to_results[sim_odds]["actual_wins"] = odds_to_results[sim_odds]["actual_wins"] + 1
            else:
                odds_to_results[sim_odds]["actual_losses"] = odds_to_results[sim_odds]["actual_losses"] + 1

            simulated_runs_vs_actual["sim"].append(sum(sim_runs) / len(sim_runs))
            simulated_runs_vs_actual["actual"].append(actual_score[team] + actual_score[opponent])

            debug_logging("Current odds to results {}".format(odds_to_results))
            debug_logging("Current sim runs vs actual results odds {}".format(simulated_runs_vs_actual))
            next_game = get_next_game(game_date, team)
            prevDate = game_date

        team_no_spaces = team.replace(" ", "")
        save_dict('{}_run_{}_record'.format(team_no_spaces, i), odds_to_results)
        save_dict('{}_run_{}_runs'.format(team_no_spaces, i), simulated_runs_vs_actual)

def run_simulation(team1, team2, team1_pitcher_stats, team1_batter_stats, team2_pitcher_stats, team2_batter_stats):
    team1_event_probabilities = {}
    for key in team1_batter_stats:
        team1_event_probabilities[key] = log5(team1_batter_stats[key], team2_pitcher_stats)

    team2_event_probabilities = {}
    for key in team2_batter_stats:
        team2_event_probabilities[key] = log5(team2_batter_stats[key], team1_pitcher_stats)

    debug_logging("team1_event_probabilities {}".format(team1_event_probabilities))
    debug_logging("team2_event_probabilities {}".format(team2_event_probabilities))

    score = {
        team1 : 0,
        team2 : 0,
    }

    event_probabilities = {
        team1 : team1_event_probabilities,
        team2 : team2_event_probabilities,
    }

    batter_orders = {
        team1 : list(team1_event_probabilities.keys()),
        team2 : list(team2_event_probabilities.keys()),
    }

    i = 0
    while (i < __n_innings) or (score[team1] == score[team2]):
        for team in [team1, team2]:
            game_matrix = {
                "outs" : 0,
                "strikes" : 0,
                "balls" : 0,
                "1B" : 0,
                "2B" : 0,
                "3B" : 0,
                "batter_num" : 0
            }

            while game_matrix['outs'] < 3:
                debug_logging("Batter line up: {}, line up number {}".format(batter_orders, game_matrix['batter_num']))
                batter_id = batter_orders[team][game_matrix['batter_num']]
                outcome = simulate_pitch(event_probabilities[team][batter_id])
                debug_logging("Simulated pitch. Outcome: " + outcome)
                debug_logging("Game matrix prior to pitch: {}".format(game_matrix))
                update_game_matrix(team, outcome, game_matrix, score)
                debug_logging("Game matrix post pitch: {}".format(game_matrix))
                debug_logging("Score post pitch: {}".format(score))
        i = i + 1
    return score

def debug_logging(text):
    if debug:
        print(text)

def get_pregame_stats(date, team, rosters):
    lineup = get_batting_lineup(team, rosters)
    debug_logging("Got batting lineup {} for {}".format(lineup, team))

    batter_num = 0
    batter_stats = {}
    for player in lineup:
        debug_logging("Getting batting statistics for {}".format(player))
        batter_stats_for_id = calculate_stats("1900-01-01", date, player, False)
        batter_stats[batter_num] = batter_stats_for_id
        batter_num = batter_num + 1

    debug_logging("Finished getting batting statistics for {}".format(team))

    pitcher = get_starting_pitcher(team, rosters)

    debug_logging("Got starting pitcher {} for team".format(pitcher, team))

    pitcher_stats = calculate_stats("1900-01-01", date, pitcher, True)

    debug_logging("Finished getting batting statistics for {}".format(team))

    return {
        "{}{}".format(team, __batter_suffix) : batter_stats,
        "{}{}".format(team, __pitcher_suffix) : pitcher_stats,
    }


#aux function for get_line_up
def get_names(item):
    try:
        player_name = item.get('data-razz').split("/")[-2].replace("+"," ")
    except IndexError: player_name = ""
    return player_name

def simulate_pitch(event_probabilities):
    random_num = random.uniform(0.0, 1.0)
    prob_single = event_probabilities[single]
    prob_double = prob_single + event_probabilities[double]
    prob_triple = prob_double + event_probabilities[triple]
    prob_home_run = prob_triple + event_probabilities[home_run]
    prob_strike = prob_home_run + event_probabilities[strike]
    prob_foul = prob_strike + event_probabilities[foul]
    prob_ball = prob_foul + event_probabilities[ball]

    if random_num < prob_single:
        return single
    elif random_num < prob_double:
        return double
    elif random_num < prob_triple:
        return triple
    elif random_num < prob_home_run:
        return home_run
    elif random_num < prob_strike:
        return strike
    elif random_num < prob_foul:
        return foul
    elif random_num < prob_ball:
        return ball
    else:
        return field_out

def create_batter_orders(team_batter_ids):
    orders = {}
    for i in range(0, len(team_batter_ids)):
        debug_logging(team_batter_ids)
        orders[i] = team_batter_ids[i]
    return orders

def update_game_matrix(team, outcome, game_matrix, score):
    if outcome == field_out:
        update_game_matrix_field_out(game_matrix)
    elif outcome == strike or outcome == foul: #todo separate
        update_game_matrix_strike(game_matrix)
    elif outcome == ball:
        update_game_matrix_ball(team, game_matrix, score)
    elif outcome == single:
        update_game_matrix_single(team, game_matrix, score)
    elif outcome == double:
        update_game_matrix_double(team, game_matrix, score)
    elif outcome == triple:
        update_game_matrix_triple(team, game_matrix, score)
    elif outcome == home_run:
        update_game_matrix_homer(team, game_matrix, score)
    else:
        raise Exception("Can't update game matrix. Unknown outcome: {}".format(outcome))



# Event D’Espopo and Lefkowitz
# Walk: Batter to first, baserunners advance one base if forced
# Single: Batter to first, baserunners on second and third score, baserunner on first to second
# Double: Batter to second, baserunners on second and third score, baserunner on first to third
# Triple Batter to third, all baserunners score
# HR Batter scores, all baserunners score
# Out No baserunners advance
def update_game_matrix_field_out(game_matrix):
    game_matrix['outs'] += 1
    game_matrix['batter_num'] = (game_matrix['batter_num'] + 1) % __n_batters
    reset_game_matrix_balls_strikes(game_matrix)

def update_game_matrix_strike(game_matrix):
    game_matrix['strikes'] += 1
    if game_matrix['strikes'] > 2:
        game_matrix['outs'] += 1
        game_matrix['batter_num'] = (game_matrix['batter_num'] + 1) % __n_batters
        reset_game_matrix_balls_strikes(game_matrix)

def update_game_matrix_ball(team, game_matrix, score):
    game_matrix['balls'] += 1
    if game_matrix['balls'] > 3:
        if game_matrix['1B'] > 0:
            if game_matrix['2B'] > 0:
                if game_matrix['3B'] > 0:
                    score[team] += 1
                else:
                    game_matrix['3B'] = 1
            else:
                game_matrix['2B'] = 1
        else:
            game_matrix['1B'] = 1

        reset_game_matrix_balls_strikes(game_matrix)
        game_matrix['batter_num'] = (game_matrix['batter_num'] + 1) % __n_batters

def update_game_matrix_single(team, game_matrix, score):
    #runners on second and third base score
    runs_scored = 0
    if game_matrix['2B'] > 0:
        runs_scored += 1
    if game_matrix['3B'] > 0:
        runs_scored += 1

    score[team] += runs_scored
    game_matrix['2B'] = 0
    game_matrix['3B'] = 0

    #batter to 1B, runner of 1B to 2B
    if game_matrix['1B'] > 0:
        game_matrix['2B'] = 1
    else:
        game_matrix['1B'] = 1

    reset_game_matrix_balls_strikes(game_matrix)
    game_matrix['batter_num'] = (game_matrix['batter_num'] + 1) % __n_batters


def update_game_matrix_double(team, game_matrix, score):
    #runners on second and third base score
    runs_scored = 0
    if game_matrix['2B'] > 0:
        runs_scored += 1
    if game_matrix['3B'] > 0:
        runs_scored += 1

    score[team] += runs_scored
    game_matrix['2B'] = 0
    game_matrix['3B'] = 0

    #batter to 2B, runner of 1B to 3B
    if game_matrix['1B'] > 0:
        game_matrix['3B'] = 1
    else:
        game_matrix['2B'] = 1
    game_matrix['1B'] = 0

    reset_game_matrix_balls_strikes(game_matrix)
    game_matrix['batter_num'] = (game_matrix['batter_num'] + 1) % __n_batters

def update_game_matrix_triple(team, game_matrix, score):
    #runners on base score
    runs_scored = 0
    if game_matrix['1B'] > 0:
        runs_scored += 1
    if game_matrix['2B'] > 0:
        runs_scored += 1
    if game_matrix['3B'] > 0:
        runs_scored += 1

    score[team] += runs_scored
    reset_game_matrix_bases(game_matrix)
    game_matrix['3B'] = 1
    reset_game_matrix_balls_strikes(game_matrix)
    game_matrix['batter_num'] = (game_matrix['batter_num'] + 1) % __n_batters

def update_game_matrix_homer(team, game_matrix, score):
    runs_scored = 1
    if game_matrix['1B'] > 0:
        runs_scored += 1
    if game_matrix['2B'] > 0:
        runs_scored += 1
    if game_matrix['3B'] > 0:
        runs_scored += 1

    score[team] += runs_scored
    reset_game_matrix_bases(game_matrix)
    reset_game_matrix_balls_strikes(game_matrix)
    game_matrix['batter_num'] = (game_matrix['batter_num'] + 1) % __n_batters

def reset_game_matrix_balls_strikes(game_matrix):
    game_matrix['balls'] = 0
    game_matrix['strikes'] = 0

def reset_game_matrix_bases(game_matrix):
    game_matrix['1B'] = 0
    game_matrix['2B'] = 0
    game_matrix['3B'] = 0

#returns a map of probabilities of different events
#uses log5 rule pb(e) * pp(e) / pl(e) / sum ( pb(e) * pp(e) / pl(e) ) for all events e
def log5(batter_stats, pitcher_stats):
    log5_dict = {}

    sum = 0
    for key in __league_averages:
        sum += (batter_stats[key] * pitcher_stats[key]) / __league_averages[key]

    for key in __league_averages:
        log5_dict[key] = ((batter_stats[key] * pitcher_stats[key]) / __league_averages[key]) / sum

    return log5_dict



# start("2017-04-03", "Pittsburg Pirates", "New York Mets")
#simulate_2017_season("Colorado Rockies")
# team1_pitcher_stats = {'called_strike': 0.16198548954816464, 'foul': 0.1633503340277279, 'ball': 0.322606134616766, 'single': 0.04058616478701243, 'double': 0.01120609151641405, 'triple': 0.001436678399540263, 'home_run': 0.008332734717333526, 'field_out': 0.12484735292004885}
# team1_batter_stats = { 12323 : {'called_strike': 0.22533748701973, 'foul': 0.13291796469366562, 'ball': 0.27102803738317754, 'single': 0.03426791277258567, 'double': 0.005192107995846314, 'triple': 0.0, 'home_run': 0.0, 'field_out': 0.1308411214953271}}
# team2_pitcher_stats = {'called_strike': 0.16964717254712422, 'foul': 0.1677138714354761, 'ball': 0.29901723860157886, 'single': 0.03979378121475753, 'double': 0.010794264540035443, 'triple': 0.0019333011116481392, 'home_run': 0.005316578057032383, 'field_out': 0.10262606734332205}
# team2_batter_stats = { 12323 : {'called_strike': 0.1765873015873016, 'foul': 0.1130952380952381, 'ball': 0.31746031746031744, 'single': 0.027777777777777776, 'double': 0.007936507936507936, 'triple': 0.0, 'home_run': 0.007936507936507936, 'field_out': 0.041666666666666664}}
#
# run_simulation("Atlanta Braves", "New York Mets", team1_pitcher_stats, team1_batter_stats, team2_pitcher_stats, team2_batter_stats)

for team in team_to_league.keys():
    simulate_2017_season(team, 5)