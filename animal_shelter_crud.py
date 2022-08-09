# animal_shelter_crud.py
#
# Created by Sarah Kerr for CS340 - Client/Server Development
# Created on Jupyter Notebook
#
# This library provides copy, read, update, and delete methods to be 
# used when querying data for the Animal Shelter data visualization
# program.


from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps
import json

class AnimalShelter(object):
    """ 
    Class for CRUD operations on a collection from a database in MongoDB. 
    
    Attributes:
        username (str) : Username for the database
        password (str) : Password to the database
        
    Methods:
        create (data):
            Inserts data into collection using pymongo insert().
        read(data):
            Finds one document from the collection matching data criteria using pymongo find_one().
        read_all(data):
            Finds all documents from collection matching data criteria using pymongo find().
        update_all(myquery, newvalue):
            Updates selected documents with new values using pymongo update().
        delete(data):
            Deletes documents matching query data using pymongo remove().    
    
    """  
    def __init__(self, username, password):
        """
        Constructor to establish connection with and provide authorization to the database.
        
        Note - user will need proper credentials for accessing the database as well as having their
        IP address whitelisted in the database.
        
        Parameters:
            Username : str
                Username for the database
            Password : str
                Password to the database
        """
        #Connect to mongoDB, passing in credentials
        self.client = MongoClient('mongodb+srv://%s:%s@cluster0.ioleg.mongodb.net/?retryWrites=true&w=majority'%(username,password))
        #Connect to AAC database
        self.database = self.client['AAC']
        
    def create(self, data):
        """
        Inserts data into collection using pymongo insert().
        
        Parameters:
            data : str
                The data being inserted into the collection.
                
        Raises:
            Exception
                If data being passed in is None.
                
        Returns:
            True if data is successfully inserted into collection.
        """
        if data is not None:
            self.database.animals.insert(data)
            return True
        else:
            raise Exception("No data to save, data parameter empty.")
    
    def read(self, data):
        """
        Finds one document from the collection matching data criteria using pymongo find_one().
        
        Parameters:
            data : str
                The query operation on the collection
        
        Returns:
            One document from the collection as a python dictionary
        """
        return self.database.animals.find_one(data)
            
    def read_all(self, data):
        """ 
        Finds all documents from collection matching data criteria using pymongo find().
        
        Parameters:
            data : str
                The query operation on the collection
        
        Raises:
            Exception:
                If data being passed is None.
                
        Returns:
            A cursor as a pointer to a list of resulting matching documents
        """
        if data is not None:
            cursor = self.database.animals.find(data, {'_id':False} ) #setting _id to false means this wont show in results
            return cursor
        else:
            raise Exception("No data to read.")        
    
    def update_all(self, myquery, newvalue):
        """
        Updates selected documents with new values using pymongo update().
        
        Parameters:
            myquery : str
                The query on the documents to be updated.
                
            newvalue : str
                The new values of the document
                
        Raises:
            Exception:
                If MongoDB did not return a confirmation of successful update
                
        Returns:
            The updated document in BSON format
        """
        update_request = self.database.animals.update(myquery, newvalue)
            
        if ("updatedExisting", True) in update_request.items():
            updated_doc = self.database.animals.find(myquery) #returns the updated document
            return dumps(updated_doc)
        else:
            raise Exception("Error updating document.")
            
    def delete(self, data):
        """
        Deletes documents matching query data using pymongo remove().
        
        Parameters:
            Data : str
                The query for documents to be deleted.
                
        Raises:
            Exception:
                If mongoDB did not confirm the delete
                
        Return:
            MongoDB confirmation of delete in BSON format.
        """
        delete_request = self.database.animals.remove(data)
        
        if "ok" in delete_request:
            return dumps(delete_request) #returns MongoDB confirmation of delete
        else:
            raise Exception("Error deleting document")