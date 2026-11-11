# Dominican Republic Telecom & Phone Number Infrastructure
## Carriers, APIs, Numbering Plan & Integration for Governance Platform

---

## 1. DOMINICAN REPUBLIC MOBILE CARRIERS

### 1.1 Major Operators (2024 Market Share)

| Carrier | Brand | Market Share | Subscribers | Network | Parent Company |
|---------|-------|--------------|-------------|---------|----------------|
| **Claro Dominicana** | Claro | ~45% | ~5.2M | 2G/3G/4G/5G | América Móvil (Carlos Slim) |
| **Altice Dominicana** | Altice | ~35% | ~4.0M | 2G/3G/4G/5G | Altice Group (Patrick Drahi) |
| **Viva Dominicana** | Viva | ~18% | ~2.1M | 4G/5G only | Trilogy International |
| **Waoo (WiMAX)** | Waoo | ~2% | ~0.2M | Fixed wireless | Local consortium |

### 1.2 Carrier Contact & Developer Info

```python
DR_CARRIERS = {
    "claro": {
        "name": "Claro Dominicana",
        "website": "https://www.claro.com.do",
        "developer_portal": "https://developers.claro.com.do",  # If exists
        "api_contact": "api@claro.com.do",
        "business_contact": "empresas@claro.com.do",
        "wholesale_contact": "wholesale@claro.com.do",
        "ussd_gateway": "*123#",  # Balance check
        "short_codes": {
            "sms_gateway": "8080",  # Example
            "verification": "2626"
        },
        "mcc_mnc": "370-01",  # MCC=370 (DR), MNC=01 (Claro)
        "number_prefixes": ["809", "829", "849"],  # Shared pool
        "supports": {
            "sms_api": True,
            "ussd_api": True,
            "voice_api": True,
            "whatsapp_bsp": True,  # Business Solution Provider
            "number_lookup": True,
            "portability_check": True,
            "kyc_api": True,  # SIM registration verification
            "location_api": False  # Requires special approval
        }
    },
    "altice": {
        "name": "Altice Dominicana",
        "website": "https://www.altice.com.do",
        "developer_portal": "https://developers.altice.com.do",
        "api_contact": "api@altice.com.do",
        "business_contact": "corporativo@altice.com.do",
        "wholesale_contact": "carrier@altice.com.do",
        "ussd_gateway": "*111#",
        "short_codes": {
            "sms_gateway": "9090",
            "verification": "3636"
        },
        "mcc_mnc": "370-02",  # MNC=02 (Altice, formerly Orange/Tricom)
        "number_prefixes": ["809", "829", "849"],
        "supports": {
            "sms_api": True,
            "ussd_api": True,
            "voice_api": True,
            "whatsapp_bsp": True,
            "number_lookup": True,
            "portability_check": True,
            "kyc_api": True,
            "location_api": False
        }
    },
    "viva": {
        "name": "Viva Dominicana",
        "website": "https://www.viva.com.do",
        "developer_portal": None,  # No public developer portal
        "api_contact": "integraciones@viva.com.do",
        "business_contact": "empresas@viva.com.do",
        "ussd_gateway": "*222#",
        "short_codes": {
            "sms_gateway": "7070",
            "verification": "4646"
        },
        "mcc_mnc": "370-03",  # MNC=03 (Viva)
        "number_prefixes": ["809", "829", "849"],
        "supports": {
            "sms_api": True,
            "ussd_api": True,
            "voice_api": False,
            "whatsapp_bsp": False,  # Use aggregator
            "number_lookup": True,
            "portability_check": True,
            "kyc_api": True,
            "location_api": False
        }
    }
}
```

---

## 2. DR NUMBERING PLAN (ITU-T E.164)

### 2.1 Format Structure

```
+1 8XX NXX XXXX
│  │  │  └──── Line number (4 digits)
│  │  └─────── Central office code (3 digits)
│  └────────── Area code: 809, 829, 849 (overlay)
└───────────── Country code: +1 (NANP - North American Numbering Plan)
```

### 2.2 Area Codes & History

| Area Code | Introduced | Status | Notes |
|-----------|------------|--------|-------|
| **809** | 1958 (original) | Active | Original DR code, shared with Caribbean until 1990s |
| **829** | 2005 | Active | Overlay for 809 exhaustion |
| **849** | 2009 | Active | Second overlay |

