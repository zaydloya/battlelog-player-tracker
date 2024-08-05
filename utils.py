import json
import re
import requests
import os
from dotenv import load_dotenv

current_dir = os.path.dirname(__file__)
os.chdir(current_dir)


def load_servers():
    with open('servers.json', 'r') as file:
        data = json.load(file)
    return [server['server_url'] for server in data]


def check_if_spectators(server_json: dict):
    spectators_count = server_json.get('message').get('SERVER_INFO').get('slots').get('8').get('current', 0)
    return spectators_count > 0


def check_if_players(server_json: dict):
    players_count = server_json.get('message').get('SERVER_PLAYERS', [])
    return bool(players_count)


def is_valid_username(username: str):
    load_dotenv()
    url = f'https://bf4db.com/api/player/{username}/search'
    params = {
        'api_token': os.getenv('API_TOKEN'),
        'exact': '1',
    }
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request('GET', url, headers=headers, params=params)
    data = response.json()
    for player in data.get('data'):
        if player['name'].lower() == username.lower():
            return True, player.get('id')
    if not data.get('data'):
        return False, "Player does not exist. Please try again."

    return False, "Invalid username provided."


def is_valid_battlelog_url(profile_url: str):
    load_dotenv()
    if validate_battlelog_url(profile_url):
        persona_id = get_id(profile_url)

        url = f'https://bf4db.com/api/player/{persona_id}'
        params = {
            'api_token': os.getenv('API_TOKEN'),
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.request('GET', url, headers=headers, params=params)
        data = response.json()
        if 'message' in data and data.get('message', None) or data.get('data').get(
                'name') == 'ERROR: Failed To Load Name':
            return False, "Invalid Battlelog URL provided"
        else:
            return True, data.get('data').get('player_id')
    else:
        return False, "Invalid Battlelog URL provided"


def get_server_json_url(server_url: str):
    if validate_server_url(server_url):
        return server_url + "/?json=1"


def get_server_name(server_json: dict):
    return remove_excess_spaces(
        server_json.get('message', {}).get('SERVER_INFO', {}).get('name', 'Unknown Server Name'))


def get_player_name(player_data: dict):
    return player_data.get('persona').get('user').get('username')


def get_player_role(player_data: dict):
    role = player_data.get('persona', {}).get('user', {}).get('presence', {}).get('playingMp', {}).get('role')
    role_map = {1: "Soldier", 2: "Commander", 4: "Spectator"}
    return role_map.get(role, "Unknown")


def get_player_url(player_data: dict):
    name = get_player_name(player_data)
    personaId = player_data.get('personaId')
    return f'https://battlelog.battlefield.com/bf4/soldier/{name}/stats/{personaId}/pc/'


def remove_excess_spaces(text: str):
    return re.sub(r'\s+', ' ', text).strip()


def get_id(profile_url: str):
    return profile_url.split('/')[7]


def validate_battlelog_url(profile_url: str):
    pattern = r'^https:\/\/battlelog\.battlefield\.com\/bf4\/soldier\/[^\/]+\/stats\/\d+\/pc\/$'
    return bool(re.match(pattern, profile_url))


def validate_server_url(server_url: str):
    pattern = r'^https:\/\/battlelog\.battlefield\.com\/bf4\/servers\/show\/pc\/.*'
    return bool(re.match(pattern, server_url))


def validate_url(url):
    return bool(re.match(r'^https?://', url))
