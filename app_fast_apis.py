from fastapi import FastAPI, HTTPException, WebSocket,WebSocketDisconnect,Request, Depends, status, Query, Path, BackgroundTasks
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from fastapi.middleware.cors import CORSMiddleware
import bcrypt
from pymongo.errors import DuplicateKeyError
from typing import List
import asyncio
import requests
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from metrics_utility import *
from metrics_db import *
fast_api_app = None

def start_app_server():
    log_debug("Entered proxy server")
    fast_api_app= FastAPI()

    origins = ["*"]
    fast_api_app.add_middleware(
              CORSMiddleware,
                allow_origins=origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
    
# Define models for data
class SawMachineStatus(BaseModel):
    machine_id: int
    status: str
    value: int

class DataPoint(BaseModel):
    timestamp: str
    content: str

class BarGraphData(BaseModel):
    machineId: int
    jobpending: int
    jobfinished: int

@fast_api_app.post("/api/signup", response_model=Token)
async def signup(user: User):
    try:
        be_debug_enable()
        print("entered signup")
        hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())

        # Insert the new user into the database with the hashed password
        user_dict = user.dict()
        user_dict["_id"] = user.email  # Use email as the document ID
        user_dict["password"] = hashed_password.decode("utf-8")  # Store the hashed password as a string

        # await user_collection.insert_one(user_dict)

        # Generate and return a JWT token upon successful registration
        # access_token = create_access_token(data={"sub": user.email})
        # return access_token
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="User already exists")

@fast_api_app.post("/api/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_email = form_data.username
    user_password = form_data.password

    # Retrieve the user data from the database
    user_data = await user_collection.find_one({"_id": user_email})
    be_debug_enable()
    print("entered login")

    if user_data:
        # Verify the provided password against the stored hashed password
        stored_password = user_data.get("password")

        if stored_password and bcrypt.checkpw(user_password.encode("utf-8"), stored_password.encode("utf-8")):
            access_token = create_access_token(data={"sub":user_email})
            return access_token

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
@fast_api_app.get("/line_graph_data/{name}", response_model=list[DataPoint])
async def get_line_graph_data(name: str):
    cursor = collection_axes.find({"name": name})
    results = await cursor.to_list(length=None)
   
    # Extract relevant data for the line graph
    data = [DataPoint(timestamp=entry["timestamp"], content=entry["content"]) for entry in results]
    #print(data)
    return data

# Retrieve bar graph data
@fast_api_app.get("/api/bar-graph-data", response_model=List[BarGraphData])
async def get_bar_graph_data():
    be_debug_enable()
    #print("Entered bar data")

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