### 2.3 Carrier Prefix Ranges (Approximate - Number Portability Applies)

```python
# These are HISTORIC ranges - NUMBER PORTABILITY means any prefix can be any carrier
# Use NP database for actual carrier lookup

HISTORIC_PREFIX_RANGES = {
    "claro": {
        "809": ["200-299", "300-399", "400-499", "500-599", "600-699", "700-799", "800-899", "900-999"],
        "829": ["200-299", "300-399", "400-499", "500-599", "600-699", "700-799"],
        "849": ["200-299", "300-399", "400-499", "500-599"]
    },
    "altice": {
        "809": ["200-299", "300-399", "400-499", "500-599", "600-699", "700-799", "800-899", "900-999"],
        "829": ["200-299", "300-399", "400-499", "500-599", "600-699", "700-799"],
        "849": ["200-299", "300-399", "400-499", "500-599"]
    },
    "viva": {
        "809": ["200-299", "300-399", "400-499", "500-599", "600-699", "700-799"],
        "829": ["200-299", "300-399", "400-499", "500-599", "600-699", "700-799"],
        "849": ["200-299", "300-399", "400-499", "500-599"]
    }
}
```

---

## 3. NUMBER PORTABILITY (NP) - CRITICAL FOR DR

### 3.1 NP Administration
- **Administrator**: **INDOTEL** (Instituto Dominicano de las Telecomunicaciones)
- **NP Database**: Centralized, real-time, all carriers connected
- **Implementation**: Since 2009, mandatory for all carriers
- **Port Time**: Maximum 24 hours (usually 2-4 hours)

### 3.2 NP Lookup API (Required for Correct Routing)

```python
class DRNumberPortabilityLookup:
    """
    Query INDOTEL NP database to determine current carrier
    Essential for: SMS routing, USSD, WhatsApp BSP selection, KYC
    """
    
    def __init__(self, config):
        # INDOTEL provides API access to authorized entities
        # Or use commercial aggregators: Twilio, Vonage, Plivo, local providers
        self.np_api_url = config.np_api_url  # e.g., "https://np.indotel.gob.do/api"
        self.api_key = config.np_api_key
        self.cache_ttl = 3600  # Cache for 1 hour
    
    async def lookup(self, phone_number: str) -> NPResult:
        """Returns current carrier for a DR phone number"""
        
        # Normalize to E.164
        normalized = self._normalize_dr_number(phone_number)
        
        # Check cache
        cached = await self.cache.get(f"np:{normalized}")
        if cached:
            return cached
        
        # Query NP database
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with session.get(
                f"{self.np_api_url}/lookup",
                params={"number": normalized},
                headers=headers
            ) as resp:
                data = await resp.json()
        
        result = NPResult(
            number=normalized,
            carrier=data["carrier"],  # "claro", "altice", "viva"
            ported=data["ported"],
            ported_date=data.get("ported_date"),
            original_carrier=data.get("original_carrier"),
            status=data["status"]  # "active", "suspended", "deactivated"
        )
        
        await self.cache.set(f"np:{normalized}", result, ttl=self.cache_ttl)
        return result
    
    def _normalize_dr_number(self, phone: str) -> str:
        """Convert to +18XXXXXXXXX format"""
        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)
        
        # Handle various input formats
        if digits.startswith("1809") or digits.startswith("1829") or digits.startswith("1849"):
            return f"+{digits}"
        elif digits.startswith("809") or digits.startswith("829") or digits.startswith("849"):
            return f"+1{digits}"
        elif len(digits) == 10:  # 809XXXXXXX
            return f"+1{digits}"
        elif len(digits) == 7:  # XXXXXXX (local)
            # Can't determine area code - need full number
            raise ValueError("Need full 10-digit number with area code")
        
        return f"+{digits}"
```

### 3.3 Commercial NP Lookup Providers (If INDOTEL Direct Access Unavailable)

