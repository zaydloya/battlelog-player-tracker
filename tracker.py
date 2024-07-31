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
        player.get('persona').get('user').get('username')
        for player in server_data.get('message').get('SERVER_PLAYERS')
        if player.get('persona', {}).get('user', {}).get('presence', {}).get('playingMp', {}).get('role') == 4
    ]

    return {"spectators": spectators, "server_name": server_name}


async def get_all_spectators():
    servers = utils.load_servers()
    tasks = [get_server_spectators(server_url) for server_url in servers]
    results = await asyncio.gather(*tasks)
    for spectators in results:
        if isinstance(spectators, tuple):
            continue
        else:
            print(spectators)


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
            if player.get('personaId') == player_id:
                username = utils.get_player_name(player)
                role = utils.get_player_role(player)
                return {'player_name': username, 'server_name': server_name, 'role': role}


async def fetch_player(player_id: int):
    servers = utils.load_servers()
    tasks = [find_player(player_id, server_url) for server_url in servers]
    results = await asyncio.gather(*tasks)
    for result in results:
        if result:
            if result[0]:
                return result[1]
    return "Player not found in any server"


async def track_player(input_value: str):
    if not isinstance(input_value, str):
        return
    if utils.validate_url(input_value):
        is_valid, result = utils.is_valid_battlelog_url(input_value)
    else:
        is_valid, result = utils.is_valid_username(input_value)

    if not is_valid:
        return result

    player_id = int(result)
    return await fetch_player(player_id)


async def main():
    result = await track_player("SpectralSp")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
