# Authentication Service - Magic Links, Temp Email, Progressive Identity
import asyncio
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass

import structlog
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config.settings import get_settings
from models import (
    User, UserSession, MagicLinkToken, DeviceFingerprint,
    IdentityLevel, UserStatus, AuditRecord, AuditEventType
)
from utils.crypto import hash_string, verify_hash, generate_token, encrypt_data, decrypt_data
from utils.email import send_magic_link_email
from services.fraud_detection import FraudDetector
from services.trace_logger import TraceLogger

settings = get_settings()
logger = structlog.get_logger()


@dataclass
class AuthContext:
    ip_address: str
    ip_hash: str
    device_fingerprint: str
    user_agent: str
    locale: str = "es"
    country: Optional[str] = None
    city: Optional[str] = None
    is_vpn: bool = False
    is_proxy: bool = False
    is_tor: bool = False


@dataclass
class AuthResult:
    success: bool
    session: Optional[UserSession] = None
    user: Optional[User] = None
    token_id: Optional[str] = None
    reason: Optional[str] = None
    requires_escalation: bool = False
    escalation_level: Optional[IdentityLevel] = None


@dataclass
class SessionResult:
    success: bool
    session: Optional[UserSession] = None
    user: Optional[User] = None
    reason: Optional[str] = None
    identity_level: Optional[IdentityLevel] = None
    capabilities: List[str] = None


