# Digital Wallet Service - Apple Pay & Google Pay Integration
import asyncio
import base64
import hashlib
import json
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum

import structlog
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import get_settings
from models import (
    Payment, PaymentType, PaymentStatus, PaymentMethod, User, UserSession,
    AuditRecord, AuditEventType
)
from services.payment_service import PaymentService
from services.trace_logger import TraceLogger
from services.fraud_detection import FraudDetector, FraudAction

settings = get_settings()
logger = structlog.get_logger()


class WalletType(str, Enum):
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"


@dataclass
class WalletPaymentRequest:
    wallet_type: WalletType
    payment_token: Dict[str, Any]  # Apple Pay PKPaymentToken or Google Pay token
    payment_method: Dict[str, Any]  # Payment method info
    payment_type: PaymentType
    user_provided: Dict[str, Any]
    session_id: uuid.UUID


@dataclass
class WalletPaymentResult:
    success: bool
    payment_id: Optional[str] = None
    trace_id: Optional[str] = None
    receipt: Optional[Dict] = None
    merit_earned: float = 0
    reason: Optional[str] = None


class ApplePayProcessor:
    """Processes Apple Pay payments via Payment Service Provider"""
    
    def __init__(self, psp_config: Dict, central_fund, trace_logger: TraceLogger):
        self.psp_config = psp_config
        self.central_fund = central_fund
        self.trace_logger = trace_logger
        self.merchant_id = psp_config.get("apple_pay_merchant_id")
    
    async def process_payment(self, request: WalletPaymentRequest, user: User, session: UserSession) -> WalletPaymentResult:
        """Process Apple Pay payment"""
        
        try:
            # 1. Validate Apple Pay session
            session_valid = await self._verify_apple_pay_session(request.payment_token)
            if not session_valid:
                return WalletPaymentResult(success=False, reason="Invalid Apple Pay session")
            
            # 2. Decrypt payment token
            payment_data = await self._decrypt_payment_token(request.payment_token)
            
            # 3. Extract card info (tokenized)
            card_info = self._extract_card_info(payment_data)
            
            # 4. Verify DR bank support
            if not self._is_dr_bank_supported(card_info):
                return WalletPaymentResult(success=False, reason="Card issuer not supported in DR")
            
            # 5. Build payment with auto-fill
            auto_filled = await self._build_auto_filled_payment(request, user, session, card_info)
            
            # 6. Fraud check
            risk = await self.fraud_detector.assess_digital_wallet_payment(user, session, auto_filled, "apple_pay")
            if risk.action == FraudAction.BLOCK_AND_INVESTIGATE:
                return WalletPaymentResult(success=False, reason="Fraud check failed")
            
            # 7. Execute via Central AI Fund
            result = await self.central_fund.execute_payment(auto_filled)
            
            # 8. Create payment record
            payment = await self._create_payment_record(user, session, request, auto_filled, result, card_info)
            
            return WalletPaymentResult(
                success=result.success,
                payment_id=str(payment.id),
                trace_id=payment.trace_id,
                receipt=self._build_receipt(payment, result),
                merit_earned=float(result.merit_earned) if result.merit_earned else 0
            )
            
        except Exception as e:
            logger.error("Apple Pay processing failed", error=str(e))
            return WalletPaymentResult(success=False, reason=f"Processing error: {str(e)}")
    
    async def _verify_apple_pay_session(self, payment_token: Dict) -> bool:
        """Verify Apple Pay session validity"""
        # Would verify with Apple Pay servers or PSP
        return True
    
    async def _decrypt_payment_token(self, payment_token: Dict) -> Dict:
        """Decrypt Apple Pay payment token"""
        # In production, this uses the merchant private key to decrypt
        # For now, return the payment data as-is (PSP handles decryption)
        return payment_token.get("paymentData", {})
    
    def _extract_card_info(self, payment_data: Dict) -> Dict:
        """Extract tokenized card info from Apple Pay payment data"""
        payment_method = payment_data.get("paymentMethod", {})
        return {
            "token": payment_data.get("applicationData", ""),
            "network": payment_method.get("network", "").lower(),  # visa, mastercard, amex
            "type": payment_method.get("type", "").lower(),  # debit, credit, prepaid
            "issuer": self._identify_issuer(payment_method.get("displayName", "")),
            "last4": payment_method.get("displayName", "")[-4:],
            "device_account_number": payment_data.get("token", {}).get("transactionIdentifier", "")
        }
    
    def _identify_issuer(self, display_name: str) -> str:
        """Identify card issuer from display name"""
        display_lower = display_name.lower()
        if "banreservas" in display_lower or "reservas" in display_lower:
            return "Banreservas"
        elif "popular" in display_lower:
            return "Banco Popular"
        elif "bhd" in display_lower or "leon" in display_lower:
            return "BHD León"
        elif "scotia" in display_lower:
            return "Scotiabank"
        elif "banesco" in display_lower:
            return "Banesco"
        elif "caribe" in display_lower:
            return "Banco Caribe"
        elif "ademi" in display_lower:
            return "Banco Ademi"
        elif "promerica" in display_lower:
            return "Banco Promerica"
        return "Unknown"
    
    def _is_dr_bank_supported(self, card_info: Dict) -> bool:
        """Check if DR bank card is supported"""
        supported_issuers = {
            "Banreservas", "Banco Popular", "BHD León", "Scotiabank",
            "Banesco", "Banco Caribe", "Banco Ademi", "Banco Promerica"
        }
        return card_info.get("issuer") in supported_issuers
    
    async def _build_auto_filled_payment(self, request: WalletPaymentRequest, user: User, session: UserSession, card_info: Dict) -> Dict:
        """Build auto-filled payment data"""
        # This would integrate with the PaymentAutoFillEngine
        # For now, return basic structure
        return {
            **request.user_provided,
            "_wallet_type": "apple_pay",
            "_card_token": card_info["token"],
            "_card_network": card_info["network"],
            "_card_issuer": card_info["issuer"],
            "_biometric_verified": True
        }
    
    async def _create_payment_record(self, user: User, session: UserSession, request: WalletPaymentRequest,
                                     auto_filled: Dict, result, card_info: Dict) -> Payment:
        """Create payment record"""
        payment = Payment(
            user_id=user.id,
            session_id=session.id,
            payment_type=request.payment_type,
            status=PaymentStatus.COMPLETED if result.success else PaymentStatus.FAILED,
            amount=result.amount if hasattr(result, 'amount') else Decimal("0"),
            payment_method=PaymentMethod.APPLE_PAY,
            payment_method_details={
                "wallet_type": "apple_pay",
                "card_network": card_info["network"],
                "card_issuer": card_info["issuer"],
                "card_last4": card_info["last4"],
                "device_account_number": card_info["device_account_number"],
                "biometric_verified": True
            },
            auto_filled_data=auto_filled,
            user_provided_data=request.user_provided,
            gov_api_responses=result.gov_responses if hasattr(result, 'gov_responses') else {},
            gov_transaction_ids=result.transaction_ids if hasattr(result, 'transaction_ids') else {},
            description=f"Apple Pay: {request.payment_type.value}",
            trace_id=self._generate_trace_id(),
            wallet_type="apple_pay",
            biometric_verified=True,
            merit_earned=result.merit_earned if hasattr(result, 'merit_earned') else 0
        )
        return payment
    
    def _build_receipt(self, payment: Payment, result) -> Dict:
        return {
            "payment_id": str(payment.id),
            "amount": str(payment.amount),
            "type": payment.payment_type.value,
            "method": "Apple Pay",
            "card_issuer": payment.payment_method_details.get("card_issuer"),
            "card_last4": payment.payment_method_details.get("card_last4"),
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": payment.trace_id,
            "merit_earned": float(payment.merit_earned) if payment.merit_earned else 0
        }
    
    def _generate_trace_id(self) -> str:
        return f"apay_{uuid.uuid4().hex[:16]}"


