"""Service for solving math problems from images using OpenAI API."""

import os
from openai import OpenAI


# Initialize OpenAI client with API key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))




async def stream_solution(image_b64: str, websocket) -> str:
    """Send image to OpenAI and stream back the solution.

    Returns the full response text.
    """
    image_url = f"data:image/jpeg;base64,{image_b64}"
    
    try:
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Solve the math problem in this image. Provide a clear, step-by-step solution without any other text."},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            stream=True,
            max_tokens=1000,
            temperature=0.1,
        )
        
        full_text = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_text += content
                await websocket.send_text(content)
                
        return full_text
        
    except Exception as e:
        error_msg = f"OpenAI API Error: {str(e)}"
        await websocket.send_text(f"ERROR: {error_msg}")
        raise e

