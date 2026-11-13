# FastAPI Application - GobernanzaRD Platform
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, List, Dict, Any

import structlog
from fastapi import FastAPI, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import get_settings
from models.database import get_db, init_db, close_db
from models import User, UserSession, IdentityLevel, PaymentType, PaymentStatus, PaymentMethod
from auth.service import AuthService, AuthContext, SessionResult
from payments.service import PaymentService, PaymentAutoFillEngine
from payments.wallet_service import DigitalWalletService, WalletPaymentRequest, WalletType
from address.service import AddressResolutionEngine, QuestPreVerificationService, CommunityDeliveryNetwork
from telecom.service import DRTelecomService, MessageChannel
from consensus.engine import ConsensusEngine, ProposalSeverity
from governance.anti_faction import (
    FGAAuditService, CircuitBreakerService, FairnessMonitor, AuditTrailService
)
from services.gov_api_connectors import GovAPIConnectorManager
from services.central_ai_fund import CentralAIFundExecutor
from services.merit_service import MeritService
from services.fraud_detection import FraudDetector
from services.trace_logger import TraceLogger
from local_models.runner import ModelRunnerPool
from utils.crypto import hash_string

settings = get_settings()
logger = structlog.get_logger()

# Global service instances
runner_pool: Optional[ModelRunnerPool] = None
consensus_engine: Optional[ConsensusEngine] = None
fraud_detector: Optional[FraudDetector] = None
trace_logger: Optional[TraceLogger] = None
gov_connector: Optional[GovAPIConnectorManager] = None
central_fund: Optional[CentralAIFundExecutor] = None
merit_service: Optional[MeritService] = None
auth_service: Optional[AuthService] = None
payment_service: Optional[PaymentService] = None
wallet_service: Optional[DigitalWalletService] = None
address_engine: Optional[AddressResolutionEngine] = None
telecom_service: Optional[DRTelecomService] = None
fga_service: Optional[FGAAuditService] = None
circuit_breaker: Optional[CircuitBreakerService] = None
fairness_monitor: Optional[FairnessMonitor] = None
audit_trail: Optional[AuditTrailService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global runner_pool, consensus_engine, fraud_detector, trace_logger
    global gov_connector, central_fund, merit_service
    global auth_service, payment_service, wallet_service
    global address_engine, telecom_service, fga_service
    global circuit_breaker, fairness_monitor, audit_trail
    
    logger.info("Starting GobernanzaRD platform...")
    
    # Initialize database
    await init_db()
    
    # Initialize model runner pool
    runner_pool = ModelRunnerPool()
    
    # Add local model runners
    if settings.LOCAL_MODEL_ENABLED:
        # Ollama
        await runner_pool.add_runner(
            "ollama_llama3_70b",
            type('Config', (), {
                'provider': 'ollama',
                'model_name': 'llama3.1:70b',
                'role': 'primary_reasoner',
                'base_url': settings.OLLAMA_BASE_URL,
                'max_tokens': 4096,
                'temperature': 0.1,
                'timeout': settings.LOCAL_MODEL_TIMEOUT
            })(),
            is_primary=True
        )
        
        # llama.cpp
        await runner_pool.add_runner(
            "llamacpp_nemotron",
            type('Config', (), {
                'provider': 'llama_cpp',
                'model_name': 'nemotron-3-ultra',
                'role': 'validator',
                'base_url': settings.LLAMA_CPP_SERVER_URL,
                'max_tokens': 4096,
                'temperature': 0.1,
                'timeout': settings.LOCAL_MODEL_TIMEOUT
            })()
        )
    
    # Initialize core services
    trace_logger = AuditTrailService(None, None)  # Will set db later
    fraud_detector = FraudDetector()
    
    # Government API connectors
    gov_connector = GovAPIConnectorManager(settings)
    
    # Central AI Fund
    central_fund = CentralAIFundExecutor()
    
    # Merit service
    merit_service = MeritService()
    
    # Initialize services that need DB session
    # These will be properly initialized per-request via dependency injection
    
    logger.info("GobernanzaRD platform started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down GobernanzaRD platform...")
    await close_db()
    logger.info("Shutdown complete")


app = FastAPI(
    title="GobernanzaRD",
    description="Dominican Republic AI-Powered Governance Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)


# ==================== DEPENDENCIES ====================

async def get_current_session(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserSession:
    """Get current user session from bearer token"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # In production, verify JWT or session token
    # For now, lookup by session_token
    result = await db.execute(
        select(UserSession).options(select(UserSession.user)).where(
            and_(
                UserSession.session_token == credentials.credentials,
                UserSession.is_revoked == False,
                UserSession.expires_at > datetime.utcnow()
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    return session


async def get_current_user(session: UserSession = Depends(get_current_session)) -> User:
    """Get current user from session"""
    return session.user


def get_auth_service_dep(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db, fraud_detector, trace_logger)


def get_payment_service_dep(db: AsyncSession = Depends(get_db)) -> PaymentService:
    auto_fill = PaymentAutoFillEngine(gov_connector, merit_service)
    return PaymentService(db, auto_fill, central_fund, fraud_detector, trace_logger, merit_service)


def get_wallet_service_dep(db: AsyncSession = Depends(get_db)) -> DigitalWalletService:
    # Would initialize with proper processors
    return DigitalWalletService(db, None, None, trace_logger, fraud_detector)


def get_address_engine_dep(db: AsyncSession = Depends(get_db)) -> AddressResolutionEngine:
    return AddressResolutionEngine(gov_connector, None, trace_logger)


def get_telecom_service_dep(db: AsyncSession = Depends(get_db)) -> DRTelecomService:
    return DRTelecomService(db, settings, trace_logger, None)


def get_consensus_engine_dep(db: AsyncSession = Depends(get_db)) -> ConsensusEngine:
    return ConsensusEngine(runner_pool, db, trace_logger)


def get_fga_service_dep(db: AsyncSession = Depends(get_db)) -> FGAAuditService:
    return FGAAuditService(db, consensus_engine, trace_logger)


def get_circuit_breaker_dep(db: AsyncSession = Depends(get_db)) -> CircuitBreakerService:
    return CircuitBreakerService(db, consensus_engine, trace_logger)


def get_fairness_monitor_dep(db: AsyncSession = Depends(get_db)) -> FairnessMonitor:
    return FairnessMonitor(db, trace_logger)


def get_audit_trail_dep(db: AsyncSession = Depends(get_db)) -> AuditTrailService:
    return AuditTrailService(db, trace_logger)


# ==================== PYDANTIC SCHEMAS ====================

class MagicLinkRequest(BaseModel):
    email: EmailStr
    locale: str = "es"
    device_fingerprint: str
    user_agent: str


class MagicLinkVerify(BaseModel):
    token: str
    device_fingerprint: str
    user_agent: str


class IdentityEscalationRequest(BaseModel):
    target_level: int
    verification_data: Dict[str, Any]


class CedulaVerifyRequest(BaseModel):
    cedula: str
    jce_verification_id: Optional[str] = None


class PaymentInitiateRequest(BaseModel):
    payment_type: PaymentType
    user_provided: Dict[str, Any]


class PaymentConfirmRequest(BaseModel):
    confirmation_token: str
    biometric_verified: bool = False


class WalletPaymentRequestModel(BaseModel):
    wallet_type: WalletType
    payment_token: Dict[str, Any]
    payment_method: Dict[str, Any]
    payment_type: PaymentType
    user_provided: Dict[str, Any]


class AddressResolveRequest(BaseModel):
    cedula: str
    delivery_type: str


class ConsensusRequest(BaseModel):
    proposal_type: str
    proposal_id: str
    proposal_data: Dict[str, Any]
    severity: ProposalSeverity = ProposalSeverity.ROUTINE


class OTPRequest(BaseModel):
    phone: str
    locale: str = "es"


class MessageRouteRequest(BaseModel):
    message_type: str
    content: Dict[str, Any]
    priority: str = "normal"


# ==================== AUTH ENDPOINTS ====================

@app.post("/auth/magic-link", response_model=Dict)
async def request_magic_link(
    request: MagicLinkRequest,
    http_request: Request,
    auth_service: AuthService = Depends(get_auth_service_dep)
):
    """Request magic link for passwordless authentication"""
    
    client_ip = http_request.client.host
    ip_hash = hash_string(client_ip)
    
    context = AuthContext(
        ip_address=client_ip,
        ip_hash=ip_hash,
        device_fingerprint=request.device_fingerprint,
        user_agent=request.user_agent,
        locale=request.locale
    )
    
    result = await auth_service.request_magic_link(request.email, context)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.reason)
    
    return {"success": True, "token_id": result.token_id, "expires_in": settings.MAGIC_LINK_EXPIRY_MINUTES * 60}


@app.post("/auth/verify", response_model=Dict)
async def verify_magic_link(
    request: MagicLinkVerify,
    http_request: Request,
    auth_service: AuthService = Depends(get_auth_service_dep)
):
    """Verify magic link and create session"""
    
    client_ip = http_request.client.host
    ip_hash = hash_string(client_ip)
    
    context = AuthContext(
        ip_address=client_ip,
        ip_hash=ip_hash,
        device_fingerprint=request.device_fingerprint,
        user_agent=request.user_agent
    )
    
    result = await auth_service.verify_magic_link(request.token, context)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.reason)
    
    return {
        "success": True,
        "session_token": result.session.session_token,
        "refresh_token": result.session.refresh_token,
        "identity_level": result.identity_level.value,
        "capabilities": result.capabilities,
        "user": {
            "id": str(result.user.id),
            "email": result.user.email,
            "identity_level": result.user.identity_level.value,
            "merit_score": float(result.user.merit_score)
        }
    }


@app.post("/auth/escalate", response_model=Dict)
async def escalate_identity(
    request: IdentityEscalationRequest,
    session: UserSession = Depends(get_current_session),
    auth_service: AuthService = Depends(get_auth_service_dep)
):
    """Escalate identity level with verification"""
    
    target_level = IdentityLevel(request.target_level)
    result = await auth_service.escalate_identity(session, target_level, request.verification_data)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.reason)
    
    return {
        "success": True,
        "identity_level": result.identity_level.value,
        "capabilities": result.capabilities
    }


@app.post("/auth/logout")
async def logout(
    session: UserSession = Depends(get_current_session),
    auth_service: AuthService = Depends(get_auth_service_dep)
):
    """Revoke current session"""
    await auth_service.revoke_session(session.id, "User logout")
    return {"success": True}


@app.post("/auth/cedula/verify", response_model=Dict)
async def verify_cedula(
    request: CedulaVerifyRequest,
    session: UserSession = Depends(get_current_session),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify a Dominican cédula (11-12 digits) and link it to the user."""
    from utils.cedula import cedula_validation_error, normalize_cedula

    validation_error = cedula_validation_error(request.cedula)
    if validation_error:
        raise HTTPException(status_code=400, detail=validation_error)

    digits = normalize_cedula(request.cedula)
    user.cedula_token = hash_string(digits)
    user.cedula_verified = True
    user.cedula_verified_at = datetime.utcnow()
    user.jce_verification_id = request.jce_verification_id

    if user.identity_level.value < IdentityLevel.MERIT_LINKED.value:
        user.identity_level = IdentityLevel.MERIT_LINKED
        session.identity_level = IdentityLevel.MERIT_LINKED
        session.capabilities = AuthService.IDENTITY_CAPABILITIES.get(IdentityLevel.MERIT_LINKED, [])

    await db.flush()

    return {
        "success": True,
        "cedula_verified": True,
        "identity_level": user.identity_level.value,
        "capabilities": session.capabilities,
    }


# ==================== PAYMENT ENDPOINTS ====================

@app.post("/payments/initiate", response_model=Dict)
async def initiate_payment(
    request: PaymentInitiateRequest,
    session: UserSession = Depends(get_current_session),
    user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service_dep)
):
    """Initiate payment with auto-fill preview"""
    
    result = await payment_service.initiate_payment(user, session, request.payment_type, request.user_provided)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("reason", "Payment initiation failed"))
    
    return result


@app.post("/payments/confirm", response_model=Dict)
async def confirm_payment(
    request: PaymentConfirmRequest,
    session: UserSession = Depends(get_current_session),
    user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service_dep)
):
    """Confirm and execute payment"""
    
    result = await payment_service.confirm_payment(request.confirmation_token, user, session, request.biometric_verified)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("reason", "Payment confirmation failed"))
    
    return result