class GooglePayProcessor:
    """Processes Google Pay payments via PSP"""
    
    def __init__(self, psp_config: Dict, central_fund, trace_logger: TraceLogger):
        self.psp_config = psp_config
        self.central_fund = central_fund
        self.trace_logger = trace_logger
        self.gateway = psp_config.get("google_pay_gateway", "braintree")
        self.gateway_merchant_id = psp_config.get("google_pay_gateway_merchant_id")
    
    async def process_payment(self, request: WalletPaymentRequest, user: User, session: UserSession) -> WalletPaymentResult:
        """Process Google Pay payment"""
        
        try:
            # 1. Parse payment token
            payment_token = request.payment_token
            if isinstance(payment_token, str):
                payment_token = json.loads(payment_token)
            
            # 2. Verify signature (Google Pay uses JWS)
            if not await self._verify_google_pay_signature(payment_token):
                return WalletPaymentResult(success=False, reason="Invalid signature")
            
            # 3. Extract payment method
            card_info = self._extract_card_info(payment_token)
            
            # 4. Verify DR bank support
            if not self._is_dr_bank_supported(card_info):
                return WalletPaymentResult(success=False, reason="Card issuer not supported in DR")
            
            # 5. Build payment with auto-fill
            auto_filled = await self._build_auto_filled_payment(request, user, session, card_info)
            
            # 6. Fraud check
            risk = await self.fraud_detector.assess_digital_wallet_payment(user, session, auto_filled, "google_pay")
            if risk.action == FraudAction.BLOCK_AND_INVESTIGATE:
                return WalletPaymentResult(success=False, reason="Fraud check failed")
            
            # 7. Execute via Central AI Fund
            result = await self.central_fund.execute_payment(auto_filled)
            
            # 8. Create payment record
            payment = await self._create_payment_record(user, session, request, auto_filled, result, card_info)
            
            return WalletPaymentResult(
                success=result.success,
                payment_id=str(payment.id),
                trace_id=payment.trace_id,
                receipt=self._build_receipt(payment, result),
                merit_earned=float(result.merit_earned) if result.merit_earned else 0
            )
            
        except Exception as e:
            logger.error("Google Pay processing failed", error=str(e))
            return WalletPaymentResult(success=False, reason=f"Processing error: {str(e)}")
    
    async def _verify_google_pay_signature(self, payment_token: Dict) -> bool:
        """Verify Google Pay JWS signature"""
        # In production, verify the JWS signature using Google's public keys
        return True
    
    def _extract_card_info(self, payment_token: Dict) -> Dict:
        """Extract card info from Google Pay token"""
        payment_method_data = payment_token.get("paymentMethodData", {})
        info = payment_method_data.get("info", {})
        tokenization = payment_method_data.get("tokenizationData", {})
        
        return {
            "token": tokenization.get("token", ""),
            "network": info.get("cardNetwork", "").lower(),
            "type": "credit" if info.get("cardClass") == "CREDIT" else "debit",
            "issuer": self._identify_issuer(info.get("cardDetails", "")),
            "last4": info.get("cardDetails", "")[-4:],
            "device_account_number": tokenization.get("token", "")[:32]
        }
    
    def _identify_issuer(self, display_name: str) -> str:
        """Identify card issuer"""
        display_lower = display_name.lower()
        if "banreservas" in display_lower or "reservas" in display_lower:
            return "Banreservas"
        elif "popular" in display_lower:
            return "Banco Popular"
        elif "bhd" in display_lower or "leon" in display_lower:
            return "BHD León"
        elif "scotia" in display_lower:
            return "Scotiabank"
        elif "banesco" in display_lower:
            return "Banesco"
        elif "caribe" in display_lower:
            return "Banco Caribe"
        elif "ademi" in display_lower:
            return "Banco Ademi"
        elif "promerica" in display_lower:
            return "Banco Promerica"
        return "Unknown"
    
    def _is_dr_bank_supported(self, card_info: Dict) -> bool:
        supported_issuers = {
            "Banreservas", "Banco Popular", "BHD León", "Scotiabank",
            "Banesco", "Banco Caribe", "Banco Ademi", "Banco Promerica"
        }
        return card_info.get("issuer") in supported_issuers
    
    async def _build_auto_filled_payment(self, request: WalletPaymentRequest, user: User, session: UserSession, card_info: Dict) -> Dict:
        return {
            **request.user_provided,
            "_wallet_type": "google_pay",
            "_card_token": card_info["token"],
            "_card_network": card_info["network"],
            "_card_issuer": card_info["issuer"],
            "_biometric_verified": payment_token.get("authMethod") == "CRYPTOGRAM_3DS"
        }
    
    async def _create_payment_record(self, user: User, session: UserSession, request: WalletPaymentRequest,
                                     auto_filled: Dict, result, card_info: Dict) -> Payment:
        payment = Payment(
            user_id=user.id,
            session_id=session.id,
            payment_type=request.payment_type,
            status=PaymentStatus.COMPLETED if result.success else PaymentStatus.FAILED,
            amount=result.amount if hasattr(result, 'amount') else Decimal("0"),
            payment_method=PaymentMethod.GOOGLE_PAY,
            payment_method_details={
                "wallet_type": "google_pay",
                "card_network": card_info["network"],
                "card_issuer": card_info["issuer"],
                "card_last4": card_info["last4"],
                "device_account_number": card_info["device_account_number"],
                "biometric_verified": auto_filled.get("_biometric_verified", False)
            },
            auto_filled_data=auto_filled,
            user_provided_data=request.user_provided,
            gov_api_responses=result.gov_responses if hasattr(result, 'gov_responses') else {},
            gov_transaction_ids=result.transaction_ids if hasattr(result, 'transaction_ids') else {},
            description=f"Google Pay: {request.payment_type.value}",
            trace_id=self._generate_trace_id(),
            wallet_type="google_pay",
            biometric_verified=auto_filled.get("_biometric_verified", False),
            merit_earned=result.merit_earned if hasattr(result, 'merit_earned') else 0
        )
        return payment
    
    def _build_receipt(self, payment: Payment, result) -> Dict:
        return {
            "payment_id": str(payment.id),
            "amount": str(payment.amount),
            "type": payment.payment_type.value,
            "method": "Google Pay",
            "card_issuer": payment.payment_method_details.get("card_issuer"),
            "card_last4": payment.payment_method_details.get("card_last4"),
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": payment.trace_id,
            "merit_earned": float(payment.merit_earned) if payment.merit_earned else 0
        }
    
    def _generate_trace_id(self) -> str:
        return f"gpay_{uuid.uuid4().hex[:16]}"


