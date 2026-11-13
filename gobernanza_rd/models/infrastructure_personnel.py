# Infrastructure, Personnel, Governance, and Audit Models
import enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Index, UniqueConstraint, Enum as SQLEnum, Numeric, JSON, Integer, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, declared_attr
from models.database import Base, SoftDeleteMixin, AuditMixin
import uuid


# ==================== INFRASTRUCTURE MODELS ====================

class ContractorStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BLACKLISTED = "blacklisted"


class ContractorTier(str, enum.Enum):
    LOCAL = "local"
    REGIONAL = "regional"
    NATIONAL = "national"
    INTERNATIONAL = "international"
    JAPANESE_PPP = "japanese_ppp"


class GlobalContractor(Base, AuditMixin):
    """Global contractor registry with Japanese PPP/PFI models"""
    __tablename__ = "global_contractor"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contractor_code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Identity
    legal_name = Column(String(255), nullable=False)
    trade_name = Column(String(255), nullable=True)
    country_of_origin = Column(String(2), nullable=False)  # ISO 3166-1 alpha-2
    
    # Registration
    registration_number = Column(String(100), nullable=True)
    tax_id = Column(String(100), nullable=True)
    
    # Classification
    tier = Column(SQLEnum(ContractorTier), nullable=False, index=True)
    specialties = Column(JSONB, default=list, nullable=False)  # roads, bridges, water, energy, housing, digital
    certifications = Column(JSONB, default=list, nullable=False)  # ISO, PPP, PFI, LEED, etc.
    
    # Japanese PPP/PFI
    japanese_ppp_certified = Column(Boolean, default=False, nullable=False)
    japanese_partner = Column(String(255), nullable=True)  # Japanese partner company
    jica_registered = Column(Boolean, default=False, nullable=False)
    
    # Status
    status = Column(SQLEnum(ContractorStatus), default=ContractorStatus.PENDING, nullable=False, index=True)
    
    # Verification
    verified_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verification_documents = Column(JSONB, default=list, nullable=False)
    
    # Financial
    bonding_capacity_usd = Column(Numeric(15, 2), nullable=True)
    insurance_coverage_usd = Column(Numeric(15, 2), nullable=True)
    financial_rating = Column(String(20), nullable=True)
    
    # Performance
    projects_completed = Column(Integer, default=0, nullable=False)
    projects_active = Column(Integer, default=0, nullable=False)
    on_time_rate = Column(Numeric(4, 3), default=1.0, nullable=False)
    budget_adherence_rate = Column(Numeric(4, 3), default=1.0, nullable=False)
    quality_score = Column(Numeric(3, 2), default=5.0, nullable=False)
    safety_incidents = Column(Integer, default=0, nullable=False)
    
    # Merit-weighted citizen oversight
    citizen_oversight_score = Column(Numeric(3, 2), default=0, nullable=False)
    veeduria_reports_count = Column(Integer, default=0, nullable=False)
    veeduria_validated_count = Column(Integer, default=0, nullable=False)
    
    # Anti-corruption
    beneficial_owners = Column(JSONB, default=list, nullable=False)  # UBO disclosure
    pep_check = Column(Boolean, default=False, nullable=False)  # Politically Exposed Persons
    sanctions_check = Column(Boolean, default=False, nullable=False)
    adverse_media_check = Column(Boolean, default=False, nullable=False)
    
    # API Integration
    api_endpoint = Column(String(500), nullable=True)
    api_credentials = Column(JSONB, default=dict, nullable=False)  # Encrypted
    webhook_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    verifier = relationship("User")
    projects = relationship("InfrastructureProject", back_populates="contractor", lazy="dynamic")
    
    __table_args__ = (
        Index("ix_contractor_tier_status", "tier", "status"),
        Index("ix_contractor_specialties", "specialties"),
        Index("ix_contractor_performance", "on_time_rate", "quality_score"),
    )


