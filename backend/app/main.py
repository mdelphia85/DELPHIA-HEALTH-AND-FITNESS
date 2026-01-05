from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import init_db, get_engine

from app.api import auth, users, workouts, uploads, community, leaderboard, chat, profile

app = FastAPI(title="Delphia API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


# Include API Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(workouts.router, prefix="/workouts", tags=["workouts"])
app.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
app.include_router(community.router, prefix="/community", tags=["community"])
app.include_router(leaderboard.router, prefix="/leaderboard", tags=["leaderboard"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
# Simple profile endpoints for the Kivy client (development helper)
app.include_router(profile.router, prefix="/api", tags=["profile"])
