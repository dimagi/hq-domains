#!/usr/bin/env python

#
# Code taken mostly from the python std lib docs, section 21.17
#

import sys, SocketServer

#
# Couldn't get server.shutdown() to work from inside handle();
# some threading problem (I think it needs to be called from
# another thread). Used this global variable trick instead.
#

_g_shutdown = False
_g_shutdown_string = "SHUTDOWN"

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(4096).strip()
        print "{0}: {1}".format(self.client_address[0], self.data)
        self.request.send("200")
        if self.data ==  _g_shutdown_string:
            global _g_shutdown
            _g_shutdown = True

if __name__ == "__main__":

    if len(sys.argv) == 2:
        _g_shutdown_string = sys.argv[1]

    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    while True:
        server.handle_request()
        if _g_shutdown:
            break



