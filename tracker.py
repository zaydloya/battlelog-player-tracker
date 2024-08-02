import utils
import asyncio
import aiohttp
import time


async def fetch(session, url: str):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()


async def get_server_spectators(server_url: str):
    is_available, result = await check_server_availability(server_url)
    if not is_available:
        return False, result
    else:
        server_data = result

    server_name = utils.get_server_name(server_data)

    if not utils.check_if_spectators(server_data):
        return 0, "The server currently does not have any spectators"

    spectators = [
        utils.get_player_name(player)
        for player in server_data.get('message').get('SERVER_PLAYERS')
        if utils.get_player_role(player) == "Spectator"
    ]

    if not spectators:
        return True, {"spectators": "Spectator could not be determined", "server_name": server_name, }

    return True, {"spectators": spectators, "server_name": server_name, "server_url": server_url}


async def get_all_spectators():
    servers = utils.load_servers()
    tasks = [get_server_spectators(server_url) for server_url in servers]
    results = await asyncio.gather(*tasks)

    formatted_results = []

    for result in results:
        success, data = result
        if success:
            formatted_results.append({
                'server_name': data.get('server_name', 'Undefined'),
                'server_url': data.get('server_url'),
                'spectators': data.get('spectators', [])
            })

    return formatted_results


async def check_server_availability(server_url: str):
    if not utils.validate_url(server_url):
        return False, "Invalid server URL provided."
    try:
        async with aiohttp.ClientSession() as session:
            data = await fetch(session, utils.get_server_json_url(server_url))

        if data.get('type') == 'error':
            return False, "Server can not be found"

        return True, data
    except aiohttp.ClientError as e:
        return False, f"Request error: {str(e)}"
    except ValueError:
        return False, "Invalid JSON response from server"


async def find_player(player_id: int, server_url):
    is_available, result = await check_server_availability(server_url)
    if not is_available:
        return False, result
    else:
        server_data = result

    server_name = utils.get_server_name(server_data)

    if utils.check_if_players(server_data):
        for player in server_data.get('message').get('SERVER_PLAYERS'):
            if int(player.get('personaId')) == player_id:
                username = utils.get_player_name(player)
                role = utils.get_player_role(player)
                return True, {'player_name': username, 'server_name': server_name, 'server_url': server_url, 'role': role}

    return False, "Player not found in any server"


async def fetch_player(player_id: int):
    servers = utils.load_servers()
    tasks = [find_player(player_id, server_url) for server_url in servers]
    results = await asyncio.gather(*tasks)
    for result in results:
        if result[0]:
            return result[1]
    return False, "Player not found in any server"


async def track_player(input_value: str):
    if not input_value:
        return False, "Please enter a valid username."
    if not isinstance(input_value, str):
        return
    if utils.validate_url(input_value):
        is_valid, result = utils.is_valid_battlelog_url(input_value)
    else:
        print(utils.is_valid_username(input_value))
        is_valid, result = utils.is_valid_username(input_value)

    if not is_valid:
        return result

    player_id = int(result)
    return await fetch_player(player_id)

asyncio.run(get_all_spectators())