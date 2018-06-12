# -*- coding: utf-8 -*-
from . import helpers
import json
import os
import requests


def get_hmm():
    """Get a thought."""
    return 'hmmm...'


def hmm():
    """Contemplation..."""
    if helpers.get_answer():
        print(get_hmm())


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

    def get_matches(self):
        self.matches = []

        competition_list = self.get_competition_list()
        for comp in competition_list:
            self.matches = self.matches + self.get_data(
                source_dir=self.source,
                data_dir='matches',
                data_name=str(comp),
                ext='.json')

    def get_lineups(self, match_id=None):
        self.lineups = []

        match_ids = self.get_match_ids()
        for match in match_ids:
            self.lineups = self.lineups + self.get_data(
                source_dir=self.source,
                data_dir='lineups',
                data_name=str(match),
                ext='.json')

    def get_events(self, match_id=None):
        self.events = []

        match_ids = self.get_match_ids()
        for match in match_ids[0:1]:
            self.events = self.events + self.get_data(
                source_dir=self.source,
                data_dir='events',
                data_name=str(match),
                ext='.json')

    def get_competition_list(self):
        return [comp['competition_id'] for comp in self.competitions]

    def get_match_ids(self):
        return [match['match_id'] for match in self.matches]

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