class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    TENDERING = "tendering"
    AWARDED = "awarded"
    MOBILIZATION = "mobilization"
    EXECUTION = "execution"
    COMMISSIONING = "commissioning"
    COMPLETED = "completed"
    WARRANTY = "warranty"
    CLOSED = "closed"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class ProjectFundingModel(str, enum.Enum):
    GOVERNMENT = "government"
    PPP = "ppp"
    PFI = "pfi"
    CONCESSION = "concession"
    BOT = "bot"  # Build-Operate-Transfer
    BOOT = "boot"  # Build-Own-Operate-Transfer
    BLT = "blt"  # Build-Lease-Transfer
    HYBRID = "hybrid"


class InfrastructureProject(Base, AuditMixin):
    """Infrastructure project with upfront delegation and merit oversight"""
    __tablename__ = "infrastructure_project"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)  # roads, bridges, water, energy, housing, digital, health, education
    
    # Location
    provincia = Column(String(100), nullable=False)
    municipio = Column(String(100), nullable=False)
    sector = Column(String(100), nullable=True)
    gps_lat = Column(Numeric(10, 8), nullable=True)
    gps_lng = Column(Numeric(11, 8), nullable=True)
    
    # Funding
    funding_model = Column(SQLEnum(ProjectFundingModel), nullable=False)
    estimated_cost = Column(Numeric(15, 2), nullable=False)
    awarded_cost = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Contractor
    contractor_id = Column(UUID(as_uuid=True), ForeignKey("global_contractor.id"), nullable=True, index=True)
    subcontractors = Column(JSONB, default=list, nullable=False)  # List of contractor_ids
    
    # Upfront delegation
    upfront_delegation = Column(Boolean, default=False, nullable=False)
    delegation_terms = Column(JSONB, default=dict, nullable=False)  # Milestones, payments, guarantees
    performance_bond_pct = Column(Numeric(4, 3), default=0.1, nullable=False)  # 10% default
    advance_payment_pct = Column(Numeric(4, 3), default=0.2, nullable=False)  # 20% default
    
    # Milestones
    milestones = Column(JSONB, default=list, nullable=False)  # [{name, target_date, amount_pct, kpi, status}]
    
    # Timeline
    planned_start = Column(DateTime(timezone=True), nullable=True)
    planned_end = Column(DateTime(timezone=True), nullable=True)
    actual_start = Column(DateTime(timezone=True), nullable=True)
    actual_end = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.PLANNING, nullable=False, index=True)
    
    # KPIs (Japanese model)
    kpis = Column(JSONB, default=dict, nullable=False)  # {kpi_name: {target, actual, weight, frequency}}
    
    # Citizen Oversight (Merit-weighted)
    oversight_enabled = Column(Boolean, default=True, nullable=False)
    citizen_reports = Column(Integer, default=0, nullable=False)
    citizen_validated_reports = Column(Integer, default=0, nullable=False)
    merit_weighted_score = Column(Numeric(3, 2), default=0, nullable=False)
    
    # Anti-corruption
    transparency_portal_url = Column(String(500), nullable=True)
    contract_published = Column(Boolean, default=False, nullable=False)
    payments_published = Column(Boolean, default=False, nullable=False)
    
    # Japanese PPP/PFI specific
    jppa_compliant = Column(Boolean, default=False, nullable=False)
    jica_guidelines = Column(Boolean, default=False, nullable=False)
    value_for_money_assessment = Column(JSONB, default=dict, nullable=False)
    
    # Trace
    trace_id = Column(String(128), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    contractor = relationship("GlobalContractor", back_populates="projects")
    payments = relationship("ProjectPayment", back_populates="project", lazy="dynamic")
    milestones_rel = relationship("ProjectMilestone", back_populates="project", lazy="dynamic")
    
    __table_args__ = (
        Index("ix_project_status_category", "status", "category"),
        Index("ix_project_location", "provincia", "municipio"),
        Index("ix_project_contractor", "contractor_id"),
        Index("ix_project_funding", "funding_model"),
    )


class ProjectMilestone(Base, AuditMixin):
    """Project milestone with KPI verification"""
    __tablename__ = "project_milestone"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    project_id = Column(UUID(as_uuid=True), ForeignKey("infrastructure_project.id"), nullable=False, index=True)
    
    # Identity
    milestone_number = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Targets
    target_date = Column(DateTime(timezone=True), nullable=False, index=True)
    completion_date = Column(DateTime(timezone=True), nullable=True)
    amount_pct = Column(Numeric(4, 3), nullable=False)  # Percentage of contract value
    
    # KPIs for this milestone
    kpis = Column(JSONB, default=dict, nullable=False)  # {kpi_name: {target, actual, unit, verified}}
    
    # Verification
    verified_by_contractor = Column(Boolean, default=False, nullable=False)
    verified_by_supervisor = Column(Boolean, default=False, nullable=False)
    verified_by_citizen = Column(Boolean, default=False, nullable=False)
    
    # Evidence
    evidence_photos = Column(JSONB, default=list, nullable=False)
    evidence_documents = Column(JSONB, default=list, nullable=False)
    citizen_observations = Column(JSONB, default=list, nullable=False)
    
    # Status
    status = Column(String(50), default="pending", nullable=False, index=True)  # pending, in_progress, completed, verified, paid, disputed
    
    # Payment
    payment_id = Column(UUID(as_uuid=True), ForeignKey("project_payment.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    project = relationship("InfrastructureProject", back_populates="milestones_rel")
    payment = relationship("ProjectPayment")
    
    __table_args__ = (
        UniqueConstraint("project_id", "milestone_number", name="uq_project_milestone_number"),
        Index("ix_milestone_target_date", "target_date"),
    )


class ProjectPayment(Base, AuditMixin):
    """Project payment with multi-party verification"""
    __tablename__ = "project_payment"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_number = Column(String(50), unique=True, nullable=False, index=True)
    
    project_id = Column(UUID(as_uuid=True), ForeignKey("infrastructure_project.id"), nullable=False, index=True)
    milestone_id = Column(UUID(as_uuid=True), ForeignKey("project_milestone.id"), nullable=True)
    
    # Amount
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Verification chain (required for release)
    contractor_certified = Column(Boolean, default=False, nullable=False)
    supervisor_certified = Column(Boolean, default=False, nullable=False)
    citizen_oversight_approved = Column(Boolean, default=False, nullable=False)
    fga_approved = Column(Boolean, default=False, nullable=False)  # Fundación de Gobernanza Algorítmica
    
    # Verification details
    contractor_certified_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    contractor_certified_at = Column(DateTime(timezone=True), nullable=True)
    supervisor_certified_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    supervisor_certified_at = Column(DateTime(timezone=True), nullable=True)
    citizen_approved_at = Column(DateTime(timezone=True), nullable=True)
    fga_approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    status = Column(String(50), default="pending", nullable=False, index=True)  # pending, verified, approved, paid, rejected
    
    # Execution
    paid_at = Column(DateTime(timezone=True), nullable=True)
    transaction_id = Column(String(100), nullable=True)
    
    # Trace
    trace_id = Column(String(128), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    project = relationship("InfrastructureProject", back_populates="payments")
    milestone = relationship("ProjectMilestone")
    
    __table_args__ = (
        Index("ix_project_payment_status", "status"),
        Index("ix_project_payment_verification", "contractor_certified", "supervisor_certified", "citizen_oversight_approved", "fga_approved"),
    )


# ==================== PERSONNEL MODELS ====================

class PersonnelTier(str, enum.Enum):
    TIER_1_EXECUTIVE = "tier_1_executive"      # Ministers, Directors
    TIER_2_SENIOR = "tier_2_senior"            # Deputy Directors, Managers
    TIER_3_PROFESSIONAL = "tier_3_professional" # Engineers, Analysts, Lawyers
    TIER_4_TECHNICAL = "tier_4_technical"       # Technicians, Inspectors
    TIER_5_ADMINISTRATIVE = "tier_5_administrative" # Admin, Support
    TIER_6_FIELD = "tier_6_field"               # Field workers, Couriers
    TIER_7_QUEST = "tier_7_quest"               # Quest visitors
    TIER_8_CITIZEN = "tier_8_citizen"           # Citizen participants


class PersonnelStatus(str, enum.Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    RETIRED = "retired"


class Personnel(Base, AuditMixin):
    """Government personnel with well-being management"""
    __tablename__ = "personnel"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Link to user
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), unique=True, nullable=False, index=True)
    
    # Employment
    employee_number = Column(String(50), unique=True, nullable=False, index=True)
    tier = Column(SQLEnum(PersonnelTier), nullable=False, index=True)
    status = Column(SQLEnum(PersonnelStatus), default=PersonnelStatus.ACTIVE, nullable=False)
    
    # Position
    position_title = Column(String(255), nullable=False)
    department = Column(String(255), nullable=False)
    division = Column(String(255), nullable=True)
    supervisor_id = Column(UUID(as_uuid=True), ForeignKey("personnel.id"), nullable=True)
    
    # Dates
    hire_date = Column(DateTime(timezone=True), nullable=False)
    contract_type = Column(String(50), default="permanent", nullable=False)  # permanent, contract, temporary
    contract_end = Column(DateTime(timezone=True), nullable=True)
    
    # Compensation
    base_salary = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="DOP", nullable=False)
    allowances = Column(JSONB, default=dict, nullable=False)  # transport, housing, risk, etc.
    
    # Bi-directional accounting (Attendant-Citizen)
    attendant_score = Column(Numeric(3, 2), default=5.0, nullable=False)  # How well they serve citizens
    citizen_feedback_score = Column(Numeric(3, 2), default=5.0, nullable=False)  # Citizen rating of attendant
    service_quality_index = Column(Numeric(3, 2), default=5.0, nullable=False)
    
    # Support Wallet (8 categories)
    support_wallet = Column(JSONB, default=dict, nullable=False)  # {category: {balance, used, limit}}
    # Categories: health, housing, education, transport, food, emergency, family, professional_development
    
    # Leave Management
    annual_leave_balance = Column(Numeric(5, 2), default=21, nullable=False)
    sick_leave_balance = Column(Numeric(5, 2), default=14, nullable=False)
    personal_leave_balance = Column(Numeric(5, 2), default=5, nullable=False)
    maternity_paternity_balance = Column(Numeric(5, 2), default=90, nullable=False)
    
    # Zero-gap coverage
    backup_personnel_id = Column(UUID(as_uuid=True), ForeignKey("personnel.id"), nullable=True)
    coverage_arrangements = Column(JSONB, default=list, nullable=False)
    
    # Predictive Life-Stage
    life_stage = Column(String(50), nullable=True)  # single, married, first_child, school_age, elder_care, pre_retirement
    anticipated_needs = Column(JSONB, default=list, nullable=False)
    proactive_allocations = Column(JSONB, default=dict, nullable=False)
    
    # Care Channel
    care_channel_active = Column(Boolean, default=False, nullable=False)
    care_channel_cases = Column(Integer, default=0, nullable=False)
    escalation_contact = Column(JSONB, default=dict, nullable=False)
    
    # Performance
    kpis = Column(JSONB, default=dict, nullable=False)
    last_performance_review = Column(DateTime(timezone=True), nullable=True)
    next_performance_review = Column(DateTime(timezone=True), nullable=True)
    
    # Well-being
    burnout_risk_score = Column(Numeric(3, 2), default=0, nullable=False)
    last_wellbeing_check = Column(DateTime(timezone=True), nullable=True)
    wellbeing_interventions = Column(JSONB, default=list, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")
    supervisor = relationship("Personnel", remote_side=[id])
    subordinates = relationship("Personnel", back_populates="supervisor")
    leave_requests = relationship("LeaveRequest", back_populates="personnel", lazy="dynamic")
    
    __table_args__ = (
        Index("ix_personnel_tier_status", "tier", "status"),
        Index("ix_personnel_department", "department"),
        Index("ix_personnel_supervisor", "supervisor_id"),
    )


class LeaveType(str, enum.Enum):
    ANNUAL = "annual"
    SICK = "sick"
    PERSONAL = "personal"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    EMERGENCY = "emergency"
    BEREAVEMENT = "bereavement"
    STUDY = "study"
    UNPAID = "unpaid"


class LeaveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class LeaveRequest(Base, AuditMixin):
    """Leave request with zero-gap coverage"""
    __tablename__ = "leave_request"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    leave_number = Column(String(50), unique=True, nullable=False, index=True)
    
    personnel_id = Column(UUID(as_uuid=True), ForeignKey("personnel.id"), nullable=False, index=True)
    leave_type = Column(SQLEnum(LeaveType), nullable=False, index=True)
    
    # Dates
    start_date = Column(DateTime(timezone=True), nullable=False, index=True)
    end_date = Column(DateTime(timezone=True), nullable=False, index=True)
    total_days = Column(Numeric(5, 2), nullable=False)
    
    # Reason
    reason = Column(Text, nullable=True)
    medical_certificate = Column(Boolean, default=False, nullable=False)
    certificate_reference = Column(String(100), nullable=True)
    
    # Coverage (Zero-gap)
    coverage_required = Column(Boolean, default=True, nullable=False)
    backup_personnel_id = Column(UUID(as_uuid=True), ForeignKey("personnel.id"), nullable=True)
    coverage_confirmed = Column(Boolean, default=False, nullable=False)
    coverage_confirmed_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    coverage_confirmed_at = Column(DateTime(timezone=True), nullable=True)
    coverage_arrangement = Column(JSONB, default=dict, nullable=False)
    
    # Status
    status = Column(SQLEnum(LeaveStatus), default=LeaveStatus.PENDING, nullable=False, index=True)
    
    # Approval
    approved_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Trace
    trace_id = Column(String(128), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    personnel = relationship("Personnel", back_populates="leave_requests")
    backup_personnel = relationship("Personnel", foreign_keys=[backup_personnel_id])
    approver = relationship("User", foreign_keys=[approved_by])
    coverage_confirmer = relationship("User", foreign_keys=[coverage_confirmed_by])
    
    __table_args__ = (
        Index("ix_leave_personnel_dates", "personnel_id", "start_date", "end_date"),
        Index("ix_leave_status_dates", "status", "start_date"),
        Index("ix_leave_coverage", "coverage_required", "coverage_confirmed"),
    )


# ==================== GOVERNANCE MODELS ====================

class AccountabilityLayer(str, enum.Enum):
    INTERNAL_1 = "internal_1"      # Operational
    INTERNAL_2 = "internal_2"      # Managerial
    INTERNAL_3 = "internal_3"      # Strategic
    INTERNAL_4 = "internal_4"      # Executive
    INTERNAL_5 = "internal_5"      # Ministerial
    INTERNAL_6 = "internal_6"      # Presidential
    GLOBAL_UN = "global_un"
    GLOBAL_OECD = "global_oecd"
    GLOBAL_OAS = "global_oas"
    GLOBAL_IDB = "global_idb"
    GLOBAL_WB = "global_wb"
    GLOBAL_IMF = "global_imf"
    GLOBAL_WHO = "global_who"
    GLOBAL_UNESCO = "global_unesco"
    GLOBAL_ILO = "global_ilo"
    GLOBAL_TI = "global_ti"


class InstitutionScore(Base):
    """Real-time institutional accountability scoring"""
    __tablename__ = "institution_score"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Institution
    institution_code = Column(String(50), nullable=False, index=True)
    institution_name = Column(String(255), nullable=False)
    layer = Column(SQLEnum(AccountabilityLayer), nullable=False, index=True)
    
    # Scores (0-100)
    overall_score = Column(Numeric(5, 2), default=50, nullable=False)
    transparency_score = Column(Numeric(5, 2), default=50, nullable=False)
    efficiency_score = Column(Numeric(5, 2), default=50, nullable=False)
    integrity_score = Column(Numeric(5, 2), default=50, nullable=False)
    responsiveness_score = Column(Numeric(5, 2), default=50, nullable=False)
    citizen_satisfaction_score = Column(Numeric(5, 2), default=50, nullable=False)
    
    # Data sources
    internal_metrics = Column(JSONB, default=dict, nullable=False)
    global_api_scores = Column(JSONB, default=dict, nullable=False)  # From 10 global APIs
    veeduria_contribution = Column(Numeric(5, 2), default=0, nullable=False)
    merit_weighted_citizen_score = Column(Numeric(5, 2), default=0, nullable=False)
    
    # Trend
    score_trend_7d = Column(Numeric(5, 2), default=0, nullable=False)
    score_trend_30d = Column(Numeric(5, 2), default=0, nullable=False)
    
    # Alerts
    alert_level = Column(String(20), default="normal", nullable=False)  # normal, watch, warning, critical
    active_alerts = Column(JSONB, default=list, nullable=False)
    
    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    previous_calculated_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        UniqueConstraint("institution_code", "calculated_at", name="uq_institution_score_time"),
        Index("ix_institution_score_layer", "layer"),
        Index("ix_institution_score_overall", "overall_score"),
        Index("ix_institution_score_alert", "alert_level"),
    )


class LiabilityRedressCase(Base, AuditMixin):
    """Japanese-style liability-redress framework"""
    __tablename__ = "liability_redress_case"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Claimant
    claimant_user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    claimant_type = Column(String(50), nullable=False)  # citizen, personnel, contractor, institution
    
    # Respondent
    respondent_type = Column(String(50), nullable=False)  # institution, contractor, personnel, algorithm
    respondent_id = Column(String(100), nullable=False, index=True)  # Institution code, contractor code, etc.
    
    # Claim
    claim_category = Column(String(100), nullable=False)  # algorithmic_harm, service_failure, corruption, negligence, discrimination
    claim_amount = Column(Numeric(15, 2), nullable=True)
    description = Column(Text, nullable=False)
    evidence = Column(JSONB, default=list, nullable=False)
    
    # Algorithmic specifics
    algorithmic_decision_id = Column(String(128), nullable=True)
    algorithmic_trace_id = Column(String(128), nullable=True)
    model_family = Column(String(50), nullable=True)
    consensus_level = Column(String(50), nullable=True)
    
    # Status
    status = Column(String(50), default="filed", nullable=False, index=True)  # filed, under_review, mediation, arbitration, adjudicated, settled, appealed, closed
    
    # Process
    assigned_mediator = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    assigned_arbitrator = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    fga_review = Column(Boolean, default=False, nullable=False)
    fga_decision = Column(JSONB, default=dict, nullable=False)
    
    # Resolution
    resolution_type = Column(String(50), nullable=True)  # compensation, correction, apology, policy_change, systemic_fix
    resolution_amount = Column(Numeric(15, 2), nullable=True)
    resolution_details = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Precedent
    sets_precedent = Column(Boolean, default=False, nullable=False)
    precedent_category = Column(String(100), nullable=True)
    
    # Trace
    trace_id = Column(String(128), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    claimant = relationship("User", foreign_keys=[claimant_user_id])
    mediator = relationship("User", foreign_keys=[assigned_mediator])
    arbitrator = relationship("User", foreign_keys=[assigned_arbitrator])
    
    __table_args__ = (
        Index("ix_liability_respondent", "respondent_type", "respondent_id"),
        Index("ix_liability_algorithmic", "algorithmic_decision_id"),
        Index("ix_liability_status", "status"),
    )


# Import func
from sqlalchemy.sql import func