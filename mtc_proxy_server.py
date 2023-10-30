import asyncio
import websockets
import threading
import ssl
from metrics_utility import *

# Create a set to store connected clients
connected_clients = set()

async def handle_client(websocket, path):
    # Add the new client to the set
    connected_clients.add(websocket)
    try:
        # Handle messages from the client
        async for message in websocket:
            # Broadcast the message to all connected clients
            log_debug("{}".format(message))
            await websocket.send(message) 
    except websockets.exceptions.ConnectionClosedError:
        pass
    finally:
        # Remove the client from the set when they disconnect
        connected_clients.remove(websocket)

def start_websocket_server():
    ssl_context = None
    start_server = None

    # Use SSL/TLS for a secure WebSocket connection
    # ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    if ssl_enabled():     
        # Use SSL/TLS for a secure WebSocket connection
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)  
        
        # Load your SSL certificate and private key
        ssl_context.load_cert_chain("/path/to/your/server_cert.pem", "/path/to/your/server_key.pem")

        # Create a secure WebSocket server
        start_server = websockets.serve(handle_client, "127.0.0.1", 8765, ssl=ssl_context)
    else:
        start_server = websockets.serve(handle_client, "127.0.0.1", 8765)

    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(start_server)
   

# if __name__ =="__main_":
def start_mtc_proxy_server():
    mtc_proxy_server_thread = threading.Thread(target = start_websocket_server)
    mtc_proxy_server_thread.start()
    try:
         asyncio.get_event_loop().run_forever()
    except(KeyboardInterrupt,SystemExit):
         pass


class MTCData:
    def __init__(self, proxy=None):
        self.proxy = proxy if proxy else None
        if proxy :
            self.proxy_url_base = proxy
        pass  

    def get_probe_data(self,  req_path):
        if self.proxy :
            jdata, errstr = self.send_req_to_proxy(req_path)
        else :
            jdata, errstr = self.send_req_to_mtc(req_path)

        return jdata, errstr
    
    def send_req_to_proxy(self, req_path):
        pass

    def send_req_to_mtc(self, req_path):
        pass