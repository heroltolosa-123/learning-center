import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from .database import Base, engine, SessionLocal
from . import models
from .auth import hash_password
from .routers import auth as auth_router, courses as courses_router, admin as admin_router, payments as payments_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Learning Center")
app.state.site_name = os.getenv("SITE_NAME", "The Learning Center")

session_secret = os.getenv("SESSION_SECRET", "dev-only-insecure-secret-change-me")
app.add_middleware(SessionMiddleware, secret_key=session_secret, same_site="lax")

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.include_router(auth_router.router)
app.include_router(courses_router.router)
app.include_router(admin_router.router)
app.include_router(payments_router.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    _seed_admin()


def _seed_admin():
    admin_email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    admin_password = os.getenv("ADMIN_PASSWORD", "")
    admin_name = os.getenv("ADMIN_NAME", "Admin")
    if not admin_email or not admin_password:
        return

    db = SessionLocal()
    try:
        existing = db.query(models.User).filter(models.User.email == admin_email).first()
        if existing:
            if not existing.is_admin:
                existing.is_admin = True
                db.commit()
            return
        admin_user = models.User(
            name=admin_name, email=admin_email,
            password_hash=hash_password(admin_password), is_admin=True,
        )
        db.add(admin_user)
        db.commit()
        print(f"[setup] Created admin account: {admin_email}")
    finally:
        db.close()
