# -*- coding: utf-8 -*-
from .helpers import getMatchDictChildren, getLineupParse, flatten
import json
import os
import requests
import pandas as pd


class Client():
    """Connect to the data source and start getting data. Source should
    point to the folder with the data inside"""

    def __init__(self, source=None):
        self.source = source

    def get_competitions(self):

        self.competitions = self.get_data(
            source_dir=self.source,
            data_dir=None,
            data_name='competitions',
            ext='.json')

    def get_matches(self, comp_id=None):
        self.matches = []

        competition_list = self.get_competition_list(comp_id=comp_id)
        for comp in competition_list:
            self.matches = self.matches + self.get_data(
                source_dir=self.source,
                data_dir='matches',
                data_name=str(comp),
                ext='.json')

    def get_lineups(self, match_id=None):
        self.lineups = []

        match_ids = self.get_match_ids(match_id=match_id)
        for match in match_ids:
            res = self.get_data(
                source_dir=self.source,
                data_dir='lineups',
                data_name=str(match),
                ext='.json')
            # Need to add match_id to lineup
            res[0]['match_id'] = match
            res[1]['match_id'] = match

            self.lineups = self.lineups + res

    def get_events(self, match_id=None):
        self.events = []

        match_ids = self.get_match_ids()
        for match in match_ids:
            res = self.get_data(
                source_dir=self.source,
                data_dir='events',
                data_name=str(match),
                ext='.json')

            for event in res:
                event['match_id'] = match
            self.events = self.events + res

    def get_competition_list(self, comp_id=None):
        if comp_id is not None:
            comp_id_list = [comp_id]
            comp_ids = [
                comp['competition_id'] for comp in self.competitions
                if comp['competition_id'] in comp_id_list]
        else:
            comp_ids = [comp['competition_id'] for comp in self.competitions]
        return comp_ids

    def get_match_ids(self, match_id=None):
        if match_id is not None:
            match_id_list = [match_id]
            match_ids = [
                match['match_id'] for match in self.matches
                if match['match_id'] in match_id_list]
        else:
            match_ids = [match['match_id'] for match in self.matches]
        return match_ids

    def get_data(
        self, source_dir=None, data_dir=None, data_name=None, ext=None
    ):
        """This function gives you the option to open from a local file or the
        github repository for free data"""
        if source_dir is None:
            source_dir = (
                'https://raw.githubusercontent.com/statsbomb/' +
                'open-data/master/data/')
            if data_dir is None:
                pass
            else:
                source_dir = os.path.join(source_dir, data_dir)

            f = requests.get(source_dir + '/' + data_name + ext)
            return json.loads(f.text)

        else:
            if data_dir is None:
                pass
            else:
                source_dir = os.path.join(source_dir, data_dir)
            with open(
                    os.path.join(source_dir, data_name + ext), 'r') as f:
                return json.load(f)

    def get_all_sb_data(self, comp_id=None, match_id=None, toPandas=True):

        # Get all competitions
        self.get_competitions()
        self.get_matches(comp_id=comp_id)
        self.get_lineups(match_id=match_id)
        self.get_events(match_id=match_id)

        if toPandas is True:
            # Competitions
            self.df_competitions = pd.DataFrame(self.competitions)

            # Matches
            self.df_matches = pd.DataFrame(
                [getMatchDictChildren(match) for match in self.matches])

            # Lineups
            lineup_list = [getLineupParse(l) for l in self.lineups]
            lineup_flat_list = [
                player for team in lineup_list for player in team]
            self.df_lineups = pd.DataFrame(lineup_flat_list)

            # Events
            flat_events = [flatten(e) for e in self.events]
            ekeys = [list(e.keys()) for e in flat_events]
            ekeys_all = [i for s in ekeys for i in s]
            set_all_keys = set(ekeys_all)
            self.df_events = pd.DataFrame(flat_events, columns=set_all_keys)
