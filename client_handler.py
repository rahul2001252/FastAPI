import socket
import time, sys
from _thread import *
import copy
import json

#MTC Proxy Client Handler
class MTCProxyClientHandler:
    client_map = {}

    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.shopfloor_uid = None
        self.client_uid = None
        self.agent_uid = {}
  
    def update_client_map(self, client_obj, auth_data, delete=False):
        if delete == False:
            map_data = {
                    auth_data["shopfloor_uid"] :
                          {
                              auth_data["client_uid"] :
                                   { 'object' : client_obj,
                                     'agent_uid' : [ auth_data['agent_uid'] ]
                                   }
                          }
                       }
            MTCProxyClientHandler.client_map.update(map_data)
            print("Client map Added: : {}\n".format(MTCProxyClientHandler.client_map))
        else:
            map_key = self.shopfloor_uid
            if map_key in MTCProxyClientHandler.client_map:
                del MTCProxyClientHandler.client_map[map_key]
                print("Client map Deleted: {}\n".format(MTCProxyClientHandler.client_map))
 
    def cleanup(self):
        self.update_client_map(self, auth_data=None, delete=True)
        if self.socket != None :
            self.socket.close()
            self.socket = None;

    def start(self, clientObj):
        #add client obj to client obj map
        auth_status, auth_data = self.request_authenticaton()
        if auth_status == False :
            print("Authentication Failed ");
            print(auth_data)
            self.cleanup()
            return
 
        #self.shopfloor_uid = copy.deepcopy(auth_data["shopfloor_uid"])
        self.shopfloor_uid = auth_data["shopfloor_uid"]
        self.client_uid = auth_data["client_uid"]
        self.update_client_map(clientObj, auth_data)
 
        self.socket.send(str.encode('You are now connected to the replay server... Type BYE to stop'))
        while True:
            data = self.socket.recv(2048)
            message = data.decode('utf-8')
            if message == 'BYE':
                break
            reply = f'Server: {message}'
            self.socket.sendall(str.encode(reply))

        self.cleanup()

    def authenticate(self, auth_json):
        if auth_json == None and len(auth_json) == 0:
            return False, "Authentication Json Invalid"

        print("Auth record: {}".format(auth_json))
        for json_key in [ "user_uid", "pass_key", "shopfloor_uid", "agent_uid", "client_uid" ]:
            if json_key not in auth_json.keys():
                 return False, "Authentication Json key {} not present".format(json_key)

        #validate username password from db
        if auth_json["user_uid"] != "mtconnect" or auth_json["pass_key"] != "mtconnect"  :
            return False, "Unvalid user id or password"

        return True, auth_json
 
    def request_authenticaton(self ):
        #return True, { "user_uid":"mtconnect",
        #               "pass_key":"mtconnect",
        #              "shopfloor_uid":"ShopFloor001",
        #              "agent_uid": "Agent001",
        #              "client_uid": "001" }
 
        status, auth_json = self.recv_json_msg()
        if status != True :
            return status, auth_json
 
        status, auth_json = self.authenticate(auth_json)
        if status == True:
            response_json = { "status": True, "reason":"" }
            status, msg_str = self.send_json_msg(response_json)
            if status != True :
                return status, msg_str
            else:
                return True, auth_json
 
        return status, auth_json
 
    def send_json_msg(self, json_dict):
        msg_str = json.dumps(json_dict)
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
 
        json_dict = json.loads("{}".format(msg_str))
        print(type(json_dict))
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
 