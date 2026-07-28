import os
import datetime
import json
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..auth import get_current_user
from .. import paymongo
from .courses import course_progress

router = APIRouter()


def _base_url(request: Request) -> str:
    return os.getenv("BASE_URL", str(request.base_url).rstrip("/"))


@router.post("/courses/{slug}/certificate/checkout")
def start_certificate_checkout(slug: str, request: Request, db: Session = Depends(get_db)):
    """Starts a PayMongo checkout for the CERTIFICATE fee. Course access itself is always free."""
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
        return RedirectResponse(f"/courses/{slug}?error=Enroll+first+—+it's+free", status_code=303)

    if enrollment.certificate_paid_at:
        return RedirectResponse(f"/certificates/{slug}", status_code=303)

    completed, total, percent, is_complete = course_progress(db, user, course)
    if not is_complete:
        return RedirectResponse(
            f"/courses/{slug}?error=Finish+all+lessons+first+({completed}/{total}+done)", status_code=303
        )

    if float(course.price_php or 0) <= 0:
        enrollment.certificate_paid_at = datetime.datetime.utcnow()
        db.commit()
        return RedirectResponse(f"/certificates/{slug}", status_code=303)

    base = _base_url(request)
    try:
        session_data = paymongo.create_checkout_session(
            amount_php=course.price_php,
            course_title=f"Certificate: {course.title}",
            buyer_email=user.email,
            buyer_name=user.name,
            success_url=f"{base}/checkout/success?enrollment_id={enrollment.id}",
            cancel_url=f"{base}/checkout/cancel?slug={course.slug}",
            reference_number=f"CERT-{enrollment.id}",
        )
    except RuntimeError as e:
        return RedirectResponse(f"/courses/{slug}?error={str(e).replace(' ', '+')}", status_code=303)
    except Exception:
        return RedirectResponse(f"/courses/{slug}?error=Payment+gateway+error.+Please+try+again.", status_code=303)

    payment = models.Payment(
        enrollment_id=enrollment.id,
        paymongo_checkout_session_id=session_data["id"],
        amount_php=course.price_php,
        status="pending",
    )
    db.add(payment)
    db.commit()

    checkout_url = session_data["attributes"]["checkout_url"]
    return RedirectResponse(checkout_url, status_code=303)


@router.get("/checkout/success")
def checkout_success(enrollment_id: int, request: Request, db: Session = Depends(get_db)):
    enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if not enrollment:
        return RedirectResponse("/?error=Enrollment+not+found", status_code=303)

    payment = (
        db.query(models.Payment)
        .filter(models.Payment.enrollment_id == enrollment.id)
        .order_by(models.Payment.created_at.desc())
        .first()
    )
    if payment and payment.paymongo_checkout_session_id:
        try:
            session_data = paymongo.retrieve_checkout_session(payment.paymongo_checkout_session_id)
            if paymongo.checkout_session_is_paid(session_data):
                payment.status = "paid"
                enrollment.certificate_paid_at = datetime.datetime.utcnow()
                db.commit()
                return RedirectResponse(
                    f"/certificates/{enrollment.course.slug}?flash=Payment+received!+Downloading+your+certificate...",
                    status_code=303,
                )
        except Exception:
            pass

    return RedirectResponse(
        f"/courses/{enrollment.course.slug}?flash=Payment+is+processing.+This+page+will+update+once+confirmed.",
        status_code=303,
    )


@router.get("/checkout/cancel")
def checkout_cancel(slug: str):
    return RedirectResponse(f"/courses/{slug}?error=Certificate+payment+was+cancelled", status_code=303)


@router.post("/webhooks/paymongo")
async def paymongo_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Register this URL in the PayMongo dashboard: {BASE_URL}/webhooks/paymongo
    Only works when this app is deployed with a public URL (e.g. on Render) —
    PayMongo cannot reach localhost. The /checkout/success route above already
    verifies payment directly with the API as a fallback for local testing.
    """
    raw_body = await request.body()
    signature_header = request.headers.get("Paymongo-Signature", "")
    webhook_secret = os.getenv("PAYMONGO_WEBHOOK_SECRET", "")

    if not paymongo.verify_webhook_signature(raw_body, signature_header, webhook_secret):
        return JSONResponse({"error": "invalid signature"}, status_code=400)

    event = json.loads(raw_body)
    event_type = event.get("data", {}).get("attributes", {}).get("type", "")
    event_data = event.get("data", {}).get("attributes", {}).get("data", {})

    if event_type == "checkout_session.payment.paid":
        checkout_session_id = event_data.get("id")
        payment = (
            db.query(models.Payment)
            .filter(models.Payment.paymongo_checkout_session_id == checkout_session_id)
            .first()
        )
        if payment:
            payment.status = "paid"
            payment.raw_event = raw_body.decode("utf-8")[:5000]
            enrollment = payment.enrollment
            enrollment.certificate_paid_at = datetime.datetime.utcnow()
            db.commit()

    return JSONResponse({"received": True})
