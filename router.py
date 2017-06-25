from __future__ import print_function
import zmq

context = zmq.Context()

frontend = context.socket(zmq.ROUTER)
frontend.setsockopt(zmq.ROUTER_MANDATORY, 1)
frontend.bind('tcp://*:5555')

backend = context.socket(zmq.ROUTER)
backend.setsockopt(zmq.ROUTER_MANDATORY, 1)
backend.bind('tcp://*:5556')

poller = zmq.Poller()
poller.register(frontend, zmq.POLLIN)
poller.register(backend, zmq.POLLIN)

while True:
    events = poller.poll()
    for socket, event in events:
        if socket == backend:
            parts = backend.recv_multipart()
            print('from backend: {}'.format(parts))
            if len(parts) == 3:
                # This is a register call
                assert parts[2] == b'HELO'
                print('HELO from {}'.format(parts[0]))
            else:
                assert len(parts) == 4
                parts = (parts[2], b'', parts[3])
                frontend.send_multipart(parts)
        else:
            parts = frontend.recv_multipart()
            print('from frontend: {}'.format(parts))
            assert len(parts) == 4
            send_parts = (parts[2], b'', parts[0], parts[3])
            try:
                backend.send_multipart(send_parts)
            except zmq.error.ZMQError:
                # No route to host?
                reply_parts = (parts[0], b'', b'Service unavailable')
                frontend.send_multipart(reply_parts)
