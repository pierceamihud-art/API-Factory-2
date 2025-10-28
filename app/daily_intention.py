from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from datetime import datetime
import random
from typing import List

from app.rate_limiter import get_rate_limiter

router = APIRouter()

# Use centralized auth dependency
from app.auth import get_api_key  # noqa: E402

# rate limiter singleton
_rate_limiter = get_rate_limiter()


class Profile(BaseModel):
    values: List[str] = Field(default_factory=lambda: ["presence", "gratitude", "peace"])
    tradition: str = "secular"


class Context(BaseModel):
    mood: str = "neutral"
    time: str = "morning"
    moon_phase: str = "full"


class IntentionRequest(BaseModel):
    profile: Profile
    context: Context


INTENTIONS = [
    "Today I choose peace over worry.",
    "I am grounded, centered, and calm.",
    "I trust the flow of life.",
    "I welcome change as growth.",
    "I bring light to everything I do."
]

AFFIRMATIONS = [
    "I am exactly where I need to be.",
    "My energy creates my reality.",
    "Gratitude opens the door to abundance.",
    "I release what no longer serves me.",
    "I breathe in clarity, exhale doubt."
]

RITUALS = [
    {"type": "breathwork", "steps": "Inhale 4 sec, hold 4 sec, exhale 4 sec, hold 4 sec (Box breathing)"},
    {"type": "journaling", "prompt": "Write down 3 things you are thankful for."},
    {"type": "movement", "prompt": "Stretch your body gently for 3 minutes while breathing deeply."},
    {"type": "reflection", "prompt": "Visualize your ideal day unfolding with ease."}
]


@router.get("/")
def root():
    return {
        "message": "Welcome to the Daily Intention API 🌞",
        "docs": "/docs",
        "version": "1.0.0"
    }


@router.post("/intention")
async def generate_intention(request: IntentionRequest, api_key: str = Depends(get_api_key)):
    try:
        # rate-limit per API key (async)
        if await _rate_limiter.is_rate_limited(api_key):
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")

        profile = request.profile
        context = request.context

        seed = hash(f"{profile.values}{context.mood}{context.time}{datetime.now().date()}")
        random.seed(seed)

        intention = random.choice(INTENTIONS)
        affirmation = random.choice(AFFIRMATIONS)
        ritual = random.choice(RITUALS)

        # Support both pydantic v1 and v2 serialization APIs
        try:
            profile_data = profile.model_dump()
        except Exception:
            profile_data = profile.dict()

        try:
            context_data = context.model_dump()
        except Exception:
            context_data = context.dict()

        return {
            "timestamp": datetime.now().isoformat(),
            "profile": profile_data,
            "context": context_data,
            "intention": intention,
            "affirmation": affirmation,
            "ritual": ritual
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
