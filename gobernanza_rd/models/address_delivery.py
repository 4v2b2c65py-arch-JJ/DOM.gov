# Address, Delivery, Infrastructure, and Personnel Models
import enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Index, UniqueConstraint, Enum as SQLEnum, Numeric, JSON, Integer, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, declared_attr
from models.database import Base, SoftDeleteMixin, AuditMixin
import uuid


class DeliveryType(str, enum.Enum):
    HOUSING_KEYS = "housing_keys"
    APPLIANCE = "appliance"
    UTILITY_EQUIPMENT = "utility_equipment"
    FOOD_PACKAGE = "food_package"
    EMERGENCY_SUPPLIES = "emergency_supplies"
    MUTUAL_AID = "mutual_aid"
    DOCUMENTS = "documents"
    SELECTING_FRONT = "selecting_front"


class DeliveryStatus(str, enum.Enum):
    PENDING = "pending"
    PRE_VERIFYING = "pre_verifying"
    SCHEDULED = "scheduled"
    ASSIGNED = "assigned"
    EN_ROUTE = "en_route"
    DELIVERED = "delivered"
    FAILED = "failed"
    NEIGHBOR_CHAIN = "neighbor_chain"
    PICKUP_POINT = "pickup_point"
    RETURNED = "returned"


class Delivery(Base, AuditMixin):
    """Delivery with zero address entry - GPS + community references only"""
    __tablename__ = "delivery"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    delivery_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Type
    delivery_type = Column(SQLEnum(DeliveryType), nullable=False, index=True)
    status = Column(SQLEnum(DeliveryStatus), default=DeliveryStatus.PENDING, nullable=False, index=True)
    
    # Recipient (via user)
    recipient_user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    recipient_cedula_token = Column(String(128), nullable=False, index=True)  # Encrypted
    
    # Resolved Location (auto-filled from gov APIs + Quest)
    delivery_location_id = Column(UUID(as_uuid=True), ForeignKey("delivery_location.id"), nullable=False, index=True)
    
    # Package
    package_description = Column(Text, nullable=False)
    package_value = Column(Numeric(12, 2), nullable=True)
    package_weight_kg = Column(Numeric(6, 2), nullable=True)
    package_dimensions = Column(JSONB, nullable=True)  # {length, width, height} in cm
    requires_installation = Column(Boolean, default=False, nullable=False)
    temperature_controlled = Column(Boolean, default=False, nullable=False)
    fragile = Column(Boolean, default=False, nullable=False)
    
    # Scheduling
    preferred_window_start = Column(DateTime(timezone=True), nullable=True)
    preferred_window_end = Column(DateTime(timezone=True), nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Pre-verification
    pre_verification_required = Column(Boolean, default=False, nullable=False)
    pre_verification_id = Column(UUID(as_uuid=True), ForeignKey("quest_pre_verification.id"), nullable=True)
    pre_verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Courier Assignment
    courier_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True, index=True)
    courier_assigned_at = Column(DateTime(timezone=True), nullable=True)
    
    # Execution
    courier_departed_at = Column(DateTime(timezone=True), nullable=True)
    courier_arrived_at = Column(DateTime(timezone=True), nullable=True)
    delivery_attempted_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Delivery Result
    delivered_to = Column(String(50), nullable=True)  # recipient, neighbor, pickup_point
    neighbor_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    pickup_point_id = Column(UUID(as_uuid=True), ForeignKey("pickup_point.id"), nullable=True)
    
    # Proof
    delivery_photo = Column(String(500), nullable=True)
    recipient_signature = Column(String(500), nullable=True)  # Base64 encoded
    courier_gps_lat = Column(Numeric(10, 8), nullable=True)
    courier_gps_lng = Column(Numeric(11, 8), nullable=True)
    
    # Chain tracking (for neighbor/community delivery)
    delivery_chain = Column(JSONB, default=list, nullable=False)  # [{to, at, by, proof}]
    
    # Notifications
    recipient_notified = Column(Boolean, default=False, nullable=False)
    recipient_notified_at = Column(DateTime(timezone=True), nullable=True)
    notification_channels = Column(JSONB, default=list, nullable=False)  # whatsapp, sms, push, call
    
    # Trace
    trace_id = Column(String(128), nullable=False, index=True)
    previous_trace_hash = Column(String(64), nullable=True)
    trace_hash = Column(String(64), nullable=False, index=True)
    
    # Merit
    merit_earned = Column(Numeric(10, 2), default=0, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    recipient = relationship("User", foreign_keys=[recipient_user_id])
    courier = relationship("User", foreign_keys=[courier_id])
    neighbor = relationship("User", foreign_keys=[neighbor_id])
    delivery_location = relationship("DeliveryLocation")
    pre_verification = relationship("QuestPreVerification")
    pickup_point = relationship("PickupPoint")
    
    __table_args__ = (
        Index("ix_delivery_recipient_status", "recipient_user_id", "status"),
        Index("ix_delivery_courier_status", "courier_id", "status"),
        Index("ix_delivery_scheduled", "scheduled_at"),
        Index("ix_delivery_trace", "trace_id"),
    )


class CommunityReferenceType(str, enum.Enum):
    COLMADO = "colmado"
    IGLESIA = "iglesia"
    ESCUELA = "escuela"
    PARADA = "parada"
    PARQUE = "parque"
    FARMACIA = "farmacia"
    CENTRO_COMUNAL = "centro_comunal"
    JUNTA_VECINOS = "junta_vecinos"
    OTRO = "otro"


class CommunityReference(Base):
    """Community reference points for human navigation"""
    __tablename__ = "community_reference"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    delivery_location_id = Column(UUID(as_uuid=True), ForeignKey("delivery_location.id"), nullable=False, index=True)
    
    tipo = Column(SQLEnum(CommunityReferenceType), nullable=False)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # Location
    gps_lat = Column(Numeric(10, 8), nullable=False)
    gps_lng = Column(Numeric(11, 8), nullable=False)
    
    # Relative to delivery location
    distancia_metros = Column(Integer, nullable=False)
    direccion_cardinal = Column(String(20), nullable=False)  # norte, sur, este, oeste, noreste, etc.
    
    # Verification
    verified = Column(Boolean, default=False, nullable=False)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Active
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    delivery_location = relationship("DeliveryLocation", back_populates="community_references")
    verifier = relationship("User")
    
    __table_args__ = (
        Index("ix_community_ref_location", "delivery_location_id"),
    )


class DesignatedNeighbor(Base):
    """Backup recipient for delivery"""
    __tablename__ = "designated_neighbor"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    delivery_location_id = Column(UUID(as_uuid=True), ForeignKey("delivery_location.id"), nullable=False, index=True)
    
    # Neighbor info
    nombre = Column(String(255), nullable=False)
    telefono = Column(String(20), nullable=False)
    cedula_token = Column(String(128), nullable=False)  # Encrypted
    relacion = Column(String(50), nullable=False)  # vecino, familiar, lider_comunitario
    
    # Verification
    verificado = Column(Boolean, default=False, nullable=False)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Availability
    horarios_disponibles = Column(JSONB, default=list, nullable=False)  # List of time windows
    instrucciones_especiales = Column(Text, nullable=True)
    
    # Active
    is_active = Column(Boolean, default=True, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)  # Primary backup
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    delivery_location = relationship("DeliveryLocation", back_populates="designated_neighbors")
    verifier = relationship("User")
    
    __table_args__ = (
        Index("ix_designated_neighbor_location", "delivery_location_id"),
    )


class DeliveryLocation(Base):
    """Complete delivery location - NO manual address entry"""
    __tablename__ = "delivery_location"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Owner
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    cedula_token = Column(String(128), nullable=False, index=True)  # Encrypted
    
    # Core identification
    nombre_completo = Column(String(255), nullable=False)
    telefono = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    
    # GPS Coordinates (PRIMARY for courier)
    latitud = Column(Numeric(10, 8), nullable=False)
    longitud = Column(Numeric(11, 8), nullable=False)
    precision_metros = Column(Integer, default=10, nullable=False)  # GPS accuracy
    
    # Structured address (from gov APIs - auto-filled)
    provincia = Column(String(100), nullable=True)
    municipio = Column(String(100), nullable=True)
    sector = Column(String(100), nullable=True)
    calle_principal = Column(String(255), nullable=True)
    numero_casa = Column(String(50), nullable=True)
    referencia_catastral = Column(String(100), nullable=True)  # MIVHED catastro reference
    
    # Community references (for human navigation)
    community_references = relationship("CommunityReference", back_populates="delivery_location", lazy="dynamic")
    designated_neighbors = relationship("DesignatedNeighbor", back_populates="delivery_location", lazy="dynamic")
    
    # Access instructions
    instrucciones_acceso = Column(Text, nullable=True)  # "Portón azul, tocar timbre 2 veces"
    codigo_acceso = Column(String(50), nullable=True)  # Building/condo access code
    
    # Delivery constraints
    horarios_disponibles = Column(JSONB, default=list, nullable=False)  # List of time windows
    requiere_autorizacion = Column(Boolean, default=False, nullable=False)
    instrucciones_especiales = Column(Text, nullable=True)
    
    # Verification metadata
    fuente_principal = Column(String(50), nullable=False)  # jce, mivhed, superate, ede, coraasan, quest
    ultima_verificacion = Column(DateTime(timezone=True), nullable=False)
    verificado_por_quest = Column(Boolean, default=False, nullable=False)
    quest_verificador_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    quest_verificacion_fecha = Column(DateTime(timezone=True), nullable=True)
    
    # Confidence score
    confidence_score = Column(Numeric(3, 2), default=0.5, nullable=False)  # 0.0 - 1.0
    
    # Versioning (for audit trail)
    version = Column(Integer, default=1, nullable=False)
    previous_version_id = Column(UUID(as_uuid=True), ForeignKey("delivery_location.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")
    quest_verificador = relationship("User", foreign_keys=[quest_verificador_id])
    previous_version = relationship("DeliveryLocation", remote_side=[id])
    
    __table_args__ = (
        Index("ix_delivery_location_user", "user_id"),
        Index("ix_delivery_location_gps", "latitud", "longitud"),
        Index("ix_delivery_location_sector", "provincia", "municipio", "sector"),
        Index("ix_delivery_location_confidence", "confidence_score"),
    )


class PickupPointType(str, enum.Enum):
    COLMADO = "colmado"
    IGLESIA = "iglesia"
    ESCUELA = "escuela"
    JUNTA_VECINOS = "junta_vecinos"
    CENTRO_COMUNAL = "centro_comunal"
    FARMACIA = "farmacia"
    OTRO = "otro"


class PickupPointStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FULL = "full"
    MAINTENANCE = "maintenance"


class PickupPoint(Base):
    """Community pickup points for failed deliveries"""
    __tablename__ = "pickup_point"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Identity
    code = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(255), nullable=False)
    tipo = Column(SQLEnum(PickupPointType), nullable=False, index=True)
    
    # Location
    provincia = Column(String(100), nullable=False)
    municipio = Column(String(100), nullable=False)
    sector = Column(String(100), nullable=False)
    latitud = Column(Numeric(10, 8), nullable=False)
    longitud = Column(Numeric(11, 8), nullable=False)
    direccion_detallada = Column(Text, nullable=True)
    
    # Contact
    contacto_nombre = Column(String(255), nullable=False)
    contacto_telefono = Column(String(20), nullable=False)
    contacto_email = Column(String(255), nullable=True)
    
    # Capacity
    capacidad = Column(String(20), default="small", nullable=False)  # small, medium, large
    capacidad_actual = Column(Integer, default=0, nullable=False)
    capacidad_maxima = Column(Integer, default=50, nullable=False)
    
    # Hours
    horario_apertura = Column(String(10), nullable=False)  # HH:MM
    horario_cierre = Column(String(10), nullable=False)  # HH:MM
    dias_operacion = Column(JSONB, default=["mon","tue","wed","thu","fri","sat"], nullable=False)
    
    # Trust
    trust_level = Column(String(20), default="medium", nullable=False)  # high, medium, low
    verificado = Column(Boolean, default=False, nullable=False)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    status = Column(SQLEnum(PickupPointStatus), default=PickupPointStatus.ACTIVE, nullable=False, index=True)
    
    # Metrics
    deliveries_received = Column(Integer, default=0, nullable=False)
    deliveries_collected = Column(Integer, default=0, nullable=False)
    avg_collection_time_hours = Column(Numeric(5, 2), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        Index("ix_pickup_point_location", "provincia", "municipio", "sector"),
        Index("ix_pickup_point_gps", "latitud", "longitud"),
        Index("ix_pickup_point_status_tipo", "status", "tipo"),
    )


class AddressCorrection(Base, AuditMixin):
    """Quest-reported address corrections"""
    __tablename__ = "address_correction"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    cedula_token = Column(String(128), nullable=False, index=True)  # Encrypted
    
    # Reporter
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    
    # System location (what we had)
    system_latitud = Column(Numeric(10, 8), nullable=True)
    system_longitud = Column(Numeric(11, 8), nullable=True)
    system_data = Column(JSONB, default=dict, nullable=False)
    
    # Observed location (what Quest visitor found)
    observed_latitud = Column(Numeric(10, 8), nullable=False)
    observed_longitud = Column(Numeric(11, 8), nullable=False)
    observed_precision = Column(Integer, nullable=False)
    observed_data = Column(JSONB, default=dict, nullable=False)
    
    # Community references observed
    community_references = Column(JSONB, default=list, nullable=False)
    access_instructions = Column(Text, nullable=True)
    designated_neighbor = Column(JSONB, nullable=True)
    
    # Confidence
    confidence = Column(Numeric(3, 2), nullable=False)  # 0.0 - 1.0
    
    # Status
    applied = Column(Boolean, default=False, nullable=False)
    applied_at = Column(DateTime(timezone=True), nullable=True)
    applied_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    new_location_id = Column(UUID(as_uuid=True), ForeignKey("delivery_location.id"), nullable=True)
    
    # Review
    queued_for_review = Column(Boolean, default=False, nullable=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Trace
    trace_id = Column(String(128), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    reporter = relationship("User", back_populates="address_corrections")
    applier = relationship("User", foreign_keys=[applied_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    new_location = relationship("DeliveryLocation")
    
    __table_args__ = (
        Index("ix_address_correction_cedula", "cedula_token"),
        Index("ix_address_correction_status", "applied", "queued_for_review"),
    )


# Import func
from sqlalchemy.sql import func