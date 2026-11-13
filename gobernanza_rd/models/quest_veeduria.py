# Quest, Veeduria, Address, Convivencia, and Governance Models
import enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Index, UniqueConstraint, Enum as SQLEnum, Numeric, JSON, Integer, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, declared_attr
from models.database import Base, SoftDeleteMixin, AuditMixin
import uuid


class QuestStatus(str, enum.Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class QuestVisitStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RESCHEDULED = "rescheduled"
    RESIDENT_ABSENT = "resident_absent"


class ConnectionQuality(int, enum.Enum):
    VERY_POOR = 1
    POOR = 2
    FAIR = 3
    GOOD = 4
    EXCELLENT = 5


class Quest(Base, AuditMixin):
    """Quest campaign - organized community visits"""
    __tablename__ = "quest"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quest_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    territory_code = Column(String(20), nullable=False, index=True)  # province-municipality-sector
    territory_name = Column(String(255), nullable=False)
    
    # Dates
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Target
    total_homes_target = Column(Integer, nullable=False)
    homes_visited = Column(Integer, default=0, nullable=False)
    homes_completed = Column(Integer, default=0, nullable=False)
    
    # Status
    status = Column(SQLEnum(QuestStatus), default=QuestStatus.PLANNED, nullable=False, index=True)
    
    # Assignment
    coordinator_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    assigned_questers = Column(JSONB, default=list, nullable=False)  # List of user_ids
    
    # Stipend
    daily_stipend = Column(Numeric(10, 2), default=500, nullable=False)  # DOP per day
    total_budget = Column(Numeric(12, 2), nullable=False)
    
    # Metrics
    successful_connections = Column(Integer, default=0, nullable=False)
    needs_identified = Column(Integer, default=0, nullable=False)
    referrals_made = Column(Integer, default=0, nullable=False)
    
    # Trace
    trace_id = Column(String(128), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    coordinator = relationship("User", foreign_keys=[coordinator_id])
    visits = relationship("QuestVisit", back_populates="quest", lazy="dynamic")
    pre_verifications = relationship("QuestPreVerification", back_populates="quest", lazy="dynamic")
    
    __table_args__ = (
        Index("ix_quest_territory_dates", "territory_code", "start_date", "end_date"),
        Index("ix_quest_status_dates", "status", "start_date"),
    )


class QuestVisit(Base, AuditMixin):
    """Individual Quest visit to a home"""
    __tablename__ = "quest_visit"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    quest_id = Column(UUID(as_uuid=True), ForeignKey("quest.id"), nullable=False, index=True)
    quester_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    
    # Home identification (no address stored - uses delivery location)
    delivery_location_id = Column(UUID(as_uuid=True), ForeignKey("delivery_location.id"), nullable=True)
    home_reference = Column(String(255), nullable=True)  # "Casa de Doña María, esquina colmado"
    
    # GPS verification
    gps_lat = Column(Numeric(10, 8), nullable=True)
    gps_lng = Column(Numeric(11, 8), nullable=True)
    gps_accuracy = Column(Integer, nullable=True)  # meters
    gps_verified = Column(Boolean, default=False, nullable=False)
    
    # Visit protocol (Convivencia Limpia)
    greeted = Column(Boolean, default=False, nullable=False)
    explanation_given = Column(Boolean, default=False, nullable=False)
    affirmation_spoken = Column(Boolean, default=False, nullable=False)
    listened = Column(Boolean, default=False, nullable=False)
    resident_present = Column(Boolean, default=False, nullable=False)
    
    # Quality metrics
    connection_quality = Column(SQLEnum(ConnectionQuality), nullable=True)
    mutual_respect = Column(SQLEnum(ConnectionQuality), nullable=True)
    resident_sharing = Column(Text, nullable=True)  # What resident shared
    quester_notes = Column(Text, nullable=True)
    
    # Needs identified
    needs_identified = Column(JSONB, default=list, nullable=False)  # List of need categories
    referrals_made = Column(JSONB, default=list, nullable=False)  # Referrals to services
    
    # Status
    status = Column(SQLEnum(QuestVisitStatus), default=QuestVisitStatus.SCHEDULED, nullable=False, index=True)
    
    # Timing
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Validation (by trusted quester)
    validated_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    validation_notes = Column(Text, nullable=True)
    
    # Trace
    trace_id = Column(String(128), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    quest = relationship("Quest", back_populates="visits")
    quester = relationship("User", foreign_keys=[quester_id], back_populates="quest_visits")
    validator = relationship("User", foreign_keys=[validated_by])
    delivery_location = relationship("DeliveryLocation")
    
    __table_args__ = (
        Index("ix_quest_visit_quester_date", "quester_id", "scheduled_at"),
        Index("ix_quest_visit_status_date", "status", "scheduled_at"),
        Index("ix_quest_visit_location", "delivery_location_id"),
    )


class QuestPreVerification(Base, AuditMixin):
    """Pre-verification by Quest visitor day before delivery"""
    __tablename__ = "quest_pre_verification"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    quest_id = Column(UUID(as_uuid=True), ForeignKey("quest.id"), nullable=False, index=True)
    quester_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    delivery_id = Column(UUID(as_uuid=True), ForeignKey("delivery.id"), nullable=True, index=True)
    
    # Verification tasks completed
    gps_confirmed = Column(Boolean, default=False, nullable=False)
    gps_lat = Column(Numeric(10, 8), nullable=True)
    gps_lng = Column(Numeric(11, 8), nullable=True)
    gps_accuracy = Column(Integer, nullable=True)
    
    recipient_confirmed = Column(Boolean, default=False, nullable=False)
    access_instructions_confirmed = Column(Boolean, default=False, nullable=False)
    neighbor_confirmed = Column(Boolean, default=False, nullable=False)
    
    # Community references
    community_references = Column(JSONB, default=list, nullable=False)  # Colmado, iglesia, escuela
    
    # Photos
    entrance_photo = Column(String(500), nullable=True)  # URL
    street_reference_photo = Column(String(500), nullable=True)
    
    # Notes
    changes_noted = Column(Text, nullable=True)  # New construction, road work, etc.
    quester_notes = Column(Text, nullable=True)
    
    # Status
    is_complete = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Trace
    trace_id = Column(String(128), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    quest = relationship("Quest", back_populates="pre_verifications")
    quester = relationship("User")
    delivery = relationship("Delivery")
    
    __table_args__ = (
        Index("ix_pre_verification_delivery", "delivery_id"),
    )


class VeeduriaSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class VeeduriaStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    VALIDATED = "validated"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    RESOLVED = "resolved"


class VeeduriaReport(Base, AuditMixin):
    """Citizen oversight report"""
    __tablename__ = "veeduria_report"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_number = Column(String(50), unique=True, nullable=False, index=True)
    
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    
    # Target
    project_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # Infrastructure project
    contract_id = Column(UUID(as_uuid=True), nullable=True)  # Government contract
    entity_name = Column(String(255), nullable=True)  # Institution/contractor
    
    # Location
    delivery_location_id = Column(UUID(as_uuid=True), ForeignKey("delivery_location.id"), nullable=True)
    gps_lat = Column(Numeric(10, 8), nullable=True)
    gps_lng = Column(Numeric(11, 8), nullable=True)
    location_description = Column(Text, nullable=True)
    
    # Content
    severity = Column(SQLEnum(VeeduriaSeverity), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)  # corruption, environment, infrastructure, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Evidence
    photos = Column(JSONB, default=list, nullable=False)  # URLs
    documents = Column(JSONB, default=list, nullable=False)  # URLs
    witnesses = Column(JSONB, default=list, nullable=False)  # List of witness info
    
    # Status
    status = Column(SQLEnum(VeeduriaStatus), default=VeeduriaStatus.SUBMITTED, nullable=False, index=True)
    
    # Validation
    validated_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    validation_notes = Column(Text, nullable=True)
    validation_evidence = Column(JSONB, default=dict, nullable=False)
    
    # Resolution
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_summary = Column(Text, nullable=True)
    resolution_actions = Column(JSONB, default=list, nullable=False)
    
    # Escalation
    escalated_to = Column(String(255), nullable=True)  # FGA, Court, Prosecutor, Media
    escalated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Trace
    trace_id = Column(String(128), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    reporter = relationship("User", back_populates="veeduria_reports")
    validator = relationship("User", foreign_keys=[validated_by])
    delivery_location = relationship("DeliveryLocation")
    
    __table_args__ = (
        Index("ix_veeduria_reporter_status", "reporter_id", "status"),
        Index("ix_veeduria_category_severity", "category", "severity"),
        Index("ix_veeduria_project", "project_id"),
    )


class ConvivenciaInteractionType(str, enum.Enum):
    GREETING = "greeting"
    CONVERSATION = "conversation"
    ASSISTANCE = "assistance"
    CONFLICT_RESOLUTION = "conflict_resolution"
    CELEBRATION = "celebration"
    MOURNING = "mourning"
    MUTUAL_AID = "mutual_aid"


class ConvivenciaInteraction(Base):
    """Kindness/malice metric tracking"""
    __tablename__ = "convivencia_interaction"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    initiator_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    
    interaction_type = Column(SQLEnum(ConvivenciaInteractionType), nullable=False, index=True)
    
    # Metrics
    kindness_score = Column(Numeric(3, 2), default=0, nullable=False)  # 0.0 - 1.0
    malice_score = Column(Numeric(3, 2), default=0, nullable=False)  # 0.0 - 1.0
    trust_delta = Column(Numeric(3, 2), default=0, nullable=False)  # -1.0 to 1.0
    
    # Context
    context = Column(String(100), nullable=True)  # quest, mutual_aid, neighborhood, digital
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Validation
    witnessed_by = Column(JSONB, default=list, nullable=False)  # Other user IDs
    witness_confirmations = Column(Integer, default=0, nullable=False)
    
    # Trace
    trace_id = Column(String(128), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    initiator = relationship("User", foreign_keys=[initiator_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
    
    __table_args__ = (
        Index("ix_convivencia_initiator_recipient", "initiator_id", "recipient_id"),
        Index("ix_convivencia_type_date", "interaction_type", "created_at"),
    )


class ConvivenciaProfile(Base):
    """Aggregated convivencia metrics per user"""
    __tablename__ = "convivencia_profile"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True)
    
    # Scores
    kindness_index = Column(Numeric(4, 3), default=0.5, nullable=False)  # 0.0 - 1.0
    malice_index = Column(Numeric(4, 3), default=0, nullable=False)  # 0.0 - 1.0
    trust_score = Column(Numeric(4, 3), default=0.5, nullable=False)  # 0.0 - 1.0
    reciprocity_rate = Column(Numeric(4, 3), default=0, nullable=False)  # 0.0 - 1.0
    
    # Counts
    total_interactions = Column(Integer, default=0, nullable=False)
    positive_interactions = Column(Integer, default=0, nullable=False)
    negative_interactions = Column(Integer, default=0, nullable=False)
    
    # Network
    unique_connections = Column(Integer, default=0, nullable=False)
    strong_connections = Column(Integer, default=0, nullable=False)  # trust > 0.7
    weak_connections = Column(Integer, default=0, nullable=False)  # trust < 0.3
    
    # Licenses (experience-based, no tests)
    licenses = Column(JSONB, default=dict, nullable=False)  # {license_type: {level, earned_at, verified_by}}
    
    # Mutual aid
    mutual_aid_given_count = Column(Integer, default=0, nullable=False)
    mutual_aid_received_count = Column(Integer, default=0, nullable=False)
    mutual_aid_given_value = Column(Numeric(12, 2), default=0, nullable=False)
    mutual_aid_received_value = Column(Numeric(12, 2), default=0, nullable=False)
    
    # Updated
    last_calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_interaction_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index("ix_convivencia_kindness", "kindness_index"),
        Index("ix_convivencia_trust", "trust_score"),
    )


class MutualAidCategory(str, enum.Enum):
    FOOD = "food"
    MEDICINE = "medicine"
    TRANSPORT = "transport"
    CHILDCARE = "childcare"
    ELDERCARE = "eldercare"
    REPAIR = "repair"
    FINANCIAL = "financial"
    INFORMATION = "information"
    EMOTIONAL = "emotional"
    SKILLS = "skills"


class MutualAidRequest(Base, AuditMixin):
    """Mutual aid request/fulfillment"""
    __tablename__ = "mutual_aid_request"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_number = Column(String(50), unique=True, nullable=False, index=True)
    
    requester_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    helper_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True, index=True)
    
    category = Column(SQLEnum(MutualAidCategory), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Value
    estimated_value = Column(Numeric(10, 2), nullable=True)
    actual_value = Column(Numeric(10, 2), nullable=True)
    
    # Location
    delivery_location_id = Column(UUID(as_uuid=True), ForeignKey("delivery_location.id"), nullable=True)
    
    # Status
    status = Column(String(50), default="open", nullable=False, index=True)  # open, matched, in_progress, completed, cancelled, expired
    
    # Urgency
    is_urgent = Column(Boolean, default=False, nullable=False)
    needed_by = Column(DateTime(timezone=True), nullable=True)
    
    # Matching
    matched_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Feedback
    requester_rating = Column(Integer, nullable=True)  # 1-5
    requester_feedback = Column(Text, nullable=True)
    helper_rating = Column(Integer, nullable=True)
    helper_feedback = Column(Text, nullable=True)
    
    # Trace
    trace_id = Column(String(128), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    requester = relationship("User", foreign_keys=[requester_id])
    helper = relationship("User", foreign_keys=[helper_id])
    delivery_location = relationship("DeliveryLocation")
    
    __table_args__ = (
        Index("ix_mutual_aid_requester_status", "requester_id", "status"),
        Index("ix_mutual_aid_category_status", "category", "status"),
        Index("ix_mutual_aid_helper_status", "helper_id", "status"),
    )


# Import func
from sqlalchemy.sql import func