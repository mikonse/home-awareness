from threading import Thread

from flask import request, jsonify
from flask_api import FlaskAPI, status
from flask_cors import CORS

from config import config
import tracking

app = FlaskAPI(__name__)
cors = CORS(app, resources={r'/api/*': {'origins': '*'}})


@app.route('/api/tracking/')
def api_tracking_list():
    return tracking.get_current_users()


@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    if request.method == 'POST':
        try:
            data = request.get_json()
        except:
            return jsonify({'error': True}), status.HTTP_400_BAD_REQUEST
        config.update(data, full=True)
        print(config.serialize(full=False))
        return jsonify(config.serialize_json(full=True)), status.HTTP_200_OK

    # GET
    return config.serialize_json(full=True)


def main():
    thread = Thread(target=app.run, kwargs={'host': 'localhost', 'port': 8000, 'debug': True, 'use_reloader': False})
    thread.start()


if __name__ == '__main__':
    main()
