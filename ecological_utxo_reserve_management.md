# Ecological UTXO Reserve Management System
## Integrated Compliance, Monitoring & Community Governance Platform

---

## 1. SYSTEM OVERVIEW

### 1.1 Vision
A unified platform for **ecological Bitcoin reserve management** that combines:
- **Hygienic UTXO monitoring** (ecological health metrics for transaction outputs)
- **Japanese regulatory compliance** (FSA/JVCEA standards, Travel Rule, cold wallet mandates)
- **Discord management console** for operational oversight
- **Reddit community governance** for transparent stakeholder participation
- **Wire transfer integration** for fiat⇄BTC reserve operations

### 1.2 Core Principles (from Japanese Agile Governance)
| Principle | Implementation |
|-----------|----------------|
| **Goal-based regulation** | Dynamic compliance targets, not fixed rules |
| **Multi-stakeholder** | Discord ops + Reddit community + Regulatory auditors |
| **Soft law evolution** | Guidelines update via sandbox evidence |
| **Governance by Innovation** | AI/UTXO analytics TO govern reserves |
| **Human-centered** | Ecological health = human financial health |

### 1.3 Architecture Layers (METI 5-Layer Model)
```
┌─────────────────────────────────────────────────────────────────┐
│                    SOCIAL NORMS (Reddit Governance)             │
├─────────────────────────────────────────────────────────────────┤
│                       MARKET (Wire/Fiat Bridge)                 │
├─────────────────────────────────────────────────────────────────┤
│                      RULES (FSA/JVCEA Compliance)               │
├─────────────────────────────────────────────────────────────────┤
│                   ORGANIZATIONAL (Discord Ops Console)          │
├─────────────────────────────────────────────────────────────────┤
│                    TECHNICAL (UTXO Engine + AI)                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. ECOLOGICAL/HYGIENIC UTXO MONITORING ENGINE

### 2.1 UTXO Health Metrics ("Hygienic Meter")

```python
# core/utxo_hygiene.py
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
import hashlib
from datetime import datetime, timedelta

class UTXOHealthGrade(Enum):
    PRISTINE = "pristine"          # >10M sats, single origin, >1yr old
    HEALTHY = "healthy"            # >1M sats, clean history, >6mo old
    STABLE = "stable"              # >100k sats, minor mixing, >1mo old
    FRAGMENTED = "fragmented"      # <100k sats, dust risk
    CONTAMINATED = "contaminated"  # Mixed origins, privacy risk
    TOXIC = "toxic"                # Sanctioned addresses, legal risk

@dataclass
class UTXOHygieneReport:
    utxo_id: str                    # txid:vout
    value_sats: int
    health_grade: UTXOHealthGrade
    ecological_score: float         # 0.0-1.0 composite
    
    # Ecological factors
    age_days: int
    origin_diversity: float         # 0=single, 1=highly mixed
    privacy_score: float            # 0=exposed, 1=private
    spendability_index: float       # Fee-adjusted spendability
    compliance_risk: float          # 0=clean, 1=high risk
    
    # Japanese compliance
    travel_rule_compliant: bool
    cold_wallet_eligible: bool
    jvcea_listed: bool
    
    # Metadata
    labels: List[str]               # User-defined labels
    last_analyzed: datetime
    recommended_action: str         # HOLD, CONSOLIDATE, SPEND, FREEZE, REPORT

class UTXOHygieneAnalyzer:
    """
    Ecological analyzer for UTXO sets.
    Implements Japanese best practices: cold wallet eligibility,
    dust avoidance, privacy preservation, compliance screening.
    """
    
    # Thresholds from COLDCARD best practices + FSA guidance
    DUST_THRESHOLD = 600            # Sats (JVCEA standard)
    ECONOMIC_THRESHOLD = 10_000     # Sats (uneconomical below this at high fees)
    COLD_STORAGE_THRESHOLD = 1_000_000  # 0.01 BTC minimum for cold storage
    CONSOLIDATION_FEE_RATE = 5      # sat/vB - consolidate below this
    
    def __init__(self, 
                 compliance_screener: 'ComplianceScreener',
                 fee_estimator: 'FeeEstimator',
                 label_store: 'LabelStore'):
        self.compliance = compliance_screener
        self.fees = fee_estimator
        self.labels = label_store
    
    def analyze_utxo(self, utxo: UTXO) -> UTXOHygieneReport:
        # 1. Basic metrics
        age = (datetime.now() - utxo.block_time).days
        value = utxo.value_sats
        
        # 2. Origin diversity (privacy/ecological)
        origin_diversity = self._calculate_origin_diversity(utxo)
        
        # 3. Privacy score (coin control readiness)
        privacy_score = self._calculate_privacy_score(utxo, origin_diversity)
        
        # 4. Spendability (fee-adjusted)
        current_fee_rate = self.fees.get_current_rate()
        spendability = self._calculate_spendability(value, current_fee_rate)
        
        # 5. Compliance screening (Japanese Travel Rule + sanctions)
        compliance_risk = self.compliance.screen(utxo)
        travel_rule_ok = self.compliance.check_travel_rule(utxo)
        
        # 6. Cold wallet eligibility (FSA: 95%+ offline)
        cold_eligible = value >= self.COLD_STORAGE_THRESHOLD and compliance_risk < 0.1
        
        # 7. Ecological composite score
        ecological = self._composite_score(
            age=age,
            value=value,
            origin_diversity=origin_diversity,
            privacy=privacy_score,
            spendability=spendability,
            compliance=1 - compliance_risk
        )
        
        # 8. Health grade
        grade = self._determine_grade(ecological, value, compliance_risk, origin_diversity)
        
        # 9. Recommended action
        action = self._recommend_action(grade, value, age, compliance_risk, current_fee_rate)
        
        return UTXOHygieneReport(
            utxo_id=f"{utxo.txid}:{utxo.vout}",
            value_sats=value,
            health_grade=grade,
            ecological_score=ecological,
            age_days=age,
            origin_diversity=origin_diversity,
            privacy_score=privacy_score,
            spendability_index=spendability,
            compliance_risk=compliance_risk,
            travel_rule_compliant=travel_rule_ok,
            cold_wallet_eligible=cold_eligible,
            jvcea_listed=self.compliance.is_jvcea_listed(utxo),
            labels=self.labels.get(utxo.txid, []),
            last_analyzed=datetime.now(),
            recommended_action=action
        )
    
    def analyze_full_wallet(self, utxos: List[UTXO]) -> WalletHygieneReport:
        reports = [self.analyze_utxo(u) for u in utxos]
        
        # Aggregate ecological metrics
        total_value = sum(r.value_sats for r in reports)
        grade_distribution = self._grade_distribution(reports)
        
        # Wallet-level recommendations
        consolidation_candidates = [
            r for r in reports 
            if r.health_grade in [UTXOHealthGrade.FRAGMENTED, UTXOHealthGrade.STABLE]
            and r.value_sats < self.ECONOMIC_THRESHOLD
        ]
        
        freeze_candidates = [
            r for r in reports 
            if r.health_grade == UTXOHealthGrade.TOXIC
        ]
        
        cold_storage_ready = [
            r for r in reports 
            if r.cold_wallet_eligible and r.health_grade in [UTXOHealthGrade.PRISTINE, UTXOHealthGrade.HEALTHY]
        ]
        
        return WalletHygieneReport(
            total_utxos=len(reports),
            total_value_sats=total_value,
            ecological_health=sum(r.ecological_score for r in reports) / len(reports),
            grade_distribution=grade_distribution,
            consolidation_candidates=consolidation_candidates,
            freeze_candidates=freeze_candidates,
            cold_storage_ready=cold_storage_ready,
            compliance_summary=self._compliance_summary(reports),
            generated_at=datetime.now()
        )
```

### 2.2 Ecological Scoring Algorithm

```python
def _composite_score(self, age, value, origin_diversity, privacy, spendability, compliance):
    """
    Weighted ecological score based on Japanese UTXO best practices:
    - Age (20%): Older UTXOs more stable
    - Value (25%): Larger UTXOs more economically viable
    - Origin Diversity (15%): Lower = better privacy
    - Privacy (15%): Coin control readiness
    - Spendability (15%): Fee-adjusted utility
    - Compliance (10%): Regulatory cleanliness
    """
    weights = {
        'age': 0.20,
        'value': 0.25,
        'origin_diversity': 0.15,
        'privacy': 0.15,
        'spendability': 0.15,
        'compliance': 0.10
    }
    
    # Normalize each factor to 0-1
    age_score = min(age / 365, 1.0)                    # Cap at 1 year
    value_score = min(value / 10_000_000, 1.0)         # Cap at 0.1 BTC
    diversity_score = 1 - origin_diversity             # Lower diversity = better
    privacy_score = privacy
    spendability_score = spendability
    compliance_score = compliance
    
    score = (
        weights['age'] * age_score +
        weights['value'] * value_score +
        weights['origin_diversity'] * diversity_score +
        weights['privacy'] * privacy_score +
        weights['spendability'] * spendability_score +
        weights['compliance'] * compliance_score
    )
    
    return round(score, 4)
