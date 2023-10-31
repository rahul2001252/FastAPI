import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel
from metrics_utility import *

class MonitorDb:
    init = False
    db_type = None
    db_info = {}

    def __init__(self, db_type):
        pass

    def get_collection(self, col_name):
        if col_name in MonitorDb.db_info["collections"]:
            collection = MonitorDb.db_info["collections"][col_name]     
            return collection, "Found"
        return None, "Collection Not found"

    def db_write(self, col_name, json_dict):
        collection, errstr = self.get_collection(col_name)
        if collection == None :
             log_error("COlelction name {} invalid".format(col_name))
             return None, errstr
      
        # Check if the entry exists if so update
        # else Add new Entry

    def db_read(self, col_name, key_dict):
        collection, errstr = self.get_collection(col_name)
        if collection == None :
             log_error("COlelction name {} invalid".format(col_name))
             return None, errstr
      
        # Check if the entry exists if so retrun entry
        # else None with error string  
         
       
        
class MongoDb (MonitorDb):
    def init_mongo_db(self):        
        mongo_uri = "mongodb+srv://ClusterSaw:Accessit@clustersaw.tqitno2.mongodb.net"
        MonitorDb.db_info.update({"url":mongo_uri})

        mongodb_client = pymongo.MongoClient(mongo_uri)

        db_name = "monitoringdb"
        db = mongodb_client[db_name]
        MonitorDb.db_info.update({"db":  db})
    
        collection_list = [ "sysemconfig", 
                            "userprofile", 
                            "mtcuidipmap",
                            "equipment",
                            "userequipmmentmap",
                            "equipmentevents",
                            "equipmentsamples",
                            "equipmentcondition"
                        ]
        
        MonitorDb.db_info.update({ "collections": [] })
        for db_col_name in collection_list :
            db_col_name = db[db_col_name]
            log_debug("Created collection {} ".format(db_col_name))
            MonitorDb.db_info["collections"].append({ db_col_name: db_col_name})

        log_debug("Database Info: {} ".format(MonitorDb.db_info))

        collection_saw_machines: AsyncIOMotorCollection = db["saw_machines"]
        collection_axes: AsyncIOMotorCollection = db["Axes"]
        collection_bar_graph: AsyncIOMotorCollection = db["Jobs"]
        user_collection: AsyncIOMotorCollection = db["users_db"]
        
    def __init__(self, db_type):
        MonitorDb.db_type = db_type
        super().__init__(db_type)
        self.init_mongo_db()
        

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



def init_database(db_type):
    if db_type == "mongodb":
        db = MongoDb(db_type)
        return db
    else:
        print("Database type {} not supported.format(db_type)")
    
db=init_database("mongodb")