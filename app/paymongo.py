"""
Thin wrapper around the PayMongo Checkout Sessions API.
Docs: https://developers.paymongo.com/reference/the-checkout-session-object

PayMongo amounts are integers in centavos (PHP 100.00 = 10000).
"""
import os
import hmac
import hashlib
import httpx

PAYMONGO_API_BASE = "https://api.paymongo.com/v1"


def _secret_key() -> str:
    key = os.getenv("PAYMONGO_SECRET_KEY", "")
    if not key or "xxxx" in key:
        raise RuntimeError(
            "PAYMONGO_SECRET_KEY is not set. Add your real PayMongo secret key to .env "
            "(get it from https://dashboard.paymongo.com/developers)."
        )
    return key


def _auth():
    # PayMongo uses HTTP Basic auth: secret key as username, blank password.
    return (_secret_key(), "")


def php_to_centavos(amount_php) -> int:
    return int(round(float(amount_php) * 100))


def create_checkout_session(
    *,
    amount_php,
    course_title: str,
    buyer_email: str,
    buyer_name: str,
    success_url: str,
    cancel_url: str,
    reference_number: str,
) -> dict:
    """Create a PayMongo Checkout Session and return the raw response data dict."""
    payload = {
        "data": {
            "attributes": {
                "send_email_receipt": True,
                "show_description": True,
                "show_line_items": True,
                "description": f"Enrollment: {course_title}",
                "line_items": [
                    {
                        "currency": "PHP",
                        "amount": php_to_centavos(amount_php),
                        "name": course_title,
                        "quantity": 1,
                    }
                ],
                "payment_method_types": ["gcash", "card", "paymaya"],
                "billing": {"name": buyer_name, "email": buyer_email},
                "reference_number": reference_number,
                "success_url": success_url,
                "cancel_url": cancel_url,
            }
        }
    }
    with httpx.Client(timeout=20.0) as client:
        resp = client.post(
            f"{PAYMONGO_API_BASE}/checkout_sessions",
            json=payload,
            auth=_auth(),
            headers={"Content-Type": "application/json"},
        )
    resp.raise_for_status()
    return resp.json()["data"]


def retrieve_checkout_session(checkout_session_id: str) -> dict:
    with httpx.Client(timeout=20.0) as client:
        resp = client.get(
            f"{PAYMONGO_API_BASE}/checkout_sessions/{checkout_session_id}",
            auth=_auth(),
        )
    resp.raise_for_status()
    return resp.json()["data"]


def checkout_session_is_paid(session_data: dict) -> bool:
    attrs = session_data.get("attributes", {})
    payments = attrs.get("payments") or []
    for p in payments:
        if p.get("attributes", {}).get("status") == "paid":
            return True
    return attrs.get("payment_intent", {}).get("attributes", {}).get("status") == "succeeded"


def verify_webhook_signature(raw_body: bytes, signature_header: str, webhook_secret: str) -> bool:
    """
    PayMongo signs webhooks with a header like:
    t=1631234567,te=abcdef...,li=abcdef...
    'te' is the test-mode signature, 'li' is the live-mode signature (HMAC-SHA256 of "t.body").
    """
    if not signature_header or not webhook_secret:
        return False
    parts = dict(kv.split("=", 1) for kv in signature_header.split(",") if "=" in kv)
    timestamp = parts.get("t")
    provided_sig = parts.get("li") or parts.get("te")
    if not timestamp or not provided_sig:
        return False
    signed_payload = f"{timestamp}.{raw_body.decode('utf-8')}".encode("utf-8")
    expected_sig = hmac.new(webhook_secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_sig, provided_sig)
