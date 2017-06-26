from __future__ import print_function
import zmq
import os

context = zmq.Context()

frontend = context.socket(zmq.ROUTER)
frontend.setsockopt(zmq.ROUTER_MANDATORY, 1)
frontend.bind(os.environ.get('FRONTEND', 'tcp://*:5555'))

backend = context.socket(zmq.ROUTER)
backend.setsockopt(zmq.ROUTER_MANDATORY, 1)
backend.bind(os.environ.get('BACKEND', 'tcp://*:5556'))

poller = zmq.Poller()
poller.register(frontend, zmq.POLLIN)
poller.register(backend, zmq.POLLIN)

while True:
    events = poller.poll()
    for socket, event in events:
        if socket == backend:
            #service, _, client, response = backend.recv_multipart()
            parts = backend.recv_multipart(copy=True)
            print('from backend: {}'.format(parts))
            if len(parts) == 3:
                # This is a register call
                #print(dir(parts[2]))
                #assert parts[2].bytes == b'HELO'
                assert parts[2] == b'HELO'
                print('HELO from {}'.format(parts[0]))
            else:
                assert len(parts) == 4
                service, _, client, response = parts
                reply_parts = (client, b'', response)
                try:
                    frontend.send_multipart(reply_parts)
                except zmq.error.ZMQError:
                    print('Client {} went away. Dropping reply'.format(client))
        else:
            #client, _, service, args, kwargs = frontend.recv_multipart()
            parts = frontend.recv_multipart()
            print('from frontend: {}'.format(parts))
            try:
                client, _, service, command, args, kwargs = parts
                parts = (service, b'', client, command, args, kwargs)
                print('sending to backend: {}'.format(parts))
                backend.send_multipart(parts)
            except zmq.error.ZMQError:
                # No route to host?
                parts = (client, b'', b'Service unavailable')
                print('service unavailabe, notifying client.')
                frontend.send_multipart(parts)
