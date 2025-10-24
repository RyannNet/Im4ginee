from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import User, Generation
from ...schemas import GenerationCreate, GenerationOut
from ...security import get_current_user
from ...workers.tasks import task_txt2img, task_img2img, task_upscale, task_txt2video, task_img2video

router = APIRouter(prefix="/api/v1/generate", tags=["generate"])


@router.post("/image", response_model=GenerationOut)
def generate_image(
    payload: GenerationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if payload.type not in ("image", "upscale"):
        raise HTTPException(status_code=400, detail="type must be 'image' or 'upscale'")

    gen = Generation(
        user_id=user.id,
        type="image" if payload.type == "image" else "upscale",
        mode=payload.mode,
        prompt=payload.prompt,
        negative_prompt=payload.negative_prompt,
        seed=payload.seed,
        steps=payload.steps,
        width=payload.width,
        height=payload.height,
        style=payload.style,
        status="queued",
    )
    db.add(gen)
    db.commit()
    db.refresh(gen)

    if payload.type == "image":
        task_txt2img.delay(gen.id)
    else:
        task_upscale.delay(gen.id)

    return gen


@router.post("/image-from", response_model=GenerationOut)
def generate_image_from(
    payload: GenerationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    gen = Generation(
        user_id=user.id,
        type="image",
        mode=payload.mode,
        prompt=payload.prompt,
        negative_prompt=payload.negative_prompt,
        seed=payload.seed,
        steps=payload.steps,
        width=payload.width,
        height=payload.height,
        style=payload.style,
        source_path=payload.source_path,
        status="queued",
    )
    db.add(gen)
    db.commit()
    db.refresh(gen)

    task_img2img.delay(gen.id)
    return gen


@router.post("/video", response_model=GenerationOut)
def generate_video(
    payload: GenerationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    gen = Generation(
        user_id=user.id,
        type="video",
        mode=payload.mode,
        prompt=payload.prompt,
        negative_prompt=payload.negative_prompt,
        seed=payload.seed,
        steps=payload.steps,
        width=payload.width,
        height=payload.height,
        style=payload.style,
        source_path=payload.source_path,
        status="queued",
    )
    db.add(gen)
    db.commit()
    db.refresh(gen)

    if payload.source_path:
        task_img2video.delay(gen.id)
    else:
        task_txt2video.delay(gen.id)

    return gen
