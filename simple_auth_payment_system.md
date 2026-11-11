# Simplified Authentication & Traceability System
## Temporary Email Login + Automated Source Tracing + Fraud Prevention
### For Dominican Republic Governance Platform

---

## 1. DESIGN PRINCIPLES

| Principle | Implementation |
|-----------|----------------|
| **Zero-friction entry** | Magic link via temporary email, no password |
| **Full traceability** | Every action cryptographically linked to source identity |
| **Fraud prevention** | Device fingerprinting + behavioral analysis + merit-gated escalation |
| **Privacy by design** | Temporary email expires, real identity only revealed on merit threshold |
| **Progressive verification** | Anonymous → Verified → Trusted → Authorized |

---

## 2. TEMPORARY EMAIL AUTHENTICATION SYSTEM

### 2.1 Architecture

```python
# Core Components
class TempEmailAuthSystem:
    """
    Flow:
    1. User enters any email (temp or real)
    2. System sends magic link (JWT, 15-min expiry)
    3. Click → Creates session + device fingerprint
    4. Progressive identity revelation based on merit/actions
    """
    
    def __init__(self, config, services):
        self.email_provider = TempEmailProvider(config)
        self.device_fingerprinter = DeviceFingerprinter()
        self.merit_service = services.merit
        self.trace_logger = TraceLogger()
        self.fraud_detector = FraudDetector()
    
    async def request_magic_link(self, email: str, context: AuthContext) -> AuthResult:
        """Request magic link to any email"""
        
        # Validate email format (accept temp domains)
        if not self._is_valid_email(email):
            return AuthResult(success=False, reason="Invalid email format")
        
        # Check rate limits per IP/device
        if await self.fraud_detector.check_rate_limit(context):
            return AuthResult(success=False, reason="Rate limited")
        
        # Generate secure token
        token = self._generate_magic_token(email, context)
        
        # Send via email provider (handles temp email delivery)
        sent = await self.email_provider.send_magic_link(email, token, context.locale)
        
        # Log trace event
        await self.trace_logger.log(TraceEvent(
            event_type="magic_link_requested",
            email_hash=self._hash_email(email),
            token_hash=self._hash_token(token),
            device_fingerprint=context.device_fingerprint,
            ip_hash=self._hash_ip(context.ip),
            timestamp=datetime.utcnow()
        ))
        
        return AuthResult(success=sent, token_id=token.id if sent else None)
    
    async def verify_magic_link(self, token: str, context: AuthContext) -> SessionResult:
        """Verify magic link and create session"""
        
        # Validate token
        payload = self._validate_token(token)
        if not payload:
            return SessionResult(success=False, reason="Invalid/expired link")
        
        # Device fingerprint match
        fp_match = await self.device_fingerprinter.verify(
            payload.device_fingerprint, context.device_fingerprint
        )
        
        # Create progressive session
        session = await self._create_progressive_session(payload, context, fp_match)
        
        # Log verification
        await self.trace_logger.log(TraceEvent(
            event_type="magic_link_verified",
            session_id=session.id,
            email_hash=self._hash_email(payload.email),
            device_fingerprint=context.device_fingerprint,
            fp_match=fp_match,
            identity_level=session.identity_level,
            timestamp=datetime.utcnow()
        ))
        
        return SessionResult(success=True, session=session)
```

### 2.2 Progressive Identity Levels

