import os
import shutil
from typing import List

from fastapi import APIRouter, UploadFile, HTTPException, Depends

import config
from models.user import User
from routers.auth.auth_bearer import JWTBearer

router = APIRouter(
    prefix="/image",
    tags=['image']
)


@router.post("/upload_images/")
async def upload_images(files: List[UploadFile], user: User = Depends(JWTBearer())):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    upload_dir = config.IMAGE_PATH
    errors = 0
    ready_files = []

    for file in files:

        content_type = file.content_type
        if content_type not in ["image/jpeg", "image/png", "image/gif"]:
            errors += 1
            continue

        destination = os.path.join(upload_dir, file.filename)

        with open(destination, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ready_files.append(file)

    return {"filenames": [file.filename for file in ready_files], "errors": errors}


@router.get("/get_images/")
async def get_images(user: User = Depends(JWTBearer())):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    upload_dir = config.IMAGE_PATH
    ready_files = []

    for file_path in os.listdir(upload_dir):
        if os.path.isfile(os.path.join(upload_dir, file_path)):
            ready_files.append(file_path)

    return {"filenames": [file for file in ready_files]}


@router.delete("/delete_images/")
async def delete_images(filename: str, user: User = Depends(JWTBearer())):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    upload_dir = config.IMAGE_PATH
    path = os.path.join(upload_dir, filename)

    if os.path.exists(path):
        os.remove(path)
    else:
        return {"status": "failure"}

    return {"status": "success"}