```

---

## 3. JAPANESE REGULATORY COMPLIANCE ENGINE

### 3.1 FSA/JVCEA Compliance Framework

```python
# compliance/japanese_framework.py
from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from enum import Enum
import asyncio

class ComplianceCategory(Enum):
    # FSA Payment Services Act requirements
    COLD_WALLET_RATIO = "cold_wallet_ratio"           # 95%+ offline
    SEGREGATED_CUSTODY = "segregated_custody"         # User assets separated
    TRAVEL_RULE = "travel_rule"                       # Originator/beneficiary info
    AML_KYC = "aml_kyc"                               # Identity verification
    FINANCIAL_AUDIT = "financial_audit"               # Annual audit + segregation audit
    CYBERSECURITY = "cybersecurity"                   # FSA guidelines compliance
    INSIDER_TRADING = "insider_trading"               # Market integrity
    USER_PROTECTION = "user_protection"               # Disclosure, dispute resolution
    
    # JVCEA Self-Regulatory Rules
    LISTING_STANDARDS = "listing_standards"           # Token listing criteria
    ADVERTISING = "advertising"                       # Marketing restrictions
    LEVERAGE_LIMITS = "leverage_limits"               # Max 2x individual, 4x corp
    STAKING_RULES = "staking_rules"                   # Staking service standards

@dataclass
class ComplianceRule:
    category: ComplianceCategory
    description: str
    threshold: float
    measurement: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    automated_check: bool
    remediation: str

class JapaneseComplianceEngine:
    """
    Implements FSA (金融庁) and JVCEA (日本暗号資産等取引業協会) requirements.
    Based on: 資金決済法, 金商法, 犯罪収益移転防止法, 旅行規則
    """
    
    RULES = [
        ComplianceRule(
            category=ComplianceCategory.COLD_WALLET_RATIO,
            description="95%+ of user crypto assets must be in cold storage",
            threshold=0.95,
            measurement="cold_value / total_user_value",
            severity="CRITICAL",
            automated_check=True,
            remediation="Transfer hot wallet excess to cold storage multisig"
        ),
        ComplianceRule(
            category=ComplianceCategory.SEGREGATED_CUSTODY,
            description="User assets must be segregated from proprietary assets",
            threshold=1.0,
            measurement="segregated_value / total_user_value",
            severity="CRITICAL",
            automated_check=True,
            remediation="Immediate segregation; report to FSA if breached"
        ),
        ComplianceRule(
            category=ComplianceCategory.TRAVEL_RULE,
            description="Travel Rule compliance for VASP-to-VASP transfers >100k JPY",
            threshold=1.0,
            measurement="compliant_transfers / total_vasp_transfers",
            severity="CRITICAL",
            automated_check=True,
            remediation="Reject non-compliant transfers; file SAR if suspicious"
        ),
        ComplianceRule(
            category=ComplianceCategory.AML_KYC,
            description="Enhanced KYC for transactions >300k JPY; ongoing monitoring",
            threshold=1.0,
            measurement="kyc_complete_users / total_users",
            severity="HIGH",
            automated_check=True,
            remediation="Restrict non-KYC accounts; enhanced due diligence"
        ),
        ComplianceRule(
            category=ComplianceCategory.CYBERSECURITY,
            description="FSA Cybersecurity Guidelines: ISMS, incident response, 3rd party risk",
            threshold=0.9,
            measurement="controls_implemented / required_controls",
            severity="HIGH",
            automated_check=False,
            remediation="Quarterly penetration testing; annual ISMS audit"
        ),
    ]
    
    # VASP Whitelist (from bitbank support page)
    APPROVED_VASPS = {
        # Domestic
        "bitbank.cc", "okj.co.jp", "sbivc.co.jp", "gmo-coin.co.jp",
        "bitpoint.co.jp", "bittrade.co.jp", "zaif.jp", "cointrade.cc",
        "btcbox.co.jp", "rakuten-wallet.co.jp", "s-blox.co.jp",
        "coinestate.co.jp", "osl.com", "tokyohash.co.jp", "backseat.co.jp",
        "btm-tech.com", "bitlending.jp", "hashhub-lending.com",
        # International (major)
        "binance.com", "bybit.com", "mexc.com", "bitget.com", "okx.com",
        "kucoin.com", "bitkub.com", "bitrue.com", "maicoin.com",
    }
    
    def __init__(self, 
                 blockchain_analyzer: 'BlockchainAnalyzer',
                 kyc_provider: 'KYCProvider',
                 audit_logger: 'AuditLogger'):
        self.chain = blockchain_analyzer
        self.kyc = kyc_provider
        self.audit = audit_logger
    
    async def screen_utxo(self, utxo: UTXO) -> float:
        """Returns compliance risk score 0.0-1.0"""
        risk_factors = []
        
        # 1. Sanctions screening (OFAC, UN, Japan METI)
        sanctions_risk = await self._check_sanctions(utxo)
        risk_factors.append(("sanctions", sanctions_risk, 0.30))
        
        # 2. Mixer/tumbler association
        mixer_risk = await self._check_mixer_association(utxo)
        risk_factors.append(("mixer", mixer_risk, 0.25))
        
        # 3. Darknet market proximity
        darknet_risk = await self._check_darknet_proximity(utxo)
        risk_factors.append(("darknet", darknet_risk, 0.20))
        
        # 4. Travel Rule compliance (if VASP transfer)
        travel_risk = await self._check_travel_rule_compliance(utxo)
        risk_factors.append(("travel_rule", travel_risk, 0.15))
        
        # 5. JVCEA listed token check
        token_risk = 0.0 if self._is_jvcea_compliant_token(utxo) else 0.1
        risk_factors.append(("token", token_risk, 0.10))
        
        # Weighted composite
        total_risk = sum(score * weight for _, score, weight in risk_factors)
        
        # Audit log
        await self.audit.log_compliance_check(utxo, risk_factors, total_risk)
        
        return min(total_risk, 1.0)
    
    async def verify_cold_wallet_ratio(self, wallet: Wallet) -> ComplianceResult:
        """FSA requirement: 95%+ user assets in cold storage"""
        total_user_value = wallet.get_total_user_value()
        cold_value = wallet.get_cold_storage_value()
        ratio = cold_value / total_user_value if total_user_value > 0 else 1.0
        
        rule = next(r for r in self.RULES if r.category == ComplianceCategory.COLD_WALLET_RATIO)
        
        return ComplianceResult(
            category=rule.category,
            compliant=ratio >= rule.threshold,
            current_value=ratio,
            threshold=rule.threshold,
            severity=rule.severity if ratio < rule.threshold else "OK",
            details=f"Cold: {cold_value:,} sats / Total: {total_user_value:,} sats = {ratio:.2%}"
        )
    
    async def verify_segregated_custody(self, exchange: Exchange) -> ComplianceResult:
        """User assets must be legally and operationally segregated"""
        # Check: separate legal entities, separate wallets, separate accounting
        checks = {
            "legal_segregation": exchange.has_separate_custody_entity,
            "wallet_segregation": exchange.user_wallets_isolated,
            "accounting_segregation": exchange.separate_ledgers,
            "audit_confirmation": exchange.latest_segregation_audit_passed
        }
        
        compliant = all(checks.values())
        
        return ComplianceResult(
            category=ComplianceCategory.SEGREGATED_CUSTODY,
            compliant=compliant,
            current_value=sum(checks.values()) / len(checks),
            threshold=1.0,
            severity="CRITICAL" if not compliant else "OK",
            details=f"Segregation checks: {checks}"
        )
    
    def check_travel_rule(self, utxo: UTXO) -> bool:
        """Check if UTXO originated from Travel Rule compliant VASP"""
        origin_tx = self.chain.get_transaction(utxo.txid)
        if not origin_tx:
            return False
        
        # Check if any input came from approved VASP
        for inp in origin_tx.inputs:
            if inp.address in self.vasp_address_registry:
                vasp = self.vasp_address_registry[inp.address]
                if vasp in self.APPROVED_VASPS:
                    return True
        
        return False
    
    def is_jvcea_listed(self, utxo: UTXO) -> bool:
        """Check if UTXO contains JVCEA-approved tokens only"""
        # For native BTC, always true
        if utxo.asset == "BTC":
            return True
        # For tokens, check JVCEA green list
        return utxo.asset in self.jvcea_green_list