```python
class IdentityLevel(Enum):
    ANONYMOUS = 0      # Just clicked magic link, temp email
    EMAIL_VERIFIED = 1 # Verified email access (any email)
    MERIT_LINKED = 2   # Linked to merit profile (cedula validated)
    BIOMETRIC = 3      # Biometric verified (JCE)
    TRUSTED = 4        # High merit + clean history + Quest participation
    AUTHORIZED = 5     # Government official / Quest coordinator / Veeduría

IDENTITY_CAPABILITIES = {
    IdentityLevel.ANONYMOUS: {
        "view_public": True,
        "join_discord": True,
        "view_proposals": True,
        "submit_anonymous_feedback": True
    },
    IdentityLevel.EMAIL_VERIFIED: {
        **IDENTITY_CAPABILITIES[IdentityLevel.ANONYMOUS],
        "vote_proposals": True,           # Weight: 1.0
        "report_issues": True,
        "join_quest_waitlist": True
    },
    IdentityLevel.MERIT_LINKED: {
        **IDENTITY_CAPABILITIES[IdentityLevel.EMAIL_VERIFIED],
        "vote_proposals": True,           # Weight: merit-based (1.5-5.0)
        "apply_housing": True,
        "request_utility_payment": True,
        "file_veeduria_report": True,
        "access_merit_dashboard": True
    },
    IdentityLevel.BIOMETRIC: {
        **IDENTITY_CAPABILITIES[IdentityLevel.MERIT_LINKED],
        "sign_contracts": True,
        "delegate_vote": True,
        "access_sensitive_data": True
    },
    IdentityLevel.TRUSTED: {
        **IDENTITY_CAPABILITIES[IdentityLevel.BIOMETRIC],
        "moderate_discord": True,
        "validate_quest_visits": True,
        "approve_small_payments": True
    },
    IdentityLevel.AUTHORIZED: {
        **IDENTITY_CAPABILITIES[IdentityLevel.TRUSTED],
        "execute_fund_transfers": True,
        "assign_quest_territories": True,
        "override_alerts": True,
        "manage_personnel": True
    }
}
```

### 2.3 Temporary Email Provider Integration

```python
class TempEmailProvider:
    """
    Supports: 10minutemail, GuerrillaMail, TempMail, custom domains
    Also accepts real emails (Gmail, Outlook, Yahoo, etc.)
    """
    
    TEMP_DOMAINS = {
        "10minutemail.com", "10minutemail.net", "guerrillamail.com",
        "tempmail.com", "temp-mail.org", "fakeinbox.com",
        "throwawaymail.com", "yopmail.com", "mailinator.com",
        "trashmail.com", "getnada.com", "dispostable.com"
    }
    
    async def send_magic_link(self, email: str, token: MagicToken, locale: str) -> bool:
        """Send magic link - works with temp emails via SMTP/API"""
        
        domain = email.split("@")[1].lower()
        is_temp = domain in self.TEMP_DOMAINS
        
        if is_temp:
            # Temp emails: use specialized delivery
            return await self._send_to_temp_email(email, token, locale)
        else:
            # Real emails: standard SMTP/SendGrid
            return await self._send_standard_email(email, token, locale)
    
    async def _send_to_temp_email(self, email: str, token: MagicToken, locale: str) -> bool:
        """Special handling for temp email services"""
        # Some temp services have APIs, others need polling
        # We use a pool of relay addresses
        pass
```

### 2.4 Automated Source Tracing (Anti-Fraud Core)

