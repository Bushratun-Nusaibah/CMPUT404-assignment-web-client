#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse, urlencode

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    
    def get_host_port(self,url):

        """
        Gets the host and port of the url
        parameter: url (url that needs to be parsed)
        returns: host and the port 
        """

        parse_url = urlparse(url)
        get_host = parse_url.hostname
        get_port = parse_url.port

        #if host is nor found raise an exception
        if get_host is None:
            raise Exception("Could not resolve host.")


        #connect to port 80 if port not found
        if get_port is None:
            get_port = 80

       
        return get_host, get_port

    def get_path(self, url):
        '''
        gets the path of the parsed url 
        parameter: url
        Returns: path
        '''

        path = url.replace(urlparse(url).scheme+"://"+urlparse(url).netloc,"")

        if len(path) == 0:
            path = "/"

        return path


    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        '''
        get the code from the parameter data 
        Returns: code (an int value) 
        '''

        code = data.splitlines()[0].split(" ")[1]
        code = int(code)

        return code

    def get_headers(self,data):
        return None

    def get_body(self, data):
        '''
        get the body from the parameter data 
        Returns: body
        '''

        body = data.split("\r\n\r\n")
        return body[1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):


        host, port = self.get_host_port(url)
        path = self.get_path(url)

        #connect to the host and the port 
        self.connect(host, port)

        request = "GET %s HTTP/1.1\r\n" % path
        headerHost = "Host: %s\r\n" % host
        connectionHeader = "Connection: close\r\n"
        endHeader = "\r\n"
    
        getRequest = request+headerHost+connectionHeader+endHeader

        
        # send the request 
        self.sendall(getRequest)
        response = self.recvall(self.socket)

        self.close()

        code = self.get_code(response)
        body = self.get_body(response)

        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):

        argContent = ""

        # get the arguemnt 
        if args is not None:
            argContent = urlencode(args)


        # get the length of the content 
        if(args!=None):
            argContent_len = len(argContent)
        else:
            argContent_len = 0

        # host and the port     
        host, port = self.get_host_port(url)

        # path of the url
        path = self.get_path(url)


        request = "POST %s HTTP/1.1\r\n" % path
        headerHost = "Host: %s\r\n" % host
        connectionHeader = "Connection: close\r\n"
        headerType = "Content-Type: application/x-www-form-urlencoded\r\n"


        argContent_len_header = "Content-Length: %d\r\n" % argContent_len
        endHeader = "\r\n"

        postRequest = request+headerHost+headerType+connectionHeader+argContent_len_header+endHeader+argContent


        self.connect(host, port)
        self.sendall(postRequest)

        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        self.close()
        
        
        return HTTPResponse(code, body)
        
    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
