# Audit Trail and Governance Models
import enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Index, UniqueConstraint, Enum as SQLEnum, Numeric, JSON, Integer, LargeBinary, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from models.database import Base, SoftDeleteMixin
import uuid


class AuditEventType(str, enum.Enum):
    # Auth
    MAGIC_LINK_REQUESTED = "magic_link_requested"
    MAGIC_LINK_VERIFIED = "magic_link_verified"
    SESSION_CREATED = "session_created"
    SESSION_REVOKED = "session_revoked"
    IDENTITY_ESCALATED = "identity_escalated"
    
    # Merit
    MERIT_EARNED = "merit_earned"
    MERIT_SPENT = "merit_spent"
    MERIT_TRANSFERRED = "merit_transferred"
    
    # Payments
    PAYMENT_INITIATED = "payment_initiated"
    PAYMENT_CONFIRMED = "payment_confirmed"
    PAYMENT_PROCESSED = "payment_processed"
    PAYMENT_COMPLETED = "payment_completed"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_REFUNDED = "payment_refunded"
    
    # Selecting Front
    SELECTING_FRONT_ORDER = "selecting_front_order"
    SELECTING_FRONT_DELIVERED = "selecting_front_delivered"
    
    # Quest
    QUEST_STARTED = "quest_started"
    QUEST_VISIT_SCHEDULED = "quest_visit_scheduled"
    QUEST_VISIT_COMPLETED = "quest_visit_completed"
    QUEST_PRE_VERIFICATION = "quest_pre_verification"
    
    # Veeduria
    VEEDURIA_REPORT_FILED = "veeduria_report_filed"
    VEEDURIA_REPORT_VALIDATED = "veeduria_report_validated"
    VEEDURIA_REPORT_ESCALATED = "veeduria_report_escalated"
    
    # Delivery
    DELIVERY_CREATED = "delivery_created"
    DELIVERY_ASSIGNED = "delivery_assigned"
    DELIVERY_COMPLETED = "delivery_completed"
    DELIVERY_NEIGHBOR_CHAIN = "delivery_neighbor_chain"
    DELIVERY_PICKUP_POINT = "delivery_pickup_point"
    
    # Address
    ADDRESS_RESOLVED = "address_resolved"
    ADDRESS_CORRECTION = "address_correction"
    ADDRESS_SYNC = "address_sync"
    
    # Convivencia
    CONVIVENCIA_INTERACTION = "convivencia_interaction"
    MUTUAL_AID_REQUEST = "mutual_aid_request"
    MUTUAL_AID_FULFILLED = "mutual_aid_fulfilled"
    
    # Infrastructure
    PROJECT_CREATED = "project_created"
    PROJECT_MILESTONE = "project_milestone"
    PROJECT_PAYMENT = "project_payment"
    CONTRACTOR_REGISTERED = "contractor_registered"
    
    # Personnel
    LEAVE_REQUESTED = "leave_requested"
    LEAVE_APPROVED = "leave_approved"
    PERSONNEL_WELLBEING = "personnel_wellbeing"
    
    # Governance
    CONSENSUS_DECISION = "consensus_decision"
    MODEL_ROTATION = "model_rotation"
    FGA_ACTION = "fga_action"
    CIRCUIT_BREAKER = "circuit_breaker"
    LIABILITY_CLAIM = "liability_claim"
    
    # System
    CONFIG_CHANGED = "config_changed"
    SECURITY_EVENT = "security_event"
    FRAUD_DETECTED = "fraud_detected"
    ERROR_LOGGED = "error_logged"


