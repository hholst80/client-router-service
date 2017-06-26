from __future__ import print_function
import time
import threading
import subprocess
import os
import zmq
import pickle

class Controller(threading.Thread):
    def __init__(self, identity, obj):
        super(Controller, self).__init__()
        self.identity = identity
        self.obj = obj

    def run(self):
        context = zmq.Context()
        spawn = context.socket(zmq.REQ)
        spawn.identity = self.identity
        spawn.connect('tcp://127.0.0.1:5556')
        print('>>> send HELO')
        spawn.send(b'HELO')
        obj = self.obj
        done = False
        print('>>> Main loop')
        while not done:
            client, command, args, kwargs = spawn.recv_multipart()
            print('command: {}'.format(command))
            args = pickle.loads(args)
            kwargs = pickle.loads(kwargs)

            if command == b'open':
                assert obj is None
                kwargs.update(
                    {
                        'stdout': subprocess.PIPE,
                        'stderr': subprocess.PIPE,
                    }
                )
                obj = subprocess.Popen(args, **kwargs)
                identity = '{}-{}'.format('backend', obj.pid)
                identity = bytes(identity, 'utf-8')
                response = identity
                controller = Controller(identity, obj)
                controller.start()
                obj = None
            elif command == b'stdout':
                assert obj is not None
                response = pickle.dumps(obj.stdout.read())
            elif command == b'stderr':
                assert obj is not None
                response = pickle.dumps(obj.stderr.read())
            elif command == b'kill':
                assert obj is not None
                done = True
                try:
                    obj.kill()
                    response = pickle.dumps(None)
                except Exception as e:
                    response = pickle.dumps(e)
            else:
                response = pickle.dumps(ValueError())
            print('sending back {}'.format((client, response)))
            spawn.send_multipart((client, response))


if __name__ == '__main__':
    controller = Controller(b'backend', None)
    controller.start()
    controller.join()