```

### 3.2 Regulatory Reporting Automation

```python
# compliance/reporting.py
class RegulatoryReporter:
    """
    Automated FSA/JVCEA reporting:
    - Monthly: Asset segregation status, cold wallet ratio
    - Quarterly: Cybersecurity posture, incident summary
    - Annual: Financial audit, AML effectiveness, business continuity
    - Ad-hoc: SAR (Suspicious Activity Reports), breach notifications
    """
    
    def __init__(self, compliance_engine: JapaneseComplianceEngine):
        self.compliance = compliance_engine
        self.templates = ReportTemplates()
    
    async def generate_monthly_report(self) -> RegulatoryReport:
        # Cold wallet ratio verification
        cold_wallet = await self.compliance.verify_cold_wallet_ratio(self.wallet)
        
        # Segregation verification
        segregation = await self.compliance.verify_segregated_custody(self.exchange)
        
        # Travel Rule compliance rate
        travel_compliance = await self._calculate_travel_compliance_rate()
        
        # User asset summary
        user_assets = self._summarize_user_assets()
        
        return RegulatoryReport(
            period=ReportPeriod.MONTHLY,
            report_type="FSA_MONTHLY_SUPERVISION",
            cold_wallet_ratio=cold_wallet,
            segregation_status=segregation,
            travel_rule_compliance=travel_compliance,
            user_asset_summary=user_assets,
            generated_at=datetime.now(),
            submitted_to=["FSA", "JVCEA"]
        )
    
    async def generate_sar(self, trigger: SARTrigger) -> SARReport:
        """Suspicious Activity Report for FSA/POLICE"""
        return SARReport(
            trigger=trigger,
            subject=self._identify_subject(trigger),
            transaction_details=self._get_transaction_chain(trigger.utxo),
            risk_assessment=await self.compliance.screen_utxo(trigger.utxo),
            narrative=self._generate_narrative(trigger),
            filed_at=datetime.now(),
            reference_number=self._generate_ref_number()
        )
```

---

## 4. WIRE TRANSFER ⇄ BITCOIN RESERVE BRIDGE

### 4.1 Japanese Exchange Integration

```python
# bridge/japanese_exchange_bridge.py
from dataclasses import dataclass
from typing import Literal
from enum import Enum
import asyncio

class JapaneseExchange(Enum):
    COINCHECK = "coincheck"
    BITBANK = "bitbank"
    SBI_VC_TRADE = "sbivc"
    GMO_COIN = "gmo"
    BITPOINT = "bitpoint"
    BITTRADE = "bittrade"
    ZAIF = "zaif"
    # ... all FSA-registered exchanges

@dataclass
class WireTransferRequest:
    exchange: JapaneseExchange
    direction: Literal["DEPOSIT", "WITHDRAWAL"]
    amount_jpy: int
    amount_btc_sats: Optional[int] = None
    bank_account: BankAccount
    purpose: str  # Required by Japanese exchanges
    travel_rule_info: Optional[TravelRuleInfo] = None

@dataclass
class BankAccount:
    bank_code: str      # 銀行コード (4 digits)
    branch_code: str    # 支店コード (3 digits)
    account_type: Literal["ordinary", "current"]  # 普通/当座
    account_number: str # 7 digits
    account_name: str   # カタカナ名義
    zengin_compatible: bool = True

class JapaneseExchangeBridge:
    """
    Unified interface for Japanese exchange APIs.
    Implements: 銀行振込, クイック入金, ペイジー, コンビニ入金
    Coincheck API: /api/withdraw (JPY出金), /api/send_money (BTC送金)
    """
    
    def __init__(self):
        self.clients = {
            JapaneseExchange.COINCHECK: CoincheckClient(),
            JapaneseExchange.BITBANK: BitbankClient(),
            JapaneseExchange.SBI_VC_TRADE: SBIVCTradeClient(),
            # ... others
        }
        self.compliance = JapaneseComplianceEngine(...)
    
    async def execute_wire_transfer(self, request: WireTransferRequest) -> TransferResult:
        # 1. Compliance pre-check
        if request.direction == "WITHDRAWAL":
            compliance_check = await self.compliance.screen_withdrawal(
                request.amount_btc_sats,
                request.bank_account,
                request.purpose
            )
            if not compliance_check.approved:
                return TransferResult(
                    success=False,
                    error=compliance_check.rejection_reason,
                    sar_required=compliance_check.sar_required
                )
        
        # 2. Execute via exchange API
        client = self.clients[request.exchange]
        
        if request.direction == "DEPOSIT":
            # JPY → Exchange → BTC
            result = await self._deposit_jpy_buy_btc(client, request)
        else:
            # BTC → Exchange → JPY → Bank
            result = await self._sell_btc_withdraw_jpy(client, request)
        
        # 3. Post-execution compliance
        await self._post_transfer_compliance(result, request)
        
        return result
    
    async def _deposit_jpy_buy_btc(self, client, request: WireTransferRequest):
        # Step 1: Initiate JPY deposit (bank transfer)
        deposit = await client.initiate_jpy_deposit(
            amount=request.amount_jpy,
            bank_account=request.bank_account,
            method="bank_transfer"  # or quick_debit, payeasy, convenience_store
        )
        
        # Step 2: Wait for deposit confirmation (polling)
        await self._wait_for_deposit_confirmation(client, deposit.id)
        
        # Step 3: Execute BTC purchase at market/limit
        buy_order = await client.place_order(
            pair="BTC_JPY",
            side="BUY",
            order_type="MARKET",
            amount_jpy=request.amount_jpy
        )
        
        # Step 4: Wait for fill
        fill = await self._wait_for_fill(client, buy_order.id)
        
        # Step 5: Withdraw BTC to cold storage (if reserve policy)
        if self.config.auto_cold_storage:
            withdraw = await client.withdraw_btc(
                address=self.cold_storage_address,
                amount=fill.filled_amount_btc,
                purpose_type="investment"  # Required by Coincheck
            )
        
        return TransferResult(
            success=True,
            transaction_id=fill.id,
            btc_amount=fill.filled_amount_btc,
            jpy_amount=request.amount_jpy,
            exchange_rate=fill.average_price,
            cold_storage_tx=withdraw.id if self.config.auto_cold_storage else None
        )
    
    async def _sell_btc_withdraw_jpy(self, client, request: WireTransferRequest):
        # Step 1: Deposit BTC to exchange (with Travel Rule info)
        btc_deposit = await client.deposit_btc(
            amount_sats=request.amount_btc_sats,
            travel_rule_info=request.travel_rule_info
        )
        await self._wait_for_btc_confirmation(client, btc_deposit.id)
        
        # Step 2: Sell BTC for JPY
        sell_order = await client.place_order(
            pair="BTC_JPY",
            side="SELL",
            order_type="MARKET",
            amount_btc=request.amount_btc_sats / 100_000_000
        )
        fill = await self._wait_for_fill(client, sell_order.id)
        
        # Step 3: Withdraw JPY to bank
        jpy_withdraw = await client.withdraw_jpy(
            amount=fill.filled_amount_jpy,
            bank_account=request.bank_account
        )
        
        return TransferResult(
            success=True,
            transaction_id=sell_order.id,
            btc_amount=request.amount_btc_sats,
            jpy_amount=fill.filled_amount_jpy,
            exchange_rate=fill.average_price,
            bank_withdrawal_id=jpy_withdraw.id
        )
