# DR Telecom Integration - SMS, WhatsApp, USSD, Number Portability
import asyncio
import hashlib
import json
import re
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum

import structlog
import aiohttp
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import get_settings
from models import User, UserSession, AuditRecord, AuditEventType
from services.trace_logger import TraceLogger

settings = get_settings()
logger = structlog.get_logger()


class DRCarrier(str, Enum):
    CLARO = "claro"
    ALTICE = "altice"
    VIVA = "viva"


class MessageChannel(str, Enum):
    WHATSAPP = "whatsapp"
    SMS = "sms"
    USSD = "ussd"
    VOICE = "voice"
    PUSH = "push"
    CELL_BROADCAST = "cell_broadcast"


@dataclass
class AuthContext:
    ip_address: str
    ip_hash: str
    device_fingerprint: str
    user_agent: str
    locale: str = "es"


@dataclass
class NPResult:
    number: str
    carrier: DRCarrier
    ported: bool
    ported_date: Optional[datetime]
    original_carrier: Optional[DRCarrier]
    status: str  # active, suspended, deactivated


@dataclass
class SMSResult:
    success: bool
    message_id: Optional[str] = None
    carrier: Optional[DRCarrier] = None
    cost: Optional[Decimal] = None
    error: Optional[str] = None


@dataclass
class WAResult:
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


@dataclass
class USSDSession:
    session_id: str
    phone: str
    carrier: DRCarrier
    menu_state: str
    language: str
    created_at: datetime
    expires_at: datetime


