from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models import Profile, User

router = APIRouter()

# Note: For now we use a simple unauthenticated approach and operate on a single test user (user_id=1).
# This is a placeholder until auth is wired; it makes the Kivy client able to store/load a profile during development.

@router.get("/profile")
def get_profile(session: Session = Depends(get_session)):
    # Ensure a user exists
    user = session.exec(select(User).where(User.id == 1)).first()
    if not user:
        user = User(id=1, email="dev@example.com", username="dev", hashed_password="")
        session.add(user)
        session.commit()
        session.refresh(user)

    profile = session.exec(select(Profile).where(Profile.user_id == user.id)).first()
    if not profile:
        # Return an empty profile object structure
        return {
            "name": None,
            "dob": None,
            "gender": None,
            "height_value": None,
            "starting_weight": None,
            "total_weight": None,
        }

    return {
        "name": profile.display_name,
        "dob": profile.dob,
        "gender": profile.gender,
        "height_value": profile.height_value,
        "starting_weight": profile.weight,
        "total_weight": profile.weight,
    }

@router.post("/profile")
def upsert_profile(payload: dict, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.id == 1)).first()
    if not user:
        user = User(id=1, email="dev@example.com", username="dev", hashed_password="")
        session.add(user)
        session.commit()
        session.refresh(user)

    profile = session.exec(select(Profile).where(Profile.user_id == user.id)).first()
    if not profile:
        profile = Profile(user_id=user.id)

    # Map incoming payload fields
    profile.display_name = payload.get("name") or payload.get("display_name")
    profile.dob = payload.get("dob")
    profile.gender = payload.get("gender")
    profile.height_value = payload.get("height_value")
    # Use starting_weight/total_weight if provided
    w = payload.get("total_weight") or payload.get("starting_weight")
    profile.weight = w

    session.add(profile)
    session.commit()
    session.refresh(profile)

    return {"status": "ok", "id": profile.id}
