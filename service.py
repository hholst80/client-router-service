from __future__ import print_function
import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.identity = b'backend'
socket.connect('tcp://127.0.0.1:5556')
socket.send(b'HELO')
while True:
    client, expr = socket.recv_multipart()
    expr = expr.decode()
    value = eval(expr)
    response = '{}'.format(value)
    response = bytes(response, 'utf-8')
    parts = (client, response)
    print('sending back {}'.format(parts))
    socket.send_multipart(parts)
