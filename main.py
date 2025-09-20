import logging
import os
from pathlib import Path
import shutil
import tempfile
from uuid import uuid4
import cv2
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from ultralytics import YOLO
from ultralytics.engine.results import Results
from fastapi import APIRouter, FastAPI, File, Request, UploadFile


logger = logging.getLogger("uvicorn")

base_url = "http://localhost:8080"

app = FastAPI(
    description="物体検出API",
)

router = APIRouter(prefix="/api")

templates = Jinja2Templates(directory="templates")

app.mount("/img", StaticFiles(directory="tmp"), name="img")


class DetectedObject(BaseModel):
    class_name: str
    confidence: float
    bbox: list[float]


class RecognitionResult(BaseModel):
    image_url: str
    objects: list[DetectedObject]


def results_to_response_model(results: Results) -> RecognitionResult:
    bboxes = results.boxes.xyxy.numpy()
    confs = results.boxes.conf.numpy()
    cls_ids = results.boxes.cls.numpy().astype(int)
    img_arr = results.plot()  # image with bbox

    img_path = Path(__file__).parent / "tmp/{}.png".format(uuid4().hex)
    cv2.imwrite(img_path, img_arr)

    img_url = os.path.join(base_url, "img/{}".format(img_path.name))

    objects = []
    for bbox, conf, cid in zip(bboxes, confs, cls_ids):
        objects.append(
            DetectedObject(
                class_name=results.names[cid],
                confidence=conf,
                bbox=bbox,
            )
        )

    return RecognitionResult(image_url=img_url, meta=objects)


@app.get("/upload")
async def get_upload_html(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "画像認識APIのデモページ"},
    )


@router.post(
    "/recognition",
    response_model=RecognitionResult,
)
async def detect_object(
    file: UploadFile = File(...),
):
    # TODO
    suffix = "jpg"
    if file.filename:
        suffix = file.filename.split(".")[1]
        logger.info(suffix)

    with tempfile.NamedTemporaryFile(delete=True, suffix=".{}".format(suffix)) as temp:
        shutil.copyfileobj(file.file, temp)
        filepath = temp.name

        model = YOLO(modle_path="yolov8n.pt")

        results = model(filepath)
        assert len(results) == 1

        resp_data = results_to_response_model(results[0])

        return resp_data


app.include_router(router)
