# Merit, Payment, Quest, Veeduria, and Governance Models
import enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Index, UniqueConstraint, Enum as SQLEnum, Numeric, JSON, Integer, LargeBinary, Table, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, declared_attr
from models.database import Base, SoftDeleteMixin, AuditMixin
import uuid


class MeritEventType(str, enum.Enum):
    # Earning events
    TAX_COMPLIANT = "tax_compliant"
    SOCIAL_PARTICIPATION = "social_participation"
    UTILITY_PAYMENT_RESPONSIBLE = "utility_payment_responsible"
    QUEST_VISIT_COMPLETED = "quest_visit_completed"
    QUEST_PRE_VERIFICATION = "quest_pre_verification"
    VEEDURIA_REPORT_FILED = "veeduria_report_filed"
    VEEDURIA_REPORT_VALIDATED = "veeduria_report_validated"
    MUTUAL_AID_GIVEN = "mutual_aid_given"
    COMMUNITY_PICKUP_VOLUNTEER = "community_pickup_volunteer"
    ADDRESS_CORRECTION_REPORTED = "address_correction_reported"
    DIGITAL_WALLET_ADOPTION = "digital_wallet_adoption"
    HOUSING_APPLICATION = "housing_application"
    IDENTITY_ESCALATION = "identity_escalation"
    
    # Spending events
    HOUSING_BID = "housing_bid"
    UTILITY_PAYMENT = "utility_payment"
    APPLIANCE_PURCHASE = "appliance_purchase"
    MUTUAL_AID_REQUEST = "mutual_aid_request"
    EMERGENCY_RELIEF = "emergency_relief"


class MeritTransaction(Base, AuditMixin):
    """Immutable merit transaction log"""
    __tablename__ = "merit_transaction"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    
    # Event
    event_type = Column(SQLEnum(MeritEventType), nullable=False, index=True)
    event_description = Column(Text, nullable=True)
    
    # Amounts
    base_amount = Column(Numeric(10, 2), nullable=False)
    multiplier = Column(Numeric(3, 2), default=1.0, nullable=False)
    bonus_amount = Column(Numeric(10, 2), default=0, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)  # base * multiplier + bonus
    
    # Balance after transaction
    balance_before = Column(Numeric(12, 2), nullable=False)
    balance_after = Column(Numeric(12, 2), nullable=False)
    
    # Context
    related_entity_type = Column(String(50), nullable=True)  # payment, quest, veeduria, etc.
    related_entity_id = Column(UUID(as_uuid=True), nullable=True)
    metadata = Column(JSONB, default=dict, nullable=False)
    
    # Verification
    verified = Column(Boolean, default=True, nullable=False)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Traceability
    trace_id = Column(String(128), nullable=False, index=True)
    previous_trace_hash = Column(String(64), nullable=True)
    trace_hash = Column(String(64), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="merit_transactions")
    
    __table_args__ = (
        Index("ix_merit_user_event", "user_id", "event_type"),
        Index("ix_merit_trace", "trace_id"),
        CheckConstraint("total_amount = base_amount * multiplier + bonus_amount", name="ck_merit_amount"),
    )


class MeritProfile(Base):
    """Aggregated merit profile for quick lookups"""
    __tablename__ = "merit_profile"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True)
    
    # Current state
    current_score = Column(Numeric(12, 2), default=0, nullable=False)
    tier = Column(String(50), default="bronze", nullable=False)
    rank_percentile = Column(Numeric(5, 2), nullable=True)
    
    # Lifetime
    lifetime_earned = Column(Numeric(12, 2), default=0, nullable=False)
    lifetime_spent = Column(Numeric(12, 2), default=0, nullable=False)
    
    # Monthly/Yearly
    monthly_earned = Column(Numeric(10, 2), default=0, nullable=False)
    monthly_spent = Column(Numeric(10, 2), default=0, nullable=False)
    yearly_earned = Column(Numeric(12, 2), default=0, nullable=False)
    yearly_spent = Column(Numeric(12, 2), default=0, nullable=False)
    
    # By category
    by_category = Column(JSONB, default=dict, nullable=False)  # {category: {earned, spent, count}}
    
    # Eligibility
    eligible_benefits = Column(JSONB, default=list, nullable=False)
    next_threshold = Column(Numeric(12, 2), nullable=True)
    next_benefit = Column(String(100), nullable=True)
    
    # Updated
    last_calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_transaction_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index("ix_merit_profile_score", "current_score"),
        Index("ix_merit_profile_tier", "tier"),
    )