class AuditRecord(Base):
    """Immutable audit record with cryptographic chaining"""
    __tablename__ = "audit_record"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sequence = Column(Integer, unique=True, nullable=False, index=True)  # Global sequence
    
    # Event
    event_type = Column(SQLEnum(AuditEventType), nullable=False, index=True)
    event_subtype = Column(String(100), nullable=True)
    
    # Actor
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True, index=True)
    actor_session_id = Column(UUID(as_uuid=True), ForeignKey("user_session.id"), nullable=True)
    actor_identity_level = Column(Integer, nullable=True)
    actor_ip_hash = Column(String(64), nullable=True)
    actor_device_fingerprint = Column(String(64), nullable=True)
    
    # Target
    target_type = Column(String(50), nullable=True)  # user, payment, quest, project, etc.
    target_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Event data (structured)
    event_data = Column(JSONB, nullable=False)
    
    # Cryptographic chaining
    previous_hash = Column(String(64), nullable=False)  # Hash of previous record
    record_hash = Column(String(64), nullable=False, index=True)  # Hash of this record
    
    # FROST Threshold Signature (for consensus decisions)
    threshold_signature = Column(String(256), nullable=True)
    participating_families = Column(JSONB, default=list, nullable=False)
    consensus_threshold = Column(String(50), nullable=True)
    
    # Multi-jurisdiction anchoring
    anchors = Column(JSONB, default=dict, nullable=False)  # {anchor_name: {tx_hash, block_height, timestamp}}
    anchored = Column(Boolean, default=False, nullable=False)
    anchored_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timing
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    received_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Integrity
    integrity_verified = Column(Boolean, default=True, nullable=False)
    verification_error = Column(Text, nullable=True)
    
    __table_args__ = (
        Index("ix_audit_actor_time", "actor_user_id", "timestamp"),
        Index("ix_audit_target_time", "target_type", "target_id", "timestamp"),
        Index("ix_audit_event_time", "event_type", "timestamp"),
        Index("ix_audit_sequence", "sequence"),
        Index("ix_audit_anchored", "anchored"),
    )


class ConsensusDecision(Base):
    """Record of multi-model consensus decisions"""
    __tablename__ = "consensus_decision"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    decision_id = Column(String(128), unique=True, nullable=False, index=True)
    
    # Proposal
    proposal_type = Column(String(100), nullable=False, index=True)
    proposal_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    proposal_data = Column(JSONB, nullable=False)
    severity = Column(String(50), nullable=False)  # routine, significant, constitutional, emergency
    
    # Family votes
    family_votes = Column(JSONB, nullable=False)  # {family_name: {vote, confidence, reasoning, model_outputs}}
    
    # Result
    decision = Column(String(50), nullable=False)  # approved, rejected, deferred, escalated
    consensus_achieved = Column(Boolean, default=False, nullable=False)
    consensus_score = Column(Numeric(4, 3), nullable=False)  # 0.000 - 1.000
    threshold_met = Column(Boolean, default=False, nullable=False)
    required_threshold = Column(Numeric(4, 3), nullable=False)
    families_participated = Column(Integer, nullable=False)
    families_required = Column(Integer, nullable=False)
    
    # Dissenting opinions
    dissenting_families = Column(JSONB, default=list, nullable=False)
    dissenting_reasoning = Column(JSONB, default=dict, nullable=False)
    
    # Adversarial challenges
    adversarial_challenges = Column(JSONB, default=list, nullable=False)
    challenges_addressed = Column(Boolean, default=False, nullable=False)
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    # Cryptographic proof
    threshold_signature = Column(String(256), nullable=True)
    proof_hash = Column(String(64), nullable=True)
    audit_record_id = Column(UUID(as_uuid=True), ForeignKey("audit_record.id"), nullable=True)
    
    # FGA oversight
    fga_reviewed = Column(Boolean, default=False, nullable=False)
    fga_reviewed_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    fga_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    fga_approval = Column(Boolean, nullable=True)
    
    # Veeduría oversight
    veeduria_reviewed = Column(Boolean, default=False, nullable=False)
    veeduria_reviewed_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    veeduria_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    veeduria_approval = Column(Boolean, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("ix_consensus_proposal", "proposal_type", "proposal_id"),
        Index("ix_consensus_decision_time", "decision", "completed_at"),
        Index("ix_consensus_fga", "fga_reviewed", "fga_approval"),
    )


