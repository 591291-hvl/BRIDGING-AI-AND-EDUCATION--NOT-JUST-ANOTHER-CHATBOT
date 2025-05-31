from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from vectorSearch import VectorSearch
import httpx
import os
from dotenv import load_dotenv
from datetime import datetime as dt

vs = VectorSearch()
app = FastAPI()

@app.post("/chat/completions")
async def rag(request: Request):
    user_request_data = await request.json()

    headers = {
        'api-key': request.headers.get('api-key'),
        'Content-Type': 'application/json',
    }

    # Extract the latest user message
    latest_user_message = next(
        (message for message in reversed(user_request_data["messages"]) if message["role"] == "user"),
        None
    )

    # Process the content of the latest user message
    if latest_user_message:
        contents = latest_user_message['content']
        if isinstance(contents, list):
            text_content = ''.join([part['text'] for part in contents if 'text' in part])
        else:
            text_content = contents

        # Perform vector search and retrieve relevant context (lecture notes, course book, etc.)
        try:
            context = vs.search(text_content) if text_content else None
        except Exception as e:
            context = None
            print(f"Vector search failed: {e}")


        if context:  # Only add context if something was retrieved
            assistant_context_message = {
                "role": "assistant",
                "content": f"Context retrieved from course materials: {context}. Retrieved at {dt.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }

            # Insert the assistant message before the user's latest query
            user_request_data["messages"].insert(-2, assistant_context_message)

            print(f"Injected assistant message with RAG context: {assistant_context_message['content']}")

    # Make an async HTTP POST request to the Azure OpenAI endpoint
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                os.getenv("AZURE_OPENAI_ENDPOINT"),
                headers=headers,
                json=user_request_data
            )
            response.raise_for_status()
    except httpx.RequestError as e:
        return {"error": f"Failed to connect to Azure OpenAI API: {str(e)}"}        
    except httpx.HTTPStatusError as e:
        return {"error": f"Azure OpenAI API request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


    # Stream the response chunks back to the client with error handling
    async def generate():
        try:
            async for chunk in response.aiter_text():
                if chunk:
                    yield chunk
        except httpx.RequestError as e:
            yield {"error": f"Connection error while streaming response: {str(e)}"}
        except httpx.HTTPStatusError as e:
            yield {"error": f"HTTP error while streaming response: {str(e)}"}
        except Exception as e:
            yield {"error": f"Unexpected error while streaming response: {str(e)}"}

    return StreamingResponse(generate(), media_type="application/json")


@app.get("/live")
def read_root():
    return {"Hello": "World"}
