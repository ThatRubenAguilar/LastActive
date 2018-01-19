from flask import Flask, jsonify
from flask_api import status
import logging
from tcpdumpactivitymonitor import TcpDumpActivityMonitor
from config import Config
import time
import asyncio
from contextlib import closing

app = Flask(__name__)
config = Config("lastactive.config")
last_active_monitor = TcpDumpActivityMonitor(port=config.tcpdump_port(), net_interface=config.tcpdump_network_interface())


@app.route('/last_active_utc', methods=['GET'])
def get_last_active_utc():
    last_active_utc = time.gmtime(last_active_monitor.last_active_time())
    formatted_utc = time.strftime('%a, %d %b %Y %H:%M:%S GMT', last_active_utc)
    rv = {"last_active_utc": formatted_utc}
    return app.make_response((jsonify(rv), status.HTTP_200_OK))


@app.route('/last_active_time', methods=['GET'])
def get_last_active_time():
    last_active_time = last_active_monitor.last_active_time()
    rv = {"last_active_time": last_active_time}
    return app.make_response((jsonify(rv), status.HTTP_200_OK))


async def launch_flask_async():
    launch_flask()


def launch_flask():
    app.logger.setLevel(logging.INFO)
    app.run(host='127.0.0.1', port=5002)


if __name__ == '__main__':
    try:
        last_active_monitor.start_monitoring()
        launch_flask()
    except KeyboardInterrupt:
        pass
    finally:
        last_active_monitor.stop_monitoring()
