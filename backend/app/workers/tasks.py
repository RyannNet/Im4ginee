from __future__ import annotations
import os
from typing import Optional

from PIL import Image
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import SessionLocal
from ..models import Generation
from ..core.models_loader import registry
from ..core.nsfw_pipeline import NSFWSmartClassifier
from .celery_app import celery_app


settings = get_settings()


def _update_status(session: Session, gen: Generation, status: str, error: Optional[str] = None):
    gen.status = status
    gen.error = error
    session.add(gen)
    session.commit()


def _apply_nsfw_smart(gen: Generation, output_path: str, session: Session):
    classifier: NSFWSmartClassifier = registry.nsfw or NSFWSmartClassifier()
    # Combine prompt-based and output-based assessments
    prompt_res = classifier.classify_prompt(gen.prompt)
    image_res = classifier.classify_image(output_path)
    tags = list({*prompt_res.tags, *image_res.tags})
    if tags:
        gen.nsfw_tags = ",".join(tags)
    # Merge actions: block > flag > allow; but keep human-in-loop, don't auto-block
    action = "flag" if ("explicit" in tags or "fetish" in tags) else "allow"
    gen.nsfw_action = action
    # If admin has not overridden, set status accordingly
    if gen.status not in ("blocked", "completed"):
        gen.status = "flagged" if action == "flag" else "completed"
    session.add(gen)
    session.commit()


@celery_app.task(name="app.workers.tasks.task_txt2img")
def task_txt2img(gen_id: int):
    session = SessionLocal()
    try:
        gen = session.query(Generation).get(gen_id)
        if not gen:
            return
        _update_status(session, gen, "running")

        # Generate image via Stable Diffusion if available; else create placeholder
        registry.load_all()
        output_dir = os.path.join(settings.STORAGE_DIR, settings.IMAGES_DIR_NAME)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"gen_{gen.id}.png")

        if registry.sd_pipeline:
            pipe = registry.sd_pipeline
            result = pipe(
                prompt=gen.prompt,
                negative_prompt=gen.negative_prompt,
                num_inference_steps=gen.steps or 30,
                width=gen.width or 512,
                height=gen.height or 512,
                generator=None,
            )
            image = result.images[0]
            image.save(output_path)
        else:
            # Placeholder: black image with text
            img = Image.new("RGB", (gen.width or 512, gen.height or 512), color=(0, 0, 0))
            img.save(output_path)

        gen.output_path = output_path
        session.add(gen)
        session.commit()

        if gen.mode == "nsfw_smart":
            _apply_nsfw_smart(gen, output_path, session)
        else:
            _update_status(session, gen, "completed")
    except Exception as e:
        if 'gen' in locals():
            _update_status(session, gen, "failed", error=str(e))
        raise
    finally:
        session.close()


@celery_app.task(name="app.workers.tasks.task_img2img")
def task_img2img(gen_id: int):
    session = SessionLocal()
    try:
        gen = session.query(Generation).get(gen_id)
        if not gen:
            return
        _update_status(session, gen, "running")

        registry.load_all()
        output_dir = os.path.join(settings.STORAGE_DIR, settings.IMAGES_DIR_NAME)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"gen_{gen.id}.png")

        if registry.img2img_pipeline and gen.source_path and os.path.exists(gen.source_path):
            init_image = Image.open(gen.source_path).convert("RGB")
            pipe = registry.img2img_pipeline
            result = pipe(
                prompt=gen.prompt,
                image=init_image,
                strength=0.6,
                guidance_scale=7.5,
                num_inference_steps=gen.steps or 30,
            )
            image = result.images[0]
            image.save(output_path)
        else:
            # Fallback: copy or create placeholder
            if gen.source_path and os.path.exists(gen.source_path):
                Image.open(gen.source_path).save(output_path)
            else:
                Image.new("RGB", (gen.width or 512, gen.height or 512), color=(0, 0, 0)).save(output_path)

        gen.output_path = output_path
        session.add(gen)
        session.commit()

        if gen.mode == "nsfw_smart":
            _apply_nsfw_smart(gen, output_path, session)
        else:
            _update_status(session, gen, "completed")
    except Exception as e:
        if 'gen' in locals():
            _update_status(session, gen, "failed", error=str(e))
        raise
    finally:
        session.close()


