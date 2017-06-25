from __future__ import print_function
import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.identity = b'backend'
socket.connect('tcp://127.0.0.1:5556')
socket.send(b'HELO')
while True:
    client, req = socket.recv_multipart()
    req = req.decode()
    time.sleep(0.100) # simulate some work
    rep = eval(req)
    rep = '{}'.format(rep)
    rep = bytes(rep, 'utf-8')
    parts = (client, rep)
    print('sending back {}'.format(parts))
    socket.send_multipart(parts)
