from __future__ import annotations
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Generation, ModerationReview, User
from ...schemas import ModerationReviewCreate, ModerationReviewOut, GenerationOut
from ...security import get_current_admin

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/queue", response_model=List[GenerationOut])
def get_queue(_: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    gens = db.query(Generation).filter(Generation.status.in_(["queued", "flagged"]))\
        .order_by(Generation.created_at.asc()).limit(100).all()
    return gens


@router.post("/review/{generation_id}", response_model=ModerationReviewOut)
def review_generation(
    generation_id: int,
    payload: ModerationReviewCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    gen = db.query(Generation).filter(Generation.id == generation_id).first()
    if not gen:
        raise HTTPException(status_code=404, detail="Generation not found")

    review = ModerationReview(
        generation_id=gen.id,
        reviewer_id=admin.id,
        action=payload.action,
        tags=payload.tags,
        notes=payload.notes,
    )
    gen.nsfw_action = payload.action
    if payload.tags:
        gen.nsfw_tags = payload.tags
    if payload.action == "block":
        gen.status = "blocked"
    elif payload.action == "flag":
        gen.status = "flagged"
    elif payload.action == "allow":
        gen.status = "completed" if gen.output_path else gen.status

    db.add(review)
    db.add(gen)
    db.commit()
    db.refresh(review)
    return review