```

### 4.2 Reserve Management Policy Engine

```python
# bridge/reserve_policy.py
class ReservePolicyEngine:
    """
    Manages BTC reserve levels with ecological and compliance constraints.
    Implements: Dynamic rebalancing, stress testing, regulatory buffers.
    """
    
    def __init__(self, 
                 hygiene_analyzer: UTXOHygieneAnalyzer,
                 compliance: JapaneseComplianceEngine,
                 exchange_bridge: JapaneseExchangeBridge):
        self.hygiene = hygiene_analyzer
        self.compliance = compliance
        self.bridge = exchange_bridge
    
    # Policy parameters (tunable via governance)
    MIN_RESERVE_RATIO = 1.0           # 100% backing
    TARGET_COLD_RATIO = 0.98          # 98% in cold (exceeds FSA 95%)
    MAX_HOT_WALLET_SATS = 50_000_000  # 0.5 BTC max hot
    REBALANCE_THRESHOLD = 0.05        # 5% deviation triggers rebalance
    STRESS_TEST_FREQUENCY = timedelta(days=7)
    
    async def assess_reserve_health(self) -> ReserveHealthReport:
        # 1. Current state
        cold_utxos = await self.get_cold_storage_utxos()
        hot_utxos = await self.get_hot_wallet_utxos()
        total_btc = sum(u.value_sats for u in cold_utxos + hot_utxos)
        total_liabilities = await self.get_user_liabilities()
        
        # 2. Ecological health
        cold_report = self.hygiene.analyze_full_wallet(cold_utxos)
        hot_report = self.hygiene.analyze_full_wallet(hot_utxos)
        
        # 3. Compliance health
        cold_wallet_compliance = await self.compliance.verify_cold_wallet_ratio(
            Wallet(cold_utxos)
        )
        segregation_compliance = await self.compliance.verify_segregated_custody(self.exchange)
        
        # 4. Reserve adequacy
        reserve_ratio = total_btc / total_liabilities if total_liabilities > 0 else float('inf')
        cold_ratio = sum(u.value_sats for u in cold_utxos) / total_btc if total_btc > 0 else 1.0
        
        # 5. Action items
        actions = []
        if reserve_ratio < self.MIN_RESERVE_RATIO:
            actions.append(ReserveAction(
                type="URGENT_TOP_UP",
                severity="CRITICAL",
                description=f"Reserve ratio {reserve_ratio:.2%} below minimum {self.MIN_RESERVE_RATIO:.0%}",
                recommended_wire_transfer=self._calculate_top_up_amount(total_liabilities, total_btc)
            ))
        
        if cold_ratio < self.TARGET_COLD_RATIO:
            actions.append(ReserveAction(
                type="COLD_STORAGE_MIGRATION",
                severity="HIGH",
                description=f"Cold ratio {cold_ratio:.2%} below target {self.TARGET_COLD_RATIO:.0%}",
                utxos_to_migrate=self._select_utxos_for_cold_migration(hot_utxos)
            ))
        
        if hot_report.grade_distribution.get(UTXOHealthGrade.TOXIC, 0) > 0:
            actions.append(ReserveAction(
                type="TOXIC_UTXO_QUARANTINE",
                severity="CRITICAL",
                description="Toxic UTXOs detected in hot wallet",
                utxos_to_freeze=hot_report.freeze_candidates
            ))
        
        return ReserveHealthReport(
            total_reserve_btc=total_btc,
            total_liabilities_btc=total_liabilities,
            reserve_ratio=reserve_ratio,
            cold_storage_ratio=cold_ratio,
            cold_ecological_health=cold_report.ecological_health,
            hot_ecological_health=hot_report.ecological_health,
            cold_wallet_compliance=cold_wallet_compliance,
            segregation_compliance=segregation_compliance,
            recommended_actions=actions,
            assessed_at=datetime.now()
        )
    
    async def execute_rebalance(self, health: ReserveHealthReport) -> RebalanceResult:
        """Execute recommended actions via wire transfers and on-chain ops"""
        results = []
        
        for action in health.recommended_actions:
            if action.type == "URGENT_TOP_UP":
                # Wire JPY → Buy BTC → Cold storage
                wire_result = await self.bridge.execute_wire_transfer(WireTransferRequest(
                    exchange=self._select_best_exchange(),
                    direction="DEPOSIT",
                    amount_jpy=action.recommended_wire_transfer,
                    purpose="reserve_top_up",
                    bank_account=self.treasury_bank_account
                ))
                results.append(wire_result)
            
            elif action.type == "COLD_STORAGE_MIGRATION":
                # On-chain: Hot → Cold multisig
                for utxo in action.utxos_to_migrate:
                    tx = await self._create_cold_migration_tx(utxo)
                    results.append(OnChainResult(tx.id, "COLD_MIGRATION", tx.status))
            
            elif action.type == "TOXIC_UTXO_QUARANTINE":
                # Freeze in wallet (label + don't spend)
                for utxo in action.utxos_to_freeze:
                    self.hygiene.labels.add(utxo.txid, ["QUARANTINED", "TOXIC"])
                    results.append(QuarantineResult(utxo.txid, "FROZEN"))
        
        return RebalanceResult(actions_taken=results, completed_at=datetime.now())
```

---

## 5. DISCORD MANAGEMENT CONSOLE

### 5.1 Architecture (Based on Okayu Board / discord-control-center-starter)

```python
# discord/management_console.py
"""
Discord Management Console for Reserve Operations.
Integrates with: UTXO Hygiene, Compliance, Wire Bridge, Reddit Governance.
Stack: discord.py + FastAPI + React Dashboard + PostgreSQL + Redis
"""

import discord
from discord.ext import commands
from fastapi import FastAPI, WebSocket, Depends
from sqlalchemy.orm import Session
import asyncio

class ReserveManagementBot(commands.Bot):
    """Main Discord bot with management capabilities"""
    
    def __init__(self, config: DiscordConfig, services: ServiceContainer):
        intents = discord.Intents.all()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=config.prefix,
            intents=intents,
            help_command=None
        )
        
        self.config = config
        self.services = services
        self.dashboard = DashboardServer(services)
    
    async def setup_hook(self):
        # Load cogs
        await self.load_extension("cogs.reserve_monitor")
        await self.load_extension("cogs.compliance_officer")
        await self.load_extension("cogs.wire_operations")
        await self.load_extension("cogs.governance_bridge")
        await self.load_extension("cogs.emergency_response")
        
        # Start background tasks
        self.loop.create_task(self.hygiene_monitor_loop())
        self.loop.create_task(self.compliance_check_loop())
        self.loop.create_task(self.reserve_rebalance_loop())
        
        # Start dashboard
        await self.dashboard.start()

# Cogs (Modular command groups)

class ReserveMonitorCog(commands.Cog):
    """Real-time UTXO hygiene monitoring"""
    
    @commands.group(name="hygiene", invoke_without_command=True)
    async def hygiene_group(self, ctx):
        """UTXO hygiene commands"""
        report = await self.services.hygiene.get_latest_wallet_report()
        embed = self._create_hygiene_embed(report)
        await ctx.send(embed=embed)
    
    @hygiene_group.command(name="utxo")
    async def hygiene_utxo(self, ctx, txid: str, vout: int):
        """Analyze specific UTXO"""
        utxo = await self.services.chain.get_utxo(txid, vout)
        report = await self.services.hygiene.analyze_utxo(utxo)
        embed = self._create_utxo_embed(report)
        await ctx.send(embed=embed)
    
    @hygiene_group.command(name="consolidate")
    @commands.has_role("Reserve Manager")
    async def hygiene_consolidate(self, ctx, threshold_sats: int = 10000):
        """Consolidate fragmented UTXOs during low fees"""
        fee_rate = await self.services.fees.get_current_rate()
        if fee_rate > 10:
            await ctx.send("⚠️ Fee rate too high for consolidation. Current: {fee_rate} sat/vB")
            return
        
        candidates = await self.services.hygiene.get_consolidation_candidates(threshold_sats)
        if not candidates:
            await ctx.send("✅ No consolidation candidates found.")
            return
        
        # Create consolidation transaction
        tx = await self.services.wallet.create_consolidation_tx(candidates)
        await ctx.send(f"📦 Consolidation transaction created: {tx.txid}")
    
    @hygiene_group.command(name="freeze")
    @commands.has_role("Compliance Officer")
    async def hygiene_freeze(self, ctx, txid: str, vout: int, reason: str):
        """Freeze toxic/suspicious UTXO"""
        await self.services.hygiene.labels.add(txid, ["FROZEN", reason.upper()])
        await self.services.audit.log_freeze(txid, vout, reason, ctx.author.id)
        await ctx.send(f"🔒 UTXO {txid}:{vout} frozen: {reason}")

