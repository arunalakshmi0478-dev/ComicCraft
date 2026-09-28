import json
from pathlib import Path


def export_story_json(story: dict, filename: str = "comic.json") -> str:
    """
    Saves comic story as JSON.
    """

    output_folder = Path("outputs")
    output_folder.mkdir(exist_ok=True)

    output_file = output_folder / filename

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            story,
            file,
            indent=4,
            ensure_ascii=False
        )

    return str(output_file)