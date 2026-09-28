import os
import base64
import json
import random

from urllib.parse import quote
from urllib.request import Request, urlopen

from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

API_KEY = os.getenv(
    "POLLINATIONS_API_KEY",
    ""
).strip()

if not API_KEY:
    raise ValueError(
        "POLLINATIONS_API_KEY not found in .env file"
    )


# ============================================================
# AI STORY GENERATOR
# ============================================================

def generate_five_panel_story(topic: str) -> list:

    prompt = """
Create a complete 5-panel comic story.

TOPIC:
""" + topic + """

Create exactly five connected story panels.

Panel 1:
Beginning - introduce the main character and situation.

Panel 2:
Development - something important happens.

Panel 3:
Problem - a challenge or conflict appears.

Panel 4:
Action - the main character takes action.

Panel 5:
Ending - show the result and finish the story.

Rules:
- All five panels must be one connected story.
- Every panel must be different.
- Do not repeat scenes.
- Keep the same main character.
- Use simple English.
- Make the story interesting and meaningful.
- No dialogue.
- No speech bubbles.
- No captions.

Return ONLY valid JSON.

Use exactly this format:

[
  {
    "title": "Panel 1: Beginning",
    "scene": "Detailed description of panel 1",
    "story": "Two simple sentences about panel 1"
  },
  {
    "title": "Panel 2: Development",
    "scene": "Detailed description of panel 2",
    "story": "Two simple sentences about panel 2"
  },
  {
    "title": "Panel 3: Problem",
    "scene": "Detailed description of panel 3",
    "story": "Two simple sentences about panel 3"
  },
  {
    "title": "Panel 4: Action",
    "scene": "Detailed description of panel 4",
    "story": "Two simple sentences about panel 4"
  },
  {
    "title": "Panel 5: Ending",
    "scene": "Detailed description of panel 5",
    "story": "Two simple sentences about panel 5"
  }
]
"""

    request_body = json.dumps(
        {
            "model": "openai/gpt-5.4-nano",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
    ).encode("utf-8")

    request = Request(
        "https://gen.pollinations.ai/v1/chat/completions",
        data=request_body,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "ComicCraft/1.0"
        },
        method="POST"
    )

    try:

        with urlopen(
            request,
            timeout=120
        ) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        content = (
            data
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

        # Remove markdown code fences
        if content.startswith("```json"):
            content = content[7:]

        if content.startswith("```"):
            content = content[3:]

        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        panels = json.loads(content)

        if not isinstance(panels, list):
            raise ValueError(
                "AI did not return a list."
            )

        if len(panels) != 5:
            raise ValueError(
                "AI did not create exactly 5 panels."
            )

        return panels

    except Exception as e:

        raise RuntimeError(
            f"Story generation failed: {e}"
        )


# ============================================================
# IMAGE GENERATOR
# ============================================================

def generate_panel_image(
    scene: str,
    panel_number: int,
    topic: str
) -> str:

    last_error = None

    # Try up to 3 times
    for attempt in range(1, 4):

        seed = random.randint(
            1,
            2147483647
        )

        image_prompt = """
Create ONE high-quality comic illustration.

TOPIC:
""" + topic + """

THIS IS PANEL:
""" + str(panel_number) + """

SCENE:
""" + scene + """

CHARACTER CONSISTENCY:
- Same main character in all panels.
- Same face.
- Same hairstyle.
- Same clothes.
- Same body proportions.
- Same visual identity.

STYLE:
- Colorful comic-book illustration
- Cinematic lighting
- Detailed environment
- Expressive character
- Professional digital artwork
- Landscape 16:9 composition

STRICT RULES:
- Create ONLY one scene.
- Create ONLY one panel.
- Do not create a comic page.
- Do not create multiple panels.
- Do not create a collage.
- Do not split the image.
- Do not repeat another scene.
- No text.
- No captions.
- No dialogue.
- No speech bubbles.
- No logos.
- No watermark.
"""

        encoded_prompt = quote(
            image_prompt,
            safe=""
        )

        url = (
            "https://gen.pollinations.ai/image/"
            + encoded_prompt
            + "?model=flux"
            + "&width=768"
            + "&height=432"
            + f"&seed={seed}"
            + "&nologo=true"
        )

        request = Request(
            url,
            headers={
                "Authorization":
                    f"Bearer {API_KEY}",
                "User-Agent":
                    "ComicCraft/1.0"
            }
        )

        try:

            print(
                f"Generating Panel {panel_number} "
                f"(Attempt {attempt}/3)..."
            )

            with urlopen(
                request,
                timeout=300
            ) as response:

                image_bytes = response.read()

                content_type = response.headers.get(
                    "Content-Type",
                    "image/png"
                )

                content_type = (
                    content_type.split(";")[0]
                )

            if not image_bytes:
                raise RuntimeError(
                    "Empty image received."
                )

            image_base64 = base64.b64encode(
                image_bytes
            ).decode("utf-8")

            print(
                f"Panel {panel_number} generated successfully!"
            )

            return (
                f"data:{content_type};base64,"
                f"{image_base64}"
            )

        except Exception as e:

            last_error = e

            print(
                f"Panel {panel_number} "
                f"attempt {attempt} failed: {e}"
            )

    raise RuntimeError(
        f"Image generation failed for Panel "
        f"{panel_number} after 3 attempts: "
        f"{last_error}"
    )


# ============================================================
# MAIN FUNCTION
# ============================================================

def generate_image_and_story(
    prompt: str
) -> dict:

    topic = prompt.strip()

    if not topic:
        raise ValueError(
            "Please enter a topic."
        )

    print("\n==============================")
    print("Creating 5-panel story...")
    print("==============================\n")

    # STEP 1: Create 5-panel story
    story_panels = generate_five_panel_story(
        topic
    )

    panels = []

    # STEP 2: Generate 5 images
    for index, panel in enumerate(
        story_panels,
        start=1
    ):

        title = panel.get(
            "title",
            f"Panel {index}"
        )

        scene = panel.get(
            "scene",
            ""
        )

        story = panel.get(
            "story",
            ""
        )

        print(
            f"\nCreating Panel {index}/5..."
        )

        image = generate_panel_image(
            scene,
            index,
            topic
        )

        panels.append(
            {
                "title": title,
                "image": image,
                "story": story
            }
        )

    print("\n==============================")
    print("5-PANEL COMIC COMPLETED!")
    print("==============================\n")

    return {
        "panels": panels,
        "image": panels[0]["image"],
        "story": panels[0]["story"]
    }