class SelectingFrontCategory(str, enum.Enum):
    UTILITY = "utility"        # Electricity, Water, Internet
    HOUSING = "housing"        # Rent subsidy, Down payment, Relocation
    APPLIANCE = "appliance"    # Nevera, Estufa, Lavadora, Aire Acondicionado, TV


class SelectingFrontItem(Base):
    """Items available in Selecting Front"""
    __tablename__ = "selecting_front_item"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Identity
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(SQLEnum(SelectingFrontCategory), nullable=False, index=True)
    
    # Requirements
    merit_cost = Column(Numeric(10, 2), nullable=False)
    min_identity_level = Column(SQLEnum(IdentityLevel), default=IdentityLevel.MERIT_LINKED, nullable=False)
    min_merit_score = Column(Numeric(10, 2), default=0, nullable=False)
    
    # Availability
    is_active = Column(Boolean, default=True, nullable=False)
    stock_quantity = Column(Integer, nullable=True)  # None = unlimited
    stock_reserved = Column(Integer, default=0, nullable=False)
    restock_date = Column(DateTime(timezone=True), nullable=True)
    
    # Specifications
    specifications = Column(JSONB, default=dict, nullable=False)  # brand, model, capacity, energy_rating, etc.
    estimated_value_dop = Column(Numeric(12, 2), nullable=False)
    
    # Delivery
    delivery_type = Column(String(50), default="standard", nullable=False)  # standard, installation, pickup
    installation_included = Column(Boolean, default=False, nullable=False)
    warranty_months = Column(Integer, default=12, nullable=False)
    
    # Metadata
    tags = Column(JSONB, default=list, nullable=False)
    priority = Column(Integer, default=0, nullable=False)  # Higher = shown first
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        Index("ix_selecting_front_category_active", "category", "is_active"),
        Index("ix_selecting_front_merit_cost", "merit_cost"),
    )


