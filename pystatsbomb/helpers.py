import collections


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
