# Core Domain Models
import enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Index, UniqueConstraint, Enum as SQLEnum, Numeric, JSON, Integer, LargeBinary, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, declared_attr
from models.database import Base, SoftDeleteMixin, AuditMixin
import uuid


class IdentityLevel(int, enum.Enum):
    ANONYMOUS = 0
    EMAIL_VERIFIED = 1
    MERIT_LINKED = 2
    BIOMETRIC = 3
    TRUSTED = 4
    AUTHORIZED = 5


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    BANNED = "banned"


class User(Base, SoftDeleteMixin, AuditMixin):
    """Core user model with progressive identity levels"""
    __tablename__ = "user"
    
    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=True)  # Nullable for anonymous
    email_hash = Column(String(64), index=True, nullable=True)  # SHA-256 hash
    is_temp_email = Column(Boolean, default=False, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Identity
    identity_level = Column(SQLEnum(IdentityLevel), default=IdentityLevel.ANONYMOUS, nullable=False, index=True)
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING_VERIFICATION, nullable=False)
    
    # Cédula (Dominican ID) - Tokenized, never stored in plain
    cedula_token = Column(String(128), unique=True, index=True, nullable=True)  # Encrypted token
    cedula_verified = Column(Boolean, default=False, nullable=False)
    cedula_verified_at = Column(DateTime(timezone=True), nullable=True)
    jce_verification_id = Column(String(100), nullable=True)
    
    # Biometric
    biometric_verified = Column(Boolean, default=False, nullable=False)
    biometric_verified_at = Column(DateTime(timezone=True), nullable=True)
    biometric_template_hash = Column(String(64), nullable=True)  # Hash of biometric template
    
    # Profile
    full_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    phone_verified = Column(Boolean, default=False, nullable=False)
    whatsapp_opt_in = Column(Boolean, default=False, nullable=False)
    whatsapp_verified = Column(Boolean, default=False, nullable=False)
    preferred_language = Column(String(10), default="es", nullable=False)
    
    # Device & Security
    current_device_fingerprint = Column(String(64), nullable=True)
    known_devices = Column(JSONB, default=list, nullable=False)  # List of device fingerprints
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String(45), nullable=True)  # IPv6 compatible
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Merit
    merit_score = Column(Numeric(12, 2), default=0, nullable=False)
    merit_tier = Column(String(50), default="bronze", nullable=False)
    total_merits_earned = Column(Numeric(12, 2), default=0, nullable=False)
    total_merits_spent = Column(Numeric(12, 2), default=0, nullable=False)
    
    # Quest & Community
    quest_participation_count = Column(Integer, default=0, nullable=False)
    quest_hours_total = Column(Numeric(8, 2), default=0, nullable=False)
    mutual_aid_given = Column(Numeric(12, 2), default=0, nullable=False)
    mutual_aid_received = Column(Numeric(12, 2), default=0, nullable=False)
    veeduria_reports_filed = Column(Integer, default=0, nullable=False)
    veeduria_reports_validated = Column(Integer, default=0, nullable=False)
    
    # Geographic
    province = Column(String(100), nullable=True)
    municipality = Column(String(100), nullable=True)
    sector = Column(String(100), nullable=True)
    gps_lat = Column(Numeric(10, 8), nullable=True)
    gps_lng = Column(Numeric(11, 8), nullable=True)
    location_verified = Column(Boolean, default=False, nullable=False)
    location_verified_at = Column(DateTime(timezone=True), nullable=True)
    location_verification_source = Column(String(50), nullable=True)  # jce, mivhed, quest, etc.
    
    # Banking / Payments
    bank_accounts = Column(JSONB, default=list, nullable=False)  # Encrypted, minimal info
    digital_wallets = Column(JSONB, default=list, nullable=False)  # Apple Pay, Google Pay tokens
    payment_preferences = Column(JSONB, default=dict, nullable=False)
    
    # Notification Preferences
    notification_channels = Column(JSONB, default=dict, nullable=False)  # email, whatsapp, sms, push, ussd
    opt_ins = Column(JSONB, default=dict, nullable=False)
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", lazy="dynamic")
    merit_transactions = relationship("MeritTransaction", back_populates="user", lazy="dynamic")
    payments = relationship("Payment", back_populates="user", lazy="dynamic")
    quest_visits = relationship("QuestVisit", back_populates="quester", lazy="dynamic")
    veeduria_reports = relationship("VeeduriaReport", back_populates="reporter", lazy="dynamic")
    address_corrections = relationship("AddressCorrection", back_populates="reporter", lazy="dynamic")
    
    __table_args__ = (
        Index("ix_user_identity_status", "identity_level", "status"),
        Index("ix_user_location", "province", "municipality", "sector"),
        Index("ix_user_merit_score", "merit_score"),
    )


