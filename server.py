#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

class MyWebServer(socketserver.BaseRequestHandler):

    def send_invalid_http_request(self, http_request):
        if len(http_request) != 3 or http_request[0] != 'GET':
            content = '''
                <html>
                    <body>
                        <h2></h2><h1>405 Method Not Allowed</h1>
                    </body>
                </html>'''
            msg = 'HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/html\r\nContent-Length: {}\r\n\r\n'.format(len(content)) + content
            self.request.sendall(msg.encode())

    def serve_file(self, mimetype, root, path, msg):
        content = open(root + path).read()
        msg = msg.format(mimetype, len(content)) + content
        self.request.sendall(msg.encode())

    def handle(self):
        self.data = self.request.recv(1024).strip()
        data = self.data.decode().split('\r\n')
        http_request = data[0].split()
        
        # find the host address
        host = None
        i = 0
        for datum in data:
            if datum.startswith('Host: '):
                host = 'http://' + datum[6:]
                break
        
        # serve error msg if invalid http_request or not a GET request
        self.send_invalid_http_request(http_request)
        
        path = http_request[1]
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'www')

        # the possibilities are if it's a file, a directory, or invalid
        if os.path.isfile(root + os.path.abspath(path)):
            # if the path is a file
            # HTTP 200 OK
            msg = 'HTTP/1.1 200 OK\r\nContent-Type: {}\r\nContent-Length: {}\r\n\r\n'

            # MIME type for css
            if path.endswith('.css'):
                self.serve_file('text/css', root, path, msg)
            elif path.endswith('.html'):
                self.serve_file('text/html', root, path, msg)
        elif os.path.isdir(root + os.path.abspath(path)):
            # HTTP 301 Redirect
            if not path.endswith('/'):
                new_path = host + path + '/'
                msg = 'HTTP/1.1 301 Moved Permanently\r\nLocation: {}\r\n\r\n'
                msg = msg.format(new_path)
                self.request.sendall(msg.encode())
            
            # HTTP 200 OK
            content = open(os.path.join(root + path, 'index.html')).read()
            msg = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {}\r\n\r\n'
            msg = msg.format(len(content)) + content
            self.request.sendall(msg.encode())
        else:
            # not a file or a directory
            msg = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\nContent-Length: {}\r\n\r\n'
            content = '''
                <html>
                    <body>
                        <h2></h2><h1>404 Not Found</h1> The requested URL was not found on this server.
                    </body>
                </html>'''
            msg = msg.format(len(content)) + content
            self.request.sendall(msg.encode())



        # print ("Got a request of: %s\n" % data)
        # print(http_request)
        # self.request.sendall(bytearray("OK this is a test",'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
