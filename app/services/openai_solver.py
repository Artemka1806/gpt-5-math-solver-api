"""Service for solving math problems from images using OpenAI API."""

from openai import OpenAI


client = OpenAI()


async def stream_solution(image_b64: str, websocket) -> str:
    """Send image to OpenAI and stream back the solution.

    Returns the full response text.
    """
    with client.responses.stream(
        model="gpt-4o-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Solve the math problem in this image."},
                    {"type": "input_image", "image_base64": image_b64},
                ],
            }
        ],
    ) as stream:
        full_text = ""
        for event in stream:
            if event.type == "response.output_text.delta":
                chunk = event.delta
                full_text += chunk
                await websocket.send_text(chunk)
            elif event.type == "error":
                await websocket.send_text(f"ERROR: {event.error.message}")
                break

    return full_text

