import requests
import utils
import asyncio
import aiohttp
import time


async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()


async def get_server_spectators(server_url):
    is_available, result = await check_server_availability(server_url)
    if not is_available:
        return False, result
    else:
        server_data = is_available

    if not utils.check_if_spectators(server_data):
        return 0, "The server currently does not have any spectators"

    server_name = utils.get_server_name(server_data)

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


async def check_server_availability(server_url):
    if not utils.is_url_valid(server_url):
        return False, "Invalid server URL provided."
    try:
        async with aiohttp.ClientSession() as session:
            data = await fetch(session, utils.get_server_json_url(server_url))

        if data.get('type') == 'error':
            return False, "Server can not be found"

        return data, "Server found successfully"
    except aiohttp.ClientError as e:
        return False, f"Request error: {str(e)}"
    except ValueError:
        return False, "Invalid JSON response from server"


time1 = time.time()
asyncio.run(get_all_spectators())
print(time.time() - time1)