class DigitalWalletService:
    """Unified digital wallet service for Apple Pay + Google Pay"""
    
    def __init__(self, db: AsyncSession, apple_processor: ApplePayProcessor,
                 google_processor: GooglePayProcessor, trace_logger: TraceLogger,
                 fraud_detector: FraudDetector):
        self.db = db
        self.apple_pay = apple_processor
        self.google_pay = google_processor
        self.trace_logger = trace_logger
        self.fraud_detector = fraud_detector
    
    async def get_available_wallets(self, user: User, platform: str) -> List[Dict]:
        """Get available wallets for user/platform"""
        wallets = []
        
        # Check Apple Pay (iOS, macOS, Safari)
        if platform in ["ios", "macos", "safari"]:
            apple_wallet = await self._get_apple_pay_wallet(user)
            if apple_wallet:
                wallets.append(apple_wallet)
        
        # Check Google Pay (Android, Chrome, Web)
        if platform in ["android", "chrome", "web"]:
            google_wallet = await self._get_google_pay_wallet(user)
            if google_wallet:
                wallets.append(google_wallet)
        
        return wallets
    
    async def _get_apple_pay_wallet(self, user: User) -> Optional[Dict]:
        """Check if user has Apple Pay configured"""
        # Check user's digital_wallets field
        wallets = user.digital_wallets or []
        apple_cards = [w for w in wallets if w.get("type") == "apple_pay"]
        
        if apple_cards:
            return {
                "type": "apple_pay",
                "label": "Apple Pay",
                "icon": "apple_pay",
                "supported_cards": [c.get("network", "") for c in apple_cards],
                "cards": apple_cards
            }
        return None
    
    async def _get_google_pay_wallet(self, user: User) -> Optional[Dict]:
        """Check if user has Google Pay configured"""
        wallets = user.digital_wallets or []
        google_cards = [w for w in wallets if w.get("type") == "google_pay"]
        
        if google_cards:
            return {
                "type": "google_pay",
                "label": "Google Pay",
                "icon": "google_pay",
                "supported_cards": [c.get("network", "") for c in google_cards],
                "cards": google_cards
            }
        return None
    
    async def process_payment(self, request: WalletPaymentRequest, user: User, session: UserSession) -> WalletPaymentResult:
        """Route to appropriate processor"""
        
        if request.wallet_type == WalletType.APPLE_PAY:
            return await self.apple_pay.process_payment(request, user, session)
        elif request.wallet_type == WalletType.GOOGLE_PAY:
            return await self.google_pay.process_payment(request, user, session)
        else:
            return WalletPaymentResult(success=False, reason="Unsupported wallet type")
    
    async def add_wallet_card(self, user: User, wallet_type: WalletType, card_data: Dict) -> bool:
        """Add card to user's digital wallet"""
        wallets = list(user.digital_wallets or [])
        
        # Check if card already exists
        for wallet in wallets:
            if wallet.get("type") == wallet_type.value and wallet.get("last4") == card_data.get("last4"):
                return False  # Already exists
        
        # Add new card
        wallet_entry = {
            "type": wallet_type.value,
            "network": card_data.get("network"),
            "issuer": card_data.get("issuer"),
            "last4": card_data.get("last4"),
            "device_account_number": card_data.get("device_account_number"),
            "added_at": datetime.utcnow().isoformat()
        }
        
        wallets.append(wallet_entry)
        user.digital_wallets = wallets
        
        await self.db.flush()
        return True