| Provider | API | Coverage | Cost |
|----------|-----|----------|------|
| **Twilio Lookup API** | REST | Global incl DR | $0.005/lookup |
| **Vonage Number Insight** | REST | Global incl DR | $0.004/lookup |
| **Plivo Lookup** | REST | Global incl DR | $0.003/lookup |
| **Numverify** | REST | Global incl DR | Freemium |
| **Local: Datacenter Dominicana** | SOAP/REST | DR only | Negotiated |
| **Local: Tecnosol** | REST | DR + Caribbean | Negotiated |

---

## 4. SMS & OTP INTEGRATION

### 4.1 Direct Carrier SMS APIs (Enterprise)

```python
class DRCarrerSMSGateway:
    """
    Direct carrier connections for highest reliability & lowest cost
    Requires: Enterprise contract, dedicated short code, compliance approval
    """
    
    CARRIER_ENDPOINTS = {
        "claro": {
            "submit_smpp": "smpp.claro.com.do:2775",
            "submit_http": "https://api.claro.com.do/sms/v1/send",
            "delivery_receipt": "https://api.claro.com.do/sms/v1/dlr",
            "balance_check": "https://api.claro.com.do/sms/v1/balance",
            "auth": "SMPP bind / OAuth2"
        },
        "altice": {
            "submit_smpp": "smpp.altice.com.do:2775",
            "submit_http": "https://api.altice.com.do/sms/v1/send",
            "delivery_receipt": "https://api.altice.com.do/sms/v1/dlr",
            "balance_check": "https://api.altice.com.do/sms/v1/balance",
            "auth": "SMPP bind / OAuth2"
        },
        "viva": {
            "submit_smpp": "smpp.viva.com.do:2775",
            "submit_http": "https://api.viva.com.do/sms/v1/send",
            "delivery_receipt": "https://api.viva.com.do/sms/v1/dlr",
            "auth": "SMPP bind"
        }
    }
    
    async def send_otp(self, phone: str, otp: str, carrier: str = None) -> SMSResult:
        """Send OTP via optimal route"""
        
        # Determine carrier if not provided
        if not carrier:
            np_result = await self.np_lookup.lookup(phone)
            carrier = np_result.carrier
        
        # Route to carrier
        endpoint = self.CARRIER_ENDPOINTS[carrier]["submit_http"]
        
        message = f"Tu código GobernanzaRD: {otp}. Válido 5 min. No compartas."
        
        async with aiohttp.ClientSession() as session:
            resp = await session.post(
                endpoint,
                headers={"Authorization": f"Bearer {self.carrier_tokens[carrier]}"},
                json={
                    "to": self._normalize(phone),
                    "text": message,
                    "sender_id": "GOB-RD",
                    "priority": "high",
                    "dlr_url": self.config.dlr_webhook_url
                }
            )
            return SMSResult.from_response(resp)
```

### 4.2 Aggregator SMS APIs (Faster Setup)

```python
# For rapid deployment, use aggregators with DR coverage
SMS_AGGREGATORS = {
    "twilio": {
        "api": "https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json",
        "dr_coverage": True,
        "dr_short_codes": False,  # Only long codes
        "cost_per_sms": 0.0075,  # USD
        "features": ["OTP", "WhatsApp", "Voice", "Verify API"]
    },
    "vonage": {
        "api": "https://rest.nexmo.com/sms/json",
        "dr_coverage": True,
        "dr_short_codes": True,  # Via local partner
        "cost_per_sms": 0.0065,
        "features": ["OTP", "WhatsApp", "Voice", "Number Insight"]
    },
    "plivo": {
        "api": "https://api.plivo.com/v1/Account/{auth_id}/Message/",
        "dr_coverage": True,
        "dr_short_codes": False,
        "cost_per_sms": 0.0055,
        "features": ["OTP", "Voice", "Verify API"]
    },
    "messagebird": {
        "api": "https://rest.messagebird.com/messages",
        "dr_coverage": True,
        "dr_short_codes": True,
        "cost_per_sms": 0.0060,
        "features": ["OTP", "WhatsApp", "Voice", "Flow Builder"]
    },
    "local_aggregators": {
        "datacenter_do": {"contact": "ventas@datacenter.do", "short_codes": True},
        "tecnosol": {"contact": "comercial@tecnosol.com.do", "short_codes": True},
        "smsmasivos_do": {"contact": "info@smsmasivos.com.do", "short_codes": True}
    }
}
```

### 4.3 OTP Best Practices for DR