class SelectingFrontOrder(Base, AuditMixin):
    """Order from Selecting Front"""
    __tablename__ = "selecting_front_order"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    item_id = Column(UUID(as_uuid=True), ForeignKey("selecting_front_item.id"), nullable=False)
    
    # Cost
    merit_cost = Column(Numeric(10, 2), nullable=False)
    merit_discount = Column(Numeric(10, 2), default=0, nullable=False)
    final_merit_cost = Column(Numeric(10, 2), nullable=False)
    
    # Status
    status = Column(String(50), default="pending", nullable=False, index=True)  # pending, confirmed, processing, shipped, delivered, cancelled, returned
    
    # Delivery
    delivery_location_id = Column(UUID(as_uuid=True), ForeignKey("delivery_location.id"), nullable=True)
    delivery_scheduled_at = Column(DateTime(timezone=True), nullable=True)
    delivery_completed_at = Column(DateTime(timezone=True), nullable=True)
    delivery_notes = Column(Text, nullable=True)
    
    # Installation
    installation_scheduled_at = Column(DateTime(timezone=True), nullable=True)
    installation_completed_at = Column(DateTime(timezone=True), nullable=True)
    installation_notes = Column(Text, nullable=True)
    
    # Trace
    trace_id = Column(String(128), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")
    item = relationship("SelectingFrontItem")
    delivery_location = relationship("DeliveryLocation")


class PaymentType(str, enum.Enum):
    UTILITY_ELECTRICITY = "utility_electricity"
    UTILITY_WATER = "utility_water"
    HOUSING_SUBSIDY = "housing_subsidy"
    MERIT_REWARD = "merit_reward"
    QUEST_STIPEND = "quest_stipend"
    MUTUAL_AID = "mutual_aid"
    EMERGENCY_RELIEF = "emergency_relief"
    SELECTING_FRONT = "selecting_front"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PREVIEW = "preview"  # Auto-filled, awaiting confirmation
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    CENTRAL_AI_FUND = "central_ai_fund"
    BANK_TRANSFER = "bank_transfer"
    CARD = "card"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    CASH_PICKUP = "cash_pickup"
    BONO_GAS = "bono_gas"
    BONO_LUZ = "bono_luz"


class Payment(Base, AuditMixin):
    """Payment with auto-fill from government APIs"""
    __tablename__ = "payment"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_number = Column(String(50), unique=True, nullable=False, index=True)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("user_session.id"), nullable=True)
    
    # Type
    payment_type = Column(SQLEnum(PaymentType), nullable=False, index=True)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False, index=True)
    
    # Amount
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="DOP", nullable=False)
    
    # Method
    payment_method = Column(SQLEnum(PaymentMethod), default=PaymentMethod.CENTRAL_AI_FUND, nullable=False)
    payment_method_details = Column(JSONB, default=dict, nullable=False)  # card_token, wallet_type, etc.
    
    # Auto-filled data (from gov APIs)
    auto_filled_data = Column(JSONB, default=dict, nullable=False)  # All gov API data used
    user_provided_data = Column(JSONB, default=dict, nullable=False)  # Only what user entered
    
    # Government API References
    gov_api_responses = Column(JSONB, default=dict, nullable=False)  # Responses from DGII, EDE, CORAASAN, etc.
    gov_transaction_ids = Column(JSONB, default=dict, nullable=False)  # External transaction IDs
    
    # Recipient (for mutual aid, etc.)
    recipient_cedula_token = Column(String(128), nullable=True)
    recipient_name = Column(String(255), nullable=True)
    recipient_phone = Column(String(20), nullable=True)
    
    # Description
    description = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True, index=True)
    
    # Timing
    initiated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error handling
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # Fraud
    risk_score = Column(Numeric(3, 2), default=0, nullable=False)
    fraud_action_taken = Column(String(50), nullable=True)
    
    # Traceability
    trace_id = Column(String(128), nullable=False, index=True)
    previous_trace_hash = Column(String(64), nullable=True)
    trace_hash = Column(String(64), nullable=False, index=True)
    
    # Merit impact
    merit_earned = Column(Numeric(10, 2), default=0, nullable=False)
    merit_transaction_id = Column(UUID(as_uuid=True), ForeignKey("merit_transaction.id"), nullable=True)
    
    # Digital wallet specific
    wallet_type = Column(String(20), nullable=True)  # apple_pay, google_pay
    wallet_transaction_id = Column(String(100), nullable=True)
    biometric_verified = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="payments")
    session = relationship("UserSession")
    merit_transaction = relationship("MeritTransaction")
    
    __table_args__ = (
        Index("ix_payment_user_status", "user_id", "status"),
        Index("ix_payment_type_status", "payment_type", "status"),
        Index("ix_payment_trace", "trace_id"),
        Index("ix_payment_initiated", "initiated_at"),
    )


class SavedPaymentMethod(Base):
    """Minimal saved payment method - only account number + nickname"""
    __tablename__ = "saved_payment_method"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    
    # Type
    payment_type = Column(SQLEnum(PaymentType), nullable=False)
    
    # Minimal user data
    account_number = Column(String(50), nullable=False)  # Encrypted
    nickname = Column(String(100), nullable=False)
    
    # Verification
    verified = Column(Boolean, default=False, nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by_api = Column(String(50), nullable=True)  # ede, coraasan, mivhed, etc.
    
    # Usage
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    use_count = Column(Integer, default=0, nullable=False)
    
    # Default
    is_default = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        UniqueConstraint("user_id", "payment_type", "account_number", name="uq_user_payment_account"),
        Index("ix_saved_payment_user_default", "user_id", "is_default"),
    )


# Import func
from sqlalchemy.sql import func