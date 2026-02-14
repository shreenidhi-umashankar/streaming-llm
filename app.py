import os
import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class StreamRequest(BaseModel):
    prompt: str
    stream: bool = True

async def event_stream(prompt: str):
    try:
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Generate Rust code for a web scraper with at least 63 lines. Include functions and proper error handling."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=True
        )

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                yield f"data: {{\"choices\": [{{\"delta\": {{\"content\": \"{content}\"}}}}]}}\n\n"
                await asyncio.sleep(0)

        yield "data: [DONE]\n\n"

    except Exception as e:
        yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

@app.post("/stream")
async def stream_endpoint(req: StreamRequest):
    return StreamingResponse(
        event_stream(req.prompt),
        media_type="text/event-stream"
    )
