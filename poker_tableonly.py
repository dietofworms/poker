import pandas as pd
import csv
import os
from datetime import datetime, timedelta


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


def main():
    # load data into data frame
    path = os.getcwd() + "/dataset.csv"
    raw_df = pd.read_csv(path)

    # generate standings leaderboard
    df = process_dataframe(raw_df)
    print(generate_standings(df))


if __name__ == "__main__":
    main()