```python
class DROptimizedOTP:
    """
    DR-specific OTP optimization
    - High WhatsApp penetration (90%+ smartphones)
    - USSD for feature phones
    - Carrier-specific delivery optimization
    """
    
    CHANNEL_PRIORITY = [
        "whatsapp",      # 90%+ reach, rich media, free for user
        "sms",           # Universal fallback
        "ussd",          # Feature phones, no internet
        "voice_call",    # Accessibility, elderly
        "email"          # Backup
    ]
    
    async def send_otp_multi_channel(self, user: User, otp: str) -> OTPSendResult:
        """Send via best available channel based on user profile"""
        
        # 1. Check WhatsApp opt-in + phone verified
        if user.whatsapp_verified and user.whatsapp_opt_in:
            result = await self.whatsapp.send_otp(user.phone, otp)
            if result.success:
                return OTPSendResult(channel="whatsapp", **result)
        
        # 2. SMS via carrier-optimized route
        np = await self.np_lookup.lookup(user.phone)
        result = await self.sms_gateway.send_otp(user.phone, otp, np.carrier)
        if result.success:
            return OTPSendResult(channel="sms", carrier=np.carrier, **result)
        
        # 3. USSD push (if user on feature phone profile)
        if user.device_type == "feature":
            result = await self.ussd.push_otp(user.phone, otp)
            if result.success:
                return OTPSendResult(channel="ussd", **result)
        
        # 4. Voice call
        result = await self.voice.call_otp(user.phone, otp)
        return OTPSendResult(channel="voice", **result)
```

---

## 5. WHATSAPP BUSINESS API (CRITICAL FOR DR)

### 5.1 DR WhatsApp Landscape
- **Penetration**: 90%+ of smartphone users
- **Primary communication**: Personal, business, government
- **WhatsApp Business API**: Required for automated messaging

### 5.2 BSP (Business Solution Providers) with DR Support

| BSP | DR Carrier Direct | Setup Time | Cost/Conversation | Features |
|-----|-------------------|------------|-------------------|----------|
| **Twilio** | Yes (Claro, Altice) | 1-2 weeks | $0.005-0.015 | Full API, Flow Builder |
| **Vonage** | Yes | 1-2 weeks | $0.005-0.012 | Messages API, Verify |
| **MessageBird** | Yes | 1 week | $0.004-0.010 | Flow Builder, CDP |
| **Gupshup** | Yes | 3-5 days | $0.003-0.008 | Bot builder, CRM |
| **WATI** | Yes | 2-3 days | $0.004-0.009 | Team inbox, Broadcast |
| **Local: ChatBots.do** | Yes | 1 week | Negotiated | Local support, Spanish |

### 5.3 WhatsApp Integration for Gobernanza

