"""
Wrapper to Docker Attach API
"""

import struct
from socket import timeout
from docker.utils.socket import read, read_exactly, SocketError


def attach(docker_client, container, stdout=True, stderr=True, logs=False):
    headers = {
        "Connection": "Upgrade",
        "Upgrade": "tcp"
    }

    query_params = {
        "stdout": 1 if stdout else 0,
        "stderr": 1 if stderr else 0,
        "logs": 1 if logs else 0,
        "stream": 1,
        "stdin": 0,
    }

    api_client = docker_client.api

    url = "{}/containers/{}/attach".format(api_client.base_url, container.id)

    response = api_client._post(url, headers=headers, params=query_params, stream=True)
    socket = api_client._get_raw_response_socket(response)

    return _read_socket(socket)


def _read_socket(socket):
    while True:

        try:

            payload_type, payload_size = _read_header(socket)
            if payload_size < 0:
                break

            for data in _read_payload(socket, payload_size):
                yield payload_type, data

        except timeout:
            pass
        except SocketError:
            break


def _read_payload(socket, payload_size):
    remaining = payload_size
    while remaining > 0:

        data = read(socket, remaining)
        if data is None:
            continue

        if len(data) == 0:
            break

        remaining -= len(data)
        yield data


def _read_header(socket):
    data = read_exactly(socket, 8)

    return struct.unpack('>BxxxL', data)