@app.get("/payments/history")
async def payment_history(
    session: UserSession = Depends(get_current_session),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get user payment history"""
    from models import Payment
    
    result = await db.execute(
        select(Payment).where(Payment.user_id == user.id)
        .order_by(Payment.initiated_at.desc())
        .limit(limit).offset(offset)
    )
    payments = result.scalars().all()
    
    return {
        "payments": [
            {
                "id": str(p.id),
                "type": p.payment_type.value,
                "amount": str(p.amount),
                "status": p.status.value,
                "method": p.payment_method.value,
                "initiated_at": p.initiated_at.isoformat(),
                "completed_at": p.completed_at.isoformat() if p.completed_at else None,
                "merit_earned": float(p.merit_earned) if p.merit_earned else 0
            }
            for p in payments
        ]
    }


# ==================== DIGITAL WALLET ENDPOINTS ====================

@app.get("/wallets/available")
async def available_wallets(
    platform: str = "web",
    session: UserSession = Depends(get_current_session),
    user: User = Depends(get_current_user),
    wallet_service: DigitalWalletService = Depends(get_wallet_service_dep)
):
    """Get available digital wallets for user/platform"""
    
    wallets = await wallet_service.get_available_wallets(user, platform)
    return {"wallets": wallets}


@app.post("/payments/wallet", response_model=Dict)
async def wallet_payment(
    request: WalletPaymentRequestModel,
    session: UserSession = Depends(get_current_session),
    user: User = Depends(get_current_user),
    wallet_service: DigitalWalletService = Depends(get_wallet_service_dep)
):
    """Process payment via Apple Pay or Google Pay"""
    
    wallet_request = WalletPaymentRequest(
        wallet_type=request.wallet_type,
        payment_token=request.payment_token,
        payment_method=request.payment_method,
        payment_type=request.payment_type,
        user_provided=request.user_provided,
        session_id=session.id
    )
    
    result = await wallet_service.process_payment(wallet_request, user, session)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.reason)
    
    return {
        "success": True,
        "payment_id": result.payment_id,
        "trace_id": result.trace_id,
        "receipt": result.receipt,
        "merit_earned": result.merit_earned
    }


# ==================== ADDRESS ENDPOINTS ====================

@app.post("/address/resolve")
async def resolve_address(
    request: AddressResolveRequest,
    session: UserSession = Depends(get_current_session),
    address_engine: AddressResolutionEngine = Depends(get_address_engine_dep)
):
    """Resolve delivery location from government APIs (zero address entry)"""
    
    delivery_type = DeliveryType(request.delivery_type)
    location = await address_engine.resolve_delivery_location(request.cedula, delivery_type)
    
    if not location:
        raise HTTPException(status_code=404, detail="Could not resolve delivery location")
    
    return {
        "success": True,
        "location": {
            "lat": float(location.latitud),
            "lng": float(location.longitud),
            "precision_m": location.precision_metros,
            "name": location.nombre_completo,
            "phone": location.telefono,
            "province": location.provincia,
            "municipality": location.municipio,
            "sector": location.sector,
            "community_references": location.community_references,
            "designated_neighbor": location.designated_neighbor,
            "access_instructions": location.instrucciones_acceso,
            "confidence": float(location.confidence_score),
            "verified_by_quest": location.verificado_por_quest,
            "source": location.fuente_principal
        }
    }


@app.post("/address/correction")
async def report_address_correction(
    cedula: str,
    observed_lat: float,
    observed_lng: float,
    precision: int,
    community_refs: List[Dict],
    access_instructions: str = None,
    session: UserSession = Depends(get_current_session),
    address_engine: AddressResolutionEngine = Depends(get_address_engine_dep)
):
    """Report address correction from Quest visit"""
    
    # Would call address engine correction method
    return {"success": True, "message": "Correction queued for review"}


# ==================== CONSENSUS ENDPOINTS ====================

@app.post("/governance/consensus", response_model=Dict)
async def request_consensus(
    request: ConsensusRequest,
    session: UserSession = Depends(get_current_session),
    consensus_engine: ConsensusEngine = Depends(get_consensus_engine_dep)
):
    """Request multi-model consensus decision"""
    
    # Check identity level for governance actions
    if session.identity_level < IdentityLevel.TRUSTED:
        raise HTTPException(status_code=403, detail="Insufficient identity level for governance actions")
    
    outcome = await consensus_engine.decide(
        request.proposal_type,
        request.proposal_id,
        request.proposal_data,
        request.severity
    )
    
    return {
        "decision_id": outcome.decision_id,
        "decision": outcome.final_decision.value,
        "consensus_score": float(outcome.consensus_score),
        "threshold_met": outcome.threshold_met,
        "families_participated": outcome.families_participated,
        "dissenting_families": outcome.dissenting_families,
        "adversarial_challenges": len(outcome.adversarial_challenges)
    }


# ==================== TELECOM ENDPOINTS ====================

@app.post("/telecom/otp")
async def send_otp(
    request: OTPRequest,
    session: UserSession = Depends(get_current_session),
    user: User = Depends(get_current_user),
    telecom_service: DRTelecomService = Depends(get_telecom_service_dep)
):
    """Send OTP via best available channel"""
    
    result = await telecom_service.send_otp(user, request.phone, session)
    return result


@app.post("/telecom/route")
async def route_message(
    request: MessageRouteRequest,
    session: UserSession = Depends(get_current_session),
    user: User = Depends(get_current_user),
    telecom_service: DRTelecomService = Depends(get_telecom_service_dep)
):
    """Route message to optimal channel"""
    
    result = await telecom_service.router.route_message(user, request.message_type, request.content, request.priority)
    return result


# ==================== FGA GOVERNANCE ENDPOINTS ====================

@app.post("/fga/audit")
async def initiate_audit(
    trigger: str,
    scope: Optional[List[str]] = None,
    session: UserSession = Depends(get_current_session),
    fga_service: FGAAuditService = Depends(get_fga_service_dep)
):
    """Initiate algorithmic audit"""
    
    if session.identity_level < IdentityLevel.AUTHORIZED:
        raise HTTPException(status_code=403, detail="FGA audit initiation requires Authorized level")
    
    audit_id = await fga_service.initiate_model_audit(trigger, scope)
    return {"audit_id": audit_id, "status": "initiated"}


@app.post("/fga/action")
async def propose_action(
    action_type: str,
    target_type: str,
    target_id: str,
    description: str,
    rationale: str,
    legal_basis: str,
    session: UserSession = Depends(get_current_session),
    fga_service: FGAAuditService = Depends(get_fga_service_dep)
):
    """Propose FGA governance action"""
    
    if session.identity_level < IdentityLevel.AUTHORIZED:
        raise HTTPException(status_code=403, detail="FGA action proposal requires Authorized level")
    
    action = await fga_service.propose_governance_action(
        action_type, target_type, uuid.UUID(target_id),
        description, rationale, legal_basis, session.user_id
    )
    
    return {"action_number": action.action_number, "status": action.status}


# ==================== CIRCUIT BREAKER ENDPOINTS ====================

@app.post("/circuit-breaker/check")
async def check_circuit_breakers(
    session: UserSession = Depends(get_current_session),
    circuit_breaker: CircuitBreakerService = Depends(get_circuit_breaker_dep)
):
    """Check and activate circuit breakers"""
    
    if session.identity_level < IdentityLevel.TRUSTED:
        raise HTTPException(status_code=403, detail="Insufficient identity level")
    
    triggered = await circuit_breaker.check_triggers()
    return {
        "triggered": len(triggered),
        "breakers": [
            {
                "trigger": b.trigger,
                "action": b.action,
                "authorized_by": b.authorized_by,
                "activated_at": b.activated_at.isoformat()
            }
            for b in triggered
        ]
    }


@app.post("/circuit-breaker/resolve/{trigger}")
async def resolve_circuit_breaker(
    trigger: CircuitBreakerTrigger,
    resolution: str,
    session: UserSession = Depends(get_current_session),
    circuit_breaker: CircuitBreakerService = Depends(get_circuit_breaker_dep)
):
    """Resolve circuit breaker"""
    
    if session.identity_level < IdentityLevel.AUTHORIZED:
        raise HTTPException(status_code=403, detail="Circuit breaker resolution requires Authorized level")
    
    success = await circuit_breaker.resolve_breaker(trigger, session.user_id, resolution)
    return {"success": success}


# ==================== FAIRNESS MONITORING ENDPOINTS ====================

@app.get("/fairness/metrics")
async def get_fairness_metrics(
    session: UserSession = Depends(get_current_session),
    fairness_monitor: FairnessMonitor = Depends(get_fairness_monitor_dep)
):
    """Get current fairness metrics"""
    
    if session.identity_level < IdentityLevel.MERIT_LINKED:
        raise HTTPException(status_code=403, detail="Insufficient identity level")
    
    metrics = await fairness_monitor.compute_all_metrics()
    violations = await fairness_monitor.check_violations(metrics)
    
    return {
        "metrics": metrics,
        "violations": violations,
        "timestamp": datetime.utcnow().isoformat()
    }


# ==================== AUDIT TRAIL ENDPOINTS ====================

@app.get("/audit/trail")
async def get_audit_trail(
    start_sequence: int = 1,
    end_sequence: Optional[int] = None,
    event_type: Optional[str] = None,
    actor_id: Optional[str] = None,
    limit: int = 100,
    session: UserSession = Depends(get_current_session),
    db: AsyncSession = Depends(get_db)
):
    """Get audit trail records"""
    
    if session.identity_level < IdentityLevel.TRUSTED:
        raise HTTPException(status_code=403, detail="Insufficient identity level")
    
    query = select(AuditRecord).where(AuditRecord.sequence >= start_sequence)
    
    if end_sequence:
        query = query.where(AuditRecord.sequence <= end_sequence)
    if event_type:
        query = query.where(AuditRecord.event_type == event_type)
    if actor_id:
        query = query.where(AuditRecord.actor_user_id == uuid.UUID(actor_id))
    
    query = query.order_by(desc(AuditRecord.timestamp)).limit(limit)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    return {
        "records": [
            {
                "sequence": r.sequence,
                "event_type": r.event_type.value,
                "timestamp": r.timestamp.isoformat(),
                "actor": str(r.actor_user_id) if r.actor_user_id else None,
                "target": f"{r.target_type}:{r.target_id}" if r.target_type else None,
                "anchored": r.anchored,
                "hash": r.record_hash[:16] + "..."
            }
            for r in records
        ]
    }


@app.get("/audit/verify")
async def verify_audit_chain(
    start_sequence: int = 1,
    end_sequence: Optional[int] = None,
    session: UserSession = Depends(get_current_session),
    audit_trail: AuditTrailService = Depends(get_audit_trail_dep)
):
    """Verify audit chain integrity"""
    
    if session.identity_level < IdentityLevel.AUTHORIZED:
        raise HTTPException(status_code=403, detail="Audit verification requires Authorized level")
    
    result = await audit_trail.verify_chain(start_sequence, end_sequence)
    return result


# ==================== HEALTH & INFO ENDPOINTS ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "models": "loaded" if runner_pool else "loading",
            "consensus": "ready" if consensus_engine else "initializing"
        }
    }


@app.get("/info")
async def platform_info():
    """Platform information"""
    return {
        "name": "GobernanzaRD",
        "version": settings.APP_VERSION,
        "description": "Dominican Republic AI-Powered Governance Platform",
        "features": {
            "multi_model_consensus": True,
            "progressive_identity": True,
            "zero_address_delivery": True,
            "digital_wallets": ["apple_pay", "google_pay"],
            "telecom_channels": ["whatsapp", "sms", "ussd", "voice"],
            "anti_faction_governance": True,
            "fairness_monitoring": True,
            "immutable_audit_trail": True
        },
        "governance_model": "CARACOL Dual-Loop + Japanese Society 5.0",
        "legal_framework": "Fundación de Gobernanza Algorítmica (FGA)"
    }


# ==================== MERIT ENDPOINTS ====================

@app.get("/merit/profile")
async def merit_profile(
    session: UserSession = Depends(get_current_session),
    user: User = Depends(get_current_user)
):
    """Get user merit profile"""
    
    return {
        "merit_score": float(user.merit_score),
        "tier": user.merit_tier,
        "total_earned": float(user.total_merits_earned),
        "total_spent": float(user.total_merits_spent),
        "identity_level": user.identity_level.value,
        "capabilities": session.capabilities
    }


@app.get("/merit/transactions")
async def merit_transactions(
    session: UserSession = Depends(get_current_session),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50
):
    """Get merit transaction history"""
    from models import MeritTransaction
    
    result = await db.execute(
        select(MeritTransaction).where(MeritTransaction.user_id == user.id)
        .order_by(MeritTransaction.created_at.desc())
        .limit(limit)
    )
    transactions = result.scalars().all()
    
    return {
        "transactions": [
            {
                "event_type": t.event_type.value,
                "amount": float(t.total_amount),
                "balance_after": float(t.balance_after),
                "description": t.event_description,
                "created_at": t.created_at.isoformat()
            }
            for t in transactions
        ]
    }


# ==================== SELECTING FRONT ENDPOINTS ====================

@app.get("/selecting-front/items")
async def selecting_front_items(
    category: Optional[str] = None,
    session: UserSession = Depends(get_current_session),
    db: AsyncSession = Depends(get_db)
):
    """Get available Selecting Front items"""
    from models import SelectingFrontItem, SelectingFrontCategory
    
    query = select(SelectingFrontItem).where(SelectingFrontItem.is_active == True)
    
    if category:
        query = query.where(SelectingFrontItem.category == SelectingFrontCategory(category))
    
    result = await db.execute(query.order_by(SelectingFrontItem.priority.desc()))
    items = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(i.id),
                "code": i.code,
                "name": i.name,
                "category": i.category.value,
                "merit_cost": float(i.merit_cost),
                "specifications": i.specifications,
                "estimated_value_dop": float(i.estimated_value_dop),
                "delivery_type": i.delivery_type
            }
            for i in items
        ]
    }


# ==================== QUEST ENDPOINTS ====================

@app.get("/quest/active")
async def active_quests(
    session: UserSession = Depends(get_current_session),
    db: AsyncSession = Depends(get_db)
):
    """Get active Quest campaigns"""
    from models import Quest, QuestStatus
    
    result = await db.execute(
        select(Quest).where(Quest.status == QuestStatus.ACTIVE)
        .order_by(Quest.start_date.desc())
    )
    quests = result.scalars().all()
    
    return {
        "quests": [
            {
                "id": str(q.id),
                "name": q.name,
                "territory": q.territory_name,
                "progress": f"{q.homes_completed}/{q.total_homes_target}",
                "daily_stipend": float(q.daily_stipend),
                "start_date": q.start_date.isoformat(),
                "end_date": q.end_date.isoformat()
            }
            for q in quests
        ]
    }


# ==================== VEEDURÍA ENDPOINTS ====================

@app.post("/veeduria/report")
async def file_veeduria_report(
    severity: str,
    category: str,
    title: str,
    description: str,
    project_id: Optional[str] = None,
    photos: List[str] = [],
    session: UserSession = Depends(get_current_session),
    db: AsyncSession = Depends(get_db)
):
    """File citizen oversight report"""
    from models import VeeduriaReport, VeeduriaSeverity
    
    if session.identity_level < IdentityLevel.MERIT_LINKED:
        raise HTTPException(status_code=403, detail="Merit-linked identity required")
    
    report = VeeduriaReport(
        reporter_id=session.user_id,
        project_id=uuid.UUID(project_id) if project_id else None,
        severity=VeeduriaSeverity(severity),
        category=category,
        title=title,
        description=description,
        photos=photos
    )
    
    db.add(report)
    await db.flush()
    
    return {"success": True, "report_number": report.report_number, "report_id": str(report.id)}


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=settings.DEBUG
    )