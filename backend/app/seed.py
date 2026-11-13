"""Load demo data. Safe to re-run: records are upserted by slug."""

import json
import uuid
from pathlib import Path

from sqlalchemy import delete, func, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db import get_engine
from app.models import (
    Business,
    BusinessHours,
    Faq,
    HairLength,
    Service,
    ServiceLengthRule,
    Stylist,
    StylistBreak,
    StylistHours,
)
from app.schemas import BusinessSeed

SEED_FILE = Path(__file__).parent / "seed_data" / "demo_business.json"


def seed_business(session: Session) -> None:
    seed = BusinessSeed.model_validate(json.loads(SEED_FILE.read_text()))
    profile = seed.model_dump(exclude={"hours", "stylists", "hair_lengths", "services", "faqs"})
    updates = {key: value for key, value in profile.items() if key != "slug"}
    business_id = session.scalar(
        insert(Business)
        .values(**profile)
        .on_conflict_do_update(
            index_elements=[Business.slug], set_={**updates, "updated_at": func.now()}
        )
        .returning(Business.id)
    )

    # Hours and FAQs have nothing pointing at them, so the seed file simply replaces them.
    session.execute(delete(BusinessHours).where(BusinessHours.business_id == business_id))
    session.add_all(
        BusinessHours(business_id=business_id, **hours.model_dump()) for hours in seed.hours
    )
    session.execute(delete(Faq).where(Faq.business_id == business_id))
    session.add_all(
        Faq(business_id=business_id, display_order=order, **faq.model_dump())
        for order, faq in enumerate(seed.faqs)
    )

    for stylist in seed.stylists:
        stylist_id = _upsert(
            session,
            Stylist,
            business_id,
            stylist.slug,
            {"display_name": stylist.display_name, "is_active": True},
        )
        session.execute(delete(StylistHours).where(StylistHours.stylist_id == stylist_id))
        session.add_all(
            StylistHours(stylist_id=stylist_id, **period.model_dump()) for period in stylist.hours
        )
        session.execute(delete(StylistBreak).where(StylistBreak.stylist_id == stylist_id))
        session.add_all(
            StylistBreak(stylist_id=stylist_id, **period.model_dump()) for period in stylist.breaks
        )

    # Services and hair lengths keep their ids so that future bookings can reference them.
    length_ids = {
        hair_length.slug: _upsert(
            session,
            HairLength,
            business_id,
            hair_length.slug,
            {**hair_length.model_dump(exclude={"slug"}), "display_order": order},
        )
        for order, hair_length in enumerate(seed.hair_lengths)
    }
    service_ids = []
    for order, service in enumerate(seed.services):
        service_id = _upsert(
            session,
            Service,
            business_id,
            service.slug,
            {
                "name": service.name,
                "description": service.description,
                "is_active": True,
                "display_order": order,
            },
        )
        service_ids.append(service_id)
        session.execute(delete(ServiceLengthRule).where(ServiceLengthRule.service_id == service_id))
        session.add_all(
            ServiceLengthRule(
                service_id=service_id,
                hair_length_id=length_ids[option.hair_length],
                duration_minutes=option.duration_minutes,
                price_cents=option.price_cents,
            )
            for option in service.options
        )
    session.execute(
        update(Service)
        .where(Service.business_id == business_id, Service.id.not_in(service_ids))
        .values(is_active=False)
    )
    session.flush()


def _upsert(
    session: Session,
    model: type[Service | HairLength | Stylist],
    business_id,
    slug: str,
    values: dict,
) -> uuid.UUID:
    return session.scalar(
        insert(model)
        .values(business_id=business_id, slug=slug, **values)
        .on_conflict_do_update(index_elements=[model.business_id, model.slug], set_=values)
        .returning(model.id)
    )


def main() -> None:
    with Session(get_engine()) as session, session.begin():
        seed_business(session)
    print("Demo data seeded.")


if __name__ == "__main__":
    main()
