import pandas as pd
import numpy as np
import pickle
import datetime
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler


class PassingModel():

    def __init__(self, data, lineups):

        self.df_passes = self.getPassDF(data, lineups)

    def runPassModel(
        self, pass_model_type="knn", agg_level="player",
        knn_model_file=None, expected_knn_file=None
    ):

        # Build model on df_pass_model copy of df_passes
        df_pass_model = self.df_passes.copy()
        timestamp = datetime.datetime.strftime(
            datetime.datetime.today(), "%Y_%m_%d_%H_%M_%S")

        if pass_model_type == "knn":
            simple_model_cols = [
                "id", "duration", "pass_length", "pass_angle",
                "location_origin_x", "location_origin_y",
                "location_dest_x", "location_dest_y"]
            df_knn = self.df_passes[simple_model_cols].set_index("id")
            df_completions = self.df_passes[["id", "pass_outcome_name"]]\
                .set_index("id")
            completion_array = np.array(np.where(
                df_completions["pass_outcome_name"] == "Complete", 1, 0))

            # Scale Data and Build Model
            min_max_scaler = MinMaxScaler()
            df_knn_norm = min_max_scaler.fit_transform(df_knn)
            n_neighbors = int(np.floor(len(df_knn) / 100)) + 1

            if knn_model_file is not None:
                nn_model = pickle.load(open("data/" + knn_model_file, 'rb'))
            else:
                nn_model = NearestNeighbors(
                    algorithm='ball_tree', n_neighbors=n_neighbors, p=2,
                    metric="euclidean", metric_params=None)
                nn_model.fit(df_knn_norm)
                pickle.dump(
                    nn_model, open("data/knn_model_file_" + timestamp, 'wb'))

            if expected_knn_file is not None:
                expected_pass_rate = pickle.load(
                    open("data/" + expected_knn_file, 'rb'))
            else:
                completion_array = np.array(
                    df_pass_model["pass_outcome_name_binary"])
                expected_pass_rate = []
                passes_per_ep = []
                print(f"Total Number of Passes: {len(df_knn)}")
                n = 0
                for row in df_knn_norm:
                    sim_passes = self.get_similar_passes(
                        row.reshape(1, -1), df_knn_norm, nn_model, cutoff=.2)
                    passes_per_ep.append(len(sim_passes))
                    expected_value = completion_array[sim_passes].mean()
                    expected_pass_rate.append(expected_value)
                    n += 1
                    if n % 5000 == 0:
                        print(f"Progress: {n} of {len(df_knn_norm)}")
                pickle.dump(
                    expected_pass_rate,
                    open('expected_knn_file_' + timestamp, 'wb'))

            df_pass_model["xP"] = expected_pass_rate

        elif pass_model_type == "box_grid":
            origin_box, dest_box = [], []
            for i, x in self.df_passes[[
                "location_origin_x", "location_origin_y",
                "location_dest_x", "location_dest_y"
            ]].iterrows():
                x, y = self.make_pass_grid(
                    x[0], x[1], x[2], x[3],
                    nrows=np.linspace(0, 120, 13), ncols=np.linspace(0, 80, 9))
                origin_box.append(x)
                dest_box.append(y)
                if i % 5000 == 0:
                    print(f"Pass {i} of {len(self.df_passes)}: {round(100*float(i)/len(self.df_passes),2)}% ")

            df_pass_model.loc[:, "origin_box"] = origin_box
            df_pass_model.loc[:, "dest_box"] = dest_box

            df_pass_model["pass_desc"] = list(zip(
                df_pass_model["origin_box"], df_pass_model["dest_box"]))

            # Get expected value (average) for each grid combination

            pass_grid_dict = df_pass_model\
                .groupby("pass_desc")["pass_outcome_name_binary"]\
                .mean().to_dict()

            df_pass_model.loc[:, ("xP")] = df_pass_model["pass_desc"]\
                .map(pass_grid_dict)

        if agg_level == "player":
            # df_pass_model['pass_direction'] = df_pass_model['pass_angle']\
            #     .apply(self.pass_direction)
            df_pass_model["position_name_parsed"] = (
                df_pass_model["position_name"].apply(
                    self.position_base_parser))
            df_pass_model["position_detail_parsed"] = (
                df_pass_model["position_name"].apply(
                    self.position_detail_parser))

            passing_model = df_pass_model\
                .groupby(["team_name", "player_name"], as_index=False)\
                .agg({
                    "position_name_parsed": "max",
                    "position_detail_parsed": "max",
                    "pass_outcome_name_binary": ["count", "sum"],
                    "xP": ["sum", "mean"]})

            passing_model.columns = [
                "Team", "Player", "Position", "Position_Detail",
                "Passes", "Completed", "xP", "xP_Mean"]

            passing_model["xP_Rating"] = (
                passing_model["Completed"] / passing_model["xP"])
            passing_model["comp_pct"] = (
                passing_model["Completed"] / passing_model["Passes"])

        elif agg_level == "team":

            passing_model = df_pass_model\
                .groupby(["team_name"], as_index=False)\
                .agg({
                    "pass_outcome_name_binary": ["count", "sum"],
                    "xP": ["sum", "mean"]})

            passing_model.columns = [
                "Team", "Passes", "Completed", "xP", "xP_Mean"]

            passing_model["xP_Rating"] = (
                passing_model["Completed"] / passing_model["xP"])
            passing_model["comp_pct"] = (
                passing_model["Completed"] / passing_model["Passes"])
        else:
            # self.passing_model = None
            print("Choose player or team")
            return None

        self.df_pass_model = df_pass_model
        self.passing_model = passing_model
        return passing_model

    def make_pass_grid(
        self, origin_x, origin_y, dest_x, dest_y, nrows=None, ncols=None
    ):

        if nrows is None:
            nrows = [18, 60, 102, 120]
        if ncols is None:
            ncols = [18, 40, 62, 80]

        o_x = np.searchsorted(nrows, origin_x, side="left")
        o_y = np.searchsorted(ncols, origin_y, side="left")

        d_x = np.searchsorted(nrows, dest_x, side="left")
        d_y = np.searchsorted(ncols, dest_y, side="left")

        origin_box = (o_x) * 4 + (o_y + 1)
        dest_box = (d_x) * 4 + (d_y + 1)

        return(origin_box, dest_box)

    def pass_direction(self, x):
        """
        According to statsbomb, pass_angle is between 0 (pass ahead)
        and pi (pass behind). Clockwise

        We divide the circle into 4 equal sections.
        Directions are forward, right, left, behind"""

        pi_div = np.pi / 4
        if (x <= pi_div) & (x >= -pi_div):
            return "Forward"
        elif (x > pi_div) & (x <= 3 * pi_div):
            return "Right"
        elif (x > 3 * pi_div) | (x < -3 * pi_div):
            return "Behind"
        else:
            return "Left"

    def position_base_parser(self, pos):

        # Midfield
        if "Center Midfield" in pos:
            return "Midfield"
        elif "Defensive Midfield" in pos:
            return "Midfield"
        elif "Attacking Midfield" in pos:
            return "Midfield"
        elif "Midfield" in pos:
            return "Midfield"

        # Defense
        elif "Wing Back" in pos:
            return "Defense"
        elif "Center Back" in pos:
            return "Defense"
        elif "Back" in pos:
            return "Defense"

        # Forward
        elif "Forward" in pos:
            return "Forward"
        elif "Striker" in pos:
            return "Forward"

        # Other
        elif "Wing" in pos:
            return "Forward"
        elif "Goalkeeper" in pos:
            return "Goalkeeper"
        else:
            return pos

    def position_detail_parser(self, pos):

        # Midfield
        if "Center Midfield" in pos:
            return "Midfield"
        elif "Defensive Midfield" in pos:
            return "Defensive Midfield"
        elif "Attacking Midfield" in pos:
            return "Attacking Midfield"
        elif "Midfield" in pos:
            return "Wide Midfield"

        # Defense
        elif "Wing Back" in pos:
            return "Wing Back"
        elif "Center Back" in pos:
            return "Center Back"
        elif "Back" in pos:
            return "Fullback"

        # Forward
        elif "Forward" in pos:
            return "Forward"
        elif "Striker" in pos:
            return "Forward"

        # Other
        elif "Wing" in pos:
            return "Winger"
        elif "Goalkeeper" in pos:
            return "Goalkeeper"
        else:
            return pos

    def get_similar_passes(self, p, df, model, cutoff=.2, n_top=5):
        dist, passes = model.kneighbors(
            p, n_neighbors=len(df), return_distance=True)
        return passes[0][1:np.searchsorted(dist[0], cutoff)]

    def getPassDF(self, df_events, lineups):

        pass_values = [
            'index', "match_id", 'duration', 'id', 'period', 'minute',
            'second', 'type_name', 'player_name', 'position_name', "team_name",
            'possession_team_name', 'possession', 'possession_team_id',
            'related_events', 'under_pressure', 'location',

            # Pass details
            'pass_aerial_won', 'pass_angle', 'pass_assisted_shot_id',
            'pass_backheel', 'pass_body_part_id', 'pass_body_part_name',
            'pass_cross', 'pass_deflected', 'pass_end_location',
            'pass_goal_assist', 'pass_height_id', 'pass_height_name',
            'pass_length', 'pass_outcome_id', 'pass_outcome_name',
            'pass_recipient_id', 'pass_recipient_name', 'pass_shot_assist',
            'pass_switch', 'pass_through_ball', 'pass_type_id',
            'pass_type_name']

        df_passes = df_events.loc[
            (df_events['type_name'].isin(['Pass'])) &
            (~df_events["pass_type_name"].isin(
                ["Goal Kick", "Corner", "Throw-in", "Free Kick", "Kick Off"])),
            pass_values]
        df_passes.reset_index(inplace=True)
        del df_passes["level_0"]

        df_passes["under_pressure"] = df_passes["under_pressure"].fillna(False)
        df_passes['pass_outcome_name'].fillna('Complete', inplace=True)

        for col in [
            "pass_backheel", "pass_cross", "pass_aerial_won",
            "pass_deflected", "pass_goal_assist", "pass_shot_assist",
            "pass_switch", "pass_through_ball"]:
            df_passes[col].fillna(False, inplace=True)

        # extract pass location data
        p_origin = pd.DataFrame(df_passes["location"].values.tolist(), columns=["location_origin_x", "location_origin_y"])
        p_dest = pd.DataFrame(df_passes["pass_end_location"].values.tolist(), columns=["location_dest_x", "location_dest_y"])
        df_passes = pd.concat([df_passes, p_origin, p_dest], axis=1)

        overall_positions = lineups[[
            "team_name", "player.name", "overall_position"
        ]].drop_duplicates().rename({
            "player.name": "player_name",
            "overall_position": "position_name"}, axis=1)

        pass_grid_cols = [
            "team_name", "player_name", "under_pressure", "pass_height_name",
            "pass_outcome_name", "pass_angle", "pass_length",
            "location_origin_x", "location_origin_y",
            "location_dest_x", "location_dest_y"]

        df_pass_model = df_passes[pass_grid_cols]
        df_pass_model = pd.merge(
            df_pass_model, overall_positions,
            on=["team_name", "player_name"], how="left")
        df_pass_model["pass_outcome_name_binary"] = np.where(
            df_pass_model["pass_outcome_name"] == "Complete", True, False)


        return df_pass_model
