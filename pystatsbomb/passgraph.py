import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import linear_kernel
from sklearn.preprocessing import StandardScaler
from scipy.sparse import csr_matrix
import networkx as nx


class graph():

    def __init__(
        self, df, team_name, match_id, pass_cols=None,
        max_minute=70, until_first_sub=True
    ):

        # Store some parameters
        self.team_name = team_name
        self.match_id = match_id

        if pass_cols is None:
            self.pass_cols = [
                "player_name", "pass_recipient_name", "position_name"]
        else:
            self.pass_cols = pass_cols

        df_completed_passes = df.loc[
            (df["pass_outcome_name"] == "Complete") &
            (df["match_id"] == self.match_id) &
            (df["team_name"] == self.team_name), self.pass_cols]
        df_completed_passes.loc[:, "weight"] = 1
        df = df_completed_passes\
            .groupby(["player_name", "pass_recipient_name"], as_index=False)\
            .agg({"weight": "sum"})
        df_pos = df_completed_passes\
            .groupby(["player_name"], as_index=False)\
            .agg({"position_name": "max"})

        df = pd.merge(df, df_pos, on="player_name", how="left")

        position_x_y = self.position_map()
        df["pos_x_y"] = df["position_name"].map(position_x_y)
        df["x"] = df["pos_x_y"].apply(lambda x: x[0])
        df["y"] = df["pos_x_y"].apply(lambda x: x[1])

        self.df = df

        # Get list of unique players for nodes
        self.unique_players = list(set(
            df["player_name"]).union(df["pass_recipient_name"]))

        # Check if the DF is null
        if len(self.df) == 0:
            print("No passes for team and match")
            raise

        # Build the Graph
        g = nx.DiGraph()

        for i, row in self.df.iterrows():
            g.add_node(
                node_for_adding=row["player_name"],
                player_name=row["player_name"],
                position=row["position_name"],
                loc=(row["x"], row["y"]))

        g.add_weighted_edges_from(
            zip(
                df["player_name"],
                df["pass_recipient_name"],
                df["weight"]))

        self.g = g

    def degree_centrality(self):
        """
        The degree centrality is the number of neighbors divided by
        all possible neighbors that it could have.
        Will return a sorted list of players with their values
        """
        centrality = sorted(
            nx.degree_centrality(g).items(),
            key=lambda kv: kv[1], reverse=True)

        return centrality




    def position_map():

        position_x_y = {
            # GK
            'Goalkeeper': (10, 40),

            # Defense
            'Left Back': (30, 70),
            'Left Center Back': (30, 50),
            'Center Back': (30, 40),
            'Right Back': (30, 10),
            'Right Center Back': (30, 30),
            'Left Wing Back': (40, 70),
            'Right Wing Back': (40, 10),

            # DM
            'Left Defensive Midfield': (50, 50),
            'Center Defensive Midfield': (50, 40),
            'Right Defensive Midfield': (50, 30),

            # CM
            'Left Midfield': (60, 70),
            'Left Center Midfield': (60, 50),
            'Center Midfield': (60, 40),
            'Right Center Midfield': (60, 30),
            'Right Midfield': (60, 10),

            # AMD
            'Left Attacking Midfield': (70, 50),
            'Center Attacking Midfield': (70, 40),
            'Right Attacking Midfield': (70, 30),

            # FWD
            'Left Center Forward': (90, 50),
            'Center Forward': (90, 40),
            'Right Center Forward': (90, 30),

            # Wing/SS
            'Left Wing': (70, 70),
            'Right Wing': (70, 10),
            'Secondary Striker': (80, 35)}
        return position_x_y
