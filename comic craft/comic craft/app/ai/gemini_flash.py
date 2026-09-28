import os
import base64
import requests

from dotenv import load_dotenv


load_dotenv()

POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")

if not POLLINATIONS_API_KEY:
    raise ValueError("POLLINATIONS_API_KEY not found in .env file")


def generate_image_and_story(prompt: str) -> dict:

    # -------------------------------------------------
    # 1. Generate IMAGE
    # -------------------------------------------------

    image_prompt = f"""
Create a beautiful cinematic AI image based on this idea:

{prompt}

Requirements:
- One single scene
- No comic panels
- No dialogue
- No speech bubbles
- No captions
- No text inside the image
- Detailed environment
- Cinematic lighting
- High quality
- Storybook style
"""

    image_url = "https://gen.pollinations.ai/image/" + requests.utils.quote(
        image_prompt
    )

    image_response = requests.get(
        image_url,
        headers={
            "Authorization": f"Bearer {POLLINATIONS_API_KEY}"
        },
        params={
            "model": "flux",
            "width": 1024,
            "height": 1024,
            "nologo": "true"
        },
        timeout=120
    )

    if image_response.status_code != 200:
        raise RuntimeError(
            f"Pollinations image error: "
            f"{image_response.status_code} - "
            f"{image_response.text}"
        )

    image_base64 = base64.b64encode(
        image_response.content
    ).decode("utf-8")

    image_data_url = (
        "data:image/png;base64,"
        + image_base64
    )


    # -------------------------------------------------
    # 2. Generate SHORT STORY
    # -------------------------------------------------

    story_prompt = f"""
Write a short story based on this idea:

{prompt}

Requirements:
- 3 to 5 sentences only
- Simple English
- No dialogue
- No speech
- No character conversations
- Make it feel like a small story
"""

    story_response = requests.post(
        "https://gen.pollinations.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-5.4-nano",
            "messages": [
                {
                    "role": "user",
                    "content": story_prompt
                }
            ]
        },
        timeout=120
    )

    if story_response.status_code != 200:
        raise RuntimeError(
            f"Pollinations story error: "
            f"{story_response.status_code} - "
            f"{story_response.text}"
        )

    story_data = story_response.json()

    story = (
        story_data["choices"][0]["message"]["content"]
    )


    # -------------------------------------------------
    # 3. Return image + story
    # -------------------------------------------------

    return {
        "image": image_data_url,
        "story": story.strip()
    }