```python
class TraceLogger:
    """
    Immutable audit trail linking every action to source
    Uses append-only log with cryptographic chaining
    """
    
    def __init__(self, db_pool, encryption_key):
        self.db = db_pool
        self.chain = HashChain(encryption_key)
    
    async def log(self, event: TraceEvent):
        """Log event with cryptographic link to previous"""
        
        # Get previous hash
        prev_hash = await self._get_latest_hash()
        
        # Create chained record
        record = TraceRecord(
            event=event,
            previous_hash=prev_hash,
            hash=self.chain.compute_hash(event, prev_hash),
            sequence=await self._get_next_sequence()
        )
        
        # Store immutably
        await self.db.execute("""
            INSERT INTO trace_log (sequence, event_type, event_data, previous_hash, hash, timestamp)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, record.sequence, event.event_type, event.to_json(), 
             record.previous_hash, record.hash, event.timestamp)
        
        # Also stream to real-time fraud detector
        await self.fraud_detector.ingest(event)
    
    async def trace_action_to_source(self, action_id: str) -> TracePath:
        """Trace any action back to original identity"""
        
        path = []
        current = await self._get_event(action_id)
        
        while current:
            path.append(current)
            if current.previous_hash == "genesis":
                break
            current = await self._get_event_by_hash(current.previous_hash)
        
        return TracePath(
            action_id=action_id,
            chain=path,
            root_identity=await self._resolve_root_identity(path),
            integrity_verified=self._verify_chain(path)
        )

class FraudDetector:
    """
    Real-time fraud detection using:
    - Device fingerprinting
    - Behavioral analysis
    - Merit-gated risk scoring
    - Cross-reference with JCE/merit data
    """
    
    RISK_FACTORS = {
        "new_device": 0.3,
        "new_ip": 0.2,
        "temp_email": 0.15,
        "velocity_anomaly": 0.4,
        "geographic_impossible": 0.5,
        "merit_mismatch": 0.35,
        "behavioral_deviation": 0.3,
        "known_fraud_pattern": 0.6
    }
    
    async def assess_risk(self, session: Session, action: Action) -> RiskScore:
        """Calculate real-time risk score"""
        
        score = 0.0
        factors = []
        
        # Device analysis
        if not await self._is_known_device(session.device_fingerprint):
            score += self.RISK_FACTORS["new_device"]
            factors.append("new_device")
        
        # IP analysis
        if await self._is_suspicious_ip(session.ip):
            score += self.RISK_FACTORS["new_ip"]
            factors.append("suspicious_ip")
        
        # Temp email check
        if await self._is_temp_email(session.email):
            score += self.RISK_FACTORS["temp_email"]
            factors.append("temp_email")
        
        # Velocity check
        if await self._check_velocity_anomaly(session.id, action.type):
            score += self.RISK_FACTORS["velocity_anomaly"]
            factors.append("velocity_anomaly")
        
        # Merit mismatch (action requires higher identity than session has)
        required = IDENTITY_CAPABILITIES.get(action.required_level, {})
        if session.identity_level < action.required_level:
            score += self.RISK_FACTORS["merit_mismatch"]
            factors.append("identity_escalation_attempt")
        
        # Behavioral analysis
        if await self._detect_behavioral_deviation(session, action):
            score += self.RISK_FACTORS["behavioral_deviation"]
            factors.append("behavioral_deviation")
        
        return RiskScore(
            score=min(score, 1.0),
            factors=factors,
            recommended_action=self._get_recommended_action(score)
        )
    
    def _get_recommended_action(self, score: float) -> FraudAction:
        if score < 0.3: return FraudAction.ALLOW
        if score < 0.5: return FraudAction.CHALLENGE  # Additional verification
        if score < 0.7: return FraudAction.REQUIRE_MERIT_LINK  # Must link cedula
        if score < 0.9: return FraudAction.REQUIRE_BIOMETRIC  # JCE verification
        return FraudAction.BLOCK_AND_INVESTIGATE
```

---

## 3. SIMPLIFIED PAYMENT SYSTEM

### 3.1 Design: Minimal Information, Maximum Automation

```python
class SimplePaymentSystem:
    """
    Philosophy: User provides ONLY what's absolutely necessary
    Everything else auto-filled from merit profile / government APIs
    """
    
    PAYMENT_TYPES = {
        "utility_electricity": {"required": ["account_number"], "auto": ["amount", "due_date", "cedula", "name"]},
        "utility_water": {"required": ["account_number"], "auto": ["amount", "due_date", "cedula", "name"]},
        "housing_subsidy": {"required": ["project_id"], "auto": ["amount", "beneficiary", "bank_details"]},
        "merit_reward": {"required": [], "auto": ["amount", "recipient", "reason"]},
        "quest_stipend": {"required": [], "auto": ["amount", "quester", "period"]},
        "mutual_aid": {"required": ["recipient_id", "category"], "auto": ["sender", "max_amount"]},
        "emergency_relief": {"required": ["beneficiary_id"], "auto": ["amount", "items", "delivery"]}
    }
    
    async def initiate_payment(self, user_session: Session, payment_type: str, 
                               provided: Dict) -> PaymentResult:
        """One-click payment with auto-fill"""
        
        # Verify identity level allows this payment
        required_level = self._get_required_level(payment_type)
        if user_session.identity_level < required_level:
            return PaymentResult(success=False, reason="Insufficient identity level")
        
        # Auto-fill from merit profile + government APIs
        auto_filled = await self._auto_fill_payment(payment_type, user_session, provided)
        
        # Validate required fields present
        missing = self._validate_required(payment_type, auto_filled)
        if missing:
            return PaymentResult(success=False, reason=f"Missing: {missing}")
        
        # Fraud check
        risk = await self.fraud_detector.assess_payment_risk(user_session, auto_filled)
        if risk.action == FraudAction.BLOCK_AND_INVESTIGATE:
            return PaymentResult(success=False, reason="Blocked: fraud risk")
        
        # Execute via Central AI Fund
        result = await self.central_ai_fund.execute(auto_filled)
        
        # Trace log
        await self.trace_logger.log(TraceEvent(
            event_type="payment_executed",
            payment_id=result.payment_id,
            session_id=user_session.id,
            amount=auto_filled["amount"],
            type=payment_type,
            auto_filled=list(auto_filled.keys()),
            timestamp=datetime.utcnow()
        ))
        
        return result
```

