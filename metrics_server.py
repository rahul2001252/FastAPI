from metrics_utility import *
from app_fast_apis import start_app_server
from mtc_proxy_server import start_mtc_proxy_server
import time, sys

if __name__ == "__main__":
    print("Monitoring and Control Backend Server Started")
    mtc_proxy_server_host =  "127.0.0.1"  
    mtc_proxy_server_port = int(sys.argv[1])
    be_debug_enable()

    mtc_proxy_server = start_mtc_proxy_server(mtc_proxy_server_host, mtc_proxy_server_port)
    
    start_app_server()

    
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        mtc_proxy_server.cleanup()
        print("Terminating Backend Server")