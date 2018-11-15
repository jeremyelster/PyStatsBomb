import collections
import numpy as np
import pandas as pd
import datetime
from pandas.io.json import json_normalize

def getMatchDictChildren(d):
    dict_children = {}
    for k, v in d.items():
        if isinstance(v, dict):
            for k, v in v.items():
                dict_children[k] = v
        else:
            dict_children[k] = v
    return dict_children


def getLineupParse(l):

    lineup = []
    team_name = l.get('team_name', None)
    team_id = l.get('team_id', None)
    match_id = l.get('match_id', None)
    players = l.get('lineup', 'Structure has changed')

    if isinstance(players, list):
        for p in players:
            name = p.get('player_name', None)
            pid = p.get('player_id', None)
            jersey = p.get('jersey_number', None)
            country_id = p.get('country', {'id': None}).get('id', None)
            country_name = p.get('country', {'name': None}).get('name', None)

            lineup.append({
                "match_id": match_id,
                "team_name": team_name,
                "team_id": team_id,
                "player_name": name,
                "player_id": pid,
                "jersey_number": jersey,
                "country_id": country_id,
                "country_name": country_name})

    else:
        print(players)
    return lineup

# https://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys


def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


# Plotting

def pass_direction(x):
    """According to statsbomb, pass_angle is between 0 (pass ahead) and pi (pass behind). Clockwise
    We divide the circle into 4 equal sections. Directions are forward, right, left, behind"""

    pi_div = np.pi / 4
    if (x <= pi_div) & (x >= -pi_div):
        return "Forward"
    elif (x > pi_div) & (x <= 3 * pi_div):
        return "Right"
    elif (x > 3 * pi_div) & (x < -3 * pi_div):
        return "Behind"
    else:
        return "Left"