### 3.2 Auto-Fill Engine (Government API Integration)

```python
class PaymentAutoFillEngine:
    """
    Pulls data from: DGII, SUPÉRATE, ADESS, EDE, CORAASAN, MIVHED, JCE, Banco Central
    Caches for 24h, refreshes on payment initiation
    """
    
    async def auto_fill(self, payment_type: str, session: Session, provided: Dict) -> Dict:
        """Auto-fill all possible fields"""
        
        profile = await self.merit_service.get_profile(session.personnel_id)
        cedula = profile.cedula
        
        filled = {**provided}
        
        # Common auto-fill
        filled.setdefault("cedula", cedula)
        filled.setdefault("nombre_completo", profile.full_name)
        filled.setdefault("telefono", profile.phone)
        filled.setdefault("email", profile.email)
        
        if payment_type == "utility_electricity":
            # Get from EDE APIs
            ede_data = await self.ede_connector.get_account_info(
                provided["account_number"], cedula
            )
            filled.setdefault("monto", ede_data.balance)
            filled.setdefault("fecha_vencimiento", ede_data.due_date)
            filled.setdefault("periodo", ede_data.period)
            
        elif payment_type == "utility_water":
            # Get from CORAASAN/CAASD/INAPA
            water_data = await self.water_connector.get_account_info(
                provided["account_number"], cedula
            )
            filled.setdefault("monto", water_data.balance)
            filled.setdefault("fecha_vencimiento", water_data.due_date)
            
        elif payment_type == "housing_subsidy":
            # Get from MIVHED + ADESS
            mivhed = await self.mivhed_connector.get_subsidy_details(
                provided["project_id"], cedula
            )
            adess = await self.adess_connector.get_bank_details(cedula)
            filled.setdefault("monto", mivhed.amount)
            filled.setdefault("cuenta_bancaria", adess.account)
            filled.setdefault("banco", adess.bank)
            
        elif payment_type == "merit_reward":
            # Fully automatic from merit system
            reward = await self.merit_service.calculate_reward(session.personnel_id)
            filled.setdefault("monto", reward.amount)
            filled.setdefault("concepto", reward.reason)
            filled.setdefault("destinatario_cedula", cedula)
            
        elif payment_type == "quest_stipend":
            # From Quest engine
            quest = await self.quest_engine.get_active_quest(session.personnel_id)
            filled.setdefault("monto", quest.daily_stipend * quest.days_completed)
            filled.setdefault("periodo", f"{quest.start_date} a {quest.end_date}")
            filled.setdefault("territorio", quest.territory_name)
            
        elif payment_type == "mutual_aid":
            # Check sender limits + recipient eligibility
            limits = await self.mutual_aid.get_limits(session.personnel_id)
            filled.setdefault("max_monto", limits.remaining)
            filled.setdefault("categoria_valida", provided["category"] in VALID_CATEGORIES)
            
        elif payment_type == "emergency_relief":
            # From COE + SUPÉRATE
            coe = await self.coe_connector.get_active_emergency(provided["beneficiary_id"])
            filled.setdefault("items", coe.standard_package)
            filled.setdefault("monto_estimado", coe.estimated_value)
            filled.setdefault("entrega", "domicilio" if coe.home_delivery else "centro")
        
        return filled
```