class ComplianceOfficerCog(commands.Cog):
    """FSA/JVCEA compliance operations"""
    
    @commands.group(name="compliance")
    async def compliance_group(self, ctx):
        pass
    
    @compliance_group.command(name="status")
    async def compliance_status(self, ctx):
        """Full compliance dashboard"""
        results = await self.services.compliance.run_full_check()
        embed = self._create_compliance_embed(results)
        await ctx.send(embed=embed)
    
    @compliance_group.command(name="cold-wallet")
    @commands.has_role("Reserve Manager")
    async def compliance_cold_wallet(self, ctx):
        """Verify cold wallet ratio"""
        result = await self.services.compliance.verify_cold_wallet_ratio(
            self.services.wallet
        )
        embed = self._create_compliance_result_embed(result)
        await ctx.send(embed=embed)
    
    @compliance_group.command(name="segregation")
    @commands.has_role("Compliance Officer")
    async def compliance_segregation(self, ctx):
        """Verify asset segregation"""
        result = await self.services.compliance.verify_segregated_custody(
            self.services.exchange
        )
        embed = self._create_compliance_result_embed(result)
        await ctx.send(embed=embed)
    
    @compliance_group.command(name="travel-rule")
    async def compliance_travel_rule(self, ctx, txid: str):
        """Check Travel Rule compliance for transaction"""
        utxo = await self.services.chain.get_utxo_from_txid(txid)
        compliant = self.services.compliance.check_travel_rule(utxo)
        await ctx.send(
            f"{'✅' if compliant else '❌'} Travel Rule: "
            f"{'Compliant' if compliant else 'Non-compliant'} for {txid}"
        )
    
    @compliance_group.command(name="sar")
    @commands.has_role("Compliance Officer")
    async def compliance_sar(self, ctx, txid: str, reason: str):
        """File Suspicious Activity Report"""
        utxo = await self.services.chain.get_utxo_from_txid(txid)
        sar = await self.services.reporter.generate_sar(SARTrigger(
            utxo=utxo,
            reason=reason,
            filed_by=ctx.author.id
        ))
        await ctx.send(f"📋 SAR filed: {sar.reference_number}")

class WireOperationsCog(commands.Cog):
    """Fiat⇄BTC wire transfer operations"""
    
    @commands.group(name="wire")
    async def wire_group(self, ctx):
        pass
    
    @wire_group.command(name="deposit")
    @commands.has_role("Treasury")
    async def wire_deposit(self, ctx, exchange: str, amount_jpy: int, purpose: str):
        """JPY deposit → BTC purchase"""
        result = await self.services.bridge.execute_wire_transfer(WireTransferRequest(
            exchange=JapaneseExchange(exchange),
            direction="DEPOSIT",
            amount_jpy=amount_jpy,
            purpose=purpose,
            bank_account=self.config.treasury_bank_account
        ))
        embed = self._create_wire_result_embed(result)
        await ctx.send(embed=embed)
    
    @wire_group.command(name="withdraw")
    @commands.has_role("Treasury")
    async def wire_withdraw(self, ctx, exchange: str, amount_btc: float, purpose: str):
        """BTC sale → JPY withdrawal"""
        result = await self.services.bridge.execute_wire_transfer(WireTransferRequest(
            exchange=JapaneseExchange(exchange),
            direction="WITHDRAWAL",
            amount_btc_sats=int(amount_btc * 100_000_000),
            purpose=purpose,
            bank_account=self.config.treasury_bank_account
        ))
        embed = self._create_wire_result_embed(result)
        await ctx.send(embed=embed)
    
    @wire_group.command(name="status")
    async def wire_status(self, ctx, transaction_id: str):
        """Check wire transfer status"""
        status = await self.services.bridge.get_transfer_status(transaction_id)
        await ctx.send(f"📊 Transfer {transaction_id}: {status}")

class GovernanceBridgeCog(commands.Cog):
    """Bridge to Reddit governance"""
    
    @commands.group(name="governance")
    async def governance_group(self, ctx):
        pass
    
    @governance_group.command(name="propose")
    async def governance_propose(self, ctx, title: str, *, description: str):
        """Create governance proposal on Reddit"""
        proposal = await self.services.reddit.create_proposal(
            title=title,
            description=description,
            author=ctx.author.display_name,
            discord_ref=f"{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id}"
        )
        await ctx.send(f"📝 Proposal created: {proposal.url}")
    
    @governance_group.command(name="vote")
    async def governance_vote(self, ctx, proposal_id: str, vote: Literal["yes", "no", "abstain"]):
        """Vote on Reddit proposal"""
        result = await self.services.reddit.vote(proposal_id, vote, ctx.author.display_name)
        await ctx.send(f"🗳️ Vote recorded: {result}")

class EmergencyResponseCog(commands.Cog):
    """Emergency procedures"""
    
    @commands.command(name="emergency-freeze")
    @commands.has_role("Emergency Council")
    async def emergency_freeze(self, ctx, *, reason: str):
        """EMERGENCY: Freeze all hot wallet operations"""
        await self.services.wallet.enable_emergency_freeze(reason, ctx.author.id)
        await self.services.alerts.notify_all_channels(
            "🚨 EMERGENCY FREEZE ACTIVATED",
            f"Reason: {reason}\nInitiated by: {ctx.author.mention}"
        )
        await ctx.send("🔴 Emergency freeze activated. All hot wallet operations suspended.")
    
    @commands.command(name="emergency-rebalance")
    @commands.has_role("Emergency Council")
    async def emergency_rebalance(self, ctx):
        """EMERGENCY: Force reserve rebalance"""
        health = await self.services.policy.assess_reserve_health()
        result = await self.services.policy.execute_rebalance(health)
        await ctx.send(f"⚡ Emergency rebalance complete: {len(result.actions_taken)} actions")
```

### 5.2 Dashboard API (FastAPI + WebSocket)

```python
# discord/dashboard_api.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import json

app = FastAPI(title="Reserve Management Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for conn in self.active_connections:
            await conn.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle client messages
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# REST Endpoints

@app.get("/api/v1/hygiene/summary")
async def get_hygiene_summary():
    report = await services.hygiene.get_latest_wallet_report()
    return report.dict()

@app.get("/api/v1/hygiene/utxos")
async def get_utxos(grade: str = None, limit: int = 100):
    utxos = await services.hygiene.get_utxos_filtered(grade, limit)
    return [u.dict() for u in utxos]

@app.get("/api/v1/compliance/status")
async def get_compliance_status():
    results = await services.compliance.run_full_check()
    return [r.dict() for r in results]

@app.get("/api/v1/reserve/health")
async def get_reserve_health():
    health = await services.policy.assess_reserve_health()
    return health.dict()

@app.post("/api/v1/wire/transfer")
async def execute_wire_transfer(request: WireTransferRequestModel):
    result = await services.bridge.execute_wire_transfer(request.to_domain())
    return result.dict()

@app.get("/api/v1/governance/proposals")
async def get_proposals(status: str = "active"):
    proposals = await services.reddit.get_proposals(status)
    return [p.dict() for p in proposals]

# Background broadcast task
async def broadcast_updates():
    while True:
        # Send real-time updates to dashboard
        hygiene = await services.hygiene.get_latest_wallet_report()
        compliance = await services.compliance.run_full_check()
        reserve = await services.policy.assess_reserve_health()
        
        await manager.broadcast({
            "type": "dashboard_update",
            "timestamp": datetime.now().isoformat(),
            "hygiene": hygiene.dict(),
            "compliance": [c.dict() for c in compliance],
            "reserve": reserve.dict()
        })
        await asyncio.sleep(30)  # 30-second updates
```

### 5.3 Dashboard Frontend (React + TypeScript)

```tsx
// dashboard/src/components/ReserveDashboard.tsx
import React, { useEffect, useState } from 'react';
import { 
  HygieneOverview, 
  UTXOTable, 
  CompliancePanel, 
  ReserveHealthCard,
  WireTransferForm,
  GovernanceFeed
} from './components';

export const ReserveDashboard: React.FC = () => {
  const [hygiene, setHygiene] = useState<WalletHygieneReport>();
  const [compliance, setCompliance] = useState<ComplianceResult[]>([]);
  const [reserve, setReserve] = useState<ReserveHealthReport>();
  const [ws, setWs] = useState<WebSocket>();

  useEffect(() => {
    // Connect to WebSocket
    const socket = new WebSocket(`${WS_URL}/ws/dashboard`);
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'dashboard_update') {
        setHygiene(data.hygiene);
        setCompliance(data.compliance);
        setReserve(data.reserve);
      }
    };
    setWs(socket);
    return () => socket.close();
  }, []);

  return (
    <div className="dashboard-grid">
      {/* Top Row: Key Metrics */}
      <div className="metric-cards">
        <ReserveHealthCard data={reserve} />
        <HygieneOverview data={hygiene} />
        <ComplianceSummary data={compliance} />
      </div>
      
      {/* Middle Row: Detailed Views */}
      <div className="detail-panels">
        <UTXOTable 
          utxos={hygiene?.utxos || []}
          onFreeze={handleFreeze}
          onConsolidate={handleConsolidate}
        />
        <CompliancePanel 
          results={compliance}
          onRemediate={handleRemediation}
        />
      </div>
      
      {/* Bottom Row: Operations */}
      <div className="operations">
        <WireTransferForm 
          onSubmit={handleWireTransfer}
          exchanges={JAPANESE_EXCHANGES}
        />
        <GovernanceFeed 
          proposals={governanceProposals}
          onVote={handleVote}
        />
      </div>
    </div>
  );
};
```

---

## 6. REDDIT COMMUNITY GOVERNANCE

### 6.1 PRAW-Based Governance Engine

```python
# reddit/governance.py
"""
Reddit Governance Integration using PRAW.
Implements: Proposal creation, voting, execution tracking, transparency.
"""

