def build_comic_layout(story: dict) -> dict:
    """
    Creates a simple comic layout structure.
    """

    panels = story.get("panels", [])

    layout = []

    for index, panel in enumerate(panels, start=1):
        layout.append(
            {
                "position": index,
                "panel": panel.get("panel", index),
                "scene": panel.get("scene", ""),
                "dialogue": panel.get("dialogue", "")
            }
        )

    return {
        "title": story.get("title", "ComicCraft Comic"),
        "panel_count": len(layout),
        "panels": layout
    }