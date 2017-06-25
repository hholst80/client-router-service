from __future__ import print_function
import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.identity = b'client'
socket.connect('tcp://127.0.0.1:5555')
parts = [b'backend', b'1*2*3']
socket.send_multipart(parts)
response = socket.recv()
print('response: {}'.format(response))
