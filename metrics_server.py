import metrics_utility;
from fastapi import FastAPI
import metrics_db
import mtc_proxy_server
from metrics_utility import *
from mtc_proxy_server import start_mtc_proxy_server
from app_fast_apis import start_app_server

 



if __name__ == "__main__":
   
    print("Monitoring and Control Backend Server Started")
    be_debug_enable()
    # start_mtc_proxy_server()
    start_app_server()