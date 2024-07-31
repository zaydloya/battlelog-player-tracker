import json
import re

import requests
from bs4 import BeautifulSoup


def load_servers():
    with open('servers.json', 'r') as file:
        data = json.load(file)
    return [server['server_url'] for server in data]


def check_if_spectators(server_json):
    if server_json.get('message').get('SERVER_INFO').get('slots').get('8').get('current') == 0:
        return False
    return True


def is_valid_username(username: str):
    page = requests.get(f"https://battlelog.battlefield.com/bf4/user/{username}/")
    if BeautifulSoup(page.text, 'html.parser').title.string.strip() == ("404 That page doesn't exist Battlelog\n / "
                                                                        "Battlefield 4"):
        return False
    return True


def get_server_json_url(server_url):
    if is_url_valid(server_url):
        return server_url + "/?json=1"


def get_server_name(server_json):
    return remove_excess_spaces(
        server_json.get('message', {}).get('SERVER_INFO', {}).get('name', {'Unknown Server Name'}).strip())


def remove_excess_spaces(text):
    return re.sub(r'\s+', ' ', text).strip()


def is_url_valid(server_url):
    pattern = r'^https:\/\/battlelog\.battlefield\.com\/bf4\/servers\/show\/pc\/.*'
    return bool(re.match(pattern, server_url))
