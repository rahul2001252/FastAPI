import asyncio
import websockets
import ssl
from metrics_utility import *

async def secure_websocket_client():
    log_debug("secure webscoket client loop")
    
    ssl_context = None
    server_ip = "localhost"
    uri = ""
    
    if ssl_enabled():
        uri = "wss://" + server_ip
    # Create an SSL context to establish a secure connection
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.load_verify_locations("/path/to/your/ca_certificate.pem")  # Add your CA certificate
    else:
         uri = "ws://" + server_ip

    # async with websockets.connect(uri, ssl=ssl_context) as websocket:
    async with websockets.connect(uri) as websocket:
        log_debug("Connected to the secure WebSocket server")

        # Your WebSocket communication logic here
        try:
            # Handle messages from the client
            async for message in websocket:
                # Broadcast the message to all connected clients
                await websocket.send(message)
        except websockets.exceptions.ConnectionClosedError:
            pass
        finally: 
            pass

        # Remove the client from the set when they disconnect

if __name__ =="__main__":
    asyncio.get_event_loop().run_until_complete(secure_websocket_client)