```python
class GobernanzaWhatsApp:
    """
    WhatsApp Business API for:
    - OTP delivery
    - Merit notifications
    - Quest reminders
    - Veeduría alerts
    - Payment confirmations
    - Document delivery (PDF certificates)
    """
    
    TEMPLATES = {
        "otp": {
            "name": "gobernanza_otp",
            "language": "es",
            "components": [
                {"type": "body", "text": "Tu código GobernanzaRD: {{1}}. Válido 5 min. No compartas."}
            ]
        },
        "merit_threshold": {
            "name": "merit_threshold_reached",
            "language": "es",
            "components": [
                {"type": "header", "text": "🏆 ¡Nuevo beneficio desbloqueado!"},
                {"type": "body", "text": "Has alcanzado {{1}} méritos. Ahora calificas para: {{2}}. Ver detalles: {{3}}"},
                {"type": "button", "sub_type": "url", "text": "Ver beneficios", "url": "{{4}}"}
            ]
        },
        "quest_reminder": {
            "name": "quest_visit_reminder",
            "language": "es",
            "components": [
                {"type": "header", "text": "🚶 Visita Quest programada"},
                {"type": "body", "text": "Mañana visitarás el sector {{1}}. Hogar asignado: {{2}}. Confirma: {{3}}"},
                {"type": "button", "sub_type": "quick_reply", "text": "Confirmar", "payload": "quest_confirm_{{1}}"},
                {"type": "button", "sub_type": "quick_reply", "text": "Reprogramar", "payload": "quest_reschedule_{{1}}"}
            ]
        },
        "payment_confirmation": {
            "name": "payment_confirmed",
            "language": "es",
            "components": [
                {"type": "header", "text": "✅ Pago confirmado"},
                {"type": "body", "text": "Pago de {{1}} por {{2}} procesado. Trace ID: {{3}}. Méritos ganados: +{{4}}"},
                {"type": "button", "sub_type": "url", "text": "Ver recibo", "url": "{{5}}"}
            ]
        },
        "veeduria_alert": {
            "name": "veeduria_new_report",
            "language": "es",
            "components": [
                {"type": "header", "text": "📋 Nueva veeduría en tu zona"},
                {"type": "body", "text": "Reporte #{1} en {{2}}. Tipo: {{3}}. ¿Deseas apoyar?"},
                {"type": "button", "sub_type": "quick_reply", "text": "Apoyar", "payload": "veeduria_support_{{1}}"},
                {"type": "button", "sub_type": "quick_reply", "text": "Ver detalles", "payload": "veeduria_view_{{1}}"}
            ]
        }
    }
    
    async def send_template(self, phone: str, template_name: str, params: List[str]) -> WAResult:
        """Send templated message (required for outbound)"""
        
        # Normalize phone
        normalized = self._normalize_for_whatsapp(phone)
        
        # Send via BSP (Twilio example)
        async with aiohttp.ClientSession() as session:
            resp = await session.post(
                f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json",
                auth=aiohttp.BasicAuth(self.account_sid, self.auth_token),
                data={
                    "From": f"whatsapp:{self.whatsapp_number}",
                    "To": f"whatsapp:{normalized}",
                    "ContentSid": self.TEMPLATES[template_name]["content_sid"],
                    "ContentVariables": json.dumps({str(i+1): v for i, v in enumerate(params)})
                }
            )
        return WAResult.from_response(resp)
```

### 5.4 WhatsApp Opt-In Flow (Required by Meta)

```python
# User must explicitly opt-in for each notification type
OPT_IN_FLOWS = {
    "qr_code": "Scan QR at government office → Opens WhatsApp → Pre-filled 'INSCRIBIR'",
    "web_form": "Checkbox on Gobernanza portal: 'Recibir notificaciones por WhatsApp'",
    "ussd": "*GOB# → Option 3 → Enter WhatsApp number → Confirm",
    "call_center": "Agent verbal consent → SMS with opt-in link",
    "in_person": "Quest visitor explains → User sends 'INICIAR' to short code"
}
```

---

## 6. USSD INTEGRATION (FEATURE PHONES & UNBANKED)

### 6.1 USSD Gateway Setup

```python
class DRUSSDGateway:
    """
    USSD for: Feature phones, no internet, elderly, rural
    Codes: *GOB# (*462#) or carrier-specific
    """
    
    USSD_CODES = {
        "claro": "*462#",      # *GOB#
        "altice": "*462#",
        "viva": "*462#",
        "universal": "*462#"   # If INDOTEL assigns universal code
    }
    
    MENU_TREE = {
        "main": {
            "text": "GOBIERNO RD\n1. Consultar méritos\n2. Pagar servicios\n3. Vivienda\n4. Quest/Visitas\n5. Veeduría\n6. Alertas\n0. Salir",
            "options": {
                "1": "merits_menu",
                "2": "payments_menu",
                "3": "housing_menu",
                "4": "quest_menu",
                "5": "veeduria_menu",
                "6": "alerts_menu"
            }
        },
        "merits_menu": {
            "text": "TUS MÉRITOS\nTotal: {{merits}}\nNivel: {{level}}\n1. Ver detalles\n2. Beneficios disponibles\n3. Historial\n0. Volver",
            "options": {"1": "merits_detail", "2": "benefits", "3": "merits_history"}
        },
        "payments_menu": {
            "text": "PAGAR SERVICIOS\n1. Luz (EDE)\n2. Agua (CORAASAN/CAASD)\n3. BonoGas/BonoLuz\n4. Ver deudas\n0. Volver",
            "options": {"1": "pay_ede", "2": "pay_water", "3": "pay_bonos", "4": "view_debts"}
        }
    }
    
    async def handle_request(self, request: USSDRequest) -> USSDResponse:
        """Process USSD session"""
        
        session = await self.get_session(request.session_id, request.phone)
        
        # Identify carrier
        np = await self.np_lookup.lookup(request.phone)
        
        # Route to menu handler
        handler = getattr(self, f"handle_{session.current_menu}")
        return await handler(session, request.input, np.carrier)
```

