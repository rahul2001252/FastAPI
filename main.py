from fastapi import FastAPI, HTTPException, Depends, Form
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi.middleware.cors import CORSMiddleware
import bcrypt
from pymongo.errors import DuplicateKeyError
from typing import List

 
app = FastAPI()

# CORS Configuration
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB using AsyncIOMotorClient
uri = "mongodb+srv://ClusterSaw:Accessit@clustersaw.tqitno2.mongodb.net"

client = AsyncIOMotorClient(uri)
db = client["H&M"]

collection_saw_machines: AsyncIOMotorCollection = db["saw_machines"]
collection_axes: AsyncIOMotorCollection = db["Axes"]
collection_bar_graph: AsyncIOMotorCollection = db["Jobs"]
user_collection: AsyncIOMotorCollection = db["users_db"]

class User(BaseModel):
    email: str
    password: str

@app.post("/api/signup")
async def signup(user: User):
    try:
        # Hash the user's password
        hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())

        # Insert the new user into the database with the hashed password
        user_dict = user.dict()
        user_dict["_id"] = user.email  # Use email as the document ID
        user_dict["password"] = hashed_password.decode("utf-8")  # Store the hashed password as a string
        await user_collection.insert_one(user_dict)
        return {"message": "Registration successful"}
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="User already exists")

@app.post("/api/login")
async def login(user: User):
    # Retrieve the user data from the database
    user_data = await user_collection.find_one({"_id": user.email})

    if user_data:
        # Verify the provided password against the stored hashed password
        stored_password = user_data.get("password")

        if stored_password and bcrypt.checkpw(user.password.encode("utf-8"), stored_password.encode("utf-8")):
            return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Login failed")

class SawMachineStatus(BaseModel):
    machine_id: int
    status: str
    value: int

class DataPoint(BaseModel):
    timestamp: str
    position: int

class BarGraphData(BaseModel):
    machineId: int
    jobpending: int
    jobfinished: int

be_debug = True

def be_debug_enable():
    global be_debug
    be_debug = True

def be_debug_disable():
    global be_debug
    be_debug = False

@app.get("/api/saw-machines", response_model=List[SawMachineStatus])
async def get_saw_machines():
    cursor = collection_saw_machines.find({})

    # Convert the cursor to a list of documents
    documents = await cursor.to_list(length=None)

    # Convert the documents to a list of SawMachineStatus objects
    saw_machine_data = [SawMachineStatus(**data) for data in documents]

    return saw_machine_data

@app.get("/api/line-graph-data", response_model=List[DataPoint])
async def get_line_graph_data():
    be_debug_enable()

    # Retrieve data from MongoDB collection for axes and sort by timestamp
    async with collection_axes.find({}).sort("timestamp", 1) as cursor:
        data_points_axes = [DataPoint(**data) async for data in cursor]
    return data_points_axes

@app.get("/api/bar-graph-data", response_model=List[BarGraphData])
async def get_bar_graph_data():

    be_debug_enable()

    async with collection_bar_graph.find({}) as cursor:
        bar_graph_data = []
        async for data in cursor:
            bar_graph_data.append(BarGraphData(
                machineId=data["machineId"],
                jobpending=data["Jobpending"],
                jobfinished=data["Jobfinished"]
            ))
    return bar_graph_data

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000,
#                 reload = True,
#                 ssl_keyfile = "C:/Users/NISHA/Desktop/Farmstack/localhost+2-key.pem",
#                 ssl_certfile = "C:/Users/NISHA/Desktop/Farmstack/localhost+2.pem")
    import uvicorn

# if __name__ == '__main__':
#     # import uvicorn
#     # uvicorn.run("app.main:app",
#     #             ssl_keyfile = "C:/Users/NISHA/Desktop/Farmstack/create-cert-key.key",
#     #             ssl_certfile = "C:/Users/NISHA/Desktop/Farmstack/create-cert.crt"
