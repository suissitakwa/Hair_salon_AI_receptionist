from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Booking, Business, HairLength, Service, Stylist


def make_booking(
    db: Session,
    start: datetime,
    minutes: int = 30,
    status: str = "confirmed",
    buffer_minutes: int = 15,
    key: str | None = None,
) -> Booking:
    """Insert a booking directly, bypassing the API, as another customer or staff would."""
    business_id = db.scalar(select(Business.id).where(Business.slug == "shearline-demo"))
    end = start + timedelta(minutes=minutes)
    booking = Booking(
        business_id=business_id,
        stylist_id=db.scalar(select(Stylist.id).where(Stylist.business_id == business_id)),
        service_id=db.scalar(select(Service.id).where(Service.slug == "beard-trim")),
        hair_length_id=db.scalar(select(HairLength.id).where(HairLength.slug == "short")),
        starts_at=start,
        ends_at=end,
        occupied_until=end + timedelta(minutes=buffer_minutes),
        status=status,
        reference=f"SL-T{start:%H%M}{status[:1].upper()}{abs(hash(key or start)) % 1000:03d}",
        price_cents=2000,
        customer_name="Another Customer",
        customer_email="another@example.com",
        customer_phone=None,
        summary={},
        idempotency_key=key or f"factory-{start.isoformat()}-{status}",
        request_hash="0" * 64,
    )
    db.add(booking)
    db.commit()
    return booking
