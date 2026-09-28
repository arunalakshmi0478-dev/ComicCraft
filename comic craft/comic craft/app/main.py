from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.routes import router


app = FastAPI(
    title="ComicCraft",
    description="AI 5-Panel Comic Generator",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


@app.get(
    "/",
    response_class=HTMLResponse
)
async def home():

    html_file = (
        Path(__file__).resolve().parent.parent
        / "templates"
        / "index.html"
    )

    if not html_file.exists():

        return HTMLResponse(
            content="<h1>index.html not found</h1>",
            status_code=404
        )

    return HTMLResponse(
        content=html_file.read_text(
            encoding="utf-8"
        )
    )