class AuthService:
    """Authentication service with magic links, temp email support, and progressive identity"""
    
    IDENTITY_CAPABILITIES = {
        IdentityLevel.ANONYMOUS: [
            "view_public", "join_discord", "view_proposals", "submit_anonymous_feedback"
        ],
        IdentityLevel.EMAIL_VERIFIED: [
            "view_public", "join_discord", "view_proposals", "submit_anonymous_feedback",
            "vote_proposals", "report_issues", "join_quest_waitlist"
        ],
        IdentityLevel.MERIT_LINKED: [
            "view_public", "join_discord", "view_proposals", "submit_anonymous_feedback",
            "vote_proposals", "report_issues", "join_quest_waitlist",
            "apply_housing", "request_utility_payment", "file_veeduria_report",
            "access_merit_dashboard", "selecting_front_access"
        ],
        IdentityLevel.BIOMETRIC: [
            "view_public", "join_discord", "view_proposals", "submit_anonymous_feedback",
            "vote_proposals", "report_issues", "join_quest_waitlist",
            "apply_housing", "request_utility_payment", "file_veeduria_report",
            "access_merit_dashboard", "selecting_front_access",
            "sign_contracts", "delegate_vote", "access_sensitive_data"
        ],
        IdentityLevel.TRUSTED: [
            "view_public", "join_discord", "view_proposals", "submit_anonymous_feedback",
            "vote_proposals", "report_issues", "join_quest_waitlist",
            "apply_housing", "request_utility_payment", "file_veeduria_report",
            "access_merit_dashboard", "selecting_front_access",
            "sign_contracts", "delegate_vote", "access_sensitive_data",
            "moderate_discord", "validate_quest_visits", "approve_small_payments"
        ],
        IdentityLevel.AUTHORIZED: [
            "view_public", "join_discord", "view_proposals", "submit_anonymous_feedback",
            "vote_proposals", "report_issues", "join_quest_waitlist",
            "apply_housing", "request_utility_payment", "file_veeduria_report",
            "access_merit_dashboard", "selecting_front_access",
            "sign_contracts", "delegate_vote", "access_sensitive_data",
            "moderate_discord", "validate_quest_visits", "approve_small_payments",
            "execute_fund_transfers", "assign_quest_territories", "override_alerts", "manage_personnel"
        ]
    }
    
    def __init__(self, db: AsyncSession, fraud_detector: FraudDetector, trace_logger: TraceLogger):
        self.db = db
        self.fraud_detector = fraud_detector
        self.trace_logger = trace_logger
    
    async def request_magic_link(self, email: str, context: AuthContext) -> AuthResult:
        """Request magic link for any email (temp or real)"""
        
        # Validate email format
        if not self._is_valid_email(email):
            return AuthResult(success=False, reason="Invalid email format")
        
        # Check if temp email
        is_temp = self._is_temp_email(email)
        
        # Rate limiting
        rate_check = await self.fraud_detector.check_rate_limit(context.ip_hash, "magic_link", limit=5, window=300)
        if not rate_check.allowed:
            return AuthResult(success=False, reason="Rate limit exceeded. Try again later.")
        
        # Check device rate limit
        device_check = await self.fraud_detector.check_rate_limit(context.device_fingerprint, "magic_link", limit=3, window=300)
        if not device_check.allowed:
            return AuthResult(success=False, reason="Too many requests from this device.")
        
        # Generate secure token
        token = generate_token(32)
        token_hash = hash_string(token)
        
        # Create magic link token record
        magic_token = MagicLinkToken(
            token=token,
            token_hash=token_hash,
            email=email,
            email_hash=hash_string(email.lower()),
            is_temp_email=is_temp,
            device_fingerprint=context.device_fingerprint,
            ip_hash=context.ip_hash,
            locale=context.locale,
            expires_at=datetime.utcnow() + timedelta(minutes=settings.MAGIC_LINK_EXPIRY_MINUTES)
        )
        
        self.db.add(magic_token)
        
        # Send email
        magic_link_url = f"https://{settings.MAGIC_LINK_DOMAIN}/auth/verify?token={token}"
        email_sent = await send_magic_link_email(
            to_email=email,
            magic_link=magic_link_url,
            locale=context.locale,
            is_temp=is_temp,
            expiry_minutes=settings.MAGIC_LINK_EXPIRY_MINUTES
        )
        
        if not email_sent:
            await self.db.rollback()
            return AuthResult(success=False, reason="Failed to send magic link. Please try again.")
        
        await self.db.flush()
        
        # Log trace event
        await self.trace_logger.log_event(
            event_type=AuditEventType.MAGIC_LINK_REQUESTED,
            event_data={
                "email_hash": hash_string(email.lower()),
                "token_id": str(magic_token.id),
                "is_temp_email": is_temp,
                "locale": context.locale
            },
            actor_user_id=None,
            actor_ip_hash=context.ip_hash,
            actor_device_fingerprint=context.device_fingerprint
        )
        
        return AuthResult(
            success=True,
            token_id=str(magic_token.id)
        )
    
    async def verify_magic_link(self, token: str, context: AuthContext) -> SessionResult:
        """Verify magic link and create session with progressive identity"""
        
        token_hash = hash_string(token)
        
        # Find valid token
        result = await self.db.execute(
            select(MagicLinkToken).where(
                and_(
                    MagicLinkToken.token_hash == token_hash,
                    MagicLinkToken.is_used == False,
                    MagicLinkToken.is_revoked == False,
                    MagicLinkToken.expires_at > datetime.utcnow()
                )
            )
        )
        magic_token = result.scalar_one_or_none()
        
        if not magic_token:
            return SessionResult(success=False, reason="Invalid or expired magic link")
        
        # Verify device fingerprint (allow some flexibility for mobile)
        fp_match = await self._verify_device_fingerprint(magic_token.device_fingerprint, context.device_fingerprint)
        
        # Mark token as used
        magic_token.is_used = True
        magic_token.used_at = datetime.utcnow()
        
        # Find or create user
        user = await self._find_or_create_user(magic_token.email, magic_token.email_hash, magic_token.is_temp_email)
        
        # Determine identity level
        identity_level = await self._determine_identity_level(user, fp_match)
        
        # Create session
        session = await self._create_session(user, context, identity_level, fp_match, magic_token.id)
        magic_token.used_by_session_id = session.id
        
        # Update user last login
        user.last_login_at = datetime.utcnow()
        user.last_login_ip = context.ip_address
        user.current_device_fingerprint = context.device_fingerprint
        if context.device_fingerprint not in (user.known_devices or []):
            devices = list(user.known_devices or [])
            devices.append(context.device_fingerprint)
            user.known_devices = devices[:10]  # Keep last 10
        
        await self.db.flush()
        
        # Log trace event
        await self.trace_logger.log_event(
            event_type=AuditEventType.MAGIC_LINK_VERIFIED,
            event_data={
                "session_id": str(session.id),
                "user_id": str(user.id),
                "email_hash": magic_token.email_hash,
                "device_fingerprint_match": fp_match,
                "identity_level": identity_level.value,
                "is_temp_email": magic_token.is_temp_email
            },
            actor_user_id=user.id,
            actor_session_id=session.id,
            actor_identity_level=identity_level.value,
            actor_ip_hash=context.ip_hash,
            actor_device_fingerprint=context.device_fingerprint
        )
        
        return SessionResult(
            success=True,
            session=session,
            user=user,
            identity_level=identity_level,
            capabilities=self.IDENTITY_CAPABILITIES.get(identity_level, [])
        )
    
    async def escalate_identity(self, session: UserSession, target_level: IdentityLevel, 
                                 verification_data: Dict[str, Any]) -> SessionResult:
        """Escalate user identity level with verification"""
        
        user = await self.db.get(User, session.user_id)
        if not user:
            return SessionResult(success=False, reason="User not found")
        
        # Verify current session is valid
        if session.is_revoked or session.expires_at < datetime.utcnow():
            return SessionResult(success=False, reason="Session expired or revoked")
        
        # Check if escalation is valid (can only go up one level at a time, except for specific paths)
        current_level = user.identity_level
        if target_level.value <= current_level.value:
            return SessionResult(success=False, reason="Target level must be higher than current")
        
        # Verify based on target level
        verification_result = await self._verify_escalation(user, target_level, verification_data)
        if not verification_result.success:
            return SessionResult(success=False, reason=verification_result.reason)
        
        # Update user identity level
        old_level = user.identity_level
        user.identity_level = target_level
        
        # Update specific verification flags
        if target_level == IdentityLevel.EMAIL_VERIFIED:
            user.email_verified = True
            user.email_verified_at = datetime.utcnow()
        elif target_level == IdentityLevel.MERIT_LINKED:
            user.cedula_verified = True
            user.cedula_verified_at = datetime.utcnow()
            user.jce_verification_id = verification_data.get("jce_verification_id")
        elif target_level == IdentityLevel.BIOMETRIC:
            user.biometric_verified = True
            user.biometric_verified_at = datetime.utcnow()
            user.biometric_template_hash = verification_data.get("biometric_hash")
        elif target_level == IdentityLevel.TRUSTED:
            # Trusted requires: merit threshold + clean history + quest participation
            pass
        elif target_level == IdentityLevel.AUTHORIZED:
            # Authorized requires: government appointment + FGA approval
            pass
        
        # Update session capabilities
        session.identity_level = target_level
        session.capabilities = self.IDENTITY_CAPABILITIES.get(target_level, [])
        
        await self.db.flush()
        
        # Log trace event
        await self.trace_logger.log_event(
            event_type=AuditEventType.IDENTITY_ESCALATED,
            event_data={
                "user_id": str(user.id),
                "old_level": old_level.value,
                "new_level": target_level.value,
                "verification_method": verification_data.get("method"),
                "session_id": str(session.id)
            },
            actor_user_id=user.id,
            actor_session_id=session.id,
            actor_identity_level=target_level.value,
            actor_ip_hash=session.ip_hash,
            actor_device_fingerprint=session.device_fingerprint
        )
        
        return SessionResult(
            success=True,
            session=session,
            user=user,
            identity_level=target_level,
            capabilities=self.IDENTITY_CAPABILITIES.get(target_level, [])
        )
    
    async def revoke_session(self, session_id: uuid.UUID, reason: str = "User logout") -> bool:
        """Revoke a session"""
        result = await self.db.execute(
            select(UserSession).where(UserSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            return False
        
        session.is_revoked = True
        session.revoked_at = datetime.utcnow()
        session.revoked_reason = reason
        
        await self.db.flush()
        return True
    
    async def revoke_all_user_sessions(self, user_id: uuid.UUID, except_session: Optional[uuid.UUID] = None, reason: str = "Security revocation") -> int:
        """Revoke all sessions for a user"""
        query = update(UserSession).where(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_revoked == False
            )
        )
        if except_session:
            query = query.where(UserSession.id != except_session)
        
        query = query.values(
            is_revoked=True,
            revoked_at=datetime.utcnow(),
            revoked_reason=reason
        )
        
        result = await self.db.execute(query)
        return result.rowcount
    
    async def get_session(self, session_token: str) -> Optional[UserSession]:
        """Get session by token"""
        result = await self.db.execute(
            select(UserSession).options(selectinload(UserSession.user)).where(
                and_(
                    UserSession.session_token == session_token,
                    UserSession.is_revoked == False,
                    UserSession.expires_at > datetime.utcnow()
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def refresh_session(self, session: UserSession) -> UserSession:
        """Extend session expiry"""
        session.expires_at = datetime.utcnow() + timedelta(days=30)
        session.last_activity_at = datetime.utcnow()
        await self.db.flush()
        return session
    
    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _is_temp_email(self, email: str) -> bool:
        """Check if email domain is a known temp email provider"""
        domain = email.split("@")[-1].lower()
        return domain in settings.TEMP_EMAIL_DOMAINS
    
    async def _verify_device_fingerprint(self, stored_fp: str, current_fp: str) -> bool:
        """Verify device fingerprint with some tolerance"""
        # Exact match
        if stored_fp == current_fp:
            return True
        
        # Could implement fuzzy matching here for minor browser updates
        # For now, require exact match for security
        return False
    
    async def _find_or_create_user(self, email: str, email_hash: str, is_temp_email: bool) -> User:
        """Find existing user or create new anonymous user"""
        
        # Try to find by email hash
        result = await self.db.execute(
            select(User).where(User.email_hash == email_hash)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Update email if it was temp before and now is real
            if user.is_temp_email and not is_temp_email:
                user.email = email
                user.is_temp_email = False
            return user
        
        # Create new user
        user = User(
            email=email if not is_temp_email else None,
            email_hash=email_hash,
            is_temp_email=is_temp_email,
            email_verified=not is_temp_email,  # Temp emails can't be "verified" in traditional sense
            identity_level=IdentityLevel.EMAIL_VERIFIED if not is_temp_email else IdentityLevel.ANONYMOUS,
            status=UserStatus.ACTIVE if not is_temp_email else UserStatus.PENDING_VERIFICATION,
            preferred_language="es"
        )
        
        self.db.add(user)
        await self.db.flush()
        
        return user
    
    async def _determine_identity_level(self, user: User, fp_match: bool) -> IdentityLevel:
        """Determine identity level based on user state and device match"""
        
        # If user has higher level already, keep it (but require device match for high levels)
        if user.identity_level in [IdentityLevel.MERIT_LINKED, IdentityLevel.BIOMETRIC, IdentityLevel.TRUSTED, IdentityLevel.AUTHORIZED]:
            if not fp_match and user.identity_level >= IdentityLevel.MERIT_LINKED:
                # Device mismatch for high identity level - require re-verification
                return IdentityLevel.EMAIL_VERIFIED
            return user.identity_level
        
        # New or low-level user
        if user.email_verified and not user.is_temp_email:
            return IdentityLevel.EMAIL_VERIFIED
        
        return IdentityLevel.ANONYMOUS
    
    async def _create_session(self, user: User, context: AuthContext, identity_level: IdentityLevel, 
                              fp_match: bool, magic_token_id: uuid.UUID) -> UserSession:
        """Create new user session"""
        
        session_token = generate_token(32)
        refresh_token = generate_token(32)
        
        # Session expires in 30 days, refresh token in 90 days
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        session = UserSession(
            user_id=user.id,
            session_token=session_token,
            refresh_token=refresh_token,
            device_fingerprint=context.device_fingerprint,
            device_info={
                "user_agent": context.user_agent,
                "fp_match": fp_match
            },
            device_trusted=fp_match,
            ip_address=context.ip_address,
            ip_hash=context.ip_hash,
            country=context.country,
            city=context.city,
            is_vpn=context.is_vpn,
            is_proxy=context.is_proxy,
            is_tor=context.is_tor,
            identity_level=identity_level,
            capabilities=self.IDENTITY_CAPABILITIES.get(identity_level, []),
            expires_at=expires_at,
            last_activity_at=datetime.utcnow()
        )
        
        self.db.add(session)
        return session
    
    async def _verify_escalation(self, user: User, target_level: IdentityLevel, verification_data: Dict) -> AuthResult:
        """Verify escalation requirements"""
        
        if target_level == IdentityLevel.EMAIL_VERIFIED:
            # Already handled by magic link
            return AuthResult(success=True)
        
        elif target_level == IdentityLevel.MERIT_LINKED:
            # Require JCE cédula verification
            jce_verification_id = verification_data.get("jce_verification_id")
            if not jce_verification_id:
                return AuthResult(success=False, reason="JCE verification required")
            
            # Verify with JCE API (would call external service)
            # For now, accept if provided
            return AuthResult(success=True)
        
        elif target_level == IdentityLevel.BIOMETRIC:
            # Require biometric verification
            biometric_hash = verification_data.get("biometric_hash")
            if not biometric_hash:
                return AuthResult(success=False, reason="Biometric verification required")
            
            # Verify biometric matches enrolled template
            # Would integrate with JCE biometric system
            return AuthResult(success=True)
        
        elif target_level == IdentityLevel.TRUSTED:
            # Require: high merit + clean history + quest participation + community vouching
            if user.merit_score < 1000:
                return AuthResult(success=False, reason="Insufficient merit score for Trusted level")
            if user.quest_participation_count < 10:
                return AuthResult(success=False, reason="Insufficient Quest participation")
            if user.veeduria_reports_validated < 5:
                return AuthResult(success=False, reason="Insufficient validated Veeduría reports")
            
            return AuthResult(success=True)
        
        elif target_level == IdentityLevel.AUTHORIZED:
            # Require: government appointment + FGA approval
            appointment_id = verification_data.get("appointment_id")
            fga_approval_id = verification_data.get("fga_approval_id")
            
            if not appointment_id or not fga_approval_id:
                return AuthResult(success=False, reason="Government appointment and FGA approval required")
            
            return AuthResult(success=True)
        
        return AuthResult(success=False, reason="Unknown target level")


# Dependency injection
async def get_auth_service(db: AsyncSession, fraud_detector: FraudDetector, trace_logger: TraceLogger) -> AuthService:
    return AuthService(db, fraud_detector, trace_logger)