from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from pydantic import BaseModel

from io import BytesIO
import base64
import html

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image
)

from app.services.image_generator import (
    generate_image_and_story
)


router = APIRouter()


# ============================================================
# REQUEST MODELS
# ============================================================

class ImageRequest(BaseModel):

    prompt: str


class PanelRequest(BaseModel):

    title: str
    image: str
    story: str


class PDFRequest(BaseModel):

    panels: list[PanelRequest]
    title: str = "ComicCraft 5-Panel Comic"


# ============================================================
# GENERATE COMIC
# ============================================================

@router.post("/generate-image")
async def create_image(
    request: ImageRequest
):

    prompt = request.prompt.strip()

    if not prompt:

        raise HTTPException(
            status_code=400,
            detail="Please enter a topic."
        )

    try:

        result = generate_image_and_story(
            prompt
        )

        return {
            "success": True,
            "panels": result["panels"]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# DOWNLOAD PDF
# ============================================================

@router.post("/download-pdf")
async def download_pdf(
    request: PDFRequest
):

    try:

        if not request.panels:

            raise HTTPException(
                status_code=400,
                detail="No comic panels were provided."
            )


        pdf_buffer = BytesIO()


        document = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )


        styles = getSampleStyleSheet()

        title_style = styles["Title"]
        heading_style = styles["Heading2"]
        body_style = styles["BodyText"]


        elements = []


        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        safe_title = html.escape(
            request.title
        )

        elements.append(
            Paragraph(
                safe_title,
                title_style
            )
        )

        elements.append(
            Spacer(1, 20)
        )


        # ----------------------------------------------------
        # PANELS
        # ----------------------------------------------------

        for panel in request.panels:

            safe_panel_title = html.escape(
                panel.title
            )

            elements.append(
                Paragraph(
                    safe_panel_title,
                    heading_style
                )
            )

            elements.append(
                Spacer(1, 10)
            )


            # ------------------------------------------------
            # IMAGE
            # ------------------------------------------------

            if panel.image:

                try:

                    if "," in panel.image:

                        image_base64 = (
                            panel.image.split(
                                ",",
                                1
                            )[1]
                        )

                    else:

                        image_base64 = panel.image


                    image_bytes = (
                        base64.b64decode(
                            image_base64
                        )
                    )


                    image_buffer = BytesIO(
                        image_bytes
                    )


                    pdf_image = Image(
                        image_buffer
                    )


                    max_width = 7 * inch
                    max_height = 4.8 * inch


                    image_width = (
                        pdf_image.imageWidth
                    )

                    image_height = (
                        pdf_image.imageHeight
                    )


                    if (
                        image_width > 0
                        and image_height > 0
                    ):

                        ratio = min(
                            max_width / image_width,
                            max_height / image_height
                        )

                        pdf_image.drawWidth = (
                            image_width * ratio
                        )

                        pdf_image.drawHeight = (
                            image_height * ratio
                        )


                    elements.append(
                        pdf_image
                    )


                except Exception:

                    elements.append(
                        Paragraph(
                            "Image could not be added.",
                            body_style
                        )
                    )


            elements.append(
                Spacer(1, 12)
            )


            # ------------------------------------------------
            # STORY
            # ------------------------------------------------

            elements.append(
                Paragraph(
                    "<b>Story</b>",
                    body_style
                )
            )

            elements.append(
                Spacer(1, 6)
            )


            safe_story = html.escape(
                panel.story
                or "No story generated."
            )


            safe_story = safe_story.replace(
                "\n",
                "<br/>"
            )


            elements.append(
                Paragraph(
                    safe_story,
                    body_style
                )
            )


            elements.append(
                Spacer(1, 25)
            )


        # ----------------------------------------------------
        # BUILD PDF
        # ----------------------------------------------------

        document.build(
            elements
        )


        pdf_buffer.seek(0)


        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                'attachment; filename="ComicCraft_5_Panel_Comic.pdf"'
            }
        )


    except HTTPException:

        raise


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )