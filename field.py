from fastapi import FastAPI
import pymongo
import json
from lxml import etree

app = FastAPI()

# MongoDB Atlas connection information
mongo_uri = "mongodb+srv://ClusterSaw:Accessit@clustersaw.tqitno2.mongodb.net"
db_name = "prax"
collection_name = "mtconnect"

# Connect to MongoDB Atlas
client = pymongo.MongoClient(mongo_uri)
db = client[db_name]
collection = db[collection_name]

# Retrieve the XML data from MongoDB
documents = collection.find({})  # You may need to specify a query to retrieve the correct document

# for document in documents:
#     print(document)

def extract_values_and_timestamps(documents):
    values = []
    timestamps = []

    for document in documents:
        for key, value in document.items():
            if key == "value":
                values.append(value)
            elif key == "timestamp":
                timestamps.append(value)

    return values, timestamps

# Retrieve all documents from the MongoDB collection
cursor = collection.find({})
documents = list(cursor)

# Extract values and timestamps
values, timestamps = extract_values_and_timestamps(documents)

# Print the extracted values and timestamps
print("Values:", values)
print("Timestamps:", timestamps)