class DRNumberPortabilityLookup:
    """Query INDOTEL NP database for carrier lookup"""
    
    def __init__(self, config, cache):
        self.np_api_url = config.INDOTEL_NP_API_URL
        self.api_key = config.INDOTEL_NP_API_KEY
        self.cache = cache
        self.cache_ttl = 3600
    
    async def lookup(self, phone_number: str) -> NPResult:
        """Get current carrier for DR phone number"""
        
        normalized = self._normalize_dr_number(phone_number)
        
        # Check cache
        cache_key = f"np:{normalized}"
        cached = await self.cache.get(cache_key)
        if cached:
            return NPResult(**cached)
        
        # Try INDOTEL API first
        if self.np_api_url and self.api_key:
            try:
                result = await self._query_indotel_api(normalized)
                if result:
                    await self.cache.set(cache_key, result.__dict__, ttl=self.cache_ttl)
                    return result
            except Exception as e:
                logger.warning("INDOTEL NP API failed, trying aggregators", error=str(e))
        
        # Fallback to commercial aggregators
        return await self._lookup_via_aggregators(normalized)
    
    async def _query_indotel_api(self, normalized: str) -> Optional[NPResult]:
        """Query INDOTEL NP database directly"""
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with session.get(
                f"{self.np_api_url}/lookup",
                params={"number": normalized},
                headers=headers
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return NPResult(
                        number=normalized,
                        carrier=DRCarrier(data["carrier"]),
                        ported=data["ported"],
                        ported_date=datetime.fromisoformat(data["ported_date"]) if data.get("ported_date") else None,
                        original_carrier=DRCarrier(data["original_carrier"]) if data.get("original_carrier") else None,
                        status=data["status"]
                    )
        return None
    
    async def _lookup_via_aggregators(self, normalized: str) -> NPResult:
        """Use commercial aggregators as fallback"""
        # Try Twilio Lookup
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                result = await self._twilio_lookup(normalized)
                if result:
                    return result
            except Exception:
                pass
        
        # Default to Claro (largest carrier) if all else fails
        return NPResult(
            number=normalized,
            carrier=DRCarrier.CLARO,
            ported=False,
            ported_date=None,
            original_carrier=None,
            status="active"
        )
    
    async def _twilio_lookup(self, normalized: str) -> Optional[NPResult]:
        """Lookup via Twilio Number Insight"""
        import base64
        auth = base64.b64encode(f"{settings.TWILIO_ACCOUNT_SID}:{settings.TWILIO_AUTH_TOKEN}".encode()).decode()
        
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Basic {auth}"}
            async with session.get(
                f"https://lookups.twilio.com/v2/PhoneNumbers/{normalized}",
                params={"Fields": "carrier"},
                headers=headers
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    carrier_name = data.get("carrier", {}).get("name", "").lower()
                    
                    carrier_map = {
                        "claro": DRCarrier.CLARO,
                        "altice": DRCarrier.ALTICE,
                        "orange": DRCarrier.ALTICE,
                        "tricom": DRCarrier.ALTICE,
                        "viva": DRCarrier.VIVA
                    }
                    
                    for key, carrier in carrier_map.items():
                        if key in carrier_name:
                            return NPResult(
                                number=normalized,
                                carrier=carrier,
                                ported=True,
                                ported_date=None,
                                original_carrier=None,
                                status="active"
                            )
        return None
    
    def _normalize_dr_number(self, phone: str) -> str:
        """Normalize to +18XXXXXXXXX format"""
        digits = re.sub(r'\D', '', phone)
        
        if digits.startswith("1809") or digits.startswith("1829") or digits.startswith("1849"):
            return f"+{digits}"
        elif digits.startswith("809") or digits.startswith("829") or digits.startswith("849"):
            return f"+1{digits}"
        elif len(digits) == 10:
            return f"+1{digits}"
        elif len(digits) == 7:
            raise ValueError("Need full 10-digit number with area code")
        
        return f"+{digits}"


class DRCarrierSMSGateway:
    """Direct carrier SMS gateway integration"""
    
    CARRIER_CONFIGS = {
        DRCarrier.CLARO: {
            "http_endpoint": "https://api.claro.com.do/sms/v1/send",
            "smpp_host": "smpp.claro.com.do",
            "smpp_port": 2775,
            "sender_id": "GOB-RD"
        },
        DRCarrier.ALTICE: {
            "http_endpoint": "https://api.altice.com.do/sms/v1/send",
            "smpp_host": "smpp.altice.com.do",
            "smpp_port": 2775,
            "sender_id": "GOB-RD"
        },
        DRCarrier.VIVA: {
            "http_endpoint": "https://api.viva.com.do/sms/v1/send",
            "smpp_host": "smpp.viva.com.do",
            "smpp_port": 2775,
            "sender_id": "GOB-RD"
        }
    }
    
    def __init__(self, config, np_lookup: DRNumberPortabilityLookup, cache):
        self.config = config
        self.np_lookup = np_lookup
        self.cache = cache
        self.carrier_tokens = {
            DRCarrier.CLARO: config.CLARO_SMS_TOKEN,
            DRCarrier.ALTICE: config.ALTICE_SMS_TOKEN,
            DRCarrier.VIVA: config.VIVA_SMS_TOKEN
        }
    
    async def send_sms(self, phone: str, message: str, priority: str = "normal") -> SMSResult:
        """Send SMS via optimal carrier route"""
        
        # Determine carrier
        np_result = await self.np_lookup.lookup(phone)
        carrier = np_result.carrier
        
        # Get carrier config
        carrier_config = self.CARRIER_CONFIGS[carrier]
        endpoint = carrier_config["http_endpoint"]
        sender_id = carrier_config["sender_id"]
        token = self.carrier_tokens.get(carrier)
        
        if not token:
            return SMSResult(success=False, error="Carrier token not configured")
        
        # Send via HTTP API
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            payload = {
                "to": np_result.number,
                "text": message,
                "sender_id": sender_id,
                "priority": priority,
                "dlr_url": f"{settings.MAGIC_LINK_DOMAIN}/webhooks/sms/dlr"
            }
            
            try:
                async with session.post(endpoint, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return SMSResult(
                            success=True,
                            message_id=data.get("message_id"),
                            carrier=carrier,
                            cost=Decimal(str(data.get("cost", "0")))
                        )
                    else:
                        error_data = await resp.text()
                        return SMSResult(success=False, carrier=carrier, error=error_data)
            except Exception as e:
                return SMSResult(success=False, carrier=carrier, error=str(e))
    
    async def send_otp(self, phone: str, otp: str, locale: str = "es") -> SMSResult:
        """Send OTP via SMS"""
        messages = {
            "es": f"Tu código GobernanzaRD: {otp}. Válido 5 min. No compartas.",
            "en": f"Your GobernanzaRD code: {otp}. Valid 5 min. Do not share.",
            "ht": f"Kòd GobernanzaRD ou a: {otp}. Valid 5 min. Pa pataje l."
        }
        message = messages.get(locale, messages["es"])
        return await self.send_sms(phone, message, priority="high")


class SMSAggregatorGateway:
    """Aggregator-based SMS (Twilio, Vonage, Plivo, etc.)"""
    
    def __init__(self, config, np_lookup: DRNumberPortabilityLookup):
        self.config = config
        self.np_lookup = np_lookup
    
    async def send_sms(self, phone: str, message: str, priority: str = "normal") -> SMSResult:
        """Send via configured aggregator"""
        
        # Try Twilio first
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            return await self._send_via_twilio(phone, message)
        
        # Try Vonage
        if settings.VONAGE_API_KEY and settings.VONAGE_API_SECRET:
            return await self._send_via_vonage(phone, message)
        
        # Try Plivo
        if hasattr(settings, 'PLIVO_AUTH_ID') and hasattr(settings, 'PLIVO_AUTH_TOKEN'):
            return await self._send_via_plivo(phone, message)
        
        return SMSResult(success=False, error="No SMS aggregator configured")
    
    async def _send_via_twilio(self, phone: str, message: str) -> SMSResult:
        import base64
        auth = base64.b64encode(f"{settings.TWILIO_ACCOUNT_SID}:{settings.TWILIO_AUTH_TOKEN}".encode()).decode()
        
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "To": phone,
                "From": settings.TWILIO_WHATSAPP_NUMBER or "+15551234567",
                "Body": message
            }
            
            async with session.post(
                f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json",
                data=data,
                headers=headers
            ) as resp:
                if resp.status in [200, 201]:
                    result = await resp.json()
                    return SMSResult(success=True, message_id=result.get("sid"))
                return SMSResult(success=False, error=await resp.text())
    
    async def _send_via_vonage(self, phone: str, message: str) -> SMSResult:
        async with aiohttp.ClientSession() as session:
            payload = {
                "api_key": settings.VONAGE_API_KEY,
                "api_secret": settings.VONAGE_API_SECRET,
                "to": phone,
                "from": "GobRD",
                "text": message
            }
            
            async with session.post("https://rest.nexmo.com/sms/json", json=payload) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result["messages"][0]["status"] == "0":
                        return SMSResult(success=True, message_id=result["messages"][0]["message-id"])
                return SMSResult(success=False, error=await resp.text())
    
    async def _send_via_plivo(self, phone: str, message: str) -> SMSResult:
        # Similar implementation for Plivo
        return SMSResult(success=False, error="Plivo not implemented")


class WhatsAppBusinessAPI:
    """WhatsApp Business API integration via BSP"""
    
    TEMPLATES = {
        "otp": "gobernanza_otp",
        "merit_threshold": "merit_threshold_reached",
        "quest_reminder": "quest_visit_reminder",
        "payment_confirmation": "payment_confirmed",
        "veeduria_alert": "veeduria_new_report",
        "delivery_update": "delivery_status_update",
        "identity_escalation": "identity_level_changed"
    }
    
    def __init__(self, config):
        self.config = config
        self.bsp = config.WHATSAPP_BSP
        self.whatsapp_number = self._get_whatsapp_number()
    
    def _get_whatsapp_number(self) -> str:
        if self.bsp == "twilio":
            return settings.TWILIO_WHATSAPP_NUMBER
        elif self.bsp == "vonage":
            return settings.VONAGE_WHATSAPP_NUMBER
        return ""
    
    async def send_template(self, phone: str, template_name: str, params: List[str], locale: str = "es") -> WAResult:
        """Send templated WhatsApp message"""
        
        normalized = self._normalize_for_whatsapp(phone)
        
        if self.bsp == "twilio":
            return await self._send_twilio_template(normalized, template_name, params)
        elif self.bsp == "vonage":
            return await self._send_vonage_template(normalized, template_name, params)
        elif self.bsp == "messagebird":
            return await self._send_messagebird_template(normalized, template_name, params)
        
        return WAResult(success=False, error="BSP not configured")
    
    async def _send_twilio_template(self, phone: str, template_name: str, params: List[str]) -> WAResult:
        import base64
        auth = base64.b64encode(f"{settings.TWILIO_ACCOUNT_SID}:{settings.TWILIO_AUTH_TOKEN}".encode()).decode()
        
        content_vars = {str(i+1): v for i, v in enumerate(params)}
        
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "From": f"whatsapp:{self.whatsapp_number}",
                "To": f"whatsapp:{phone}",
                "ContentSid": self._get_template_sid(template_name),
                "ContentVariables": json.dumps(content_vars)
            }
            
            async with session.post(
                f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json",
                data=data,
                headers=headers
            ) as resp:
                if resp.status in [200, 201]:
                    result = await resp.json()
                    return WAResult(success=True, message_id=result.get("sid"))
                return WAResult(success=False, error=await resp.text())
    
    async def _send_vonage_template(self, phone: str, template_name: str, params: List[str]) -> WAResult:
        # Vonage Messages API implementation
        return WAResult(success=False, error="Vonage WhatsApp not implemented")
    
    async def _send_messagebird_template(self, phone: str, template_name: str, params: List[str]) -> WAResult:
        # MessageBird implementation
        return WAResult(success=False, error="MessageBird WhatsApp not implemented")
    
    def _get_template_sid(self, template_name: str) -> str:
        """Get ContentSid for approved template"""
        # Would be configured per template
        template_sids = {
            "gobernanza_otp": "HX...",
            "merit_threshold_reached": "HX...",
            "quest_visit_reminder": "HX...",
            "payment_confirmed": "HX...",
            "veeduria_new_report": "HX...",
            "delivery_status_update": "HX...",
            "identity_level_changed": "HX..."
        }
        return template_sids.get(template_name, "")
    
    def _normalize_for_whatsapp(self, phone: str) -> str:
        """Normalize phone for WhatsApp (E.164 without +)"""
        digits = re.sub(r'\D', '', phone)
        if digits.startswith("1"):
            return digits
        elif digits.startswith("809") or digits.startswith("829") or digits.startswith("849"):
            return f"1{digits}"
        return digits


class USSDGateway:
    """USSD Gateway for feature phones and offline access"""
    
    USSD_CODE = "*462#"  # *GOB#
    
    MENU_TREE = {
        "main": {
            "text": "GOBIERNO RD\n1. Consultar méritos\n2. Pagar servicios\n3. Vivienda\n4. Quest/Visitas\n5. Veeduría\n6. Alertas\n0. Salir",
            "options": {"1": "merits", "2": "payments", "3": "housing", "4": "quest", "5": "veeduria", "6": "alerts"}
        },
        "merits": {
            "text": "TUS MÉRITOS\nTotal: {{merits}}\nNivel: {{level}}\n1. Ver detalles\n2. Beneficios disponibles\n3. Historial\n0. Volver",
            "options": {"1": "merits_detail", "2": "benefits", "3": "history"}
        },
        "payments": {
            "text": "PAGAR SERVICIOS\n1. Luz (EDE)\n2. Agua (CORAASAN/CAASD)\n3. BonoGas/BonoLuz\n4. Ver deudas\n0. Volver",
            "options": {"1": "pay_ede", "2": "pay_water", "3": "pay_bonos", "4": "view_debts"}
        }
    }
    
    def __init__(self, config, np_lookup: DRNumberPortabilityLookup):
        self.config = config
        self.np_lookup = np_lookup
        self.sessions: Dict[str, USSDSession] = {}
    
    async def handle_request(self, phone: str, session_id: str, user_input: str, carrier: DRCarrier) -> Dict:
        """Handle USSD request"""
        
        # Get or create session
        if session_id not in self.sessions:
            self.sessions[session_id] = USSDSession(
                session_id=session_id,
                phone=phone,
                carrier=carrier,
                menu_state="main",
                language="es",
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(minutes=20)
            )
        
        session = self.sessions[session_id]
        
        # Check expiry
        if datetime.utcnow() > session.expires_at:
            del self.sessions[session_id]
            return {"text": "Sesión expirada. Marque *462# de nuevo.", "end": True}
        
        # Handle input
        return await self._process_menu(session, user_input)
    
    async def _process_menu(self, session: USSDSession, user_input: str) -> Dict:
        """Process menu navigation"""
        
        current_menu = self.MENU_TREE.get(session.menu_state, self.MENU_TREE["main"])
        
        if user_input == "0":
            session.menu_state = "main"
            if session.menu_state == "main" and user_input == "0":
                return {"text": "Gracias por usar Gobierno RD. ¡Hasta pronto!", "end": True}
            current_menu = self.MENU_TREE["main"]
        
        # Navigate
        if user_input in current_menu.get("options", {}):
            next_state = current_menu["options"][user_input]
            session.menu_state = next_state
            next_menu = self.MENU_TREE.get(next_state, self.MENU_TREE["main"])
            return {"text": next_menu["text"], "end": False}
        
        # Invalid input
        return {"text": "Opción inválida. Intente de nuevo.\n" + current_menu["text"], "end": False}
    
    def cleanup_expired(self):
        """Clean up expired sessions"""
        now = datetime.utcnow()
        expired = [sid for sid, s in self.sessions.items() if now > s.expires_at]
        for sid in expired:
            del self.sessions[sid]


class DRCommunicationRouter:
    """Routes messages to optimal channel based on user profile and message type"""
    
    CHANNEL_PRIORITY = {
        "emergency": [MessageChannel.CELL_BROADCAST, MessageChannel.SMS, MessageChannel.WHATSAPP, MessageChannel.PUSH],
        "otp": [MessageChannel.WHATSAPP, MessageChannel.SMS, MessageChannel.USSD, MessageChannel.VOICE],
        "interactive": [MessageChannel.WHATSAPP, MessageChannel.USSD, MessageChannel.SMS],
        "notification": [MessageChannel.WHATSAPP, MessageChannel.PUSH, MessageChannel.SMS],
        "marketing": [MessageChannel.WHATSAPP, MessageChannel.SMS]  # Opt-in only
    }
    
    def __init__(self, sms_gateway: DRCarrierSMSGateway, sms_aggregator: SMSAggregatorGateway,
                 whatsapp: WhatsAppBusinessAPI, ussd: USSDGateway, trace_logger: TraceLogger):
        self.sms_gateway = sms_gateway
        self.sms_aggregator = sms_aggregator
        self.whatsapp = whatsapp
        self.ussd = ussd
        self.trace_logger = trace_logger
    
    async def route_message(self, user: User, message_type: str, content: Dict,
                            priority: str = "normal") -> Dict:
        """Route message to best channel"""
        
        # Emergency -> all channels
        if priority == "emergency":
            return await self._broadcast_all_channels(user, content)
        
        # Get channel priority for message type
        channels = self.CHANNEL_PRIORITY.get(message_type, self.CHANNEL_PRIORITY["notification"])
        
        # Try channels in order
        for channel in channels:
            result = await self._send_via_channel(user, channel, content)
            if result.get("success"):
                return {"success": True, "channel": channel.value, "result": result}
        
        return {"success": False, "reason": "All channels failed"}
    
    async def _send_via_channel(self, user: User, channel: MessageChannel, content: Dict) -> Dict:
        """Send via specific channel"""
        
        if channel == MessageChannel.WHATSAPP and user.whatsapp_opt_in and user.whatsapp_verified:
            template = content.get("template")
            params = content.get("params", [])
            return await self.whatsapp.send_template(user.phone, template, params, user.preferred_language)
        
        elif channel == MessageChannel.SMS:
            message = content.get("sms_text") or content.get("text", "")
            return await self.sms_gateway.send_sms(user.phone, message)
        
        elif channel == MessageChannel.USSD and user.device_type == "feature":
            # USSD is session-based, not push
            return {"success": False, "reason": "USSD requires user initiation"}
        
        elif channel == MessageChannel.PUSH:
            # Would integrate with push notification service
            return {"success": False, "reason": "Push not implemented"}
        
        elif channel == MessageChannel.CELL_BROADCAST:
            # Coordinated via COE/INDOTEL
            return {"success": False, "reason": "Cell broadcast requires COE coordination"}
        
        return {"success": False, "reason": f"Channel {channel} not available"}
    
    async def _broadcast_all_channels(self, user: User, content: Dict) -> Dict:
        """Send emergency alert via all available channels"""
        results = {}
        
        # Cell Broadcast (highest priority, handled by COE)
        results["cell_broadcast"] = {"success": True, "note": "Queued via COE"}
        
        # SMS
        sms_result = await self.sms_gateway.send_sms(user.phone, content.get("emergency_text", ""))
        results["sms"] = {"success": sms_result.success}
        
        # WhatsApp
        if user.whatsapp_opt_in:
            wa_result = await self.whatsapp.send_template(
                user.phone, "emergency_alert", [content.get("title", ""), content.get("action", "")]
            )
            results["whatsapp"] = {"success": wa_result.success}
        
        # Push
        results["push"] = {"success": False, "note": "Not implemented"}
        
        return {"success": True, "channels": results}


class DRTelecomService:
    """Main telecom service orchestrating all channels"""
    
    def __init__(self, db: AsyncSession, config, trace_logger: TraceLogger, cache):
        self.db = db
        self.config = config
        self.trace_logger = trace_logger
        self.cache = cache
        
        # Initialize components
        self.np_lookup = DRNumberPortabilityLookup(config, cache)
        self.sms_gateway = DRCarrierSMSGateway(config, self.np_lookup, cache)
        self.sms_aggregator = SMSAggregatorGateway(config, self.np_lookup)
        self.whatsapp = WhatsAppBusinessAPI(config)
        self.ussd = USSDGateway(config, self.np_lookup)
        self.router = DRCommunicationRouter(
            self.sms_gateway, self.sms_aggregator, self.whatsapp, self.ussd, trace_logger
        )
    
    async def enrich_user_profile(self, phone: str, cedula: str = None) -> Dict:
        """Build complete communication profile for user"""
        
        # Number portability lookup
        np = await self.np_lookup.lookup(phone)
        
        # WhatsApp check
        wa_status = await self._check_whatsapp(phone)
        
        # Device detection (would come from last interaction)
        device_type = await self._detect_device_type(phone)
        
        return {
            "phone": phone,
            "carrier": np.carrier.value,
            "carrier_verified": np.status == "active",
            "ported": np.ported,
            "whatsapp_available": wa_status.get("available", False),
            "whatsapp_verified": wa_status.get("verified", False),
            "device_type": device_type,
            "preferred_language": "es",
            "opt_ins": await self._get_user_opt_ins(phone)
        }
    
    async def send_otp(self, user: User, otp: str, session: UserSession) -> Dict:
        """Send OTP via best available channel"""
        
        # Try WhatsApp first if opted in
        if user.whatsapp_opt_in and user.whatsapp_verified:
            result = await self.whatsapp.send_template(user.phone, "otp", [otp], user.preferred_language)
            if result.success:
                await self._log_otp_sent(user, session, "whatsapp", result.message_id)
                return {"success": True, "channel": "whatsapp"}
        
        # Fallback to SMS
        sms_result = await self.sms_gateway.send_otp(user.phone, otp, user.preferred_language)
        if sms_result.success:
            await self._log_otp_sent(user, session, "sms", sms_result.message_id)
            return {"success": True, "channel": "sms", "carrier": sms_result.carrier.value}
        
        # Fallback to voice
        # Would implement voice OTP
        
        return {"success": False, "reason": "All OTP channels failed"}
    
    async def _check_whatsapp(self, phone: str) -> Dict:
        """Check WhatsApp availability for number"""
        # Would call BSP API to check
        return {"available": True, "verified": False}
    
    async def _detect_device_type(self, phone: str) -> str:
        """Detect device type from last interaction"""
        return "smartphone"
    
    async def _get_user_opt_ins(self, phone: str) -> Dict:
        """Get user communication opt-ins"""
        return {"whatsapp": True, "sms": True, "push": False}
    
    async def _log_otp_sent(self, user: User, session: UserSession, channel: str, message_id: str):
        await self.trace_logger.log_event(
            event_type=AuditEventType.MAGIC_LINK_VERIFIED,  # Reuse for OTP
            event_data={
                "channel": channel,
                "message_id": message_id,
                "otp_sent": True
            },
            actor_user_id=user.id,
            actor_session_id=session.id
        )