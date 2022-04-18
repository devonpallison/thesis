from constants import team_to_league
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statistics



def plot_histogram_of_runs(sim=False):
    list_of_runs = []

    for team in team_to_league.keys():
        runs = pd.read_pickle("/Users/devonallison/code/Monopoly/src/main/thesis/data/results/{}_runs.pkl".format(team.replace(" ", "")))
        runs_list = runs["sim" if sim else "actual"]

        for run in runs_list:
            list_of_runs.append(run)

        for i in range(1,5):
            runs = pd.read_pickle("/Users/devonallison/code/Monopoly/src/main/thesis/data/results/20220414/{}_run_{}_runs.pkl".format(team.replace(" ", ""), i))
            runs_list = runs["sim" if sim else "actual"]

        for run in runs_list:
            list_of_runs.append(run)

    plt.hist(list_of_runs)
    plt.ylabel('Frequency')
    plt.xlabel('Number of Runs - {}'.format("Simulated" if sim else "Historical"))
    plt.show()


def get_mean_and_std_dev_of_runs(sim=False):
    list_of_runs = []

    for team in team_to_league.keys():
        runs = pd.read_pickle("/Users/devonallison/code/Monopoly/src/main/thesis/data/results/{}_runs.pkl".format(team.replace(" ", "")))
        runs_list = runs["sim" if sim else "actual"]

        for run in runs_list:
            list_of_runs.append(run)

        for i in range(1,5):
            runs = pd.read_pickle("/Users/devonallison/code/Monopoly/src/main/thesis/data/results/20220414/{}_run_{}_runs.pkl".format(team.replace(" ", ""), i))
            runs_list = runs["sim" if sim else "actual"]

        for run in runs_list:
            list_of_runs.append(run)

    std = statistics.stdev(list_of_runs)
    print("Standard deviation of the number of runs in {} games = {} ".format("simulated" if sim else "historical", std))
    mean = statistics.mean(list_of_runs)
    print("Mean of the number of runs in {} games = {} ".format("simulated" if sim else "historical", mean))

def plot_simperc_vs_actual():
    histogram_of_results = {}

    for team in team_to_league.keys():
        results = pd.read_pickle("/Users/devonallison/code/Monopoly/src/main/thesis/data/results/{}_record.pkl".format(team.replace(" ", "")))
        for result in results.keys():
            if result not in histogram_of_results:
                histogram_of_results[result] = {"wins" : 0, "losses" : 0, "actual_wins" : 0, "actual_losses" : 0}
            res = results[result]
            histogram_of_results[result]["wins"] = histogram_of_results[result]["wins"] + res["wins"]
            histogram_of_results[result]["losses"] = histogram_of_results[result]["losses"] + res["losses"]
            histogram_of_results[result]["actual_wins"] = histogram_of_results[result]["actual_wins"] + res["actual_wins"]
            histogram_of_results[result]["actual_losses"] = histogram_of_results[result]["actual_losses"] + res["actual_losses"]

    for team in team_to_league.keys():
        for i in range(1,5):
            results = pd.read_pickle("/Users/devonallison/code/Monopoly/src/main/thesis/data/results/20220414/{}_run_{}_record.pkl".format(team.replace(" ", ""), i))
            for result in results.keys():
                if result not in histogram_of_results:
                    histogram_of_results[result] = {"wins" : 0, "losses" : 0, "actual_wins" : 0, "actual_losses" : 0}
                res = results[result]
                histogram_of_results[result]["wins"] = histogram_of_results[result]["wins"] + res["wins"]
                histogram_of_results[result]["losses"] = histogram_of_results[result]["losses"] + res["losses"]
                histogram_of_results[result]["actual_wins"] = histogram_of_results[result]["actual_wins"] + res["actual_wins"]
                histogram_of_results[result]["actual_losses"] = histogram_of_results[result]["actual_losses"] + res["actual_losses"]

    print(histogram_of_results)
    labels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    actual_wins_list = []
    actual_losses_list = []
    for label in labels:
        if label in histogram_of_results:
            actual_wins_list.append(histogram_of_results[label]["actual_wins"])
            actual_losses_list.append(histogram_of_results[label]["actual_losses"])

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, actual_wins_list, width, label='Actual Wins')
    rects2 = ax.bar(x + width/2, actual_losses_list, width, label='Actual Losses')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_xlabel('Win Percentage in 10 Simulated Games')
    ax.set_xticks(x, labels)
    ax.legend()

    fig.tight_layout()

    plt.show()

def agg_sim_vs_actual():
    num_games = 0
    correctly_picked = 0

    for team in team_to_league.keys():
        results = pd.read_pickle("/Users/devonallison/code/Monopoly/src/main/thesis/data/results/{}_record.pkl".format(team.replace(" ", "")))
        for result in results.keys():
            res = results[result]
            if result < 0.5:
                num_games = num_games + res["actual_wins"] + res["actual_losses"]
                correctly_picked = correctly_picked + res["actual_losses"]
            elif result > 0.5:
                num_games = num_games + res["actual_wins"] + res["actual_losses"]
                correctly_picked = correctly_picked + res["actual_wins"]

    for team in team_to_league.keys():
        for i in range(1,5):
            results = pd.read_pickle("/Users/devonallison/code/Monopoly/src/main/thesis/data/results/20220414/{}_run_{}_record.pkl".format(team.replace(" ", ""), i))
            for result in results.keys():
                res = results[result]
                if result < 0.5:
                    num_games = num_games + res["actual_wins"] + res["actual_losses"]
                    correctly_picked = correctly_picked + res["actual_losses"]
                elif result > 0.5:
                    num_games = num_games + res["actual_wins"] + res["actual_losses"]
                    correctly_picked = correctly_picked + res["actual_wins"]

    print("Win loss record was {}-{}".format(correctly_picked, num_games - correctly_picked))

def get_win_loss_by_team():
    for team in team_to_league.keys():
        wins = 0
        losses = 0

        results = pd.read_pickle("/Users/devonallison/code/Monopoly/src/main/thesis/data/results/{}_record.pkl".format(team.replace(" ", "")))
        for result in results.keys():
            res = results[result]
            if result < 0.5 or result > 0.5:
                wins = wins + res["wins"]
                losses = losses + res["losses"]
            else:
                num_games = res["wins"] + res["losses"]
                wins = wins + num_games / 2
                losses = losses + num_games / 2

        for i in range(1,5):
            results = pd.read_pickle("/Users/devonallison/code/Monopoly/src/main/thesis/data/results/20220414/{}_run_{}_record.pkl".format(team.replace(" ", ""), i))
            for result in results.keys():
                res = results[result]
                if result < 0.5 or result > 0.5:
                    wins = wins + res["wins"]
                    losses = losses + res["losses"]
                else:
                    num_games = res["wins"] + res["losses"]
                    wins = wins + num_games / 2
                    losses = losses + num_games / 2
        print("Win loss record for {} was {}-{}".format(team, wins, losses))
        print("Win pct for {} was {}".format(team, wins / (losses + wins)))

get_win_loss_by_team()