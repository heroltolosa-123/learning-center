import datetime
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..auth import get_current_user

router = APIRouter()


@router.get("/")
def homepage(request: Request, db: Session = Depends(get_db), q: str = "", category: str = ""):
    from ..main import templates
    user = get_current_user(request, db)

    base_query = db.query(models.Course).filter(models.Course.is_published == True)  # noqa: E712
    all_published = base_query.all()
    categories = sorted({c.category for c in all_published if c.category})

    query = base_query
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            (models.Course.title.ilike(like)) | (models.Course.description.ilike(like))
        )
    if category:
        query = query.filter(models.Course.category == category)

    courses = query.order_by(models.Course.created_at.desc()).all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request, "user": user, "courses": courses, "site_name": request.app.state.site_name,
            "categories": categories, "q": q, "active_category": category,
            "total_count": len(all_published),
        },
    )


@router.get("/courses/{slug}")
def course_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    from ..main import templates
    user = get_current_user(request, db)
    course = db.query(models.Course).filter(models.Course.slug == slug).first()
    if not course or (not course.is_published and not (user and user.is_admin)):
        return RedirectResponse("/?error=Course+not+found", status_code=303)

    enrollment = None
    if user:
        enrollment = (
            db.query(models.Enrollment)
            .filter(models.Enrollment.user_id == user.id, models.Enrollment.course_id == course.id)
            .first()
        )

    return templates.TemplateResponse(
        "course_detail.html",
        {
            "request": request, "user": user, "course": course, "enrollment": enrollment,
            "site_name": request.app.state.site_name,
        },
    )


@router.post("/courses/{slug}/enroll-free")
def enroll_free(slug: str, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(f"/login?next=/courses/{slug}", status_code=303)

    course = db.query(models.Course).filter(models.Course.slug == slug).first()
    if not course or not course.is_free:
        return RedirectResponse(f"/courses/{slug}?error=This+course+is+not+free", status_code=303)

    enrollment = (
        db.query(models.Enrollment)
        .filter(models.Enrollment.user_id == user.id, models.Enrollment.course_id == course.id)
        .first()
    )
    if not enrollment:
        enrollment = models.Enrollment(user_id=user.id, course_id=course.id)
        db.add(enrollment)
    enrollment.status = "paid"
    enrollment.paid_at = datetime.datetime.utcnow()
    db.commit()
    return RedirectResponse(f"/courses/{slug}?flash=Enrolled!", status_code=303)


@router.get("/lessons/{lesson_id}")
def view_lesson(lesson_id: int, request: Request, db: Session = Depends(get_db)):
    from ..main import templates
    user = get_current_user(request, db)
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        return RedirectResponse("/?error=Lesson+not+found", status_code=303)
    course = lesson.course

    unlocked = lesson.is_preview or (user and user.is_admin)
    if not unlocked and user:
        enrollment = (
            db.query(models.Enrollment)
            .filter(
                models.Enrollment.user_id == user.id,
                models.Enrollment.course_id == course.id,
                models.Enrollment.status == "paid",
            )
            .first()
        )
        unlocked = enrollment is not None

    if not unlocked:
        if not user:
            return RedirectResponse(f"/login?next=/lessons/{lesson_id}", status_code=303)
        return RedirectResponse(f"/courses/{course.slug}?error=Enroll+to+access+this+lesson", status_code=303)

    ordered_lessons = course.lessons  # already ordered by Lesson.order via relationship
    idx = next((i for i, l in enumerate(ordered_lessons) if l.id == lesson.id), 0)
    prev_lesson = ordered_lessons[idx - 1] if idx > 0 else None
    next_lesson = ordered_lessons[idx + 1] if idx < len(ordered_lessons) - 1 else None

    return templates.TemplateResponse(
        "lesson.html",
        {
            "request": request, "user": user, "lesson": lesson, "course": course,
            "lesson_index": idx + 1, "prev_lesson": prev_lesson, "next_lesson": next_lesson,
            "site_name": request.app.state.site_name,
        },
    )


@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    from ..main import templates
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login?next=/dashboard", status_code=303)

    enrollments = (
        db.query(models.Enrollment)
        .filter(models.Enrollment.user_id == user.id)
        .order_by(models.Enrollment.created_at.desc())
        .all()
    )
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user, "enrollments": enrollments, "site_name": request.app.state.site_name},
    )