### 6.2 USSD Carrier Integration

| Carrier | USSD Gateway | Protocol | Setup |
|---------|--------------|----------|-------|
| **Claro** | MAP/CAMEL | SMPP/HTTP | Enterprise contract |
| **Altice** | MAP/CAMEL | SMPP/HTTP | Enterprise contract |
| **Viva** | MAP/CAMEL | SMPP | Enterprise contract |
| **Aggregator** | Cellcast, MobiWeb, Local | HTTP/SMPP | Faster setup |

---

## 7. KYC & SIM REGISTRATION VERIFICATION

### 7.1 DR SIM Registration Law
- **Law**: Ley 153-13 (Registro de Usuarios de Telefonía Móvil)
- **Requirement**: All SIMs registered with Cédula + biometrics
- **Database**: INDOTEL central registry, accessible to carriers
- **Verification**: Carriers can verify identity ↔ SIM linkage

### 7.2 Carrier KYC API

```python
class DRCarrierKYC:
    """
    Verify: Phone number belongs to Cédula holder
    Used for: Identity escalation (Level 1 → Level 2)
    """
    
    async def verify_sim_ownership(self, phone: str, cedula: str) -> KYCResult:
        """Check if SIM registered to Cédula"""
        
        np = await self.np_lookup.lookup(phone)
        carrier = np.carrier
        
        # Call carrier KYC API
        endpoint = self.CARRIER_KYC_ENDPOINTS[carrier]
        
        async with aiohttp.ClientSession() as session:
            resp = await session.post(
                endpoint,
                headers={"Authorization": f"Bearer {self.carrier_tokens[carrier]}"},
                json={
                    "phone": self._normalize(phone),
                    "cedula": cedula,
                    "requestor": "GOBIERNO_RD",
                    "purpose": "IDENTITY_VERIFICATION"
                }
            )
        
        data = await resp.json()
        
        return KYCResult(
            match=data["match"],  # True/False
            registered_name=data.get("registered_name"),
            registered_cedula=data.get("registered_cedula"),
            registration_date=data.get("registration_date"),
            carrier=carrier,
            confidence=data.get("confidence", 1.0)  # Biometric match score
        )
```

---

## 8. VOICE & IVR INTEGRATION

### 8.1 Voice API Providers (DR Coverage)

| Provider | DR DID Numbers | IVR | Recording | TTS (Spanish) | Cost/min |
|----------|----------------|-----|-----------|---------------|----------|
| **Twilio** | Yes (809, 829, 849) | Yes | Yes | Yes (Neural) | $0.013 |
| **Vonage** | Yes | Yes | Yes | Yes | $0.011 |
| **Plivo** | Yes | Yes | Yes | Yes | $0.009 |
| **SignalWire** | Yes | Yes | Yes | Yes | $0.008 |
| **Local: Voz.do** | Yes | Yes | Yes | Yes | Negotiated |

### 8.2 IVR Flow for Gobernanza

```python
class GobernanzaIVR:
    """
    Automated phone support for:
    - Merit balance check
    - Payment status
    - Quest schedule
    - Emergency alerts
    - Language: Spanish + Haitian Creole
    """
    
    IVR_TREE = {
        "welcome": {
            "prompt": "Bienvenido a Gobernanza RD. Para español presione 1. Pou Kreyòl preze 2.",
            "options": {"1": "main_es", "2": "main_ht"}
        },
        "main_es": {
            "prompt": "Menú principal. 1. Méritos. 2. Pagos. 3. Vivienda. 4. Quest. 5. Veeduría. 6. Hablar con agente. 0. Repetir.",
            "options": {
                "1": "merits_check",
                "2": "payments_status",
                "3": "housing_status",
                "4": "quest_schedule",
                "5": "veeduria_menu",
                "6": "transfer_agent"
            }
        },
        "merits_check": {
            "prompt": "Tus méritos actuales: {{merits}}. Nivel: {{level}}. 1. Detalles. 2. Beneficios. 3. Historial. * Volver.",
            "action": "fetch_merits"
        }
    }
```

