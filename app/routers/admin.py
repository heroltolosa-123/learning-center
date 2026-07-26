from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from slugify import slugify
from ..database import get_db
from .. import models
from ..auth import get_current_user

router = APIRouter(prefix="/admin")


def _require_admin_or_redirect(request: Request, db: Session):
    user = get_current_user(request, db)
    if not user or not user.is_admin:
        return None
    return user


@router.get("")
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    from ..main import templates
    user = _require_admin_or_redirect(request, db)
    if not user:
        return RedirectResponse("/login?next=/admin", status_code=303)

    courses = db.query(models.Course).order_by(models.Course.created_at.desc()).all()
    for c in courses:
        c.paid_count = sum(1 for e in c.enrollments if e.status == "paid")

    return templates.TemplateResponse(
        "admin_dashboard.html", {"request": request, "user": user, "courses": courses, "site_name": request.app.state.site_name}
    )


@router.get("/courses/new")
def new_course_form(request: Request, db: Session = Depends(get_db)):
    from ..main import templates
    user = _require_admin_or_redirect(request, db)
    if not user:
        return RedirectResponse("/login?next=/admin", status_code=303)
    return templates.TemplateResponse(
        "course_form.html", {"request": request, "user": user, "course": None, "site_name": request.app.state.site_name}
    )


@router.post("/courses/new")
def create_course(
    request: Request,
    title: str = Form(...),
    slug: str = Form(...),
    description: str = Form(""),
    instructor_name: str = Form(""),
    category: str = Form(""),
    level: str = Form(""),
    price_php: float = Form(0),
    is_published: str = Form(None),
    db: Session = Depends(get_db),
):
    user = _require_admin_or_redirect(request, db)
    if not user:
        return RedirectResponse("/login?next=/admin", status_code=303)

    clean_slug = slugify(slug)
    if db.query(models.Course).filter(models.Course.slug == clean_slug).first():
        return RedirectResponse("/admin/courses/new?error=That+slug+is+already+taken", status_code=303)

    course = models.Course(
        title=title.strip(), slug=clean_slug, description=description.strip(),
        instructor_name=instructor_name.strip(), category=category.strip(), level=level.strip(),
        price_php=price_php, is_published=bool(is_published),
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return RedirectResponse(f"/admin/courses/{course.id}?flash=Course+created", status_code=303)


@router.get("/courses/{course_id}")
def edit_course_form(course_id: int, request: Request, db: Session = Depends(get_db)):
    from ..main import templates
    user = _require_admin_or_redirect(request, db)
    if not user:
        return RedirectResponse("/login?next=/admin", status_code=303)

    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        return RedirectResponse("/admin?error=Course+not+found", status_code=303)

    return templates.TemplateResponse(
        "course_form.html", {"request": request, "user": user, "course": course, "site_name": request.app.state.site_name}
    )


@router.post("/courses/{course_id}")
def update_course(
    course_id: int,
    request: Request,
    title: str = Form(...),
    slug: str = Form(...),
    description: str = Form(""),
    instructor_name: str = Form(""),
    category: str = Form(""),
    level: str = Form(""),
    price_php: float = Form(0),
    is_published: str = Form(None),
    db: Session = Depends(get_db),
):
    user = _require_admin_or_redirect(request, db)
    if not user:
        return RedirectResponse("/login?next=/admin", status_code=303)

    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        return RedirectResponse("/admin?error=Course+not+found", status_code=303)

    clean_slug = slugify(slug)
    conflict = db.query(models.Course).filter(models.Course.slug == clean_slug, models.Course.id != course_id).first()
    if conflict:
        return RedirectResponse(f"/admin/courses/{course_id}?error=That+slug+is+already+taken", status_code=303)

    course.title = title.strip()
    course.slug = clean_slug
    course.description = description.strip()
    course.instructor_name = instructor_name.strip()
    course.category = category.strip()
    course.level = level.strip()
    course.price_php = price_php
    course.is_published = bool(is_published)
    db.commit()
    return RedirectResponse(f"/admin/courses/{course_id}?flash=Saved", status_code=303)


@router.get("/courses/{course_id}/lessons/new")
def new_lesson_form(course_id: int, request: Request, db: Session = Depends(get_db)):
    from ..main import templates
    user = _require_admin_or_redirect(request, db)
    if not user:
        return RedirectResponse("/login?next=/admin", status_code=303)

    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        return RedirectResponse("/admin?error=Course+not+found", status_code=303)

    return templates.TemplateResponse(
        "lesson_form.html", {"request": request, "user": user, "course": course, "lesson": None, "site_name": request.app.state.site_name}
    )


@router.post("/courses/{course_id}/lessons/new")
def create_lesson(
    course_id: int,
    request: Request,
    title: str = Form(...),
    video_url: str = Form(""),
    content: str = Form(""),
    order: int = Form(0),
    is_preview: str = Form(None),
    db: Session = Depends(get_db),
):
    user = _require_admin_or_redirect(request, db)
    if not user:
        return RedirectResponse("/login?next=/admin", status_code=303)

    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        return RedirectResponse("/admin?error=Course+not+found", status_code=303)

    lesson = models.Lesson(
        course_id=course.id, title=title.strip(), video_url=video_url.strip(),
        content=content, order=order, is_preview=bool(is_preview),
    )
    db.add(lesson)
    db.commit()
    return RedirectResponse(f"/admin/courses/{course_id}?flash=Lesson+added", status_code=303)


@router.get("/courses/{course_id}/lessons/{lesson_id}")
def edit_lesson_form(course_id: int, lesson_id: int, request: Request, db: Session = Depends(get_db)):
    from ..main import templates
    user = _require_admin_or_redirect(request, db)
    if not user:
        return RedirectResponse("/login?next=/admin", status_code=303)

    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id, models.Lesson.course_id == course_id).first()
    if not course or not lesson:
        return RedirectResponse("/admin?error=Not+found", status_code=303)

    return templates.TemplateResponse(
        "lesson_form.html", {"request": request, "user": user, "course": course, "lesson": lesson, "site_name": request.app.state.site_name}
    )


@router.post("/courses/{course_id}/lessons/{lesson_id}")
def update_lesson(
    course_id: int,
    lesson_id: int,
    request: Request,
    title: str = Form(...),
    video_url: str = Form(""),
    content: str = Form(""),
    order: int = Form(0),
    is_preview: str = Form(None),
    db: Session = Depends(get_db),
):
    user = _require_admin_or_redirect(request, db)
    if not user:
        return RedirectResponse("/login?next=/admin", status_code=303)

    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id, models.Lesson.course_id == course_id).first()
    if not lesson:
        return RedirectResponse(f"/admin/courses/{course_id}?error=Lesson+not+found", status_code=303)

    lesson.title = title.strip()
    lesson.video_url = video_url.strip()
    lesson.content = content
    lesson.order = order
    lesson.is_preview = bool(is_preview)
    db.commit()
    return RedirectResponse(f"/admin/courses/{course_id}?flash=Lesson+saved", status_code=303)


@router.get("/courses/{course_id}/lessons/{lesson_id}/delete")
def delete_lesson(course_id: int, lesson_id: int, request: Request, db: Session = Depends(get_db)):
    user = _require_admin_or_redirect(request, db)
    if not user:
        return RedirectResponse("/login?next=/admin", status_code=303)

    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id, models.Lesson.course_id == course_id).first()
    if lesson:
        db.delete(lesson)
        db.commit()
    return RedirectResponse(f"/admin/courses/{course_id}?flash=Lesson+deleted", status_code=303)
