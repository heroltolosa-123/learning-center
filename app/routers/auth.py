from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..auth import hash_password, verify_password

router = APIRouter()


@router.get("/register")
def register_form(request: Request):
    from ..main import templates
    return templates.TemplateResponse("register.html", {"request": request, "user": None, "site_name": request.app.state.site_name})


@router.post("/register")
def register_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    email = email.strip().lower()
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        return RedirectResponse(f"/register?error=An+account+with+that+email+already+exists", status_code=303)
    if len(password) < 8:
        return RedirectResponse(f"/register?error=Password+must+be+at+least+8+characters", status_code=303)

    user = models.User(name=name.strip(), email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)

    request.session["user_id"] = user.id
    return RedirectResponse("/dashboard?flash=Welcome!+Your+account+is+ready.", status_code=303)


@router.get("/login")
def login_form(request: Request):
    from ..main import templates
    return templates.TemplateResponse("login.html", {"request": request, "user": None, "site_name": request.app.state.site_name})


@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    email = email.strip().lower()
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return RedirectResponse("/login?error=Incorrect+email+or+password", status_code=303)

    request.session["user_id"] = user.id
    next_url = request.query_params.get("next") or "/dashboard"
    return RedirectResponse(next_url, status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/?flash=You+have+been+logged+out", status_code=303)