---

## 9. EMERGENCY ALERT SYSTEMS (CELL BROADCAST)

### 9.1 Cell Broadcast (CBS) / EU-Alert / CMAS

```python
class DREmergencyAlert:
    """
    Cell Broadcast for: Hurricanes, floods, earthquakes, national alerts
    Works on ALL phones (smart + feature), no app, no internet, no opt-in
    """
    
    # Requires coordination with INDOTEL + COE (Centro de Operaciones de Emergencia)
    # Carriers broadcast to specific cell towers (geotargeted)
    
    ALERT_CHANNELS = {
        "cell_broadcast": {
            "coverage": "100% phones",
            "latency": "< 10 seconds",
            "geotargeting": "Cell tower level",
            "requires_internet": False,
            "requires_app": False,
            "carriers": ["claro", "altice", "viva"]
        },
        "sms_broadcast": {
            "coverage": "100% phones",
            "latency": "< 5 minutes",
            "geotargeting": "Number range / NP database",
            "requires_internet": False,
            "carriers": ["claro", "altice", "viva"]
        },
        "whatsapp_broadcast": {
            "coverage": "90% smartphones",
            "latency": "< 30 seconds",
            "rich_media": True,
            "requires_internet": True,
            "requires_opt_in": True
        },
        "app_push": {
            "coverage": "App users",
            "latency": "< 5 seconds",
            "rich_media": True,
            "requires_internet": True
        }
    }
```

---

## 10. INTEGRATION ARCHITECTURE FOR GOBERNANZA

### 10.1 Unified Communication Router

```python
class DRCommunicationRouter:
    """
    Routes messages to optimal channel based on:
    - User profile (device, preferences, opt-ins)
    - Message type (OTP, alert, notification, interactive)
    - Carrier (for SMS/USSD optimization)
    - Cost optimization
    """
    
    async def route_message(self, user: User, message: Message) -> RouteResult:
        
        # Emergency → All channels simultaneously
        if message.priority == "emergency":
            return await self._broadcast_all_channels(user, message)
        
        # OTP → Best verified channel
        if message.type == "otp":
            return await self._route_otp(user, message)
        
        # Interactive → WhatsApp if opted in, else SMS/USSD
        if message.interactive:
            if user.whatsapp_opt_in and user.whatsapp_verified:
                return RouteResult(channel="whatsapp", provider=self.whatsapp_bsp)
            elif user.device_type == "feature":
                return RouteResult(channel="ussd", carrier=user.carrier)
            else:
                return RouteResult(channel="sms", carrier=user.carrier)
        
        # Notification → WhatsApp > App Push > SMS
        if user.whatsapp_opt_in:
            return RouteResult(channel="whatsapp")
        elif user.app_push_token:
            return RouteResult(channel="push")
        else:
            return RouteResult(channel="sms", carrier=user.carrier)
```

### 10.2 User Profile Enrichment (On Registration)

```python
async def enrich_user_profile(phone: str, cedula: str = None) -> UserProfile:
    """Build complete communication profile"""
    
    # 1. Number portability lookup
    np = await np_lookup.lookup(phone)
    
    # 2. KYC verification (if cedula provided)
    kyc = None
    if cedula:
        kyc = await carrier_kyc.verify_sim_ownership(phone, cedula)
    
    # 3. WhatsApp check
    wa_status = await whatsapp_bsp.check_number(phone)
    
    # 4. Device detection (via user agent / last interaction)
    device_type = await detect_device_type(phone)
    
    return UserProfile(
        phone=phone,
        carrier=np.carrier,
        carrier_verified=np.status == "active",
        kyc_verified=kyc.match if kyc else False,
        whatsapp_available=wa_status.available,
        whatsapp_verified=wa_status.verified,
        device_type=device_type,  # "smartphone" | "feature"
        preferred_language="es",  # or "ht" for Haitian Creole
        opt_ins=await get_user_opt_ins(phone)
    )
```

---

## 11. COST ESTIMATES (MONTHLY, 1M USERS)