import praw
from praw.models import Subreddit, Submission, Comment
from dataclasses import dataclass
from typing import List, Optional, Literal
from enum import Enum
import asyncio

class ProposalStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"           # Voting period
    PASSED = "passed"
    REJECTED = "rejected"
    EXECUTED = "executed"
    CANCELLED = "cancelled"

class VoteOption(Enum):
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"

@dataclass
class GovernanceProposal:
    id: str                     # Reddit submission ID
    title: str
    description: str
    author: str
    status: ProposalStatus
    created_at: datetime
    voting_ends_at: datetime
    yes_votes: int
    no_votes: int
    abstain_votes: int
    quorum: int
    threshold: float            # e.g., 0.66 for 2/3 supermajority
    discord_ref: str            # Link to Discord discussion
    execution_tx: Optional[str] = None
    tags: List[str] = None

@dataclass
class VoteRecord:
    proposal_id: str
    voter: str
    vote: VoteOption
    weight: float               # 1.0 = standard, >1 = weighted (e.g., stake)
    timestamp: datetime
    signature: str              # Cryptographic proof

class RedditGovernanceEngine:
    """
    Manages governance on dedicated subreddit (e.g., r/BTCReserveGovernance).
    Uses PRAW for Reddit API interaction.
    """
    
    def __init__(self, config: RedditConfig):
        self.reddit = praw.Reddit(
            client_id=config.client_id,
            client_secret=config.client_secret,
            user_agent=config.user_agent,
            username=config.username,
            password=config.password
        )
        self.subreddit = self.reddit.subreddit(config.subreddit_name)
        self.config = config
        
        # Vote weights (can be configured via governance)
        self.vote_weights = {
            "resident": 1.0,      # General community member
            "contributor": 1.5,   # Active contributors
            "validator": 2.0,     # Running validation nodes
            "treasury": 3.0,      # Treasury multisig signers
            "emergency": 5.0,     # Emergency council
        }
    
    async def create_proposal(self, 
                            title: str, 
                            description: str, 
                            author: str,
                            discord_ref: str,
                            tags: List[str] = None,
                            voting_days: int = 7,
                            quorum: int = 10,
                            threshold: float = 0.66) -> GovernanceProposal:
        
        # Format proposal with structured markdown
        body = self._format_proposal_body(
            description, author, discord_ref, voting_days, quorum, threshold, tags
        )
        
        # Submit to subreddit
        submission = self.subreddit.submit(
            title=f"[PROPOSAL] {title}",
            selftext=body,
            flair_id=self.config.proposal_flair_id
        )
        
        # Create proposal record
        proposal = GovernanceProposal(
            id=submission.id,
            title=title,
            description=description,
            author=author,
            status=ProposalStatus.ACTIVE,
            created_at=datetime.fromtimestamp(submission.created_utc),
            voting_ends_at=datetime.fromtimestamp(submission.created_utc) + timedelta(days=voting_days),
            yes_votes=0,
            no_votes=0,
            abstain_votes=0,
            quorum=quorum,
            threshold=threshold,
            discord_ref=discord_ref,
            tags=tags or []
        )
        
        # Store in database
        await self.db.store_proposal(proposal)
        
        # Pin announcement
        self.subreddit.mod.distinguish(submission, sticky=True)
        
        return proposal
    
    def _format_proposal_body(self, description, author, discord_ref, 
                              voting_days, quorum, threshold, tags) -> str:
        return f"""
## Proposal Details

**Author:** u/{author}
**Discord Discussion:** {discord_ref}
**Status:** 🟢 VOTING ACTIVE
**Voting Ends:** <t:{int((datetime.now() + timedelta(days=voting_days)).timestamp())}:F>
**Quorum Required:** {quorum} weighted votes
**Passing Threshold:** {threshold:.0%} YES votes

---

## Description

{description}

---

## Voting Instructions

1. **Comment your vote** on this post using exactly one of:
   - `VOTE: YES`
   - `VOTE: NO`
   - `VOTE: ABSTAIN`

2. **Vote weight** is determined by your community role (see wiki).

3. **Votes are final** once cast. Edit your comment to change.

4. **Results** will be tallied automatically at voting end.

---

## Tags
{', '.join(tags) if tags else 'None'}

---

*This proposal is managed by the BTC Reserve Governance Bot. 
For questions, visit our Discord or check the [wiki](/wiki/governance).*
"""
    
    async def vote(self, proposal_id: str, vote: VoteOption, voter: str) -> VoteRecord:
        """Record a vote on a proposal"""
        proposal = await self.db.get_proposal(proposal_id)
        if not proposal:
            raise ValueError("Proposal not found")
        
        if proposal.status != ProposalStatus.ACTIVE:
            raise ValueError("Voting not active")
        
        if datetime.now() > proposal.voting_ends_at:
            raise ValueError("Voting period ended")
        
        # Get voter weight
        weight = await self._get_voter_weight(voter)
        
        # Create vote record
        vote_record = VoteRecord(
            proposal_id=proposal_id,
            voter=voter,
            vote=vote,
            weight=weight,
            timestamp=datetime.now(),
            signature=await self._sign_vote(proposal_id, voter, vote)
        )
        
        # Store vote
        await self.db.store_vote(vote_record)
        
        # Post vote comment on Reddit
        submission = self.reddit.submission(id=proposal_id)
        vote_text = f"VOTE: {vote.value.upper()}"
        comment = submission.reply(vote_text)
        
        # Update proposal tally
        await self._update_tally(proposal_id)
        
        return vote_record
    
    async def tally_votes(self, proposal_id: str) -> GovernanceProposal:
        """Tally votes and determine outcome"""
        proposal = await self.db.get_proposal(proposal_id)
        votes = await self.db.get_votes(proposal_id)
        
        # Calculate weighted totals
        yes_weight = sum(v.weight for v in votes if v.vote == VoteOption.YES)
        no_weight = sum(v.weight for v in votes if v.vote == VoteOption.NO)
        abstain_weight = sum(v.weight for v in votes if v.vote == VoteOption.ABSTAIN)
        total_weight = yes_weight + no_weight + abstain_weight
        
        # Check quorum
        quorum_met = total_weight >= proposal.quorum
        
        # Determine outcome
        if not quorum_met:
            proposal.status = ProposalStatus.REJECTED
        elif yes_weight / (yes_weight + no_weight) >= proposal.threshold:
            proposal.status = ProposalStatus.PASSED
        else:
            proposal.status = ProposalStatus.REJECTED
        
        proposal.yes_votes = yes_weight
        proposal.no_votes = no_weight
        proposal.abstain_votes = abstain_weight
        
        await self.db.update_proposal(proposal)
        
        # Post results
        await self._post_results(proposal)
        
        return proposal
    
    async def execute_proposal(self, proposal_id: str) -> str:
        """Execute passed proposal (returns execution transaction)"""
        proposal = await self.db.get_proposal(proposal_id)
        if proposal.status != ProposalStatus.PASSED:
            raise ValueError("Proposal not passed")
        
        # Execute based on proposal type (parsed from tags/description)
        execution_tx = await self._execute_proposal_action(proposal)
        
        proposal.status = ProposalStatus.EXECUTED
        proposal.execution_tx = execution_tx
        await self.db.update_proposal(proposal)
        
        # Post execution confirmation
        await self._post_execution(proposal, execution_tx)
        
        return execution_tx
    
    async def monitor_proposals(self):
        """Background task to monitor proposal lifecycles"""
        while True:
            active = await self.db.get_active_proposals()
            for proposal in active:
                if datetime.now() > proposal.voting_ends_at:
                    await self.tally_votes(proposal.id)
            await asyncio.sleep(300)  # Check every 5 minutes
