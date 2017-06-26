from __future__ import print_function
import os
import zmq
#import msgpack as m
import pickle

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.identity = b'client'
address = os.environ.get('FRONTEND', 'tcp://127.0.0.1:5555')
socket.connect(address)
service = b'backend'
command = b'open'
args = pickle.dumps(['./test.sh'])
kwargs = pickle.dumps({})
parts = (service, command, args, kwargs)
socket.send_multipart(parts)
identity = socket.recv()
print('response: {}'.format(identity))

command = b'stdout'
args = pickle.dumps([])
kwargs = pickle.dumps({})
parts = (identity, command, args, kwargs)
socket.send_multipart(parts)
response = socket.recv()
response = pickle.loads(response)
print('stdout: {}'.format(response.decode().strip()))

command = b'kill'
args = pickle.dumps([])
kwargs = pickle.dumps({})
parts = (identity, command, args, kwargs)
socket.send_multipart(parts)
response = socket.recv()
response = pickle.loads(response)
print('kill: {}'.format(response))