### 3.3 One-Click Payment UI Flow

```python
# Frontend flow (pseudo-code for reference)
PAYMENT_FLOW = {
    "step_1": {
        "user_action": "Clicks 'Pagar Luz' button",
        "system": "Detects identity_level, shows only allowed payment types"
    },
    "step_2": {
        "user_action": "Enters ONLY account number (or selects from saved)",
        "system": "Auto-fills: monto, vencimiento, nombre, cédula, banco"
    },
    "step_3": {
        "user_action": "Reviews auto-filled data (read-only except account)",
        "system": "Shows: '¿Confirmar pago de RD$X,XXX por periodo MM/YYYY?'"
    },
    "step_4": {
        "user_action": "Clicks 'Confirmar' (or biometric if high amount)",
        "system": "Executes via Central AI Fund → EDE API → Trace log"
    },
    "step_5": {
        "user_action": "Receives instant confirmation",
        "system": "Discord/Email notification + Merit update + Trace ID"
    }
}
```

### 3.4 Saved Payment Methods (Minimal Storage)

```python
class SavedPaymentMethod:
    """Store ONLY: account_number, type, nickname, last_used"""
    
    STORED_FIELDS = ["account_number", "payment_type", "nickname", "last_used", "verified"]
    
    # NEVER store: amounts, due dates, full bank details, passwords
    # These are always fetched fresh from government APIs
    
    async def save(self, session: Session, method: PaymentMethodInput) -> SavedMethod:
        # Verify account belongs to user via government API
        verified = await self._verify_account_ownership(
            method.account_number, method.payment_type, session.cedula
        )
        
        if not verified:
            raise ValidationError("Account verification failed")
        
        return await self.db.insert("saved_payment_methods", {
            "personnel_id": session.personnel_id,
            "account_number": method.account_number,
            "payment_type": method.payment_type,
            "nickname": method.nickname or f"{method.payment_type} ***{method.account_number[-4:]}",
            "verified": True,
            "created_at": datetime.utcnow()
        })
```

---

## 4. INTEGRATION WITH EXISTING SYSTEMS

### 4.1 Merit System Integration

```python
# Identity level gates merit capabilities
MERIT_GATES = {
    IdentityLevel.ANONYMOUS: {"max_daily_actions": 5, "can_earn_merits": False},
    IdentityLevel.EMAIL_VERIFIED: {"max_daily_actions": 20, "can_earn_merits": True},
    IdentityLevel.MERIT_LINKED: {"max_daily_actions": 100, "merit_multiplier": 1.0},
    IdentityLevel.BIOMETRIC: {"max_daily_actions": 500, "merit_multiplier": 1.5},
    IdentityLevel.TRUSTED: {"max_daily_actions": 2000, "merit_multiplier": 2.0},
    IdentityLevel.AUTHORIZED: {"max_daily_actions": -1, "merit_multiplier": 3.0}
}

# Payment history builds merit
async def on_payment_completed(payment: PaymentResult, session: Session):
    if payment.type in MERIT_BUILDING_PAYMENTS:
        await merit_service.add_merits(
            session.personnel_id,
            MeritEvent.PAYMENT_RESPONSIBLE,
            base_amount=10 * MERIT_GATES[session.identity_level]["merit_multiplier"]
        )
```

### 4.2 Quest System Integration

```python
# Quest participation requires EMAIL_VERIFIED minimum
# Quest leadership requires MERIT_LINKED
# Quest validation requires TRUSTED

QUEST_IDENTITY_REQUIREMENTS = {
    "join_waitlist": IdentityLevel.EMAIL_VERIFIED,
    "conduct_visit": IdentityLevel.MERIT_LINKED,
    "validate_visits": IdentityLevel.TRUSTED,
    "assign_territory": IdentityLevel.AUTHORIZED
}
```

### 4.3 Central AI Fund Integration

