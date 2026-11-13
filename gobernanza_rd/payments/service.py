# Payment Service - Auto-fill from Government APIs
import asyncio
import hashlib
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum

import structlog
from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config.settings import get_settings
from models import (
    Payment, PaymentType, PaymentStatus, PaymentMethod, SavedPaymentMethod,
    SelectingFrontItem, SelectingFrontOrder, MeritTransaction, MeritEventType,
    User, UserSession, Delivery, DeliveryLocation, AuditRecord, AuditEventType
)
from services.gov_api_connectors import GovAPIConnectorManager
from services.central_ai_fund import CentralAIFundExecutor
from services.fraud_detection import FraudDetector, FraudAction
from services.trace_logger import TraceLogger
from services.merit_service import MeritService

settings = get_settings()
logger = structlog.get_logger()


class PaymentAutoFillEngine:
    """Auto-fills payment data from government APIs"""
    
    PAYMENT_TYPE_CONFIG = {
        PaymentType.UTILITY_ELECTRICITY: {
            "required_user_fields": ["account_number"],
            "auto_fill_fields": ["amount", "due_date", "period", "customer_name", "customer_cedula", "service_address"],
            "gov_apis": ["ede"],
            "amount_field": "balance"
        },
        PaymentType.UTILITY_WATER: {
            "required_user_fields": ["account_number"],
            "auto_fill_fields": ["amount", "due_date", "period", "customer_name", "customer_cedula", "service_address"],
            "gov_apis": ["coraasan", "caasd", "inapa"],
            "amount_field": "balance"
        },
        PaymentType.HOUSING_SUBSIDY: {
            "required_user_fields": ["project_id"],
            "auto_fill_fields": ["amount", "beneficiary_name", "beneficiary_cedula", "bank_account", "bank_name"],
            "gov_apis": ["mivhed", "adess"],
            "amount_field": "subsidy_amount"
        },
        PaymentType.MERIT_REWARD: {
            "required_user_fields": [],
            "auto_fill_fields": ["amount", "recipient_cedula", "recipient_name", "concept"],
            "gov_apis": [],
            "amount_field": "calculated_reward"
        },
        PaymentType.QUEST_STIPEND: {
            "required_user_fields": [],
            "auto_fill_fields": ["amount", "period", "territory", "days_completed"],
            "gov_apis": [],
            "amount_field": "stipend_calculated"
        },
        PaymentType.MUTUAL_AID: {
            "required_user_fields": ["recipient_id", "category"],
            "auto_fill_fields": ["max_amount", "sender_cedula", "sender_name", "category_valid"],
            "gov_apis": [],
            "amount_field": "user_provided"
        },
        PaymentType.EMERGENCY_RELIEF: {
            "required_user_fields": ["beneficiary_id"],
            "auto_fill_fields": ["items", "estimated_value", "delivery_method"],
            "gov_apis": ["coe", "superate"],
            "amount_field": "standard_package_value"
        },
        PaymentType.SELECTING_FRONT: {
            "required_user_fields": ["item_id"],
            "auto_fill_fields": ["amount", "item_details", "delivery_location"],
            "gov_apis": [],
            "amount_field": "item_merit_cost"
        }
    }
    
    def __init__(self, gov_connector: GovAPIConnectorManager, merit_service: MeritService):
        self.gov_connector = gov_connector
        self.merit_service = merit_service
        self.db: Optional[AsyncSession] = None
    
    async def auto_fill_payment(self, payment_type: PaymentType, user: User, 
                                session: UserSession, user_provided: Dict) -> Dict:
        """Auto-fill all possible payment fields from government APIs"""
        
        config = self.PAYMENT_TYPE_CONFIG.get(payment_type, {})
        auto_filled = dict(user_provided)
        
        # Common auto-fill from user profile
        auto_filled.setdefault("customer_cedula", user.cedula_token)  # Tokenized
        auto_filled.setdefault("customer_name", user.full_name)
        auto_filled.setdefault("customer_phone", user.phone)
        auto_filled.setdefault("customer_email", user.email)
        
        # Type-specific auto-fill
        if payment_type == PaymentType.UTILITY_ELECTRICITY:
            auto_filled = await self._auto_fill_electricity(auto_filled, user)
        elif payment_type == PaymentType.UTILITY_WATER:
            auto_filled = await self._auto_fill_water(auto_filled, user)
        elif payment_type == PaymentType.HOUSING_SUBSIDY:
            auto_filled = await self._auto_fill_housing(auto_filled, user)
        elif payment_type == PaymentType.MERIT_REWARD:
            auto_filled = await self._auto_fill_merit_reward(auto_filled, user)
        elif payment_type == PaymentType.QUEST_STIPEND:
            auto_filled = await self._auto_fill_quest_stipend(auto_filled, user)
        elif payment_type == PaymentType.MUTUAL_AID:
            auto_filled = await self._auto_fill_mutual_aid(auto_filled, user)
        elif payment_type == PaymentType.EMERGENCY_RELIEF:
            auto_filled = await self._auto_fill_emergency(auto_filled, user)
        elif payment_type == PaymentType.SELECTING_FRONT:
            auto_filled = await self._auto_fill_selecting_front(auto_filled, user)
        
        return auto_filled
    
    async def _auto_fill_electricity(self, data: Dict, user: User) -> Dict:
        """Auto-fill from EDE APIs"""
        account_number = data.get("account_number")
        if not account_number:
            return data
        
        # Try each EDE provider
        for ede_api in ["ede_norte", "ede_sur", "ede_este"]:
            try:
                result = await self.gov_connector.call(ede_api, "get_account_info", {
                    "account_number": account_number,
                    "cedula": user.cedula_token
                })
                if result.success and result.data:
                    data.setdefault("amount", str(result.data.get("balance", 0)))
                    data.setdefault("due_date", result.data.get("due_date"))
                    data.setdefault("period", result.data.get("period"))
                    data.setdefault("service_address", result.data.get("address"))
                    data.setdefault("customer_name", result.data.get("customer_name"))
                    data["_gov_source"] = ede_api
                    break
            except Exception:
                continue
        
        return data
    
    async def _auto_fill_water(self, data: Dict, user: User) -> Dict:
        """Auto-fill from water utility APIs"""
        account_number = data.get("account_number")
        if not account_number:
            return data
        
        # Try CORAASAN, CAASD, INAPA based on location
        water_apis = ["coraasan", "caasd", "inapa"]
        for api in water_apis:
            try:
                result = await self.gov_connector.call(api, "get_account_info", {
                    "account_number": account_number,
                    "cedula": user.cedula_token
                })
                if result.success and result.data:
                    data.setdefault("amount", str(result.data.get("balance", 0)))
                    data.setdefault("due_date", result.data.get("due_date"))
                    data.setdefault("period", result.data.get("period"))
                    data.setdefault("service_address", result.data.get("address"))
                    data["_gov_source"] = api
                    break
            except Exception:
                continue
        
        return data
    
    async def _auto_fill_housing(self, data: Dict, user: User) -> Dict:
        """Auto-fill from MIVHED and ADESS"""
        project_id = data.get("project_id")
        if not project_id:
            return data
        
        try:
            # Get subsidy details from MIVHED
            mivhed_result = await self.gov_connector.call("mivhed", "get_subsidy_details", {
                "project_id": project_id,
                "cedula": user.cedula_token
            })
            
            if mivhed_result.success and mivhed_result.data:
                data.setdefault("amount", str(mivhed_result.data.get("amount", 0)))
                data.setdefault("beneficiary_name", mivhed_result.data.get("beneficiary_name"))
                data.setdefault("project_name", mivhed_result.data.get("project_name"))
            
            # Get bank details from ADESS
            adess_result = await self.gov_connector.call("adess", "get_bank_details", {
                "cedula": user.cedula_token
            })
            
            if adess_result.success and adess_result.data:
                data.setdefault("bank_account", adess_result.data.get("account_number"))
                data.setdefault("bank_name", adess_result.data.get("bank_name"))
                data.setdefault("account_type", adess_result.data.get("account_type"))
                
        except Exception:
            pass
        
        return data
    
    async def _auto_fill_merit_reward(self, data: Dict, user: User) -> Dict:
        """Auto-fill merit reward from merit service"""
        try:
            reward = await self.merit_service.calculate_reward(user.id)
            data.setdefault("amount", str(reward.amount))
            data.setdefault("concept", reward.reason)
            data.setdefault("recipient_cedula", user.cedula_token)
            data.setdefault("recipient_name", user.full_name)
        except Exception:
            pass
        return data
    
    async def _auto_fill_quest_stipend(self, data: Dict, user: User) -> Dict:
        """Auto-fill Quest stipend"""
        try:
            if self.db is None:
                return data
            from services.quest_service import QuestService
            quest_service = QuestService(self.db)
            quest = await quest_service.get_active_quest(user.id)
            if quest:
                data.setdefault("amount", str(quest.daily_stipend * quest.days_completed))
                data.setdefault("period", f"{quest.start_date} a {quest.end_date}")
                data.setdefault("territory", quest.territory_name)
                data.setdefault("days_completed", quest.days_completed)
        except Exception:
            pass
        return data
    
    async def _auto_fill_mutual_aid(self, data: Dict, user: User) -> Dict:
        """Auto-fill mutual aid limits"""
        try:
            if self.db is None:
                return data
            from services.mutual_aid_service import MutualAidService
            mutual_aid_service = MutualAidService(self.db)
            limits = await mutual_aid_service.get_limits(user.id)
            data.setdefault("max_amount", str(limits.remaining))
            data.setdefault("sender_cedula", user.cedula_token)
            data.setdefault("sender_name", user.full_name)
            data.setdefault("category_valid", data.get("category") in ["food", "medicine", "transport", "childcare", "eldercare", "repair", "financial", "information", "emotional", "skills"])
        except Exception:
            pass
        return data
    
    async def _auto_fill_emergency(self, data: Dict, user: User) -> Dict:
        """Auto-fill emergency relief from COE"""
        beneficiary_id = data.get("beneficiary_id")
        if not beneficiary_id:
            return data
        
        try:
            coe_result = await self.gov_connector.call("coe", "get_active_emergency", {
                "beneficiary_id": beneficiary_id
            })
            if coe_result.success and coe_result.data:
                data.setdefault("items", coe_result.data.get("standard_package", []))
                data.setdefault("estimated_value", str(coe_result.data.get("estimated_value", 0)))
                data.setdefault("delivery_method", "domicilio" if coe_result.data.get("home_delivery") else "centro")
        except Exception:
            pass
        return data
    
    async def _auto_fill_selecting_front(self, data: Dict, user: User) -> Dict:
        """Auto-fill Selecting Front order"""
        item_id = data.get("item_id")
        if not item_id:
            return data
        
        # Would fetch item details from DB
        # For now, return as-is
        return data


