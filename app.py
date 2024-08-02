from flask import Flask, request, jsonify, send_from_directory
import asyncio
from tracker import track_player, get_server_spectators, get_all_spectators

app = Flask(__name__, static_folder='static')

# Serve the HTML file
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/track_player', methods=['POST'])
def track_player_route():
    data = request.json
    input_value = data.get('input_value')
    result = asyncio.run(track_player(input_value))
    print('track_player response:', result)
    return jsonify(result)

@app.route('/get_server_spectators', methods=['POST'])
def get_server_spectators_route():
    data = request.json
    server_url = data.get('server_url')
    result = asyncio.run(get_server_spectators(server_url))
    print('get_server_spectators response:', result)
    return jsonify(result)

@app.route('/get_all_spectators', methods=['POST'])
def get_all_spectators_route():
    result = asyncio.run(get_all_spectators())
    print(result)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)