| Channel | Volume | Unit Cost | Monthly Cost | Notes |
|---------|--------|-----------|--------------|-------|
| **WhatsApp (session)** | 500K | $0.005 | $2,500 | Template messages |
| **WhatsApp (template)** | 200K | $0.012 | $2,400 | Outbound notifications |
| **SMS (aggregator)** | 300K | $0.006 | $1,800 | OTP + fallback |
| **SMS (direct carrier)** | 200K | $0.003 | $600 | Requires enterprise contract |
| **USSD sessions** | 50K | $0.010 | $500 | Feature phone users |
| **Voice IVR** | 20K min | $0.010 | $200 | Automated support |
| **Cell Broadcast** | 10 alerts | Fixed | $0 | COE/INDOTEL coordinated |
| **Number Lookup (NP)** | 100K | $0.004 | $400 | Cache reduces by 80% |
| **KYC Verification** | 10K | $0.050 | $500 | Carrier API calls |
| **Total** | | | **~$8,900/mo** | Scales with usage |

---

## 12. REGULATORY & COMPLIANCE

### 12.1 Key Regulations

| Regulation | Authority | Requirement |
|------------|-----------|-------------|
| **Ley 153-13** | INDOTEL | SIM registration with Cédula + biometrics |
| **Ley 172-13** | INDOTEL | Data protection, consent for communications |
| **Resolución 001-2020** | INDOTEL | Spam/SMS marketing regulations (opt-in required) |
| **Ley 358-05** | PROCONSUMIDOR | Consumer rights, transparent pricing |
| **Norma ISO 27001** | INDOTEL | Information security for telecom data |

### 12.2 Compliance Checklist

```python
COMPLIANCE_REQUIREMENTS = {
    "opt_in_management": {
        "whatsapp": "Explicit opt-in per template category (Meta policy)",
        "sms_marketing": "Written/digital consent (INDOTEL Res 001-2020)",
        "ussd": "Implicit via session initiation",
        "voice": "Verbal consent recorded"
    },
    "data_protection": {
        "pii_encryption": "AES-256 at rest, TLS 1.3 in transit",
        "phone_hashing": "SHA-256 with salt for logs",
        "retention": "Communication logs: 2 years. KYC: 5 years.",
        "deletion": "User can request deletion (Ley 172-13 Art 14)"
    },
    "carrier_contracts": {
        "sla": "99.9% uptime, <5s SMS latency, <10s WhatsApp",
        "data_sovereignty": "Data stays in DR",
        "audit_rights": "Government can audit carrier handling"
    }
}
```

---

## 13. IMPLEMENTATION ROADMAP

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **1. Foundation** | 2 weeks | NP lookup integration, carrier KYC contracts, WhatsApp BSP selection |
| **2. Core Channels** | 3 weeks | SMS gateway (aggregator + direct), WhatsApp templates approved, USSD menu |
| **3. Intelligence** | 2 weeks | User profile enrichment, channel routing, cost optimization |
| **4. Advanced** | 2 weeks | IVR, Cell Broadcast integration, emergency alerts |
| **5. Compliance** | 1 week | Opt-in flows, data protection audit, carrier SLA monitoring |
| **6. Testing** | 2 weeks | Load test (100K msgs/hr), failover, DR-specific scenarios |

---

## 14. KEY CONTACTS & RESOURCES

| Entity | Contact | Purpose |
|--------|---------|---------|
| **INDOTEL** | regulacion@indotel.gob.do | NP database access, universal short code, regulations |
| **COE** | alertas@coe.gob.do | Cell Broadcast coordination, emergency protocols |
| **Claro Empresas** | empresas@claro.com.do | Direct SMS/USSD/KYC/API contracts |
| **Altice Corporativo** | corporativo@altice.com.do | Direct SMS/USSD/KYC/API contracts |
| **Viva Empresas** | empresas@viva.com.do | Direct SMS/USSD/KYC/API contracts |
| **Banco Central** | pagos@bancentral.gov.do | Payment system coordination, QR standard |

---

*File: F:\managements\dr_telecom_infrastructure.md*
*Version: 1.0 | Date: 2026-11-10*
*Sources: INDOTEL regulations, carrier public docs, GSMA DR market data, Twilio/Vonage/Plivo coverage maps, Meta WhatsApp BSP directory, local aggregator interviews*