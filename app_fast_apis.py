from fastapi import FastAPI, HTTPException, WebSocket,WebSocketDisconnect,Request, Depends, status, Query, Path, BackgroundTasks
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from fastapi.middleware.cors import CORSMiddleware
import bcrypt
from pymongo.errors import DuplicateKeyError
from typing import List
import asyncio
import requests
import uvicorn
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from metrics_utility import *
#from metrics_db import fast_api_app
from old_db import collection_saw_machines, collection_axes, collection_bar_graph, user_collection,SawMachineStatus, DataPoint, BarGraphData, User
fast_api_app = None

fast_api_app = FastAPI()

origins = ["*"]
fast_api_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )
        
# Define models for data
@fast_api_app.post("/api/signup")
async def signup(user: User):
    try:
        be_debug_enable()
        print("entered signup")
        hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())

        # Insert the new user into the database with the hashed password
        user_dict = user.dict()
        user_dict["_id"] = user.email 
        user_dict["password"] = hashed_password.decode("utf-8")  

        await user_collection.insert_one(user_dict)
        return {"message": "Signup successful"}
       
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="User already exists")

@fast_api_app.post("/api/login")
async def login(user:User):
    # Retrieve the user data from the database
    user_data = await user_collection.find_one({"_id": user.email})
    be_debug_enable()
    print("entered login")

    if user_data:
        # Verify the provided password against the stored hashed password
        stored_password = user_data.get("password")
        if stored_password and bcrypt.checkpw(user.password.encode("utf-8"), stored_password.encode("utf-8")):
            return {"message": "Login successful"}

        raise HTTPException(status_code=401, detail="Login failed")

@fast_api_app.get("/api/saw-machines", response_model=List[SawMachineStatus])
async def get_saw_machines():
    cursor = collection_saw_machines.find({})

    # Convert the cursor to a list of documents
    documents = await cursor.to_list(length=None)

    # Convert the documents to a list of SawMachineStatus objects
    saw_machine_data = [SawMachineStatus(**data) for data in documents]

    return saw_machine_data

    
# Define an endpoint to retrieve data and return it using the schema
@fast_api_app.get("/api/line-graph-data", response_model=List[DataPoint])
async def get_line_graph_data():
    be_debug_enable()

    # Retrieve data from MongoDB collection for axes and sort by timestamp
    async with collection_axes.find({}).sort("timestamp", 1) as cursor:
        data_points_axes = [DataPoint(**data) async for data in cursor]
    return data_points_axes

# Retrieve bar graph data
@fast_api_app.get("/api/bar-graph-data", response_model=List[BarGraphData])
async def get_bar_graph_data():
    be_debug_enable()
    print("Entered bar data")

    async with collection_bar_graph.find({}) as cursor:
        bar_graph_data = []

        async for data in cursor:
            bar_graph_data.append(BarGraphData(
                machineId=data["machineId"],
                jobpending=data["Jobpending"],
                jobfinished=data["Jobfinished"]
            ))

    return bar_graph_data
@fast_api_app.websocket("/status")
async def get_status(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
           await websocket.send_text("Start")
           await asyncio.sleep(1)
    except WebSocketDisconnect:
           print("Client Disconnected")
    except Exception as e:
           print(f"WebSocket Error: {str(e)}")
           await websocket.close()


def start_app_server():
    log_debug("Fast API Server Statrted")
    uvicorn.run(fast_api_app)

    