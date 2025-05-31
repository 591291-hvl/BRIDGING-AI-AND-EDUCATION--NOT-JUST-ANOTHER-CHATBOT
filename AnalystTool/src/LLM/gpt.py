import json
from dotenv import load_dotenv
import os
from openai import AzureOpenAI, OpenAIError  

# Load environment variables
load_dotenv()

class GPT:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )

    def sumUpWeekly(self, weeklyReport):
        return self.sendQuery('src/LLM/prompts/sumup.txt', weeklyReport)
    
    def weeklyChange(self, weeklyReport, lastWeeksReport):
        combinedReport = "This week:" + weeklyReport + "Last week" + lastWeeksReport
        return self.sendQuery('src/LLM/prompts/weeklyChange.txt', combinedReport)

    def aggregateQuestion(self, questions):            
        return self.sendQuery('src/LLM/prompts/aggregateQuestions.txt', questions)
        

    def classifyTopics(self, conversation):
        # Topic list
        with open("src/json/topics.json", "r", encoding="utf-8") as file:
            topicList = file.read()
        
        return self.sendQuery('src/LLM/prompts/topics.txt', conversation, return_json=True, additional_system_message = topicList)

    def classifyModule(self, conversation):
        with open("src/json/modules.json", "r", encoding="utf-8") as file:
            moduleList = file.read()

        return self.sendQuery('src/LLM/prompts/modules.txt', conversation, return_json=True, additional_system_message = moduleList)

    def classifyAreaOfUse(self, conversation):
        return self.sendQuery("src/LLM/prompts/areaofuse.txt", conversation, return_json=True)



    def sendQuery(self, system_message_path, user_message, return_json=False, additional_system_message=None):
        try:
            # Read system message from file
            with open(system_message_path, "r", encoding="utf-8") as file:
                system_message = file.read().strip()

            if additional_system_message:
                system_message += additional_system_message
                
            response = self.client.chat.completions.create(
                model="gpt-4o-norwayeast-ped",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                response_format={"type": "json_object"} if return_json else {"type": "text"}
            )

            response_text = response.choices[0].message.content

            if return_json:
                try:
                    return json.loads(response_text)  # Convert string to JSON dictionary
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON response from Azure OpenAI."}

            return response_text

        except FileNotFoundError:
            return {"error": "System message file not found."} if return_json else "Error: System message file not found."
        except OpenAIError as e:
            return {"error": str(e)} if return_json else f"OpenAI Error: {str(e)}"
        except Exception as e:
            return {"error": str(e)} if return_json else f"Unexpected Error: {str(e)}"