@celery_app.task(name="app.workers.tasks.task_upscale")
def task_upscale(gen_id: int):
    session = SessionLocal()
    try:
        gen = session.query(Generation).get(gen_id)
        if not gen:
            return
        _update_status(session, gen, "running")

        registry.load_all()
        output_dir = os.path.join(settings.STORAGE_DIR, settings.UPSCALES_DIR_NAME)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"gen_{gen.id}.png")

        if registry.upscaler and gen.source_path and os.path.exists(gen.source_path):
            img = Image.open(gen.source_path).convert("RGB")
            upscaled = registry.upscaler.predict(img)
            upscaled.save(output_path)
        else:
            # Placeholder: copy as is
            if gen.source_path and os.path.exists(gen.source_path):
                Image.open(gen.source_path).save(output_path)
            else:
                Image.new("RGB", (gen.width or 512, gen.height or 512), color=(0, 0, 0)).save(output_path)

        gen.output_path = output_path
        session.add(gen)
        session.commit()

        if gen.mode == "nsfw_smart":
            _apply_nsfw_smart(gen, output_path, session)
        else:
            _update_status(session, gen, "completed")
    except Exception as e:
        if 'gen' in locals():
            _update_status(session, gen, "failed", error=str(e))
        raise
    finally:
        session.close()


@celery_app.task(name="app.workers.tasks.task_txt2video")
def task_txt2video(gen_id: int):
    session = SessionLocal()
    try:
        gen = session.query(Generation).get(gen_id)
        if not gen:
            return
        _update_status(session, gen, "running")

        # Placeholder video creation using ffmpeg: create a black mp4 with prompt as metadata
        output_dir = os.path.join(settings.STORAGE_DIR, settings.VIDEOS_DIR_NAME)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"gen_{gen.id}.mp4")

        # Try to create a 2-second black video using ffmpeg if available
        try:
            os.system(
                f"ffmpeg -y -f lavfi -i color=c=black:s={gen.width or 512}x{gen.height or 512}:d=2 -pix_fmt yuv420p {output_path} >/dev/null 2>&1"
            )
        except Exception:
            # If ffmpeg not available, just create an empty file
            open(output_path, "wb").close()

        gen.output_path = output_path
        session.add(gen)
        session.commit()

        # NSFW smart applies conceptually; videos could be assessed by first frame for placeholder
        if gen.mode == "nsfw_smart":
            _apply_nsfw_smart(gen, output_path, session)
        else:
            _update_status(session, gen, "completed")
    except Exception as e:
        if 'gen' in locals():
            _update_status(session, gen, "failed", error=str(e))
        raise
    finally:
        session.close()


@celery_app.task(name="app.workers.tasks.task_img2video")
def task_img2video(gen_id: int):
    session = SessionLocal()
    try:
        gen = session.query(Generation).get(gen_id)
        if not gen:
            return
        _update_status(session, gen, "running")

        output_dir = os.path.join(settings.STORAGE_DIR, settings.VIDEOS_DIR_NAME)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"gen_{gen.id}.mp4")

        if gen.source_path and os.path.exists(gen.source_path):
            # Create a short zoom/pan effect video from the image if ffmpeg is available
            try:
                # Simple still image to video
                os.system(
                    f"ffmpeg -y -loop 1 -t 2 -i {gen.source_path} -vf scale={gen.width or 512}:{gen.height or 512} -pix_fmt yuv420p {output_path} >/dev/null 2>&1"
                )
            except Exception:
                open(output_path, "wb").close()
        else:
            try:
                os.system(
                    f"ffmpeg -y -f lavfi -i color=c=black:s={gen.width or 512}x{gen.height or 512}:d=2 -pix_fmt yuv420p {output_path} >/dev/null 2>&1"
                )
            except Exception:
                open(output_path, "wb").close()

        gen.output_path = output_path
        session.add(gen)
        session.commit()

        if gen.mode == "nsfw_smart":
            _apply_nsfw_smart(gen, output_path, session)
        else:
            _update_status(session, gen, "completed")
    except Exception as e:
        if 'gen' in locals():
            _update_status(session, gen, "failed", error=str(e))
        raise
    finally:
        session.close()
