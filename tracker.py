import requests
import utils


def get_server_spectators(server_url):
    is_available, result = check_server_availability(server_url)
    if not is_available:
        return False, result
    else:
        server_data = is_available

    if not check_if_spectators(server_data):
        return 0, "The server currently does not have any spectators"

    server_name = utils.get_server_name(server_data)

    spectators = [
        player.get('persona').get('user').get('username')
        for player in server_data.get('message').get('SERVER_PLAYERS')
        if player.get('persona', {}).get('user', {}).get('presence', {}).get('playingMp', {}).get('role') == 4
    ]

    return {"spectators": spectators, "server_name": server_name}


def get_all_spectators():
    servers = utils.load_servers()
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
    if not utils.is_url_valid(server_url):
        return False, "Invalid server URL provided."
    try:
        response = requests.get(utils.get_server_json_url(server_url))
        response.raise_for_status()
        data = response.json()

        if data.get('type') == 'error':
            return False, "Server can not be found"

        return data, "Server found successfully"
    except requests.exceptions.RequestException as e:
        return False, f"Request error: {str(e)}"
    except ValueError:
        return False, "Invalid JSON response from server"


get_server_spectators("https://battlelog.battlefield.com/bf4/servers/show/pc/c067dded-25ad-4b31-b1c2-f44072c635d0/bZ1-HARDCORE-ALL-MAPS-BANZORE-COM/")