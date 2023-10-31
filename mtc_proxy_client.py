import socket

import time, sys

from _thread import *

import json

 

class MTCProxyClient:

    def __init__(self,

                 shopfloor_uid, client_uid,

                 server_address, server_port,

                 user_uid="mtconnect", pass_key='mtconnect'

                ):

        self.server_address = server_address

        self.server_port = server_port

        self.shopfloor_uid = shopfloor_uid

        self.client_uid = client_uid

        self.user_uid = user_uid

        self.pass_key = pass_key

        self.socket = None

 

    def cleanup(self):

        self.socket.close()

        self.socket = None;

        sys.exit()

 

    def connect_to_proxy_server(self):

        self.socket = socket.socket()

 

        print('Waiting for connection')

        try :

            self.socket.connect((self.server_address, self.server_port))

        except socket.error as e:

            print(str(e))

            return False, "Connection to Server failed"

 

        return True, "Success"

 

    def send_authention_request(self, agent_uid):

        auth_json = {  "user_uid": self.user_uid,

                       "pass_key": self.pass_key,

                       "shopfloor_uid": self.shopfloor_uid,

                       "client_uid" : self.client_uid,

                       "agent_uid": agent_uid }

 

        status, msg_str = self.send_json_msg(auth_json)

        if status == False:

            return status, msg_str

 

        status, json_dict = self.recv_json_msg()

        if status == False:

            return status, json_dict

 

        if json_dict['status'] == True :

             return True, "Authentication Success"

        else:

             return False, json_dict["reason"]

 

    def send_json_msg(self, json_dict):

        msg_str = json.dumps(json_dict)

        #msg_str = str(json_dict)

        return self.send_msg(msg_str)

 

    def send_msg(self, msg_str):

       try:

           data = msg_str.encode('utf-8')

           self.socket.send(data)

           print("Sent msg: {}".format(msg_str))

       except socket.error as e:

            print(str(e))

            return False, "Send message failed"

       return True, msg_str

 

    def recv_json_msg(self):

        status, msg_str = self.recv_msg()

        if status != True:

            return status, { "Error" : msg_str }

 

        json_dict = json.loads(msg_str)

        return True, json_dict

 

    def recv_msg(self):

       try:

           data = self.socket.recv(1024 * 8)

           msg_str = data.decode('utf-8')

           print("Received msg: {}".format(msg_str))

           return True, msg_str

       except socket.error as e:

           print(str(e))

           self.cleanup()

           return False, "Receive message failed"

 

    def start(self, client_obj):

        status, msg_str = self.connect_to_proxy_server()

        if status != True :

             return status, msg_str

 

        status, msg_str = self.send_authention_request("Agent001")

 

def start_client(host, port):

    ClientSocket = socket.socket()

 

    print('Waiting for connection')

    try:

        ClientSocket.connect((host, port))

    except socket.error as e:

        print(str(e))

        return

 

    Response = ClientSocket.recv(2048)

    print(Response.decode('utf-8'))

 

    while True:

        Input = input('Your message: ')

        ipstr = '{}'.format(Input)

        if str(Input) == 'BYE':

                break

        ClientSocket.send(str.encode(Input))

        Response = ClientSocket.recv(2048)

        print(Response.decode('utf-8'))

 

    ClientSocket.close()

 

if __name__ == "__main__":

    host = '127.0.0.1'

    port = int(sys.argv[1])

 

    client_obj = MTCProxyClient(shopfloor_uid = "ShopFloor01",

                                client_uid = "001",

                                server_address = "127.0.0.1",

                                server_port = port)

 

    start_new_thread(client_obj.start, (client_obj, ))

 

    try:

        while True:

            time.sleep(10)

    except KeyboardInterrupt:

        sys.exit();
