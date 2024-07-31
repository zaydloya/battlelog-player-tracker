import re
import requests
import json
from bs4 import BeautifulSoup


def load_servers():
    with open('servers.json', 'r') as file:
        data = json.load(file)
    return [server['server_url'] for server in data]


def get_server_spectators(server_url):
    is_available, result = check_server_availability(server_url)
    if not is_available:
        return False, result
    else:
        server_data = is_available

    if not check_if_spectators(server_data):
        return 0, "The server currently does not have any spectators"

    server_name = get_server_name(server_data)

    spectators = [
        player.get('persona').get('user').get('username')
        for player in server_data.get('message').get('SERVER_PLAYERS')
        if player.get('persona', {}).get('user', {}).get('presence', {}).get('playingMp', {}).get('role') == 4
    ]

    return {"spectators": spectators, "server_name": server_name}


def get_all_spectators():
    servers = load_servers()
    for server_url in servers:
        spectators = get_server_spectators(server_url)
        if isinstance(spectators, tuple):
            continue
        else:
            print(spectators)


def check_if_spectators(server_json):
    if server_json.get('message').get('SERVER_INFO').get('slots').get('8').get('current') == 0:
        return False
    return True


def check_server_availability(server_url):
    if not is_url_valid(server_url):
        return False, "Invalid server URL provided."
    try:
        response = requests.get(get_server_json_url(server_url))
        response.raise_for_status()
        data = response.json()

        if data.get('type') == 'error':
            return False, "Server can not be found"

        return data, "Server found successfully"
    except requests.exceptions.RequestException as e:
        return False, f"Request error: {str(e)}"
    except ValueError:
        return False, "Invalid JSON response from server"

def is_valid_username(username : str):
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

get_server_spectators("https://battlelog.battlefield.com/bf4/servers/show/pc/c067dded-25ad-4b31-b1c2-f44072c635d0/bZ1-HARDCORE-ALL-MAPS-BANZORE-COM/")