```python
# All payments route through Central AI Fund
# Fund executes via government APIs (EDE, CORAASAN, ADESS, MIVHED)
# Trace log captures: who authorized, what APIs called, result, timestamps

class CentralAIFundPaymentExecutor:
    async def execute(self, payment: AutoFilledPayment) -> PaymentResult:
        # Route to correct API based on type
        executor = self.executors[payment.type]
        
        # Execute with idempotency key
        idempotency_key = f"pay_{payment.type}_{payment.cedula}_{payment.account_number}_{datetime.utcnow().date()}"
        
        result = await executor.execute(payment, idempotency_key)
        
        # Update merit if successful
        if result.success:
            await self.merit_service.record_payment(payment.personnel_id, result)
        
        return result
```

---

## 5. SECURITY & COMPLIANCE

### 5.1 Data Minimization (Ley 172-13)

| Data Type | Stored? | Retention | Encryption |
|-----------|---------|-----------|------------|
| Temp email | Hash only | 30 days | SHA-256 |
| Real email | Encrypted | 2 years | AES-256 |
| Cédula | Tokenized | Permanent | Token vault |
| Device fingerprint | Hashed | 90 days | SHA-256 |
| IP address | Hashed | 30 days | SHA-256 |
| Payment amounts | Encrypted | 7 years | AES-256 |
| Trace logs | Immutable | Permanent | Hash-chained |

### 5.2 Fraud Prevention Layers

```
Layer 1: Rate limiting (IP/device/email)
Layer 2: Device fingerprinting + behavioral baseline
Layer 3: Identity level gating (progressive verification)
Layer 4: Merit-weighted risk scoring
Layer 5: Cross-reference with JCE/DGII/SUPÉRATE
Layer 6: Immutable trace log for forensic analysis
Layer 7: Human review for high-risk (veeduría escalation)
```

---

## 6. API SPECIFICATIONS

### 6.1 Auth Endpoints

```yaml
# POST /auth/magic-link
request:
  email: string
  locale: string (es/en/ht/ja)
  device_fingerprint: string
response:
  success: boolean
  token_id: string (if success)
  expires_in: 900

# POST /auth/verify
request:
  token: string
  device_fingerprint: string
response:
  success: boolean
  session:
    id: string
    identity_level: integer (0-5)
    personnel_id: string (if linked)
    capabilities: string[]
    expires_in: 3600
  trace_id: string

# POST /auth/escalate
request:
  session_id: string
  target_level: integer
  verification: 
    type: "cedula" | "biometric" | "quest" | "veeduria"
    data: object
response:
  success: boolean
  new_level: integer
```

### 6.2 Payment Endpoints

```yaml
# POST /payments/initiate
request:
  session_id: string
  payment_type: string (utility_electricity | utility_water | housing_subsidy | merit_reward | quest_stipend | mutual_aid | emergency_relief)
  provided_fields: object (only user-provided, e.g., {"account_number": "12345"})
response:
  success: boolean
  payment_preview:
    auto_filled: object (all fields including auto-filled)
    requires_confirmation: boolean
    risk_score: float
  confirmation_token: string

# POST /payments/confirm
request:
  confirmation_token: string
  biometric_verification: string (optional, for high amounts)
response:
  success: boolean
  payment_id: string
  trace_id: string
  receipt: object
  merit_earned: integer
```

---

## 7. IMPLEMENTATION ROADMAP

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **1. Core Auth** | 2 weeks | Magic link + temp email + device fingerprint + trace logger |
| **2. Identity Levels** | 1 week | Progressive verification + capability gating |
| **3. Fraud Engine** | 2 weeks | Risk scoring + behavioral analysis + JCE/DGII cross-ref |
| **4. Payment Auto-Fill** | 2 weeks | Government API connectors + auto-fill engine |
| **5. One-Click Payments** | 1 week | Payment flow + Central AI Fund integration |
| **6. Integration** | 1 week | Merit + Quest + Veeduría + Convivencia Limpia |
| **7. Testing & Audit** | 1 week | Pen testing + load testing + compliance audit |

---

*File: F:\managements\simple_auth_payment_system.md*
*Version: 1.0 | Date: 2026-11-10*