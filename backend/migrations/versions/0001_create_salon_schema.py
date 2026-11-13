"""Create the salon schema

One revision for the whole first release. btree_gist comes first because the booking
exclusion constraint needs it, so a managed host that refuses the extension fails on the
first deploy rather than later.

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.create_table(
        "businesses",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("tagline", sa.String(length=200), nullable=False),
        sa.Column("about", sa.Text(), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("contact_email", sa.String(length=254), nullable=False),
        sa.Column("contact_phone", sa.String(length=32), nullable=False),
        sa.Column("address", sa.String(length=200), nullable=False),
        sa.Column("is_demo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "slot_increment_minutes", sa.Integer(), server_default=sa.text("15"), nullable=False
        ),
        sa.Column("buffer_minutes", sa.Integer(), server_default=sa.text("15"), nullable=False),
        sa.Column(
            "min_notice_minutes", sa.Integer(), server_default=sa.text("120"), nullable=False
        ),
        sa.Column(
            "booking_horizon_days", sa.Integer(), server_default=sa.text("30"), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("slot_increment_minutes > 0", name="slot_increment_positive"),
        sa.CheckConstraint("buffer_minutes >= 0", name="buffer_not_negative"),
        sa.CheckConstraint("min_notice_minutes >= 0", name="min_notice_not_negative"),
        sa.CheckConstraint("booking_horizon_days > 0", name="horizon_positive"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "business_hours",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("weekday", sa.SmallInteger(), nullable=False),
        sa.Column("opens_at", sa.Time(), nullable=False),
        sa.Column("closes_at", sa.Time(), nullable=False),
        sa.CheckConstraint("closes_at > opens_at", name="closes_after_opens"),
        sa.CheckConstraint("weekday BETWEEN 0 AND 6", name="weekday_range"),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_id", "weekday"),
    )
    op.create_table(
        "faqs",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("question", sa.String(length=200), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_id", "slug"),
    )
    op.create_table(
        "hair_lengths",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=32), nullable=False),
        sa.Column("label", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(length=200), nullable=False),
        sa.Column(
            "requires_consultation", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_id", "slug"),
    )
    op.create_table(
        "services",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_id", "slug"),
    )
    op.create_table(
        "staff_users",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("display_name", sa.String(length=80), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("failed_attempts", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_id", "email", name="uq_staff_users_business_email"),
    )
    op.create_table(
        "stylists",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_id", "slug"),
    )
    op.create_table(
        "voice_sessions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("mode", sa.String(length=8), nullable=False),
        sa.Column("model", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=16), server_default="started", nullable=False),
        sa.Column("end_reason", sa.String(length=32), nullable=True),
        sa.Column("client_hash", sa.String(length=64), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("usage", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tool_calls", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("tool_failures", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("booking_reference", sa.String(length=16), nullable=True),
        sa.CheckConstraint("mode IN ('test', 'live')", name="voice_mode_known"),
        sa.CheckConstraint("status IN ('started', 'ended')", name="voice_status_known"),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_table(
        "blocked_periods",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("stylist_id", sa.Uuid(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.String(length=200), server_default="", nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("ends_at > starts_at", name="blocked_end_after_start"),
        sa.ForeignKeyConstraint(["created_by"], ["staff_users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["stylist_id"], ["stylists.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "booking_drafts",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("stylist_id", sa.Uuid(), nullable=False),
        sa.Column("service_id", sa.Uuid(), nullable=False),
        sa.Column("hair_length_id", sa.Uuid(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("occupied_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("customer_name", sa.String(length=80), nullable=False),
        sa.Column("customer_email", sa.String(length=254), nullable=True),
        sa.Column("customer_phone", sa.String(length=20), nullable=True),
        sa.Column("summary", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("summary_hash", sa.String(length=64), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("voice_session_id", sa.Uuid(), nullable=True),
        sa.CheckConstraint(
            "customer_email IS NOT NULL OR customer_phone IS NOT NULL", name="draft_has_contact"
        ),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["hair_length_id"],
            ["hair_lengths.id"],
        ),
        sa.ForeignKeyConstraint(
            ["service_id"],
            ["services.id"],
        ),
        sa.ForeignKeyConstraint(
            ["stylist_id"],
            ["stylists.id"],
        ),
        sa.ForeignKeyConstraint(["voice_session_id"], ["voice_sessions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_table(
        "callback_requests",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("voice_session_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=254), nullable=True),
        sa.Column("reason", sa.String(length=32), nullable=False),
        sa.Column("note", sa.String(length=300), server_default="", nullable=False),
        sa.Column("status", sa.String(length=8), server_default="open", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by", sa.Uuid(), nullable=True),
        sa.CheckConstraint("status IN ('open', 'done')", name="callback_status_known"),
        sa.CheckConstraint("phone IS NOT NULL OR email IS NOT NULL", name="callback_has_contact"),
        sa.CheckConstraint(
            "reason IN ('color_consultation', 'extensions', 'sensitivity', "
            "'booking_help', 'other')",
            name="callback_reason_known",
        ),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resolved_by"], ["staff_users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["voice_session_id"], ["voice_sessions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "service_length_rules",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("service_id", sa.Uuid(), nullable=False),
        sa.Column("hair_length_id", sa.Uuid(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.CheckConstraint("duration_minutes > 0", name="duration_positive"),
        sa.CheckConstraint("price_cents >= 0", name="price_not_negative"),
        sa.ForeignKeyConstraint(["hair_length_id"], ["hair_lengths.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("service_id", "hair_length_id"),
    )
    op.create_table(
        "staff_sessions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("staff_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["staff_id"], ["staff_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_table(
        "stylist_breaks",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("stylist_id", sa.Uuid(), nullable=False),
        sa.Column("weekday", sa.SmallInteger(), nullable=False),
        sa.Column("starts_at", sa.Time(), nullable=False),
        sa.Column("ends_at", sa.Time(), nullable=False),
        sa.CheckConstraint("ends_at > starts_at", name="stylist_breaks_end_after_start"),
        sa.CheckConstraint("weekday BETWEEN 0 AND 6", name="stylist_breaks_weekday_range"),
        sa.ForeignKeyConstraint(["stylist_id"], ["stylists.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "stylist_hours",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("stylist_id", sa.Uuid(), nullable=False),
        sa.Column("weekday", sa.SmallInteger(), nullable=False),
        sa.Column("starts_at", sa.Time(), nullable=False),
        sa.Column("ends_at", sa.Time(), nullable=False),
        sa.CheckConstraint("ends_at > starts_at", name="stylist_hours_end_after_start"),
        sa.CheckConstraint("weekday BETWEEN 0 AND 6", name="stylist_hours_weekday_range"),
        sa.ForeignKeyConstraint(["stylist_id"], ["stylists.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stylist_id", "weekday"),
    )
    op.create_table(
        "bookings",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("stylist_id", sa.Uuid(), nullable=False),
        sa.Column("service_id", sa.Uuid(), nullable=False),
        sa.Column("hair_length_id", sa.Uuid(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("occupied_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=16), server_default="confirmed", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("reference", sa.String(length=16), nullable=False),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("customer_name", sa.String(length=80), nullable=False),
        sa.Column("customer_email", sa.String(length=254), nullable=True),
        sa.Column("customer_phone", sa.String(length=20), nullable=True),
        sa.Column("summary", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("draft_id", sa.Uuid(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_by", sa.Uuid(), nullable=True),
        sa.Column("voice_session_id", sa.Uuid(), nullable=True),
        sa.CheckConstraint("status IN ('confirmed', 'cancelled')", name="booking_status_known"),
        sa.CheckConstraint(
            "customer_email IS NOT NULL OR customer_phone IS NOT NULL", name="booking_has_contact"
        ),
        sa.CheckConstraint("ends_at > starts_at", name="booking_end_after_start"),
        sa.CheckConstraint("occupied_until >= ends_at", name="booking_buffer_after_end"),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["cancelled_by"], ["staff_users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["draft_id"], ["booking_drafts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["hair_length_id"],
            ["hair_lengths.id"],
        ),
        sa.ForeignKeyConstraint(
            ["service_id"],
            ["services.id"],
        ),
        sa.ForeignKeyConstraint(["stylist_id"], ["stylists.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["voice_session_id"], ["voice_sessions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_id", "idempotency_key", name="uq_bookings_idempotency_key"),
        sa.UniqueConstraint("draft_id", name="uq_bookings_draft_id"),
        sa.UniqueConstraint("reference", name="uq_bookings_reference"),
    )
    op.create_index(
        "ix_blocked_periods_stylist_start", "blocked_periods", ["stylist_id", "starts_at"]
    )
    op.create_index("ix_bookings_stylist_start", "bookings", ["stylist_id", "starts_at"])
    op.create_index(
        "ix_voice_sessions_business_started", "voice_sessions", ["business_id", "started_at"]
    )
    op.create_index(
        "ix_voice_sessions_client_started", "voice_sessions", ["client_hash", "started_at"]
    )
    # The guarantee against double booking. Each confirmed booking occupies its appointment
    # plus its trailing buffer, and no two such ranges may overlap for one stylist, however
    # many requests arrive at once.
    op.execute(
        """
        ALTER TABLE bookings ADD CONSTRAINT bookings_no_overlap
        EXCLUDE USING gist (
            stylist_id WITH =,
            tstzrange(starts_at, occupied_until, '[)') WITH &&
        ) WHERE (status = 'confirmed')
        """
    )


def downgrade() -> None:
    op.drop_table("bookings")
    op.drop_table("stylist_hours")
    op.drop_table("stylist_breaks")
    op.drop_table("staff_sessions")
    op.drop_table("service_length_rules")
    op.drop_table("callback_requests")
    op.drop_table("booking_drafts")
    op.drop_table("blocked_periods")
    op.drop_table("voice_sessions")
    op.drop_table("stylists")
    op.drop_table("staff_users")
    op.drop_table("services")
    op.drop_table("hair_lengths")
    op.drop_table("faqs")
    op.drop_table("business_hours")
    op.drop_table("businesses")
    op.execute("DROP EXTENSION IF EXISTS btree_gist")
