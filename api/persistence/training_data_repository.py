import os
from .mongodb import mongo
from bson import ObjectId

class TrainingDataRepository():

    def __init__(self):
        self.training_data_collection = mongo.db.trainingData

    def find_training_data(self, id):
        """Find training data by id"""
        return self.training_data_collection.find_one({"_id": ObjectId(id)})

    def find_agent_training_data(self, agent_name):
        """Find all training data linked to a specific agent"""
        return self.training_data_collection.find({"agentName": agent_name})

    def count_agent_training_data(self, agent_name):
        return self.training_data_collection.count({"agentName": agent_name})  

    def delete_training_data(self, agent_name, id):
        try:
            self.training_data_collection.delete_one({"agentName": agent_name, "_id": ObjectId(id)})
            return True
        except:
            return False       
  
    def update_training_data(self, agent_name, id, data):
        try:
            self.training_data_collection.update_one({"agentName": agent_name, "_id": ObjectId(id)}, {"$set": {"data": data}}, upsert = True)
            return True
        except:
            return False   

    def insert_training_data(self, data):
        """Add sequentially multiple training data based on bulk size"""
        bulk_insert_size = int(os.environ.get("BULK_INSERT_SIZE", 500))
        q = len(data) // bulk_insert_size
        r = len(data) % bulk_insert_size
        try:
            for i in range(q):
                self.training_data_collection.insert_many(data[bulk_insert_size*i:bulk_insert_size*(i+1)])
            return(self.training_data_collection.insert_many(data[bulk_insert_size*q:(bulk_insert_size * q + r)+1]))
        except Exception as e:
            logger.error("Can't insert data {0}".format(e), exc_info=True)
            return(False)  

    def get_agent_training_data(self, agent_name, intent, pageNumber, pageSize):
        """retrieve training data based on filters: intent, page size and page number"""
        if pageSize > int(os.environ.get("MAX_PAGE_SIZE")):
            pageSize = int(os.environ.get("MAX_PAGE_SIZE"))
        if intent:
            return self.training_data_collection.find({"agentName": agent_name, "data.intent": intent}, {"agentName": 0}).skip((pageNumber - 1) * pageSize).limit(pageSize)
        else:
            return self.training_data_collection.find({"agentName": agent_name}, {"agentName": 0}).skip((pageNumber - 1) * pageSize).limit(pageSize)
    
    def get_intent_by_text(self, text, agent_name):
        return(self.training_data_collection.find_one({"agentName": agent_name, "data.text": text}, {"_id": 0, "data.intent": 1, "data.entities": 1}))
    
    def delete_all_training_data(self, agent_name):
        self.training_data_collection.delete_many({"agentName": agent_name})