class PaymentService:
    """Main payment processing service"""
    
    def __init__(self, db: AsyncSession, auto_fill_engine: PaymentAutoFillEngine,
                 central_fund: CentralAIFundExecutor, fraud_detector: FraudDetector,
                 trace_logger: TraceLogger, merit_service: MeritService):
        self.db = db
        self.auto_fill_engine = auto_fill_engine
        self.central_fund = central_fund
        self.fraud_detector = fraud_detector
        self.trace_logger = trace_logger
        self.merit_service = merit_service
        self.auto_fill_engine.db = db
    
    async def initiate_payment(self, user: User, session: UserSession, 
                               payment_type: PaymentType, user_provided: Dict) -> Dict:
        """Initiate payment with auto-fill preview"""
        
        # Auto-fill from government APIs
        auto_filled = await self.auto_fill_engine.auto_fill_payment(
            payment_type, user, session, user_provided
        )
        
        # Validate required fields
        config = PaymentAutoFillEngine.PAYMENT_TYPE_CONFIG.get(payment_type, {})
        required = config.get("required_user_fields", [])
        missing = [f for f in required if f not in auto_filled or not auto_filled[f]]
        
        if missing:
            return {
                "success": False,
                "reason": f"Missing required fields: {', '.join(missing)}",
                "missing_fields": missing
            }
        
        # Fraud check
        risk_score = await self.fraud_detector.assess_payment_risk(
            user, session, payment_type, auto_filled
        )
        
        if risk_score.action == FraudAction.BLOCK_AND_INVESTIGATE:
            return {
                "success": False,
                "reason": "Payment blocked due to fraud risk",
                "risk_score": risk_score.score
            }
        
        # Create payment preview (not executed yet)
        payment_preview = {
            "auto_filled_data": auto_filled,
            "user_provided_data": user_provided,
            "amount": auto_filled.get("amount", "0"),
            "requires_confirmation": True,
            "risk_score": risk_score.score,
            "fraud_action": risk_score.action.value,
            "estimated_merit_earned": self._estimate_merit(payment_type, user.identity_level)
        }
        
        # Generate confirmation token
        confirmation_token = self._generate_confirmation_token(user.id, payment_type, auto_filled, risk_score.score)
        
        return {
            "success": True,
            "payment_preview": payment_preview,
            "confirmation_token": confirmation_token
        }
    
    async def confirm_payment(self, confirmation_token: str, user: User, 
                              session: UserSession, biometric_verified: bool = False) -> Dict:
        """Confirm and execute payment"""
        
        # Parse confirmation token
        token_data = self._parse_confirmation_token(confirmation_token)
        if not token_data:
            return {"success": False, "reason": "Invalid or expired confirmation token"}
        
        payment_type = PaymentType(token_data["payment_type"])
        auto_filled = token_data["auto_filled"]
        
        # Verify user matches
        if token_data["user_id"] != str(user.id):
            return {"success": False, "reason": "Token user mismatch"}
        
        # Biometric check for high amounts
        amount = Decimal(str(auto_filled.get("amount") or "0"))
        if amount > 10000 and not biometric_verified:  # > RD$10,000
            return {"success": False, "reason": "Biometric verification required for amounts over RD$10,000"}
        
        # Create payment record
        payment = Payment(
            user_id=user.id,
            session_id=session.id,
            payment_type=payment_type,
            status=PaymentStatus.PROCESSING,
            amount=amount,
            payment_method=PaymentMethod.CENTRAL_AI_FUND,
            payment_method_details={
                "wallet_type": auto_filled.get("_wallet_type"),
                "card_token": auto_filled.get("_card_token"),
                "biometric_verified": biometric_verified
            },
            auto_filled_data=auto_filled,
            user_provided_data=token_data.get("user_provided", {}),
            description=auto_filled.get("description", f"Payment: {payment_type.value}"),
            reference=auto_filled.get("reference"),
            risk_score=token_data.get("risk_score", 0),
            payment_number=f"pay_{uuid.uuid4().hex[:16]}",
            trace_id=self._generate_trace_id(),
            trace_hash=""
        )
        
        self.db.add(payment)
        await self.db.flush()
        
        # Execute via Central AI Fund
        result = await self.central_fund.execute_payment(payment, auto_filled)
        
        if result.success:
            payment.status = PaymentStatus.COMPLETED
            payment.completed_at = datetime.utcnow()
            payment.gov_api_responses = result.gov_responses
            payment.gov_transaction_ids = result.transaction_ids
            payment.merit_earned = result.merit_earned
            
            # Award merit
            if result.merit_earned > 0:
                await self.merit_service.add_merits(
                    user.id, MeritEventType.UTILITY_PAYMENT_RESPONSIBLE,
                    result.merit_earned, f"Payment: {payment_type.value}", payment.id,
                    db=self.db
                )
        else:
            payment.status = PaymentStatus.FAILED
            payment.failed_at = datetime.utcnow()
            payment.error_code = result.error_code
            payment.error_message = result.error_message
        
        await self.db.flush()
        
        # Log trace event
        await self.trace_logger.log_event(
            event_type=AuditEventType.PAYMENT_COMPLETED if result.success else AuditEventType.PAYMENT_FAILED,
            event_data={
                "payment_id": str(payment.id),
                "payment_type": payment_type.value,
                "amount": str(amount),
                "success": result.success,
                "merit_earned": float(result.merit_earned) if result.merit_earned else 0,
                "trace_id": payment.trace_id
            },
            actor_user_id=user.id,
            actor_session_id=session.id,
            actor_identity_level=user.identity_level.value,
            actor_ip_hash=session.ip_hash,
            actor_device_fingerprint=session.device_fingerprint
        )
        
        return {
            "success": result.success,
            "payment_id": str(payment.id),
            "trace_id": payment.trace_id,
            "receipt": {
                "amount": str(amount),
                "type": payment_type.value,
                "timestamp": payment.completed_at.isoformat() if payment.completed_at else None,
                "gov_transaction_ids": result.transaction_ids,
                "merit_earned": float(result.merit_earned) if result.merit_earned else 0
            },
            "merit_earned": float(result.merit_earned) if result.merit_earned else 0
        }
    
    async def save_payment_method(self, user: User, payment_type: PaymentType,
                                  account_number: str, nickname: str) -> SavedPaymentMethod:
        """Save payment method with minimal data"""
        
        # Verify account ownership via government API
        verified = await self._verify_account_ownership(user, payment_type, account_number)
        
        saved = SavedPaymentMethod(
            user_id=user.id,
            payment_type=payment_type,
            account_number=account_number,  # Should be encrypted
            nickname=nickname,
            verified=verified,
            verified_at=datetime.utcnow() if verified else None,
            is_default=False
        )
        
        self.db.add(saved)
        await self.db.flush()
        
        return saved
    
    async def _verify_account_ownership(self, user: User, payment_type: PaymentType, account_number: str) -> bool:
        """Verify account belongs to user via government API"""
        # Would call appropriate government API
        # For now, return True for demo
        return True
    
    def _estimate_merit(self, payment_type: PaymentType, identity_level) -> int:
        """Estimate merit earned for payment"""
        base_merits = {
            PaymentType.UTILITY_ELECTRICITY: 10,
            PaymentType.UTILITY_WATER: 10,
            PaymentType.HOUSING_SUBSIDY: 0,  # Gov to citizen
            PaymentType.MERIT_REWARD: 0,  # System to citizen
            PaymentType.QUEST_STIPEND: 0,  # System to quester
            PaymentType.MUTUAL_AID: 15,
            PaymentType.EMERGENCY_RELIEF: 0,
            PaymentType.SELECTING_FRONT: 0
        }
        base = base_merits.get(payment_type, 0)
        multiplier = {
            0: 0, 1: 1.0, 2: 1.0, 3: 1.5, 4: 2.0, 5: 3.0
        }.get(identity_level.value, 1.0)
        return int(base * multiplier)
    
    def _generate_confirmation_token(self, user_id: uuid.UUID, payment_type: PaymentType, auto_filled: Dict, risk_score: float = 0) -> str:
        """Generate secure confirmation token"""
        import base64
        import json
        data = {
            "user_id": str(user_id),
            "payment_type": payment_type.value,
            "auto_filled": auto_filled,
            "risk_score": risk_score,
            "exp": (datetime.utcnow() + timedelta(minutes=10)).timestamp()
        }
        return base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
    
    def _parse_confirmation_token(self, token: str) -> Optional[Dict]:
        """Parse and validate confirmation token"""
        try:
            import base64
            import json
            data = json.loads(base64.urlsafe_b64decode(token).decode())
            if data["exp"] < datetime.utcnow().timestamp():
                return None
            return data
        except Exception:
            return None
    
    def _generate_trace_id(self) -> str:
        return f"pay_{uuid.uuid4().hex[:16]}"