class LineupsSB():

    def __init__(self, data=None, from_file=None):

        if from_file:
            self.lineups_df = pd.read_csv(from_file)
            print(f"Successfully acquired lineup data from {from_file}")

        elif data:
            self.lineups_df = self.lineupParse(data)

        else:
            raise Exception("Supply data source for lineups")

        self.calcPlayTime()
        self.calcPositions()

    def calcPlayTime(self):
        """Aggregate the amount of time on the field for each player including
        stoppage time in seconds, minutes, and game minutes"""

        self.player_play_time = self.lineups_df\
            .groupby(["team_name", "match_id", "player.name"], as_index=False)\
            .agg({
                "game_minutes_played": sum,
                "seconds_played": sum,
                "total_minutes_played": sum})

    def calcPositions(self):
        """Return the starting positions and position played by player for
        majority of time on pitch"""

        # Starting Positions
        starting_positions = self.lineups_df\
            .groupby(["team_name", "match_id", "player.name"], as_index=False)[ "position.name"].first()\
            .rename({"position.name": "starting_position"}, axis=1)

        most_time = self.lineups_df\
            .groupby(["team_name", "match_id", "player.name", "position.name"], as_index=False)["total_minutes_played"].sum()\
            .sort_values(["team_name", "match_id", "player.name", "total_minutes_played"], ascending=[True, True, True, False ])\
            .drop_duplicates(["player.name", "match_id"])\
            .rename({"position.name": "match_position"}, axis=1)\
            .drop({"total_minutes_played"}, axis=1)

        #overall
        most_time_overall = self.lineups_df\
            .groupby(["team_name", "player.name", "position.name"], as_index=False)["total_minutes_played"].sum()\
            .sort_values(["team_name", "player.name", "total_minutes_played"], ascending=[True, True, False])\
            .drop_duplicates(["player.name"])\
            .rename({"position.name": "overall_position"}, axis=1)\
            .drop({"total_minutes_played"}, axis=1)

        self.positions = pd.merge(
            starting_positions, most_time,
            on=["team_name", "match_id", "player.name"], how="left")
        self.positions = pd.merge(
            self.positions, most_time_overall,
            on=["team_name", "player.name"], how="left")

    def getPlayTimeDF(
        self, agg_level="Match", team=None, match_id=None, player_name=None
    ):
        """Select playing time data frame you want.

        With no args, returns the playing time for each player in each match

        * agg_level = "Match", "Sum"
            If "Match", will return a row with each match for a player
            If "Sum", will sum values to get total minutes for competitions

        * team
            If passed a team name, will try to subset data

        * match_id
            If passed a match_id, will try to subset data

        * player_name
            If passed a player_name, will try to subset data
        """
        if agg_level == "Sum":
            play_time = self.player_play_time\
                .groupby(["team_name", "player.name"], as_index=False)[
                    'game_minutes_played', 'seconds_played',
                    'total_minutes_played']\
                .sum().sort_values("total_minutes_played", ascending=False)
        else:
            play_time = self.player_play_time

        if team is not None:
            play_time = play_time.loc[play_time["team_name"] == team]

        if (agg_level is None) & (match_id is not None):
            play_time = play_time.loc[play_time["match_id"] == match_id]

        if player_name is not None:
            play_time = play_time.loc[play_time["player.name"] == player_name]

        self.df_play_time = play_time

    def getPositionsDF(
        self, team=None, match_id=None, player_name=None
    ):
        """Select positions data frame you want.

        With no args, returns the positions for each player in each match

        * team
            If passed a team name, will try to subset data

        * match_id
            If passed a match_id, will try to subset data

        * player_name
            If passed a player_name, will try to subset data
        """
        df_positions = self.positions

        if team is not None:
            df_positions = (
                df_positions.loc[df_positions["team_name"] == team])

        if match_id is not None:
            df_positions = (
                df_positions.loc[df_positions["match_id"] == match_id])

        if player_name is not None:
            df_positions = (
                df_positions.loc[df_positions["player.name"] == player_name])

        self.df_positions = df_positions

    def lineupParse(self, data):

        lineups_df = pd.DataFrame()

        for match_id in data.df_lineups.match_id.unique():

            lineup_cols = [
                'country_id', 'jersey_number', 'match_id', 'player_id',
                'player_name', 'team_id', 'team_name']

            parse_merge_col = [
                'match_id', 'team_name', 'player.id', 'player.name']

            df_lineups = data.df_lineups.loc[
                data.df_lineups.match_id == match_id, lineup_cols]\
                .rename(
                    {"player_id": "player.id", "player_name": "player.name"},
                    axis=1)
            df_events = data.df_events.loc[
                data.df_events.match_id == match_id, :]

            if len(df_events) == 0:
                print("Completed Parse")
                return lineups_df

            match_df_temp = pd.DataFrame()

            for team_name in df_events.team_name.unique():

                filt_vec = (
                    (df_events["match_id"] == match_id) &
                    (df_events["team_name"] == team_name) &
                    (df_events["period"] <= 4))
                df_match = df_events.loc[filt_vec, :]

                # Need to establish TIME -
                # 1. Only keep 90 + 30' of ET (remove pks)
                # 1. Count up of total seconds in match
                # 2. Establish the game minute for subs and tactical switches
                last_minute = df_match["minute"].max()
                t0 = datetime.datetime.strptime("00:00:00.00", "%H:%M:%S.%f")

                df_match["ts"] = pd.to_datetime(
                    df_match["timestamp"], format="%H:%M:%S.%f")
                df_match["ts_seconds"] = df_match["ts"].apply(
                    lambda x: (x - t0).total_seconds())

                time_df = df_match.loc[
                    (df_match.type_name == "Half End"),
                    ("period", "ts")].groupby("period").first()

                time_df["ts_seconds"] = time_df["ts"].apply(
                    lambda x: (x - t0).total_seconds())

                time_df["ts_cum"] = time_df["ts_seconds"]\
                    .cumsum().shift().fillna(0)

                period_time_dict = time_df["ts_cum"].to_dict()

                df_match["total_time_period"] = df_match["period"]\
                    .map(period_time_dict)

                df_match["total_elapsed_time"] = (
                    df_match["ts_seconds"] + df_match["total_time_period"])

                last_second = df_match["total_elapsed_time"].max()

                tactics_names = [
                    "Starting XI", "Substitution", "Tactical Shift"]

                df_tactics = df_match.loc[
                    filt_vec & df_match["type_name"].isin(tactics_names), :]

                # Step 1: Get Starting Lineups

                for i, row in df_tactics.iterrows():
                    if row["type_name"] == "Starting XI":
                        temp_df = json_normalize(row["tactics_lineup"])
                        temp_df["match_id"] = row["match_id"]
                        temp_df["team_name"] = row["team_name"]
                        temp_df["tactics_formation"] = row["tactics_formation"]
                        self.formation = row["tactics_formation"]
                        temp_df["tactics_action"] = row["type_name"]
                        temp_df["start_minute"] = 0
                        temp_df["start_second"] = 0
                        temp_df["end_minute"] = np.nan
                        temp_df["end_second"] = np.nan
                        temp_df["sub_off"] = np.nan
                        temp_df["sub_minute"] = np.nan
                        temp_df["sub_second"] = row["total_elapsed_time"]
                        temp_df["active"] = True
                        temp_df["sub_outcome_name"] = np.nan
                        match_df_temp = match_df_temp.append(temp_df)

                    if row["type_name"] == "Substitution":
                        # First Update existing table to note sub_off
                        # and end minute and deactivate player
                        player_name = row["player_name"]

                        filt_vec = (
                            (match_df_temp["active"]) &
                            (match_df_temp["player.name"] == player_name))

                        match_df_temp.loc[filt_vec, ("sub_off")] = True
                        match_df_temp.loc[filt_vec,
                            ("sub_minute")] = row["minute"]
                        match_df_temp.loc[
                            filt_vec,
                            ("sub_second")] = row["total_elapsed_time"]
                        match_df_temp.loc[
                            filt_vec,
                            ("end_minute")] = row["minute"]
                        match_df_temp.loc[
                            filt_vec,
                            ("end_second")] = row["total_elapsed_time"]
                        match_df_temp.loc[
                            filt_vec,
                            ("sub_outcome_name")] = (
                                row["substitution_outcome_name"])
                        match_df_temp.loc[
                            filt_vec,
                            ("active")] = False


                        # Second Add a new row with the player
                        temp_df = pd.DataFrame({
                            "jersey_number": np.nan,
                            "player.id": row["substitution_replacement_id"],
                            'player.name': row["substitution_replacement_name"],
                            'position.id': row["position_id"],
                            'position.name': row["position_name"],
                            'match_id': row["match_id"],
                            'team_name': row["team_name"],
                            'tactics_action': "Substitution",
                            'tactics_formation': self.formation,
                            'start_minute': row["minute"],
                            'start_second': row["total_elapsed_time"],
                            'end_minute': np.nan,
                            'end_second': np.nan,
                            'sub_minute': row["minute"],
                            'sub_second': row["total_elapsed_time"],
                            'sub_off': False,
                            'active': True},
                            index=[0])
                        match_df_temp = match_df_temp.append(
                            temp_df, sort=False)

                    if row["type_name"] == "Tactical Shift":
                        # First Step is to mark the time to end current tactics
                        # and mark all current players inactive
                        match_df_temp.loc[
                            (match_df_temp["team_name"] == team_name) &
                            (match_df_temp["active"]), ("end_minute")] = row["minute"]
                        match_df_temp.loc[
                            (match_df_temp["team_name"] == team_name) &
                            (match_df_temp["active"]), ("end_second")] = row["total_elapsed_time"]
                        match_df_temp.loc[
                            match_df_temp["team_name"] == team_name, "active"] = False
                        # Then append new lineup
                        temp_df = json_normalize(row["tactics_lineup"])
                        temp_df["match_id"] = row["match_id"]
                        temp_df["team_name"] = row["team_name"]
                        temp_df["tactics_formation"] = row["tactics_formation"]
                        self.formation = row["tactics_formation"]
                        temp_df["tactics_action"] = row["type_name"]
                        temp_df["start_minute"] = row["minute"]
                        temp_df["start_second"] = row["total_elapsed_time"]
                        temp_df["end_minute"] = np.nan
                        temp_df["end_second"] = np.nan
                        temp_df["sub_off"] = np.nan
                        temp_df["sub_minute"] = np.nan
                        temp_df["sub_second"] = np.nan
                        temp_df["active"] = True
                        temp_df["sub_outcome_name"] = np.nan
                        match_df_temp = match_df_temp.append(
                            temp_df, sort=False)


                # Fill End Minute Values with the max value
                match_df_temp["end_minute"] = match_df_temp["end_minute"].fillna(last_minute)
                match_df_temp["end_second"] = match_df_temp["end_second"].fillna(last_second)
            del match_df_temp["jersey_number"]
            match_df_temp["player.id"] = match_df_temp["player.id"].astype(int)
            match_df_temp["position.id"] = match_df_temp["position.id"].astype(int)

            match_df_temp = pd.merge(
                df_lineups, match_df_temp, how="left",
                on=parse_merge_col)
            lineups_df = lineups_df.append(match_df_temp)

        lineups_df["game_minutes_played"] = (
            lineups_df["end_minute"] - lineups_df["start_minute"])
        lineups_df["seconds_played"] = (
            lineups_df["end_second"] - lineups_df["start_second"])
        lineups_df["total_minutes_played"] = (
            lineups_df["seconds_played"] / 60)
        return lineups_df