```

### 6.2 Automated Moderation (PRAW ModTools)

```python
# reddit/moderation.py
class SubredditModerator:
    """Automated moderation for governance subreddit"""
    
    def __init__(self, reddit: praw.Reddit, subreddit_name: str):
        self.subreddit = reddit.subreddit(subreddit_name)
        self.mod = self.subreddit.mod
    
    async def setup_automod(self):
        """Configure AutoModerator rules"""
        rules = [
            # Require specific format for proposals
            {
                "type": "submission",
                "title": [{"regex": r"^\[PROPOSAL\]"}],
                "set_flair": "Proposal",
                "comment": "Proposal submitted. Voting begins now."
            },
            # Enforce vote format
            {
                "type": "comment",
                "body": [{"regex": r"^VOTE:\s*(YES|NO|ABSTAIN)$"}],
                "action": "approve"
            },
            # Remove non-vote comments on proposals
            {
                "type": "comment",
                "parent_title": [{"regex": r"^\[PROPOSAL\]"}],
                "body": [{"regex": r"^(?!VOTE:)"}],
                "action": "remove",
                "comment": "Only VOTE: YES/NO/ABSTAIN comments allowed on proposals."
            },
            # Spam protection
            {
                "type": "any",
                "user_conditions": {
                    "account_age": "< 7 days",
                    "combined_karma": "< 10"
                },
                "action": "filter"
            }
        ]
        
        # Update wiki/config/automoderator
        await self.mod.update_wiki_page("config/automoderator", yaml.dump(rules))
    
    async def moderate_modqueue(self):
        """Process modqueue items"""
        for item in self.mod.modqueue(limit=100):
            if isinstance(item, Submission):
                await self._moderate_submission(item)
            elif isinstance(item, Comment):
                await self._moderate_comment(item)
    
    async def log_moderation_action(self, action: str, target: str, moderator: str, reason: str):
        """Log to modlog and Discord"""
        await self.mod.log(action, target, moderator=moderator, reason=reason)
        await self.discord_webhook.send({
            "action": action,
            "target": target,
            "moderator": moderator,
            "reason": reason
        })
