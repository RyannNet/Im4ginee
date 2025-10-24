from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
import re


EXPLICIT_KEYWORDS = {
    "sex", "sexy", "nude", "naked", "pussy", "penis", "vagina", "boobs", "breasts",
    "cum", "cumshot", "sperm", "semen", "anal", "fuck", "hardcore", "porn", "xxx",
    "fetish", "bondage", "bdsm", "slave", "rape", "tentacle", "fellatio", "blowjob",
    "handjob", "threesome", "orgy", "69", "hentai", "nsfw", "explicit",
}
SOFT_KEYWORDS = {"bikini", "lingerie", "cleavage", "seethrough", "underboob", "nipple"}
FETISH_KEYWORDS = {"feet", "armpit", "pregnant", "macro", "giantess", "vore"}


@dataclass
class NSFWResult:
    action: str  # allow|flag|block
    tags: List[str]


class NSFWSmartClassifier:
    def __init__(self) -> None:
        # Placeholders for possible ML-based safety/nudity detectors
        # In a production setup, integrate multiple detectors and fuse with prompt heuristics
        pass

    def classify_prompt(self, prompt: str) -> NSFWResult:
        lower = prompt.lower()
        tags: List[str] = []
        explicit = any(k in lower for k in EXPLICIT_KEYWORDS)
        soft = any(k in lower for k in SOFT_KEYWORDS)
        fetish = any(k in lower for k in FETISH_KEYWORDS)
        if explicit:
            tags.append("explicit")
        if soft:
            tags.append("soft")
        if fetish:
            tags.append("fetish")
        # Never auto-block purely from prompt; enable admin-in-loop
        action = "flag" if explicit or fetish else "allow"
        return NSFWResult(action=action, tags=tags)

    def classify_image(self, image_path: str) -> NSFWResult:
        # Placeholder: Implement real detectors (e.g., OpenAI safety checker replacement, nude-detector)
        # For now, be permissive and only flag if filename hints explicit content
        lower = image_path.lower()
        tags: List[str] = []
        if any(k in lower for k in EXPLICIT_KEYWORDS):
            tags.append("explicit")
        if any(k in lower for k in SOFT_KEYWORDS):
            tags.append("soft")
        if any(k in lower for k in FETISH_KEYWORDS):
            tags.append("fetish")
        action = "flag" if tags else "allow"
        return NSFWResult(action=action, tags=tags)
