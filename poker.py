import pandas as pd
import csv
import os
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters as converter
import seaborn as sns; sns.set()
from collections import Counter


def process_dataframe(df: pd.DataFrame()) -> pd.DataFrame():
    """ takes in pandas dataframe and cleans it
        returns processed dataframe
    """
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    return df


def generate_standings(df: pd.DataFrame()) -> pd.DataFrame():
    """ takes pandas dataframe, performs operations to generate
        a traditional standings style leaderboard
        returns dataframe
    """
    # get unique player names as keys
    players = df['player'].unique()
    players = pd.DataFrame(players, columns=['player']) 

    # getting player points
    points = df.groupby('player').agg({'points': 'sum'})

    # getting total games played
    games_played = df[df.played > 0]
    games_played = games_played["player"].value_counts()
    games_played = games_played.to_frame(name='games_played')

    # joining dataframes
    result = players.join(games_played)
    result = result.join(points).fillna(0)
    result = pd.merge(points, games_played, left_index=True, right_index=True)

    # getting points per game
    result['ppg'] = round((result['points'] / result['games_played']),2)

    # getting count of wins
    wins = df[df['position'] == 1]
    wins = wins['player'].value_counts()
    wins = wins.to_frame(name='wins')

    # join result df to wins
    final_result = result.join(wins)

    # format final result set for presentation in table format
    table = final_result.fillna(0)
    table['wins'] = table['wins'].astype('int64')
    table['games_played'] = table['games_played'].astype('int64')
    table = table[['games_played', 'points', 'ppg', 'wins']]
    table=table.sort_values(by=['points'], ascending=False)
    
    return table


def generate_plot(data: pd.DataFrame()):
    df = data.groupby(['date','game_id','player', 'position']).sum() \
             .groupby(level=2).cumsum().reset_index()
    df = df.sort_values(by=['date','game_id','position']).reset_index()
    df = df[['date', 'game_id', 'player', 'position', 'points']]
        
    plt.rcParams["figure.figsize"] = (26, 22)

    # setting font family
    plt.rcParams['font.family'] = 'Jetbrains Mono'

    # plt.rcParams['lines.linewidth'] = 20
    # plt.rcParams['lines.markersize'] = 1

    # setting plot context
    sns.set_context("poster")
    # defining the lineplot dataset and axis 
    ax = sns.lineplot(x="date", y="points", hue="player", data=df,dashes = True)

    # adding labels to axis and title
    ax.set_title('\n Player Standings Over Time \n', fontsize = 38, weight='bold')
    ax.set_ylabel("\n Points \n", fontsize = 36)
    ax.set_xlabel("\n Date \n", fontsize = 36)

    min_date = min(df['date']) - timedelta(days=3)
    max_date = max(df['date']) + timedelta(days=3)
    plt.xlim(min_date, max_date)

    # position legend to upper right of the plot and outside the x,y plane
    ax.legend(loc='upper right', bbox_to_anchor=(1.14, 1.007), ncol=1)
    
    # save to file
    plt.savefig('plots/StandingsOverTime-line.png')


def generate_histograms(data: pd.DataFrame()):
    # create new dataframe for this analysis
    filter_mask = data[data.played>0]

    plt.rcParams["figure.figsize"] = (25, 30)

    # create list of players
    players = list(set(data['player']))

    # initialise empty list of scores for each player
    scores_steve, scores_mellick, scores_antoni, scores_robbo, scores_sam, scores_lowes = ([] for i in range(0, len(players))) 

    # create list of lists of all scores
    scores = [scores_steve, scores_mellick, scores_antoni, scores_robbo, scores_sam, scores_lowes]

    # zip the list and player names together for iteration
    score_dict = dict(zip(players, [0,0,0,0,0,0]))

    # iterate through the zipped list and assign the list of values to each list
    for player in players:
        score_dict[player] = Counter(filter_mask[filter_mask['player']==player]['position'].values.tolist())

    # for player in players:
    #     plt.figure()
    #     plt.bar(score_dict[player].keys(), score_dict[player].values())
    #     plt.xticks(range(1,7))
    #     plt.xlabel('position')
    #     plt.ylabel('frequency')
    #     plt.title('%s place distribution' % player)
    #     plt.savefig('plots/%s-hist.png' % player)

    plt.figure()
    for i in range(len(players)):
        ax = plt.subplot(3, 2, i+1)
        plt.bar(score_dict[players[i]].keys(), score_dict[players[i]].values())
        plt.xticks(range(1, 7))
        #plt.xlabel('position')
        #plt.ylabel('frequency')
        plt.title('%s' % players[i])

    plt.savefig('plots/standings-hist.png')


if __name__ == "__main__":
    # load data into data frame
    path = os.getcwd() + "/dataset.csv"
    raw_df = pd.read_csv(path)

    # generate standings leaderboard
    df = process_dataframe(raw_df)
    print(generate_standings(df))
    
    # save plot files to directory
    generate_plot(df)
    generate_histograms(df)