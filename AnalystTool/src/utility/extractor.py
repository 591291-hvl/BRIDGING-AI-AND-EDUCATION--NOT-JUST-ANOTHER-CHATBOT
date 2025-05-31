import json
from datetime import datetime
from bson import ObjectId

class Extractor:    
    def extract_fields(self, json_data):
        extracted_data = {
            "messages": [],
            "userId": str(json_data.get("userId", "")) if isinstance(json_data.get("userId"), ObjectId) else json_data.get("userId", "")
        }

        for message in json_data.get("messages", []):
            extracted_message = {
                "from": message.get("from", "user"),  
                "content": message.get("content"),
                "files": message.get("files", []),
                "createdAt": message.get("createdAt").isoformat() if isinstance(message.get("createdAt"), datetime) else "",
                "updatedAt": message.get("updatedAt").isoformat() if isinstance(message.get("updatedAt"), datetime) else ""
            }
            extracted_data["messages"].append(extracted_message)

        return extracted_data
