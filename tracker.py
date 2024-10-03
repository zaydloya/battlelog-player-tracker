import utils
import asyncio
import aiohttp


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
        (utils.get_player_name(player), utils.get_player_url(player))
        for player in server_data.get('message').get('SERVER_PLAYERS')
        if utils.get_player_role(player) == "Spectator"
    ]

    if not spectators:
        return True, {"spectators": "Spectator could not be determined", "server_name": server_name,
                      "server_url": server_url}

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
    if not utils.validate_server_url(server_url):
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


async def get_players(server):
    async with aiohttp.ClientSession() as session:
        try:
            data = await fetch(session, utils.get_server_json_url(server))

            if data.get('type') == 'error':
                return []
            elif utils.check_if_players(data):
                return [(player, server, utils.get_server_name(data)) for player in
                        data.get('message').get('SERVER_PLAYERS')]

        except aiohttp.ClientResponseError as e:
            return []
        except Exception as e:
            return []


async def find_players(valid_players):
    servers = utils.load_servers()
    tasks = []
    for server in servers:
        tasks.append(get_players(server))

    active_players = await asyncio.gather(*tasks)
    active_players = [player for server_players in active_players if server_players is not None for player in
                      server_players]

    results = []

    for player_id, player_name in valid_players:
        found = False
        for player in active_players:
            if int(player[0].get('personaId')) == player_id:
                results.append((True, {
                    'username': utils.get_player_name(player[0]),
                    'role': utils.get_player_role(player[0]),
                    'player_url': utils.get_player_url(player[0]),
                    'server': player[1],
                    'server_name': player[2],
                }))
                found = True
                break
        if not found:
            results.append((False, {'error': "Player not found in any server"}))

    return results


async def validate(input_value: str):
    players = input_value.split(',')
    players = [player.strip() for player in players]
    valid = []
    results = []
    async with aiohttp.ClientSession() as session:
        for player in players:
            if not player:
                results.append((False, {'error': f"Please enter a valid username. {player}"}))
                continue
            if not isinstance(player, str):
                results.append((False, {'error': f"Invalid input type."}))
                continue
            if utils.validate_url(player):
                is_valid, result = await utils.is_valid_battlelog_url(player, session)
            else:
                is_valid, result = await utils.is_valid_username(player, session)

            if not is_valid:
                results.append((False, result))
            else:
                valid.append((int(result), player))

    return results, valid


async def track_player(input_value: str):
    validation_results, valid_players = await validate(input_value)
    tracked_players = await find_players(valid_players)
    return validation_results + tracked_players