class ModelRotationLog(Base):
    """Log of model rotations for diversity enforcement"""
    __tablename__ = "model_rotation_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    family = Column(String(50), nullable=False, index=True)
    old_model = Column(JSONB, nullable=False)  # {provider, model, role, weight}
    new_model = Column(JSONB, nullable=False)
    
    # Reason
    reason = Column(String(100), nullable=False)  # scheduled, diversity, performance, security, emergency
    triggered_by = Column(String(50), nullable=True)  # system, fga, audit, manual
    
    # Validation
    validation_results = Column(JSONB, default=dict, nullable=False)
    diversity_check_passed = Column(Boolean, default=False, nullable=False)
    performance_check_passed = Column(Boolean, default=False, nullable=False)
    security_check_passed = Column(Boolean, default=False, nullable=False)
    
    # Approval
    approved_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    fga_approval = Column(Boolean, default=False, nullable=False)
    
    # Deployment
    deployed = Column(Boolean, default=False, nullable=False)
    deployed_at = Column(DateTime(timezone=True), nullable=True)
    rollback_at = Column(DateTime(timezone=True), nullable=True)
    rollback_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("ix_model_rotation_family_time", "family", "created_at"),
        Index("ix_model_rotation_deployed", "deployed"),
    )


class CircuitBreakerEvent(Base):
    """Circuit breaker activations"""
    __tablename__ = "circuit_breaker_event"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    trigger = Column(String(100), nullable=False, index=True)  # consensus_failure, fairness_collapse, model_capture, constitutional_crisis
    trigger_data = Column(JSONB, nullable=False)
    
    # Action taken
    action = Column(String(100), nullable=False)  # freeze, redistribute, rotate, stay
    action_details = Column(JSONB, default=dict, nullable=False)
    
    # Authority
    authorized_by = Column(String(100), nullable=False)  # system, fga, veeduria, constitutional_court
    authorized_by_user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    
    # Duration
    activated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Resolution
    resolution = Column(String(100), nullable=True)  # auto_resolved, manual_resolved, escalated, expired
    resolution_details = Column(JSONB, default=dict, nullable=False)
    
    # Impact
    affected_systems = Column(JSONB, default=list, nullable=False)
    affected_users = Column(Integer, default=0, nullable=False)
    
    __table_args__ = (
        Index("ix_circuit_breaker_trigger_time", "trigger", "activated_at"),
        Index("ix_circuit_breaker_active", "resolved_at"),
    )


class FGAGovernanceAction(Base):
    """FGA (Fundación de Gobernanza Algorítmica) actions"""
    __tablename__ = "fga_governance_action"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Action type
    action_type = Column(String(100), nullable=False, index=True)  # model_approval, model_veto, audit_initiated, audit_completed, remediation_ordered, treaty_negotiated, redress_approved
    
    # Target
    target_type = Column(String(50), nullable=True)
    target_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Details
    description = Column(Text, nullable=False)
    rationale = Column(Text, nullable=True)
    legal_basis = Column(Text, nullable=True)
    
    # Decision
    decided_by = Column(JSONB, nullable=False)  # Board members who voted
    votes_for = Column(Integer, default=0, nullable=False)
    votes_against = Column(Integer, default=0, nullable=False)
    votes_abstain = Column(Integer, default=0, nullable=False)
    quorum_met = Column(Boolean, default=False, nullable=False)
    
    # Status
    status = Column(String(50), default="proposed", nullable=False)  # proposed, approved, rejected, implemented, expired
    
    # Implementation
    implemented = Column(Boolean, default=False, nullable=False)
    implemented_at = Column(DateTime(timezone=True), nullable=True)
    implemented_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    implementation_details = Column(JSONB, default=dict, nullable=False)
    
    # Review
    review_required = Column(Boolean, default=False, nullable=False)
    review_deadline = Column(DateTime(timezone=True), nullable=True)
    reviewed = Column(Boolean, default=False, nullable=False)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_outcome = Column(JSONB, default=dict, nullable=False)
    
    # Trace
    trace_id = Column(String(128), nullable=False, index=True)
    audit_record_id = Column(UUID(as_uuid=True), ForeignKey("audit_record.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        Index("ix_fga_action_type_status", "action_type", "status"),
        Index("ix_fga_action_target", "target_type", "target_id"),
    )


# Import func
from sqlalchemy.sql import func