class UserSession(Base, SoftDeleteMixin):
    """User session with device tracking"""
    __tablename__ = "user_session"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    session_token = Column(String(128), unique=True, index=True, nullable=False)
    refresh_token = Column(String(128), unique=True, index=True, nullable=True)
    
    # Device
    device_fingerprint = Column(String(64), nullable=False, index=True)
    device_info = Column(JSONB, default=dict, nullable=False)  # browser, os, screen, etc.
    device_trusted = Column(Boolean, default=False, nullable=False)
    
    # Network
    ip_address = Column(String(45), nullable=False)
    ip_hash = Column(String(64), nullable=False, index=True)
    country = Column(String(2), nullable=True)
    city = Column(String(100), nullable=True)
    isp = Column(String(100), nullable=True)
    is_vpn = Column(Boolean, default=False, nullable=False)
    is_proxy = Column(Boolean, default=False, nullable=False)
    is_tor = Column(Boolean, default=False, nullable=False)
    
    # Identity Level at creation
    identity_level = Column(SQLEnum(IdentityLevel), nullable=False)
    
    # Capabilities (cached from identity level)
    capabilities = Column(JSONB, default=list, nullable=False)
    
    # Expiry
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    last_activity_at = Column(DateTime(timezone=True), nullable=False)
    
    # Status
    is_revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoked_reason = Column(String(255), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    __table_args__ = (
        Index("ix_session_user_active", "user_id", "is_revoked", "expires_at"),
        Index("ix_session_device", "device_fingerprint"),
    )


class MagicLinkToken(Base):
    """Magic link tokens for passwordless auth"""
    __tablename__ = "magic_link_token"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(String(128), unique=True, index=True, nullable=False)
    token_hash = Column(String(64), unique=True, index=True, nullable=False)
    
    email = Column(String(255), nullable=False, index=True)
    email_hash = Column(String(64), nullable=False, index=True)
    is_temp_email = Column(Boolean, default=False, nullable=False)
    
    # Device binding
    device_fingerprint = Column(String(64), nullable=False)
    ip_hash = Column(String(64), nullable=False)
    
    # Locale
    locale = Column(String(10), default="es", nullable=False)
    
    # Expiry
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    used_at = Column(DateTime(timezone=True), nullable=True)
    used_by_session_id = Column(UUID(as_uuid=True), ForeignKey("user_session.id"), nullable=True)
    
    # Status
    is_used = Column(Boolean, default=False, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    revoked_reason = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("ix_magic_link_email_expires", "email_hash", "expires_at"),
    )


class DeviceFingerprint(Base):
    """Device fingerprint registry for fraud detection"""
    __tablename__ = "device_fingerprint"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fingerprint = Column(String(64), unique=True, index=True, nullable=False)
    
    # Components
    components = Column(JSONB, nullable=False)  # canvas, webgl, audio, fonts, etc.
    user_agent = Column(Text, nullable=True)
    
    # Classification
    device_type = Column(String(50), nullable=True)  # desktop, mobile, tablet, feature_phone
    os = Column(String(50), nullable=True)
    browser = Column(String(50), nullable=True)
    is_bot = Column(Boolean, default=False, nullable=False)
    is_emulator = Column(Boolean, default=False, nullable=False)
    
    # Trust
    trust_score = Column(Numeric(3, 2), default=0.5, nullable=False)  # 0.0 - 1.0
    first_seen_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    seen_count = Column(Integer, default=1, nullable=False)
    
    # Associations
    associated_users = Column(JSONB, default=list, nullable=False)  # List of user_ids
    associated_sessions = Column(Integer, default=0, nullable=False)
    
    # Fraud flags
    fraud_flags = Column(JSONB, default=list, nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False)
    blocked_at = Column(DateTime(timezone=True), nullable=True)
    blocked_reason = Column(String(255), nullable=True)
    
    __table_args__ = (
        Index("ix_device_trust", "trust_score", "is_blocked"),
    )


# Import func for timestamps
from sqlalchemy.sql import func