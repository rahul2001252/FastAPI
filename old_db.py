from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pydantic import BaseModel

# Connect to MongoDB using AsyncIOMotorClient
uri = "mongodb+srv://ClusterSaw:Accessit@clustersaw.tqitno2.mongodb.net"
client = AsyncIOMotorClient(uri)
db = client["H&M"]

class User(BaseModel):
    email: str
    password: str

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

# MongoDB collections
collection_saw_machines: AsyncIOMotorCollection = db["saw_machines"]
collection_axes: AsyncIOMotorCollection = db["Axes"]
collection_bar_graph: AsyncIOMotorCollection = db["Jobs"]
user_collection: AsyncIOMotorCollection = db["users_db"]
