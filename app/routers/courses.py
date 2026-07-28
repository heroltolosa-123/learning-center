import datetime
import json
import markdown
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..auth import get_current_user
from ..certificates import generate_certificate_pdf

router = APIRouter()


def render_lesson_content(raw_content: str) -> str:
    return markdown.markdown(raw_content or "", extensions=["extra", "sane_lists"])


def course_progress(db: Session, user: models.User, course: models.Course):
    """Returns (completed_count, total_count, percent, is_complete) for a user's progress in a course."""
    total = len(course.lessons)
    if total == 0 or not user:
        return 0, total, 0, False
    lesson_ids = [l.id for l in course.lessons]
    completed = (
        db.query(models.LessonProgress)
        .filter(models.LessonProgress.user_id == user.id, models.LessonProgress.lesson_id.in_(lesson_ids))
        .count()
    )
    percent = int(round((completed / total) * 100)) if total else 0
    return completed, total, percent, completed >= total


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
    if not course:
        return RedirectResponse("/?error=Course+not+found", status_code=303)

    enrollment = (
        db.query(models.Enrollment)
        .filter(models.Enrollment.user_id == user.id, models.Enrollment.course_id == course.id)
        .first()
    )
    if not enrollment:
        enrollment = models.Enrollment(user_id=user.id, course_id=course.id)
        db.add(enrollment)
    enrollment.status = "paid"  # "paid" here just means "active enrollment" -- course access itself is free
    enrollment.paid_at = datetime.datetime.utcnow()
    db.commit()
    return RedirectResponse(f"/courses/{slug}?flash=You're+enrolled+—+start+learning!", status_code=303)


@router.get("/lessons/{lesson_id}")
def view_lesson(lesson_id: int, request: Request, db: Session = Depends(get_db), quiz: str = ""):
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

    # Enforce sequential progression: can't skip ahead of an unpassed quiz, unless admin.
    if user and not user.is_admin and prev_lesson:
        prev_has_quiz = bool(prev_lesson.quiz_json)
        if prev_has_quiz:
            prev_passed = (
                db.query(models.LessonProgress)
                .filter(models.LessonProgress.user_id == user.id, models.LessonProgress.lesson_id == prev_lesson.id)
                .first()
            ) is not None
            if not prev_passed:
                return RedirectResponse(
                    f"/lessons/{prev_lesson.id}?error=Pass+this+lesson's+quiz+first+to+continue", status_code=303
                )

    quiz_questions = []
    if lesson.quiz_json:
        try:
            quiz_questions = json.loads(lesson.quiz_json)
        except (ValueError, TypeError):
            quiz_questions = []

    already_passed = False
    if user:
        already_passed = (
            db.query(models.LessonProgress)
            .filter(models.LessonProgress.user_id == user.id, models.LessonProgress.lesson_id == lesson.id)
            .first()
        ) is not None

        if not quiz_questions and not already_passed:
            # No quiz on this lesson (e.g. a "Further Reading" lesson) -- viewing it is enough.
            db.add(models.LessonProgress(user_id=user.id, lesson_id=lesson.id))
            db.commit()
            already_passed = True

    return templates.TemplateResponse(
        "lesson.html",
        {
            "request": request, "user": user, "lesson": lesson, "course": course,
            "lesson_index": idx + 1, "prev_lesson": prev_lesson, "next_lesson": next_lesson,
            "lesson_html": render_lesson_content(lesson.content),
            "quiz_questions": quiz_questions, "already_passed": already_passed, "quiz_result": quiz,
            "site_name": request.app.state.site_name,
        },
    )


@router.post("/lessons/{lesson_id}/quiz-submit")
async def submit_quiz(lesson_id: int, request: Request, db: Session = Depends(get_db)):
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        return RedirectResponse("/?error=Lesson+not+found", status_code=303)
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(f"/login?next=/lessons/{lesson_id}", status_code=303)

    quiz_questions = []
    if lesson.quiz_json:
        try:
            quiz_questions = json.loads(lesson.quiz_json)
        except (ValueError, TypeError):
            quiz_questions = []

    if not quiz_questions:
        return RedirectResponse(f"/lessons/{lesson_id}", status_code=303)

    form = await request.form()
    all_correct = True
    for i, q in enumerate(quiz_questions):
        submitted = form.get(f"q{i}")
        if submitted is None or int(submitted) != int(q["correct"]):
            all_correct = False
            break

    if all_correct:
        already = (
            db.query(models.LessonProgress)
            .filter(models.LessonProgress.user_id == user.id, models.LessonProgress.lesson_id == lesson.id)
            .first()
        )
        if not already:
            db.add(models.LessonProgress(user_id=user.id, lesson_id=lesson.id))
            db.commit()
        return RedirectResponse(f"/lessons/{lesson_id}?quiz=pass", status_code=303)

    return RedirectResponse(f"/lessons/{lesson_id}?quiz=fail", status_code=303)


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
    progress_by_enrollment = {}
    for e in enrollments:
        completed, total, percent, is_complete = course_progress(db, user, e.course)
        progress_by_enrollment[e.id] = {
            "completed": completed, "total": total, "percent": percent, "is_complete": is_complete,
        }

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request, "user": user, "enrollments": enrollments,
            "progress_by_enrollment": progress_by_enrollment, "site_name": request.app.state.site_name,
        },
    )


@router.get("/certificates/{slug}")
def download_certificate(slug: str, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(f"/login?next=/courses/{slug}", status_code=303)

    course = db.query(models.Course).filter(models.Course.slug == slug).first()
    if not course:
        return RedirectResponse("/?error=Course+not+found", status_code=303)

    enrollment = (
        db.query(models.Enrollment)
        .filter(
            models.Enrollment.user_id == user.id,
            models.Enrollment.course_id == course.id,
            models.Enrollment.status == "paid",
        )
        .first()
    )
    if not enrollment:
        return RedirectResponse(f"/courses/{slug}?error=Enroll+first+—+it's+free", status_code=303)

    completed, total, percent, is_complete = course_progress(db, user, course)
    if not is_complete:
        return RedirectResponse(
            f"/courses/{slug}?error=Finish+all+lessons+to+unlock+your+certificate+({completed}/{total}+done)",
            status_code=303,
        )

    if not enrollment.certificate_paid_at:
        if float(course.price_php or 0) <= 0:
            # Certificate fee is free for this course -- grant it automatically.
            enrollment.certificate_paid_at = datetime.datetime.utcnow()
            db.commit()
        else:
            return RedirectResponse(
                f"/dashboard?error=Pay+the+certificate+fee+for+{course.title.replace(' ', '+')}+to+download+it",
                status_code=303,
            )

    pdf_bytes = generate_certificate_pdf(
        student_name=user.name,
        course_title=course.title,
        site_name=request.app.state.site_name,
        completed_date=enrollment.certificate_paid_at.date(),
    )
    filename = f"certificate-{course.slug}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