```

---

## 7. INTEGRATED SYSTEM ORCHESTRATION

### 7.1 Main Application

```python
# main.py
"""
Ecological UTXO Reserve Management System
Main entry point integrating all components.
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
import structlog

from core.utxo_hygiene import UTXOHygieneAnalyzer
from compliance.japanese_framework import JapaneseComplianceEngine
from bridge.japanese_exchange_bridge import JapaneseExchangeBridge
from bridge.reserve_policy import ReservePolicyEngine
from discord.management_console import ReserveManagementBot
from reddit.governance import RedditGovernanceEngine
from shared.config import Settings
from shared.database import init_db
from shared.logging import setup_logging

logger = structlog.get_logger()

class ServiceContainer:
    """Dependency injection container"""
    def __init__(self, settings: Settings):
        self.settings = settings
        self._init_services()
    
    def _init_services(self):
        # Core services
        self.chain = BlockchainClient(self.settings.bitcoin_rpc_url)
        self.fees = FeeEstimator(self.chain)
        self.labels = LabelStore(self.settings.redis_url)
        self.wallet = WalletManager(self.chain, self.settings.wallet_config)
        
        # Hygiene & Compliance
        self.hygiene = UTXOHygieneAnalyzer(
            compliance_screener=self.compliance,
            fee_estimator=self.fees,
            label_store=self.labels
        )
        self.compliance = JapaneseComplianceEngine(
            blockchain_analyzer=self.chain,
            kyc_provider=KYCProvider(self.settings.kyc_api),
            audit_logger=AuditLogger(self.settings.audit_log_path)
        )
        self.reporter = RegulatoryReporter(self.compliance)
        
        # Bridge & Policy
        self.bridge = JapaneseExchangeBridge(self.settings.exchanges)
        self.policy = ReservePolicyEngine(
            hygiene_analyzer=self.hygiene,
            compliance=self.compliance,
            exchange_bridge=self.bridge
        )
        
        # Discord
        self.discord_bot = ReserveManagementBot(
            config=self.settings.discord,
            services=self
        )
        
        # Reddit
        self.reddit = RedditGovernanceEngine(self.settings.reddit)
    
    async def start_background_tasks(self):
        """Start all background monitoring loops"""
        tasks = [
            self.hygiene_monitor_loop(),
            self.compliance_check_loop(),
            self.reserve_rebalance_loop(),
            self.reddit.monitor_proposals(),
            self.discord_bot.dashboard.broadcast_updates(),
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def hygiene_monitor_loop(self):
        while True:
            try:
                report = self.hygiene.analyze_full_wallet(
                    await self.wallet.get_all_utxos()
                )
                await self.db.store_hygiene_report(report)
                
                # Alert on critical issues
                if report.freeze_candidates:
                    await self.alerts.notify_compliance_team(report.freeze_candidates)
                
                if report.consolidation_candidates and self.fees.get_current_rate() < 5:
                    await self.alerts.notify_consolidation_opportunity(report.consolidation_candidates)
                    
            except Exception as e:
                logger.error("hygiene_monitor_error", error=str(e))
            await asyncio.sleep(300)  # 5 minutes
    
    async def compliance_check_loop(self):
        while True:
            try:
                results = await self.compliance.run_full_check()
                await self.db.store_compliance_results(results)
                
                # Alert on failures
                for result in results:
                    if not result.compliant and result.severity in ["CRITICAL", "HIGH"]:
                        await self.alerts.notify_compliance_violation(result)
                        
            except Exception as e:
                logger.error("compliance_check_error", error=str(e))
            await asyncio.sleep(3600)  # 1 hour
    
    async def reserve_rebalance_loop(self):
        while True:
            try:
                health = await self.policy.assess_reserve_health()
                await self.db.store_reserve_health(health)
                
                # Auto-rebalance if enabled and deviations exceed threshold
                if self.settings.auto_rebalance:
                    for action in health.recommended_actions:
                        if action.severity == "CRITICAL" and action.auto_executable:
                            await self.policy.execute_rebalance(health)
                            break
                            
            except Exception as e:
                logger.error("reserve_rebalance_error", error=str(e))
            await asyncio.sleep(1800)  # 30 minutes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = Settings()
    setup_logging(settings.log_level)
    await init_db(settings.database_url)
    
    services = ServiceContainer(settings)
    app.state.services = services
    
    # Start Discord bot
    discord_task = asyncio.create_task(services.discord_bot.start(settings.discord.token))
    
    # Start background tasks
    bg_task = asyncio.create_task(services.start_background_tasks())
    
    logger.info("system_started")
    yield
    
    # Shutdown
    await services.discord_bot.close()
    discord_task.cancel()
    bg_task.cancel()
    logger.info("system_stopped")

app = FastAPI(
    title="Ecological UTXO Reserve Management",
    lifespan=lifespan
)

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Include API routers
app.include_router(discord.dashboard_api.router, prefix="/api/v1")
```

---

## 8. DEPLOYMENT ARCHITECTURE

### 8.1 Infrastructure (Docker Compose)

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Core Application
  app:
    build: .
    command: python main.py
    environment:
      - DATABASE_URL=postgresql://postgres:pass@db:5432/reserve
      - REDIS_URL=redis://redis:6379
      - BITCOIN_RPC_URL=http://bitcoin:8332
    depends_on: [db, redis, bitcoin]
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs

  # Discord Bot (separate for scaling)
  discord-bot:
    build: .
    command: python -m discord.management_console
    environment:
      - DISCORD_TOKEN=${DISCORD_TOKEN}
    depends_on: [app]

  # Database
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: reserve
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data

  # Cache
  redis:
    image: redis:7-alpine
    volumes:
      - redisdata:/data

  # Bitcoin Core (for UTXO indexing)
  bitcoin:
    image: ruimarinho/bitcoin-core:26
    environment:
      BITCOIN_RPC_USER: ${BTC_RPC_USER}
      BITCOIN_RPC_PASSWORD: ${BTC_RPC_PASS}
    volumes:
      - bitcoin_data:/data
    ports:
      - "8332:8332"

  # Monitoring
  prometheus:
    image: prom/prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - ./monitoring/dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3000:3000"

volumes:
  pgdata:
  redisdata:
  bitcoin_data:
```

### 8.2 Kubernetes Deployment (Production)

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: reserve-management
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: reserve-management
  template:
    metadata:
      labels:
        app: reserve-management
    spec:
      containers:
      - name: app
        image: reserve-management:latest
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: reserve-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
      - name: discord-bot
        image: reserve-management:latest
        command: ["python", "-m", "discord.management_console"]
        envFrom:
        - secretRef:
            name: reserve-secrets
---
apiVersion: v1
kind: Secret
metadata:
  name: reserve-secrets
  namespace: production
type: Opaque
stringData:
  DISCORD_TOKEN: "your-discord-bot-token"
  REDDIT_CLIENT_ID: "your-reddit-client-id"
  REDDIT_CLIENT_SECRET: "your-reddit-client-secret"
  BTC_RPC_USER: "bitcoinrpc"
  BTC_RPC_PASS: "secure-password"
  DB_PASSWORD: "secure-db-password"
  KYC_API_KEY: "kyc-provider-key"
  EXCHANGE_API_KEYS: "json-map-of-exchange-keys"
```

---

## 9. GITHUB REPOSITORIES & REFERENCES

### 9.1 Key Japanese Compliance Repositories
| Repository | Purpose | Link |
|------------|---------|------|
| FSA Guidelines | Official regulatory documents | `https://www.fsa.go.jp/` |
| JVCEA Rules | Self-regulatory standards | `https://jvcea.org/` |
| bitbank VASP List | Travel Rule approved VASPs | `https://support.bitbank.cc/.../VASP` |

### 9.2 UTXO Management Libraries (GitHub)
| Repository | Language | Features |
|------------|----------|----------|
| `andreasgriffin/bitcoin-safe` | Python | Cold storage, multisig, UTXO labeling, Japanese UI |
| `justshiftjk/UTXO-Management` | TypeScript | Split, merge, send UTXOs, PSBT support |
| `Rezzecup/utxo-management` | TypeScript | Same as above, active fork |
| `kornpow/bitcoin-ops` | Python | OP_RETURN, UTXO discovery, embit-based |
| `ErisExchange/bitgo-utxo-lib` | JavaScript | Multi-coin UTXO lib, >90% test coverage |
| `unisat-wallet/unisat-dev-docs` | API Docs | BTC balance/UTXO endpoints, protocol asset filtering |
| `Bitcoin-PIR/Bitcoin-PIR` | Rust | Private UTXO lookups via PIR |

### 9.3 Discord Management Repositories
| Repository | Stack | Features |
|------------|-------|----------|
| `sosavz/discord-control-center-starter` | Node/Express/Prisma | Ticketing, verification, moderation, dashboard |
| `Duncan588/Discord-Analytics-Dashboard` | Python/Flask | Analytics, word clouds, member tracking |
| `openguard-bot/openguard` | FastAPI/React | AIMod dashboard, OAuth2, real-time updates |
| `PenguinMaster0226/discord-ext-dashboard` | Python/Quart | discord.py extension for dashboards |
| `Okayu Board` (Japanese) | Commercial | Full-featured Japanese Discord management |

### 9.4 Reddit Governance Tools
| Repository | Purpose |
|------------|---------|
| `praw-dev/praw` | Python Reddit API Wrapper (core library) |
| `praw-dev/prawtools` | Moderator utilities, subreddit stats, alerts |

---

## 10. IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Weeks 1-4)
- [ ] Set up Bitcoin Core + UTXO indexer (Electrs/Fulcrum)
- [ ] Implement UTXOHygieneAnalyzer with ecological scoring
- [ ] Build JapaneseComplianceEngine with FSA/JVCEA rules
- [ ] Create LabelStore for UTXO tagging
- [ ] Unit tests for all core algorithms

### Phase 2: Bridge & Policy (Weeks 5-8)
- [ ] Integrate Japanese exchange APIs (Coincheck, bitbank, SBI VC)
- [ ] Implement wire transfer request/response handling
- [ ] Build ReservePolicyEngine with rebalancing logic
- [ ] Add stress testing and scenario analysis
- [ ] Integration tests with exchange sandboxes

### Phase 3: Discord Console (Weeks 9-12)
- [ ] Deploy ReserveManagementBot with all cogs
- [ ] Build FastAPI dashboard backend + WebSocket
- [ ] Create React dashboard frontend
- [ ] Implement role-based access control
- [ ] Add real-time alerts and notifications

### Phase 4: Reddit Governance (Weeks 13-16)
- [ ] Set up governance subreddit with AutoMod
- [ ] Implement RedditGovernanceEngine (PRAW)
- [ ] Create proposal/voting/execution workflow
- [ ] Bridge Discord ↔ Reddit for cross-platform governance
- [ ] Audit trail and transparency reporting

### Phase 5: Production Hardening (Weeks 17-20)
- [ ] Security audit (smart contracts, API keys, multisig)
- [ ] Load testing (10k+ UTXOs, concurrent wire transfers)
- [ ] Disaster recovery drills (cold wallet recovery, DB restore)
- [ ] FSA/JVCEA compliance verification
- [ ] Documentation and runbooks

### Phase 6: Launch & Evolution (Week 21+)
- [ ] Soft launch with limited reserves
- [ ] Community governance activation
- [ ] Continuous improvement via Agile Governance loops
- [ ] International expansion (EU MiCA, US state licenses)

---

## 11. KEY PERFORMANCE INDICATORS

| Category | KPI | Target | Measurement |
|----------|-----|--------|-------------|
| **Ecological** | Wallet hygiene score | >0.85 | Composite ecological_score |
| **Ecological** | Fragmented UTXO ratio | <5% | FRAGMENTED + CONTAMINATED / Total |
| **Ecological** | Toxic UTXO count | 0 | TOXIC grade UTXOs |
| **Compliance** | Cold wallet ratio | >98% | Cold value / Total user value |
| **Compliance** | Segregation audit | Pass | Annual external audit |
| **Compliance** | Travel Rule compliance | 100% | Compliant VASP transfers / Total |
| **Compliance** | SAR filing time | <24h | Detection → Filing |
| **Operations** | Wire transfer success | >99.5% | Completed / Initiated |
| **Operations** | Rebalance latency | <30 min | Alert → Execution |
| **Governance** | Proposal participation | >60% | Voting weight / Eligible weight |
| **Governance** | Execution success | 100% | Passed → Executed |
| **System** | Dashboard uptime | 99.9% | Prometheus/Grafana |
| **System** | UTXO analysis latency | <5s | Full wallet scan |

---

## 12. ETHICAL & REGULATORY GUARDRAILS

```python
# core/guardrails.py
GUARDRAILS = {
    # Japanese Regulatory
    "fsa_cold_wallet_minimum": 0.95,        # Never below FSA 95%
    "fsa_segregation_absolute": True,        # Never compromise segregation
    "jvcea_listing_only": True,              # Only JVCEA-approved tokens
    "travel_rule_enforced": True,            # Never bypass Travel Rule
    "aml_kyc_mandatory": True,               # Full KYC for all users
    
    # Ecological
    "dust_threshold_sats": 600,              # JVCEA dust definition
    "economic_threshold_sats": 10_000,       # COLDCARD uneconomical threshold
    "cold_storage_min_sats": 1_000_000,      # 0.01 BTC minimum cold
    "consolidation_max_fee_rate": 5,         # sat/vB max for consolidation
    
    # Governance
    "proposal_quorum_min": 10,               # Minimum weighted votes
    "proposal_threshold_min": 0.51,          # Simple majority minimum
    "emergency_council_max_actions": 3,      # Per 24h without full vote
    "treasury_multisig_threshold": 3,        # 3-of-5 minimum
    
    # Operational
    "max_hot_wallet_sats": 50_000_000,       # 0.5 BTC max hot
    "auto_rebalance_enabled": True,          # Policy-driven rebalancing
    "audit_log_immutable": True,             # Append-only audit trail
    "key_rotation_days": 90,                 # API key rotation
}

def verify_guardrails(action: Action) -> GuardrailResult:
    """Verify action complies with all guardrails"""
    violations = []
    
    for rule, limit in GUARDRAILS.items():
        if not check_rule(action, rule, limit):
            violations.append(GuardrailViolation(rule, limit, action))
    
    return GuardrailResult(
        compliant=len(violations) == 0,
        violations=violations,
        requires_approval=len(violations) > 0
    )
```

---

## 13. CONCLUSION

This system implements a **holistic ecological reserve management platform** that unifies:

1. **UTXO Hygiene** - Ecological scoring for transaction output health
2. **Japanese Compliance** - FSA/JVCEA automated verification (cold wallet, segregation, Travel Rule, AML)
3. **Fiat⇄BTC Bridge** - Wire transfer integration with all major Japanese exchanges
4. **Discord Operations** - Real-time management console with role-based access
5. **Reddit Governance** - Transparent community governance with cryptographic voting
6. **Agile Governance Loops** - Continuous monitoring, evaluation, and improvement

The architecture follows Japan's **Society 5.0 / Agile Governance** principles:
- **Multi-layer governance** (Technical → Organizational → Rules → Market → Norms)
- **Goal-based regulation** (Dynamic compliance targets)
- **Soft law evolution** (Evidence-based guideline updates via sandbox)
- **Governance by Innovation** (AI/analytics TO govern)
- **Human-centered design** (Ecological health = financial health)

All components are designed for **regulatory auditability**, **operational resilience**, and **community transparency** — enabling a Bitcoin reserve that is ecologically sound, legally compliant, and democratically governed.

---

*Generated: 2026-11-10 | Version: 1.0.0 | Classification: Internal - Operational*