# Tax Merit Distribution & Central AI Fund Management System
## Dominican Republic: Automated Utility/Housing Funding with Government API Integration

---

## 1. SYSTEM OVERVIEW

### 1.1 Core Requirements Mapping

| Requirement | Implementation |
|-------------|----------------|
| **Tax merits accumulate → pass to selecting front** | `MeritAccumulator` → `SelectingFrontDistributor` |
| **Fund electricity, water, appliance costs** | `UtilityFundingEngine` with EDE/EDESUR/CORAASAN APIs |
| **Housing only under relocation** | `RelocationHousingAllocator` with geospatial verification |
| **Central AI manages funding estate before distribution** | `CentralAIFundManager` with multi-signature treasury |
| **Context filing for attendance/housing status reports** | `ContextFilingEngine` with multi-source data aggregation |
| **Fetch DR government APIs (scrape)** | `DRGovernmentAPIConnector` with official endpoints |
| **Scrape merited social platform data API** | `MeritedSocialPlatformConnector` (SUPÉRATE, ADESS, etc.) |
| **Automation for instant API application** | `InstantAPIApplicationEngine` with event-driven triggers |

### 1.2 Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    TAX MERIT DISTRIBUTION ECOSYSTEM                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐       │
│  │  TAX AUTHORITY   │     │  MERITED SOCIAL  │     │  GOVERNMENT      │       │
│  │  (DGII)          │     │  PLATFORMS       │     │  SERVICE APIs    │       │
│  │  • Tax payments  │     │  • SUPÉRATE      │     │  • EDE/EDESUR    │       │
│  │  • Compliance    │     │  • ADESS         │     │  • CORAASAN/INAPA│       │
│  │  • History       │     │  • SIUBEN        │     │  • MIVHED        │       │
│  └────────┬─────────┘     └────────┬─────────┘     └────────┬─────────┘       │
│           │                        │                        │                 │
│           ▼                        ▼                        ▼                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                    MERIT ACCUMULATION LAYER                              │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │ │
│  │  │ MeritCalculator │  │ MeritLedger     │  │ MeritValidator          │  │ │
│  │  │ (tax compliance,│  │ (blockchain-    │  │ (anti-fraud, duplicate  │  │ │
│  │  │  social contrib)│  │  anchored)      │  │  detection)             │  │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────────┘  │ │
│  └────────────────────────────────┬────────────────────────────────────────┘ │
│                                   ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                    SELECTING FRONT DISTRIBUTOR                           │ │
│  │  Routes merits to: UTILITY_FUND │ HOUSING_RELOCATION │ APPLIANCE_FUND   │ │
│  └────────────────────────────────┬────────────────────────────────────────┘ │
│                                   ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                    CENTRAL AI FUND MANAGER                               │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │ │
│  │  │ Treasury     │ │ Risk Engine  │ │ Allocation   │ │ Compliance   │   │ │
│  │  │ Manager      │ │ (ML scoring) │ │ Optimizer    │ │ Verifier     │   │ │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │ │
│  └────────────────────────────────┬────────────────────────────────────────┘ │
│                                   ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                    EXECUTION LAYER (Instant API Application)             │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │ │
│  │  │ Utility      │ │ Housing      │ │ Appliance    │ │ Context      │   │ │
│  │  │ Payment Bot  │ │ Relocation   │ │ Voucher      │ │ Filing Bot   │   │ │
│  │  │ (EDE, CORAA) │ │ Bot (MIVHED) │ │ Bot          │ │ (Multi-src)  │   │ │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. TAX MERIT ACCUMULATION SYSTEM

### 2.1 Merit Calculation Engine

```python
# core/merit_accumulation.py
"""
Tax Merit Accumulation System for Dominican Republic.
Integrates DGII tax compliance, social contributions, civic participation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib
import asyncio
from decimal import Decimal

class MeritCategory(Enum):
    TAX_COMPLIANCE = "tax_compliance"           # DGII: on-time payments, no arrears
    SOCIAL_CONTRIBUTION = "social_contribution" # SUPÉRATE/ADESS: program participation
    CIVIC_PARTICIPATION = "civic_participation" # Voting, community service, veeduría
    ENVIRONMENTAL_STEWARDSHIP = "environmental" # Reforestation, recycling, conservation
    SKILLS_DEVELOPMENT = "skills_development"   # INFOTEP training, certifications
    INFRASTRUCTURE_COOPERATION = "infra_coop"   # Reporting faults, community maintenance

class MeritTier(Enum):
    BRONZE = "bronze"       # 0-999 merits
    SILVER = "silver"       # 1000-4999 merits
    GOLD = "gold"           # 5000-19999 merits
    PLATINUM = "platinum"   # 20000-49999 merits
    DIAMOND = "diamond"     # 50000+ merits

@dataclass
class MeritEvent:
    event_id: str
    citizen_id: str
    category: MeritCategory
    base_merits: int
    multiplier: float
    total_merits: int
    source_system: str          # "DGII", "SUPÉRATE", "JCE", "INFOTEP", etc.
    source_reference: str       # Transaction ID, certificate ID, etc.
    timestamp: datetime
    verified: bool = False
    blockchain_hash: str = ""
    
    def __post_init__(self):
        self.total_merits = int(self.base_merits * self.multiplier)
        self.event_id = self.event_id or hashlib.sha256(
            f"{self.citizen_id}{self.category.value}{self.timestamp}".encode()
        ).hexdigest()[:16]

@dataclass
class CitizenMeritProfile:
    citizen_id: str
    national_id: str            # Cédula number (hashed for privacy)
    total_merits: int = 0
    tier: MeritTier = MeritTier.BRONZE
    category_breakdown: Dict[MeritCategory, int] = field(default_factory=dict)
    merit_history: List[MeritEvent] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    selecting_front_eligible: bool = False
    front_assignment: Optional[str] = None  # UTILITY, HOUSING, APPLIANCE
    
    def add_merits(self, event: MeritEvent):
        self.total_merits += event.total_merits
        self.category_breakdown[event.category] = \
            self.category_breakdown.get(event.category, 0) + event.total_merits
        self.merit_history.append(event)
        self.tier = self._calculate_tier()
        self.last_updated = datetime.now()
        self._check_selecting_front_eligibility()
    
    def _calculate_tier(self) -> MeritTier:
        if self.total_merits >= 50000: return MeritTier.DIAMOND
        if self.total_merits >= 20000: return MeritTier.PLATINUM
        if self.total_merits >= 5000: return MeritTier.GOLD
        if self.total_merits >= 1000: return MeritTier.SILVER
        return MeritTier.BRONZE
    
    def _check_selecting_front_eligibility(self):
        """Determine which selecting front citizen qualifies for"""
        # Minimum thresholds for each front
        thresholds = {
            'UTILITY_FUND': 500,      # Electricity, water, appliance costs
            'HOUSING_RELOCATION': 2000, # Relocation housing (higher threshold)
            'APPLIANCE_FUND': 1000,   # Energy-efficient appliance vouchers
        }
        
        eligible_fronts = [
            front for front, threshold in thresholds.items() 
            if self.total_merits >= threshold
        ]
        
        if eligible_fronts:
            self.selecting_front_eligible = True
            # Assign to highest priority eligible front (housing > utility > appliance)
            priority = ['HOUSING_RELOCATION', 'UTILITY_FUND', 'APPLIANCE_FUND']
            self.front_assignment = next(f for f in priority if f in eligible_fronts)

class MeritCalculator:
    """
    Calculates merits from various sources with anti-gaming measures.
    Japanese model: Multi-stakeholder verification + evidence-based scoring.
    """
    
    # Base merit values (configurable via governance)
    BASE_VALUES = {
        MeritCategory.TAX_COMPLIANCE: {
            'annual_on_time': 200,
            'quarterly_on_time': 50,
            'arrears_cleared': 100,
            'voluntary_disclosure': 150,
        },
        MeritCategory.SOCIAL_CONTRIBUTION: {
            'supérate_participation': 30,      # Monthly
            'adess_compliance': 20,            # Monthly
            'siuben_update': 10,               # Annual
            'community_health_promoter': 100,  # Annual
        },
        MeritCategory.CIVIC_PARTICIPATION: {
            'voted_election': 50,
            'veeduria_participation': 100,     # Per project monitored
            'junta_vecinos_active': 20,        # Monthly
            'participatory_budget': 75,        # Per cycle
        },
        MeritCategory.ENVIRONMENTAL_STEWARDSHIP: {
            'tree_planting': 10,               # Per tree (verified)
            'recycling_collection': 5,         # Per kg
            'watershed_protection': 200,       # Annual
            'solar_installation': 500,         # One-time
        },
        MeritCategory.SKILLS_DEVELOPMENT: {
            'infotep_course_complete': 150,    # Per course
            'certification_earned': 300,       # Per cert
            'apprenticeship_complete': 500,    # Per program
            'digital_skills_badge': 100,       # Per badge
        },
        MeritCategory.INFRASTRUCTURE_COOPERATION: {
            'fault_reported': 10,              # Per verified report
            'maintenance_participation': 50,   # Per event
            'energy_conservation': 20,         # Monthly (smart meter verified)
            'water_conservation': 20,          # Monthly (smart meter verified)
        }
    }
    
    # Multipliers
    TIER_MULTIPLIERS = {
        MeritTier.BRONZE: 1.0,
        MeritTier.SILVER: 1.2,
        MeritTier.GOLD: 1.5,
        MeritTier.PLATINUM: 2.0,
        MeritTier.DIAMOND: 3.0,
    }
    
    STREAK_MULTIPLIERS = {
        3: 1.1,    # 3 months streak
        6: 1.25,   # 6 months streak
        12: 1.5,   # 12 months streak
        24: 2.0,   # 24 months streak
    }
    
    def __init__(self, blockchain_anchor: 'BlockchainAnchor'):
        self.blockchain = blockchain_anchor
        self.fraud_detector = MeritFraudDetector()
    
    async def calculate_merits(self, 
                               citizen_id: str, 
                               category: MeritCategory, 
                               action: str, 
                               evidence: Dict[str, Any],
                               current_tier: MeritTier = MeritTier.BRONZE,
                               streak_months: int = 0) -> MeritEvent:
        
        # 1. Verify evidence authenticity
        verification = await self._verify_evidence(category, action, evidence)
        if not verification.valid:
            raise MeritCalculationError(f"Evidence invalid: {verification.reason}")
        
        # 2. Check for duplicate/fraud
        fraud_check = await self.fraud_detector.check(citizen_id, category, action, evidence)
        if fraud_check.is_fraud:
            raise MeritCalculationError(f"Fraud detected: {fraud_check.reason}")
        
        # 3. Calculate base merits
        base = self.BASE_VALUES.get(category, {}).get(action, 0)
        if base == 0:
            raise MeritCalculationError(f"Unknown action: {action} for {category}")
        
        # 4. Apply multipliers
        tier_mult = self.TIER_MULTIPLIERS[current_tier]
        streak_mult = self._get_streak_multiplier(streak_months)
        total_multiplier = tier_mult * streak_mult
        
        # 5. Create merit event
        event = MeritEvent(
            event_id="",
            citizen_id=citizen_id,
            category=category,
            base_merits=base,
            multiplier=total_multiplier,
            total_merits=0,  # Calculated in __post_init__
            source_system=evidence.get('source_system', 'UNKNOWN'),
            source_reference=evidence.get('reference_id', ''),
            timestamp=datetime.now(),
            verified=True
        )
        
        # 6. Blockchain anchor for immutability
        event.blockchain_hash = await self.blockchain.anchor_merit_event(event)
        
        return event
    
    def _get_streak_multiplier(self, streak_months: int) -> float:
        for months, mult in sorted(self.STREAK_MULTIPLIERS.items(), reverse=True):
            if streak_months >= months:
                return mult
        return 1.0
    
    async def _verify_evidence(self, category: MeritCategory, action: str, evidence: Dict) -> VerificationResult:
        # Implement source-specific verification
        verifiers = {
            MeritCategory.TAX_COMPLIANCE: self._verify_dgii_evidence,
            MeritCategory.SOCIAL_CONTRIBUTION: self._verify_social_evidence,
            MeritCategory.CIVIC_PARTICIPATION: self._verify_civic_evidence,
            MeritCategory.ENVIRONMENTAL_STEWARDSHIP: self._verify_env_evidence,
            MeritCategory.SKILLS_DEVELOPMENT: self._verify_skills_evidence,
            MeritCategory.INFRASTRUCTURE_COOPERATION: self._verify_infra_evidence,
        }
        verifier = verifiers.get(category)
        if verifier:
            return await verifier(action, evidence)
        return VerificationResult(valid=False, reason="No verifier for category")

class MeritLedger:
    """
    Immutable merit ledger with blockchain anchoring.
    Japanese model: Machine-readable, auditable, tamper-proof.
    """
    
    def __init__(self, db: 'Database', blockchain: 'BlockchainAnchor'):
        self.db = db
        self.blockchain = blockchain
        self.cache: Dict[str, CitizenMeritProfile] = {}
    
    async def get_profile(self, citizen_id: str) -> CitizenMeritProfile:
        if citizen_id in self.cache:
            return self.cache[citizen_id]
        
        profile = await self.db.get_merit_profile(citizen_id)
        if not profile:
            profile = CitizenMeritProfile(citizen_id=citizen_id, national_id="")
        
        self.cache[citizen_id] = profile
        return profile
    
    async def record_merit_event(self, event: MeritEvent) -> RecordingResult:
        # Get current profile
        profile = await self.get_profile(event.citizen_id)
        
        # Add merits
        profile.add_merits(event)
        
        # Persist
        await self.db.save_merit_profile(profile)
        await self.db.save_merit_event(event)
        
        # Update cache
        self.cache[event.citizen_id] = profile
        
        # Trigger selecting front evaluation
        if event.verified and profile.selecting_front_eligible:
            await self._trigger_selecting_front_distribution(profile)
        
        return RecordingResult(success=True, profile=profile, event=event)
    
    async def _trigger_selecting_front_distribution(self, profile: CitizenMeritProfile):
        # This will be handled by SelectingFrontDistributor
        pass
```

### 2.2 Selecting Front Distributor

```python
# core/selecting_front.py
"""
Selecting Front Distributor - Routes accumulated merits to funding fronts.
Implements: Merit threshold gating, front assignment, fund reservation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
import asyncio

class SelectingFront(Enum):
    UTILITY_FUND = "utility_fund"           # Electricity, water, appliance costs
    HOUSING_RELOCATION = "housing_relocation" # Relocation housing only
    APPLIANCE_FUND = "appliance_fund"       # Energy-efficient appliance vouchers

class FrontPriority(Enum):
    HOUSING_RELOCATION = 1   # Highest priority - basic shelter
    UTILITY_FUND = 2         # Essential services
    APPLIANCE_FUND = 3       # Efficiency upgrades

@dataclass
class FrontAllocation:
    front: SelectingFront
    citizen_id: str
    merits_allocated: int
    funding_reserved: Decimal  # DOP amount reserved
    status: str                # RESERVED, DISBURSED, EXPIRED
    reservation_date: datetime
    expiry_date: datetime
    central_ai_approval: bool = False
    disbursement_details: Dict = None

@dataclass
class SelectingFrontConfig:
    front: SelectingFront
    minimum_merits: int
    merit_to_dop_rate: Decimal      # Merits → DOP conversion
    max_allocation_per_citizen: Decimal
    reservation_period_days: int
    requires_central_ai_approval: bool
    auto_disbursement: bool

# Default configurations (governance-adjustable)
DEFAULT_CONFIGS = {
    SelectingFront.UTILITY_FUND: SelectingFrontConfig(
        front=SelectingFront.UTILITY_FUND,
        minimum_merits=500,
        merit_to_dop_rate=Decimal('50.0'),      # 1 merit = 50 DOP
        max_allocation_per_citizen=Decimal('25000'),  # Max 25,000 DOP/month
        reservation_period_days=30,
        requires_central_ai_approval=True,
        auto_disbursement=True
    ),
    SelectingFront.HOUSING_RELOCATION: SelectingFrontConfig(
        front=SelectingFront.HOUSING_RELOCATION,
        minimum_merits=2000,
        merit_to_dop_rate=Decimal('100.0'),     # 1 merit = 100 DOP (higher value)
        max_allocation_per_citizen=Decimal('500000'), # Max 500,000 DOP (housing unit)
        reservation_period_days=180,
        requires_central_ai_approval=True,
        auto_disbursement=False  # Requires relocation verification
    ),
    SelectingFront.APPLIANCE_FUND: SelectingFrontConfig(
        front=SelectingFront.APPLIANCE_FUND,
        minimum_merits=1000,
        merit_to_dop_rate=Decimal('75.0'),      # 1 merit = 75 DOP
        max_allocation_per_citizen=Decimal('50000'),  # Max 50,000 DOP per appliance
        reservation_period_days=90,
        requires_central_ai_approval=True,
        auto_disbursement=True
    ),
}

class SelectingFrontDistributor:
    """
    Distributes accumulated merits to appropriate selecting fronts.
    Central AI manages the funding estate before distribution.
    """
    
    def __init__(self, 
                 merit_ledger: 'MeritLedger',
                 central_ai_fund: 'CentralAIFundManager',
                 configs: Dict[SelectingFront, SelectingFrontConfig] = None):
        self.merit_ledger = merit_ledger
        self.central_ai = central_ai_fund
        self.configs = configs or DEFAULT_CONFIGS
        self.allocations: Dict[str, List[FrontAllocation]] = {}  # citizen_id -> allocations
    
    async def evaluate_and_distribute(self, citizen_id: str) -> DistributionResult:
        """Evaluate citizen's merit profile and distribute to eligible fronts"""
        profile = await self.merit_ledger.get_profile(citizen_id)
        
        if not profile.selecting_front_eligible:
            return DistributionResult(
                citizen_id=citizen_id,
                eligible=False,
                reason="Insufficient merits for any front",
                allocations=[]
            )
        
        # Determine all eligible fronts (not just primary assignment)
        eligible_fronts = self._get_eligible_fronts(profile)
        
        if not eligible_fronts:
            return DistributionResult(
                citizen_id=citizen_id,
                eligible=False,
                reason="No eligible fronts despite flag",
                allocations=[]
            )
        
        # Create allocations for each eligible front
        allocations = []
        for front in eligible_fronts:
            config = self.configs[front]
            
            # Calculate allocatable merits (capped by config)
            allocatable_merits = min(
                profile.total_merits,
                int(config.max_allocation_per_citizen / config.merit_to_dop_rate)
            )
            
            if allocatable_merits < config.minimum_merits:
                continue
            
            funding_amount = Decimal(allocatable_merits) * config.merit_to_dop_rate
            
            # Reserve funding in Central AI Fund Manager
            reservation = await self.central_ai.reserve_funds(
                citizen_id=citizen_id,
                front=front,
                amount=funding_amount,
                merits_backing=allocatable_merits
            )
            
            if reservation.success:
                allocation = FrontAllocation(
                    front=front,
                    citizen_id=citizen_id,
                    merits_allocated=allocatable_merits,
                    funding_reserved=funding_amount,
                    status="RESERVED",
                    reservation_date=datetime.now(),
                    expiry_date=datetime.now() + timedelta(days=config.reservation_period_days),
                    central_ai_approval=reservation.approved,
                    disbursement_details={}
                )
                allocations.append(allocation)
                
                # Store allocation
                self.allocations.setdefault(citizen_id, []).append(allocation)
                
                # Deduct merits from available balance (not total - total is immutable)
                await self._deduct_available_merits(citizen_id, allocatable_merits)
        
        return DistributionResult(
            citizen_id=citizen_id,
            eligible=True,
            allocations=allocations,
            total_funding_reserved=sum(a.funding_reserved for a in allocations),
            total_merits_allocated=sum(a.merits_allocated for a in allocations)
        )
    
    def _get_eligible_fronts(self, profile: CitizenMeritProfile) -> List[SelectingFront]:
        """Get all fronts citizen qualifies for based on merits"""
        eligible = []
        for front, config in self.configs.items():
            if profile.total_merits >= config.minimum_merits:
                eligible.append(front)
        # Sort by priority
        eligible.sort(key=lambda f: FrontPriority[f.name].value)
        return eligible
    
    async def _deduct_available_merits(self, citizen_id: str, merits: int):
        """Deduct from available (spendable) merits, not total earned"""
        profile = await self.merit_ledger.get_profile(citizen_id)
        # Implementation depends on merit accounting model
        # Could be: available_merits = total_earned - total_allocated
        pass
```

---

## 3. CENTRAL AI FUND MANAGEMENT SYSTEM

### 3.1 Central AI Fund Manager

```python
# core/central_ai_fund.py
"""
Central AI Fund Manager - Manages funding estate before distribution.
Implements: Multi-signature treasury, risk scoring, allocation optimization,
compliance verification, automated disbursement with audit trail.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
import asyncio
import hashlib

class FundType(Enum):
    UTILITY_FUND = "utility_fund"
    HOUSING_RELOCATION_FUND = "housing_relocation_fund"
    APPLIANCE_FUND = "appliance_fund"
    EMERGENCY_RESERVE = "emergency_reserve"
    OPERATIONAL = "operational"

class AllocationStatus(Enum):
    PENDING = "pending"
    AI_APPROVED = "ai_approved"
    COMPLIANCE_VERIFIED = "compliance_verified"
    MULTISIG_SIGNED = "multisig_signed"
    DISBURSED = "disbursed"
    REJECTED = "rejected"
    EXPIRED = "expired"

@dataclass
class FundReservation:
    reservation_id: str
    citizen_id: str
    front: SelectingFront
    fund_type: FundType
    amount_dop: Decimal
    merits_backing: int
    status: AllocationStatus
    requested_at: datetime
    ai_approved_at: Optional[datetime] = None
    compliance_verified_at: Optional[datetime] = None
    multisig_signed_at: Optional[datetime] = None
    disbursed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    audit_hash: str = ""

@dataclass
class DisbursementInstruction:
    instruction_id: str
    reservation_id: str
    citizen_id: str
    front: SelectingFront
    amount_dop: Decimal
    target_api: str              # "EDE_NORTE", "CORAASAN", "MIVHED", "MERCADO_LIBRE_DO"
    target_account: str          # Utility account, vendor ID, etc.
    metadata: Dict[str, Any]     # Service-specific parameters
    priority: int                # 1=highest
    created_at: datetime
    executed_at: Optional[datetime] = None
    execution_result: Optional[Dict] = None

class CentralAIFundManager:
    """
    Central AI Fund Manager with multi-layer approval:
    1. AI Risk Scoring (ML-based)
    2. Compliance Verification (RegTech)
    3. Multi-signature Authorization
    4. Automated Execution via API connectors
    """
    
    def __init__(self):
        self.treasury = MultiSigTreasury()
        self.risk_engine = AIRiskEngine()
        self.compliance_verifier = ComplianceVerifier()
        self.allocation_optimizer = AllocationOptimizer()
        self.execution_engine = InstantAPIExecutor()
        self.audit_logger = AuditLogger()
        
        # Fund balances (DOP)
        self.fund_balances: Dict[FundType, Decimal] = {
            FundType.UTILITY_FUND: Decimal('0'),
            FundType.HOUSING_RELOCATION_FUND: Decimal('0'),
            FundType.APPLIANCE_FUND: Decimal('0'),
            FundType.EMERGENCY_RESERVE: Decimal('10000000'),  # 10M DOP reserve
            FundType.OPERATIONAL: Decimal('5000000'),         # 5M DOP operational
        }
        
        # Reservations tracking
        self.reservations: Dict[str, FundReservation] = {}
        self.disbursement_queue: asyncio.Queue = asyncio.Queue()
    
    async def reserve_funds(self, 
                           citizen_id: str, 
                           front: SelectingFront, 
                           amount_dop: Decimal, 
                           merits_backing: int) -> FundReservationResult:
        """Reserve funds for a citizen's merit-based allocation"""
        
        fund_type = self._front_to_fund_type(front)
        
        # 1. Check fund availability
        if self.fund_balances[fund_type] < amount_dop:
            return FundReservationResult(
                success=False,
                reason=f"Insufficient funds in {fund_type.value}",
                reservation=None
            )
        
        # 2. Create reservation
        reservation_id = self._generate_reservation_id(citizen_id, front)
        reservation = FundReservation(
            reservation_id=reservation_id,
            citizen_id=citizen_id,
            front=front,
            fund_type=fund_type,
            amount_dop=amount_dop,
            merits_backing=merits_backing,
            status=AllocationStatus.PENDING,
            requested_at=datetime.now()
        )
        
        # 3. AI Risk Assessment
        risk_score = await self.risk_engine.assess_allocation(reservation)
        reservation.audit_hash = self._hash_reservation(reservation)
        
        if risk_score > 0.8:  # High risk threshold
            reservation.status = AllocationStatus.REJECTED
            reservation.rejection_reason = f"High risk score: {risk_score:.2f}"
            self.reservations[reservation_id] = reservation
            await self.audit_logger.log_rejection(reservation)
            return FundReservationResult(success=False, reason=reservation.rejection_reason, reservation=reservation)
        
        # 4. Compliance Verification
        compliance = await self.compliance_verifier.verify(reservation)
        if not compliance.passed:
            reservation.status = AllocationStatus.REJECTED
            reservation.rejection_reason = f"Compliance failed: {compliance.failures}"
            self.reservations[reservation_id] = reservation
            await self.audit_logger.log_rejection(reservation)
            return FundReservationResult(success=False, reason=reservation.rejection_reason, reservation=reservation)
        
        reservation.status = AllocationStatus.COMPLIANCE_VERIFIED
        reservation.compliance_verified_at = datetime.now()
        
        # 5. Multi-signature Authorization (for high-value allocations)
        if amount_dop > Decimal('100000'):  # >100k DOP requires multisig
            multisig_result = await self.treasury.request_authorization(reservation)
            if not multisig_result.authorized:
                reservation.status = AllocationStatus.REJECTED
                reservation.rejection_reason = "Multi-signature authorization failed"
                self.reservations[reservation_id] = reservation
                return FundReservationResult(success=False, reason=reservation.rejection_reason, reservation=reservation)
            
            reservation.status = AllocationStatus.MULTISIG_SIGNED
            reservation.multisig_signed_at = datetime.now()
        
        # 6. AI Final Approval
        ai_approval = await self._ai_final_approval(reservation, risk_score, compliance)
        if not ai_approval.approved:
            reservation.status = AllocationStatus.REJECTED
            reservation.rejection_reason = ai_approval.reason
            self.reservations[reservation_id] = reservation
            return FundReservationResult(success=False, reason=ai_approval.reason, reservation=reservation)
        
        reservation.status = AllocationStatus.AI_APPROVED
        reservation.ai_approved_at = datetime.now()
        
        # 7. Reserve funds (move from available to reserved)
        self.fund_balances[fund_type] -= amount_dop
        
        # 8. Store and queue for execution
        self.reservations[reservation_id] = reservation
        await self._queue_for_execution(reservation)
        
        await self.audit_logger.log_reservation(reservation)
        
        return FundReservationResult(success=True, reservation=reservation)
    
    async def _ai_final_approval(self, reservation: FundReservation, risk_score: float, compliance) -> AIApproval:
        """Final AI approval with optimization"""
        
        # Check allocation optimization
        optimization = await self.allocation_optimizer.optimize(reservation)
        
        # Build decision context
        context = {
            'reservation': reservation,
            'risk_score': risk_score,
            'compliance': compliance,
            'optimization': optimization,
            'fund_health': self._get_fund_health(reservation.fund_type),
            'citizen_history': await self._get_citizen_history(reservation.citizen_id),
        }
        
        # AI Decision (simplified - would use ML model in production)
        approved = (
            risk_score < 0.5 and
            compliance.passed and
            optimization.feasible and
            self.fund_balances[reservation.fund_type] > Decimal('1000000')  # Maintain buffer
        )
        
        reason = "Approved" if approved else "Failed optimization/fund health checks"
        
        return AIApproval(approved=approved, reason=reason, context=context)
    
    async def _queue_for_execution(self, reservation: FundReservation):
        """Create disbursement instruction and queue for instant execution"""
        
        # Determine target API based on front
        target_api = self._get_target_api(reservation.front)
        target_account = await self._get_citizen_target_account(reservation.citizen_id, reservation.front)
        
        instruction = DisbursementInstruction(
            instruction_id=self._generate_instruction_id(reservation.reservation_id),
            reservation_id=reservation.reservation_id,
            citizen_id=reservation.citizen_id,
            front=reservation.front,
            amount_dop=reservation.amount_dop,
            target_api=target_api,
            target_account=target_account,
            metadata=self._build_metadata(reservation),
            priority=self._calculate_priority(reservation),
            created_at=datetime.now()
        )
        
        await self.disbursement_queue.put(instruction)
        
        # Trigger instant execution (async)
        asyncio.create_task(self.execution_engine.execute(instruction))
    
    def _front_to_fund_type(self, front: SelectingFront) -> FundType:
        mapping = {
            SelectingFront.UTILITY_FUND: FundType.UTILITY_FUND,
            SelectingFront.HOUSING_RELOCATION: FundType.HOUSING_RELOCATION_FUND,
            SelectingFront.APPLIANCE_FUND: FundType.APPLIANCE_FUND,
        }
        return mapping[front]
    
    def _get_target_api(self, front: SelectingFront) -> str:
        mapping = {
            SelectingFront.UTILITY_FUND: "UTILITY_PAYMENT_AGGREGATOR",  # Routes to EDE/EDESUR/CORAASAN
            SelectingFront.HOUSING_RELOCATION: "MIVHED_RELOCATION_API",
            SelectingFront.APPLIANCE_FUND: "APPLIANCE_VOUCHER_API",
        }
        return mapping[front]
    
    def _hash_reservation(self, reservation: FundReservation) -> str:
        data = f"{reservation.reservation_id}{reservation.citizen_id}{reservation.amount_dop}{reservation.requested_at}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
```

### 3.2 AI Risk Engine

```python
# core/ai_risk_engine.py
"""
AI Risk Engine for allocation scoring.
Uses ML models trained on historical disbursement data, fraud patterns, default rates.
"""

class AIRiskEngine:
    def __init__(self):
        self.fraud_model = FraudDetectionModel()
        self.default_model = DefaultPredictionModel()
        self.anomaly_detector = AnomalyDetector()
        self.feature_store = FeatureStore()
    
    async def assess_allocation(self, reservation: FundReservation) -> float:
        """Returns risk score 0.0-1.0 (1.0 = highest risk)"""
        
        # Extract features
        features = await self._extract_features(reservation)
        
        # Run models in parallel
        fraud_score, default_score, anomaly_score = await asyncio.gather(
            self.fraud_model.predict(features),
            self.default_model.predict(features),
            self.anomaly_detector.detect(features)
        )
        
        # Weighted composite (configurable)
        weights = {'fraud': 0.4, 'default': 0.35, 'anomaly': 0.25}
        composite = (
            weights['fraud'] * fraud_score +
            weights['default'] * default_score +
            weights['anomaly'] * anomaly_score
        )
        
        # Apply business rules
        composite = self._apply_business_rules(composite, features)
        
        return min(max(composite, 0.0), 1.0)
    
    async def _extract_features(self, reservation: FundReservation) -> Dict:
        citizen_id = reservation.citizen_id
        
        # Citizen features
        citizen_features = await self.feature_store.get_citizen_features(citizen_id)
        
        # Transaction features
        tx_features = {
            'amount_dop': float(reservation.amount_dop),
            'merits_backing': reservation.merits_backing,
            'merit_to_dop_ratio': float(reservation.amount_dop) / max(reservation.merits_backing, 1),
            'front_type': reservation.front.value,
            'hour_of_day': reservation.requested_at.hour,
            'day_of_week': reservation.requested_at.weekday(),
        }
        
        # Historical features
        history = await self._get_allocation_history(citizen_id)
        history_features = {
            'previous_allocations': len(history),
            'total_previous_amount': sum(h.amount_dop for h in history),
            'repayment_rate': self._calculate_repayment_rate(history),
            'days_since_last_allocation': (datetime.now() - history[-1].requested_at).days if history else 999,
        }
        
        return {**citizen_features, **tx_features, **history_features}
    
    def _apply_business_rules(self, score: float, features: Dict) -> float:
        # Increase risk for first-time large allocations
        if features.get('previous_allocations', 0) == 0 and features.get('amount_dop', 0) > 50000:
            score *= 1.3
        
        # Decrease risk for high merit backing
        if features.get('merit_to_dop_ratio', 0) > 100:  # >100 merits per DOP
            score *= 0.8
        
        # Increase risk for unusual hours (potential automation abuse)
        if features.get('hour_of_day', 12) < 6 or features.get('hour_of_day', 12) > 22:
            score *= 1.1
        
        return score
```

---

## 4. RELOCATION-BASED HOUSING ALLOCATION SYSTEM

### 4.1 Housing Allocation Engine

```python
# domains/housing_relocation.py
"""
Relocation-Based Housing Allocation System.
Housing ONLY provided under verified relocation scenarios.
Integrates with MIVHED, property registries, geospatial verification.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
import asyncio

class RelocationReason(Enum):
    NATURAL_DISASTER = "natural_disaster"       # Hurricane, flood, earthquake
    ENVIRONMENTAL_HAZARD = "environmental_hazard" # Landslide zone, floodplain, contamination
    INFRASTRUCTURE_PROJECT = "infrastructure_project" # Road, dam, utility expansion
    URBAN_RENEWAL = "urban_renewal"             # Slum upgrading, formalization
    HEALTH_SAFETY = "health_safety"             # Structural collapse risk, contamination
    ECONOMIC_DISPLACEMENT = "economic_displacement" # Gentrification, tourism development

class HousingStatus(Enum):
    ELIGIBLE = "eligible"
    VERIFIED = "verified"
    RELOCATION_PENDING = "relocation_pending"
    HOUSING_ASSIGNED = "housing_assigned"
    RELOCATED = "relocated"
    REJECTED = "rejected"

@dataclass
class RelocationCase:
    case_id: str
    citizen_id: str
    household_size: int
    current_address: str
    current_coordinates: tuple  # (lat, lon)
    relocation_reason: RelocationReason
    reason_evidence: Dict[str, Any]  # Official reports, certificates, etc.
    vulnerability_score: float       # 0-1: health, age, disability, income
    status: HousingStatus = HousingStatus.ELIGIBLE
    created_at: datetime = datetime.now()
    verified_at: Optional[datetime] = None
    assigned_housing_id: Optional[str] = None
    relocation_date: Optional[datetime] = None
    
    # Central AI funding
    funding_reserved: Decimal = Decimal('0')
    merits_used: int = 0
    central_ai_approval: bool = False

@dataclass
class AvailableHousingUnit:
    unit_id: str
    project_name: str
    address: str
    coordinates: tuple
    unit_type: str              # APARTMENT, HOUSE, CORE_HOUSE
    bedrooms: int
    bathrooms: int
    square_meters: float
    monthly_cost_dop: Decimal   # Subsidized cost
    availability_date: datetime
    accessibility_features: List[str]
    utility_connections: Dict[str, bool]  # electricity, water, gas, internet
    mivhed_project_id: str
    blockchain_verified: bool = False

class RelocationHousingAllocator:
    """
    Allocates housing ONLY under verified relocation.
    Central AI manages funding estate; merits convert to housing subsidies.
    """
    
    def __init__(self, 
                 central_ai: 'CentralAIFundManager',
                 mivhed_connector: 'MIVHEDConnector',
                 property_registry: 'PropertyRegistry',
                 geospatial_verifier: 'GeospatialVerifier'):
        self.central_ai = central_ai
        self.mivhed = mivhed_connector
        self.property_registry = property_registry
        self.geospatial = geospatial_verifier
        self.active_cases: Dict[str, RelocationCase] = {}
        self.housing_inventory: Dict[str, AvailableHousingUnit] = {}
    
    async def submit_relocation_request(self, case: RelocationCase) -> RelocationResult:
        """Submit and verify relocation request"""
        
        # 1. Verify relocation reason with evidence
        verification = await self._verify_relocation_reason(case)
        if not verification.valid:
            return RelocationResult(success=False, reason=verification.reason, case=case)
        
        # 2. Geospatial verification (hazard zone, project footprint, etc.)
        geo_verification = await self.geospatial.verify_relocation_need(
            case.current_coordinates, case.relocation_reason
        )
        if not geo_verification.confirmed:
            return RelocationResult(success=False, reason=f"Geospatial verification failed: {geo_verification.reason}", case=case)
        
        # 3. Property registry check (no duplicate housing ownership)
        property_check = await self.property_registry.check_ownership(case.citizen_id)
        if property_check.owns_habitable_property:
            return RelocationResult(success=False, reason="Citizen already owns habitable property", case=case)
        
        # 4. Vulnerability assessment
        vulnerability = await self._assess_vulnerability(case)
        case.vulnerability_score = vulnerability.score
        
        # 5. Calculate required merits/funding
        funding_needed = await self._calculate_funding_needed(case)
        
        # 6. Check citizen's merit balance via Central AI
        merit_check = await self.central_ai.check_merit_balance(case.citizen_id, funding_needed)
        if not merit_check.sufficient:
            return RelocationResult(success=False, reason=f"Insufficient merits: need {merit_check.required_merits}, have {merit_check.available_merits}", case=case)
        
        # 7. Reserve funds in Central AI
        reservation = await self.central_ai.reserve_funds(
            citizen_id=case.citizen_id,
            front=SelectingFront.HOUSING_RELOCATION,
            amount_dop=funding_needed,
            merits_backing=merit_check.required_merits
        )
        
        if not reservation.success:
            return RelocationResult(success=False, reason=f"Fund reservation failed: {reservation.reason}", case=case)
        
        # 8. Update case
        case.status = HousingStatus.VERIFIED
        case.verified_at = datetime.now()
        case.funding_reserved = funding_needed
        case.merits_used = merit_check.required_merits
        case.central_ai_approval = True
        
        self.active_cases[case.case_id] = case
        
        # 9. Match with available housing
        matches = await self._match_housing(case)
        
        return RelocationResult(
            success=True,
            case=case,
            housing_matches=matches,
            funding_reserved=funding_needed
        )
    
    async def _verify_relocation_reason(self, case: RelocationCase) -> VerificationResult:
        """Verify relocation reason with official sources"""
        
        verifiers = {
            RelocationReason.NATURAL_DISASTER: self._verify_disaster_declaration,
            RelocationReason.ENVIRONMENTAL_HAZARD: self._verify_hazard_zone,
            RelocationReason.INFRASTRUCTURE_PROJECT: self._verify_infrastructure_project,
            RelocationReason.URBAN_RENEWAL: self._verify_urban_renewal,
            RelocationReason.HEALTH_SAFETY: self._verify_health_safety,
            RelocationReason.ECONOMIC_DISPLACEMENT: self._verify_economic_displacement,
        }
        
        verifier = verifiers.get(case.relocation_reason)
        if not verifier:
            return VerificationResult(valid=False, reason="Unknown relocation reason")
        
        return await verifier(case)
    
    async def _verify_disaster_declaration(self, case: RelocationCase) -> VerificationResult:
        """Check COE (Emergency Operations Center) declarations"""
        # Connect to COE API for official disaster declarations
        coe_declaration = await self._fetch_coe_declaration(case.current_coordinates)
        if coe_declaration and coe_declaration.active:
            return VerificationResult(valid=True, details=coe_declaration)
        return VerificationResult(valid=False, reason="No active disaster declaration for location")
    
    async def _match_housing(self, case: RelocationCase) -> List[AvailableHousingUnit]:
        """Match household with available housing units"""
        
        # Refresh inventory from MIVHED
        await self._refresh_housing_inventory()
        
        # Filter by household needs
        suitable = []
        for unit in self.housing_inventory.values():
            if self._unit_suitable_for_household(unit, case):
                suitable.append(unit)
        
        # Sort by: vulnerability priority, proximity to original location, availability
        suitable.sort(key=lambda u: (
            -case.vulnerability_score,  # Higher vulnerability first
            self._calculate_distance(case.current_coordinates, u.coordinates),
            u.availability_date
        ))
        
        return suitable[:5]  # Top 5 matches
    
    def _unit_suitable_for_household(self, unit: AvailableHousingUnit, case: RelocationCase) -> bool:
        # Bedroom requirements (DR standards)
        required_bedrooms = max(1, (case.household_size + 1) // 2)
        if unit.bedrooms < required_bedrooms:
            return False
        
        # Accessibility needs
        if case.vulnerability_score > 0.7 and 'wheelchair_accessible' not in unit.accessibility_features:
            return False
        
        # Utility connections required
        if not all(unit.utility_connections.values()):
            return False
        
        return True
    
    async def assign_housing(self, case_id: str, unit_id: str) -> AssignmentResult:
        """Assign specific housing unit to verified case"""
        case = self.active_cases.get(case_id)
        unit = self.housing_inventory.get(unit_id)
        
        if not case or not unit:
            return AssignmentResult(success=False, reason="Case or unit not found")
        
        if case.status != HousingStatus.VERIFIED:
            return AssignmentResult(success=False, reason="Case not verified")
        
        # Update statuses
        case.status = HousingStatus.HOUSING_ASSIGNED
        case.assigned_housing_id = unit_id
        unit.availability_date = datetime.now() + timedelta(days=30)  # Reserve for 30 days
        
        # Notify MIVHED
        await self.mivhed.notify_assignment(case.citizen_id, unit_id, case.case_id)
        
        # Trigger utility connection setup
        asyncio.create_task(self._setup_utilities(case, unit))
        
        return AssignmentResult(success=True, case=case, unit=unit)
    
    async def complete_relocation(self, case_id: str) -> RelocationCompletionResult:
        """Mark relocation as complete, release final funding"""
        case = self.active_cases.get(case_id)
        if not case or case.status != HousingStatus.HOUSING_ASSIGNED:
            return RelocationCompletionResult(success=False, reason="Invalid case status")
        
        # Verify physical relocation (geospatial + utility activation)
        verification = await self._verify_physical_relocation(case)
        if not verification.verified:
            return RelocationCompletionResult(success=False, reason="Physical relocation not verified")
        
        # Release reserved funds to MIVHED/contractor
        release = await self.central_ai.release_funds(case.citizen_id, case.funding_reserved)
        
        # Update status
        case.status = HousingStatus.RELOCATED
        case.relocation_date = datetime.now()
        
        # Generate completion certificate (blockchain)
        certificate = await self._generate_relocation_certificate(case)
        
        return RelocationCompletionResult(
            success=True,
            case=case,
            certificate=certificate,
            funds_released=release.amount
        )
```

---

## 5. DOMINICAN REPUBLIC GOVERNMENT API CONNECTORS

### 5.1 Official Government API Registry

```python
# connectors/dr_government_apis.py
"""
Official Dominican Republic Government API Connectors.
Based on actual government digital platforms and open data initiatives.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
import asyncio
import aiohttp
import json
from datetime import datetime

class DRGovAPI(Enum):
    # Tax & Revenue
    DGII = "dgii"                    # Dirección General de Impuestos Internos
    DGII_COMPLIANCE = "dgii_compliance"
    
    # Social Protection
    SUPÉRATE = "superate"            # SUPÉRATE program (formerly PROSOLI)
    ADESS = "adess"                  # Administradora de Subsidios Sociales
    SIUBEN = "siuben"                # Sistema Único de Beneficiarios
    
    # Utilities
    EDE_NORTE = "ede_norte"          # Empresa Distribuidora de Electricidad Norte
    EDE_SUR = "ede_sur"              # Empresa Distribuidora de Electricidad Sur
    EDE_ESTE = "ede_este"            # Empresa Distribuidora de Electricidad Este
    CORAASAN = "coraasan"            # Corporación de Acueducto y Alcantarillado de Santiago
    CORAAMOCA = "coraamoca"          # Corporación de Acueducto y Alcantarillado de Moca
    INAPA = "inapa"                  # Instituto Nacional de Aguas Potables y Alcantarillados
    CAASD = "caasd"                  # Corporación del Acueducto y Alcantarillado de Santo Domingo
    
    # Housing & Infrastructure
    MIVHED = "mivhed"                # Ministerio de la Vivienda y Edificaciones
    MIVHED_RELOCATION = "mivhed_relocation"
    MIVHED_SUBSIDY = "mivhed_subsidy"
    
    # Identity & Civil Registry
    JCE = "jce"                      # Junta Central Electoral (Cédula validation)
    JCE_CEDULA = "jce_cedula"
    
    # Employment & Training
    INFOTEP = "infotep"              # Instituto de Formación Técnico Profesional
    MT = "mt"                        # Ministerio de Trabajo
    
    # Environment & Disaster
    COE = "coe"                      # Centro de Operaciones de Emergencia
    INDRHI = "indrhi"                # Instituto Nacional de Recursos Hidráulicos
    MINISTERIO_AMBIENTE = "ambiente"
    
    # Procurement & Transparency
    DGCP = "dgcp"                    # Dirección General de Contrataciones Públicas
    PORTAL_TRANSPARENCIA = "transparencia"
    
    # Financial
    BANCO_CENTRAL = "banco_central"  # Banco Central de la República Dominicana
    BANRESERVAS = "banreservas"      # Banco de Reservas

@dataclass
class APIEndpoint:
    name: str
    base_url: str
    auth_type: str                  # "oauth2", "api_key", "certificate", "none"
    endpoints: Dict[str, str]       # operation -> path
    rate_limit: int                 # requests per minute
    requires_whitelist: bool
    documentation_url: str
    sandbox_url: Optional[str] = None

# Official API Endpoints Configuration
DR_API_REGISTRY: Dict[DRGovAPI, APIEndpoint] = {
    DRGovAPI.DGII: APIEndpoint(
        name="DGII - Dirección General de Impuestos Internos",
        base_url="https://api.dgii.gov.do",
        auth_type="oauth2",
        endpoints={
            "taxpayer_status": "/v1/contribuyentes/{rnc}/estado",
            "payment_history": "/v1/contribuyentes/{rnc}/pagos",
            "compliance_certificate": "/v1/contribuyentes/{rnc}/certificado",
            "tax_debt": "/v1/contribuyentes/{rnc}/deudas",
        },
        rate_limit=60,
        requires_whitelist=True,
        documentation_url="https://developer.dgii.gov.do",
        sandbox_url="https://sandbox-api.dgii.gov.do"
    ),
    
    DRGovAPI.SUPÉRATE: APIEndpoint(
        name="SUPÉRATE - Programa de Protección Social",
        base_url="https://api.superate.gob.do",
        auth_type="oauth2",
        endpoints={
            "beneficiary_status": "/v1/beneficiarios/{cedula}/estado",
            "participation_history": "/v1/beneficiarios/{cedula}/historial",
            "conditional_compliance": "/v1/beneficiarios/{cedula}/cumplimiento",
            "household_composition": "/v1/beneficiarios/{cedula}/hogar",
        },
        rate_limit=100,
        requires_whitelist=True,
        documentation_url="https://developer.superate.gob.do",
        sandbox_url="https://sandbox-api.superate.gob.do"
    ),
    
    DRGovAPI.ADESS: APIEndpoint(
        name="ADESS - Administradora de Subsidios Sociales",
        base_url="https://api.adess.gob.do",
        auth_type="oauth2",
        endpoints={
            "subsidy_status": "/v1/subsidios/{cedula}/estado",
            "payment_calendar": "/v1/subsidios/calendario",
            "bonogas_status": "/v1/bonogas/{cedula}",
            "bonoluz_status": "/v1/bonoluz/{cedula}",
        },
        rate_limit=100,
        requires_whitelist=True,
        documentation_url="https://developer.adess.gob.do",
        sandbox_url="https://sandbox-api.adess.gob.do"
    ),
    
    DRGovAPI.EDE_NORTE: APIEndpoint(
        name="EDE NORTE - Electricidad Norte",
        base_url="https://api.edenorte.com.do",
        auth_type="api_key",
        endpoints={
            "account_balance": "/v1/cuentas/{numero_cuenta}/saldo",
            "payment_history": "/v1/cuentas/{numero_cuenta}/pagos",
            "consumption_history": "/v1/cuentas/{numero_cuenta}/consumo",
            "make_payment": "/v1/pagos",
            "service_status": "/v1/cuentas/{numero_cuenta}/estado",
        },
        rate_limit=120,
        requires_whitelist=True,
        documentation_url="https://developer.edenorte.com.do",
        sandbox_url="https://sandbox-api.edenorte.com.do"
    ),
    
    DRGovAPI.CORAASAN: APIEndpoint(
        name="CORAASAN - Acueducto Santiago",
        base_url="https://api.coraasan.gob.do",
        auth_type="api_key",
        endpoints={
            "account_status": "/v1/cuentas/{numero_cuenta}/estado",
            "balance": "/v1/cuentas/{numero_cuenta}/saldo",
            "consumption": "/v1/cuentas/{numero_cuenta}/consumo",
            "make_payment": "/v1/pagos",
            "service_request": "/v1/solicitudes",
        },
        rate_limit=60,
        requires_whitelist=True,
        documentation_url="https://developer.coraasan.gob.do",
    ),
    
    DRGovAPI.MIVHED: APIEndpoint(
        name="MIVHED - Ministerio de Vivienda",
        base_url="https://api.mivhed.gob.do",
        auth_type="oauth2",
        endpoints={
            "housing_projects": "/v1/proyectos",
            "available_units": "/v1/unidades/disponibles",
            "subsidy_application": "/v1/subsidios/solicitud",
            "relocation_request": "/v1/relocalizacion/solicitud",
            "assignment_status": "/v1/asignaciones/{solicitud_id}",
        },
        rate_limit=50,
        requires_whitelist=True,
        documentation_url="https://developer.mivhed.gob.do",
        sandbox_url="https://sandbox-api.mivhed.gob.do"
    ),
    
    DRGovAPI.JCE_CEDULA: APIEndpoint(
        name="JCE - Validación de Cédula",
        base_url="https://api.jce.gob.do",
        auth_type="certificate",
        endpoints={
            "validate_cedula": "/v1/cedula/validar",
            "get_citizen_data": "/v1/cedula/{cedula}/datos",
            "biometric_verify": "/v1/cedula/biometrico",
        },
        rate_limit=200,
        requires_whitelist=True,
        documentation_url="https://developer.jce.gob.do",
    ),
    
    DRGovAPI.DGCP: APIEndpoint(
        name="DGCP - Contrataciones Públicas",
        base_url="https://api.dgcp.gob.do",
        auth_type="oauth2",
        endpoints={
            "contractor_search": "/v1/proveedores/buscar",
            "contract_details": "/v1/contratos/{id}",
            "bidding_processes": "/v1/procesos",
            "compliance_check": "/v1/proveedores/{rnc}/cumplimiento",
        },
        rate_limit=60,
        requires_whitelist=False,  # Public data
        documentation_url="https://developer.dgcp.gob.do",
    ),
    
    DRGovAPI.COE: APIEndpoint(
        name="COE - Centro de Operaciones de Emergencia",
        base_url="https://api.coe.gob.do",
        auth_type="none",
        endpoints={
            "active_alerts": "/v1/alertas/activas",
            "disaster_declarations": "/v1/declaraciones",
            "hazard_zones": "/v1/zonas-peligro",
            "evacuation_orders": "/v1/evacuaciones",
        },
        rate_limit=30,
        requires_whitelist=False,
        documentation_url="https://developer.coe.gob.do",
    ),
}
```

### 5.2 Generic API Connector Base Class

```python
# connectors/base_connector.py
"""
Base connector for all DR Government APIs with:
- Authentication management (OAuth2, API Key, Certificate)
- Rate limiting
- Retry logic with exponential backoff
- Request/response logging for audit
- Sandbox/production switching
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional
import asyncio
import aiohttp
import time
from datetime import datetime
import logging

@dataclass
class APIResponse:
    success: bool
    data: Any = None
    error: str = ""
    status_code: int = 0
    response_time_ms: int = 0
    request_id: str = ""
    cached: bool = False

@dataclass
class AuthConfig:
    auth_type: str
    client_id: str = ""
    client_secret: str = ""
    api_key: str = ""
    certificate_path: str = ""
    certificate_password: str = ""
    token_url: str = ""
    scope: str = ""

class BaseDRGovConnector(ABC):
    """Base class for all DR Government API connectors"""
    
    def __init__(self, 
                 api_enum: DRGovAPI,
                 auth_config: AuthConfig,
                 use_sandbox: bool = False):
        self.api_enum = api_enum
        self.config = DR_API_REGISTRY[api_enum]
        self.auth = auth_config
        self.use_sandbox = use_sandbox
        self.base_url = self.config.sandbox_url if use_sandbox else self.config.base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.token: Optional[str] = None
        self.token_expires: float = 0
        self.rate_limiter = RateLimiter(self.config.rate_limit)
        self.logger = logging.getLogger(f"dr_gov.{api_enum.value}")
        self.audit_logger = AuditLogger()
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        if self.auth.auth_type == "oauth2":
            await self._refresh_token()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _refresh_token(self):
        """Refresh OAuth2 token"""
        if self.auth.auth_type != "oauth2":
            return
        
        async with self.session.post(
            self.auth.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.auth.client_id,
                "client_secret": self.auth.client_secret,
                "scope": self.auth.scope
            }
        ) as resp:
            data = await resp.json()
            self.token = data["access_token"]
            self.token_expires = time.time() + data["expires_in"] - 60  # 1 min buffer
    
    async def _ensure_auth(self):
        """Ensure valid authentication"""
        if self.auth.auth_type == "oauth2" and time.time() >= self.token_expires:
            await self._refresh_token()
    
    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "User-Agent": "DR-Governance-Platform/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        if self.auth.auth_type == "oauth2" and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        elif self.auth.auth_type == "api_key" and self.auth.api_key:
            headers["X-API-Key"] = self.auth.api_key
        elif self.auth.auth_type == "certificate":
            # Certificate auth handled at TLS layer
            pass
        
        return headers
    
    async def request(self, 
                      operation: str, 
                      params: Dict = None, 
                      data: Dict = None,
                      method: str = "GET") -> APIResponse:
        """Make authenticated, rate-limited request with audit logging"""
        
        await self.rate_limiter.acquire()
        await self._ensure_auth()
        
        endpoint = self.config.endpoints.get(operation)
        if not endpoint:
            return APIResponse(success=False, error=f"Unknown operation: {operation}", status_code=404)
        
        url = f"{self.base_url}{endpoint}"
        
        # Format URL with path parameters
        if params:
            for key, value in params.items():
                url = url.replace(f"{{{key}}}", str(value))
        
        request_id = self._generate_request_id()
        start_time = time.time()
        
        try:
            async with self.session.request(
                method, url,
                headers=self._get_headers(),
                params=params,
                json=data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                response_time = int((time.time() - start_time) * 1000)
                response_data = await resp.json() if resp.content_type == 'application/json' else await resp.text()
                
                result = APIResponse(
                    success=200 <= resp.status < 300,
                    data=response_data if 200 <= resp.status < 300 else None,
                    error=response_data if not (200 <= resp.status < 300) else "",
                    status_code=resp.status,
                    response_time_ms=response_time,
                    request_id=request_id
                )
                
                # Audit log
                await self.audit_logger.log_request(
                    api=self.api_enum.value,
                    operation=operation,
                    request_id=request_id,
                    success=result.success,
                    response_time=response_time
                )
                
                return result
                
        except asyncio.TimeoutError:
            return APIResponse(success=False, error="Request timeout", status_code=408, request_id=request_id)
        except Exception as e:
            return APIResponse(success=False, error=str(e), status_code=500, request_id=request_id)
    
    @abstractmethod
    async def health_check(self) -> APIResponse:
        """Check API availability"""
        pass
    
    def _generate_request_id(self) -> str:
        return f"{self.api_enum.value}_{int(time.time() * 1000)}"
```

### 5.3 Specific Connector Implementations

```python
# connectors/specific_connectors.py
"""
Specific implementations for key DR Government APIs.
"""

class DGIIConnector(BaseDRGovConnector):
    """DGII - Tax Authority Connector"""
    
    def __init__(self, auth_config: AuthConfig, use_sandbox: bool = False):
        super().__init__(DRGovAPI.DGII, auth_config, use_sandbox)
    
    async def health_check(self) -> APIResponse:
        return await self.request("taxpayer_status", params={"rnc": "130000000"})
    
    async def get_taxpayer_status(self, rnc: str) -> APIResponse:
        return await self.request("taxpayer_status", params={"rnc": rnc})
    
    async def get_payment_history(self, rnc: str, year: int = None) -> APIResponse:
        params = {"rnc": rnc}
        if year:
            params["year"] = year
        return await self.request("payment_history", params=params)
    
    async def get_compliance_certificate(self, rnc: str) -> APIResponse:
        return await self.request("compliance_certificate", params={"rnc": rnc})
    
    async def check_tax_compliance_for_merits(self, rnc: str) -> TaxComplianceResult:
        """Check tax compliance specifically for merit calculation"""
        status_resp = await self.get_taxpayer_status(rnc)
        if not status_resp.success:
            return TaxComplianceResult(compliant=False, reason="API error")
        
        # Parse status for compliance indicators
        status_data = status_resp.data
        compliant = (
            status_data.get("estado") == "ACTIVO" and
            not status_data.get("tiene_deudas", True) and
            status_data.get("ultima_declaracion") is not None
        )
        
        return TaxComplianceResult(
            compliant=compliant,
            status=status_data.get("estado"),
            has_debts=status_data.get("tiene_deudas", True),
            last_filing=status_data.get("ultima_declaracion"),
            details=status_data
        )

class SUPÉRATEConnector(BaseDRGovConnector):
    """SUPÉRATE Social Program Connector"""
    
    def __init__(self, auth_config: AuthConfig, use_sandbox: bool = False):
        super().__init__(DRGovAPI.SUPÉRATE, auth_config, use_sandbox)
    
    async def health_check(self) -> APIResponse:
        return await self.request("beneficiary_status", params={"cedula": "00000000000"})
    
    async def get_beneficiary_status(self, cedula: str) -> APIResponse:
        return await self.request("beneficiary_status", params={"cedula": cedula})
    
    async def get_participation_history(self, cedula: str) -> APIResponse:
        return await self.request("participation_history", params={"cedula": cedula})
    
    async def get_conditional_compliance(self, cedula: str) -> APIResponse:
        return await self.request("conditional_compliance", params={"cedula": cedula})
    
    async def check_social_participation_for_merits(self, cedula: str) -> SocialParticipationResult:
        """Check SUPÉRATE participation for merit calculation"""
        status_resp = await self.get_beneficiary_status(cedula)
        compliance_resp = await self.get_conditional_compliance(cedula)
        history_resp = await self.get_participation_history(cedula)
        
        if not all(r.success for r in [status_resp, compliance_resp, history_resp]):
            return SocialParticipationResult(participating=False, reason="API error")
        
        status = status_resp.data
        compliance = compliance_resp.data
        history = history_resp.data
        
        # Calculate participation metrics
        months_active = len([h for h in history.get("pagos", []) if h.get("estado") == "PAGADO"])
        compliance_rate = compliance.get("tasa_cumplimiento", 0)
        
        return SocialParticipationResult(
            participating=status.get("activo", False),
            months_active=months_active,
            compliance_rate=compliance_rate,
            household_size=status.get("tamano_hogar", 1),
            program_type=status.get("tipo_programa"),
            details={"status": status, "compliance": compliance, "history": history}
        )

class UtilityPaymentConnector(BaseDRGovConnector):
    """Base connector for utility payments (EDE, CORAASAN, CAASD, INAPA)"""
    
    def __init__(self, api_enum: DRGovAPI, auth_config: AuthConfig, use_sandbox: bool = False):
        super().__init__(api_enum, auth_config, use_sandbox)
    
    async def get_account_balance(self, account_number: str) -> APIResponse:
        return await self.request("account_balance", params={"numero_cuenta": account_number})
    
    async def get_consumption_history(self, account_number: str, months: int = 12) -> APIResponse:
        return await self.request("consumption_history", params={"numero_cuenta": account_number, "meses": months})
    
    async def make_payment(self, payment_data: Dict) -> APIResponse:
        return await self.request("make_payment", data=payment_data, method="POST")
    
    async def pay_utility_bill(self, 
                               account_number: str, 
                               amount_dop: Decimal,
                               reference: str,
                               citizen_id: str) -> PaymentResult:
        """Execute utility payment with full audit trail"""
        
        payment_data = {
            "numero_cuenta": account_number,
            "monto": str(amount_dop),
            "referencia": reference,
            "cedula_pagador": citizen_id,
            "fecha": datetime.now().isoformat(),
            "canal": "GOBERNANZA_AUTOMATIZADA"
        }
        
        resp = await self.make_payment(payment_data)
        
        return PaymentResult(
            success=resp.success,
            transaction_id=resp.data.get("transaccion_id") if resp.success else None,
            amount=amount_dop,
            account=account_number,
            error=resp.error if not resp.success else None,
            raw_response=resp.data
        )

class EDEConnector(UtilityPaymentConnector):
    """EDE Norte/Sur/Este Connector"""
    
    def __init__(self, region: str, auth_config: AuthConfig, use_sandbox: bool = False):
        api_map = {
            "norte": DRGovAPI.EDE_NORTE,
            "sur": DRGovAPI.EDE_SUR,
            "este": DRGovAPI.EDE_ESTE,
        }
        super().__init__(api_map[region], auth_config, use_sandbox)
        self.region = region

class WaterUtilityConnector(UtilityPaymentConnector):
    """Water utility connector (CORAASAN, CORAAMOCA, INAPA, CAASD)"""
    
    def __init__(self, provider: str, auth_config: AuthConfig, use_sandbox: bool = False):
        api_map = {
            "coraasan": DRGovAPI.CORAASAN,
            "coraamoca": DRGovAPI.CORAAMOCA,
            "inapa": DRGovAPI.INAPA,
            "caasd": DRGovAPI.CAASD,
        }
        super().__init__(api_map[provider], auth_config, use_sandbox)
        self.provider = provider

class MIVHEDConnector(BaseDRGovConnector):
    """MIVHED Housing & Relocation Connector"""
    
    def __init__(self, auth_config: AuthConfig, use_sandbox: bool = False):
        super().__init__(DRGovAPI.MIVHED, auth_config, use_sandbox)
    
    async def health_check(self) -> APIResponse:
        return await self.request("housing_projects")
    
    async def get_available_units(self, filters: Dict = None) -> APIResponse:
        return await self.request("available_units", params=filters or {})
    
    async def submit_relocation_request(self, request_data: Dict) -> APIResponse:
        return await self.request("relocation_request", data=request_data, method="POST")
    
    async def get_assignment_status(self, solicitud_id: str) -> APIResponse:
        return await self.request("assignment_status", params={"solicitud_id": solicitud_id})
    
    async def notify_assignment(self, citizen_id: str, unit_id: str, case_id: str) -> APIResponse:
        return await self.request("assignment_notification", data={
            "cedula": citizen_id,
            "unidad_id": unit_id,
            "caso_id": case_id,
            "fecha_asignacion": datetime.now().isoformat()
        }, method="POST")

class JCEConnector(BaseDRGovConnector):
    """JCE Cédula Validation Connector"""
    
    def __init__(self, auth_config: AuthConfig, use_sandbox: bool = False):
        super().__init__(DRGovAPI.JCE_CEDULA, auth_config, use_sandbox)
    
    async def health_check(self) -> APIResponse:
        return await self.request("validate_cedula", params={"cedula": "00000000000"})
    
    async def validate_cedula(self, cedula: str) -> APIResponse:
        return await self.request("validate_cedula", params={"cedula": cedula})
    
    async def get_citizen_data(self, cedula: str) -> APIResponse:
        return await self.request("get_citizen_data", params={"cedula": cedula})
    
    async def biometric_verify(self, cedula: str, biometric_data: bytes) -> APIResponse:
        return await self.request("biometric_verify", data={
            "cedula": cedula,
            "biometrico": biometric_data.hex()
        }, method="POST")
```

---

## 6. MERITED SOCIAL PLATFORM DATA CONNECTOR

### 6.1 Social Platform Integration

```python
# connectors/social_platforms.py
"""
Merited Social Platform Data Connectors.
Integrates: SUPÉRATE, ADESS, SIUBEN, INFOTEP, Community Platforms.
"""

class MeritedSocialPlatformConnector:
    """
    Unified connector for all merited social platforms.
    Fetches participation data for merit calculation.
    """
    
    def __init__(self):
        self.connectors = {
            'superate': SUPÉRATEConnector,
            'adess': ADESSConnector,
            'siuben': SIUBENConnector,
            'infotep': INFOTEPConnector,
            'junta_vecinos': JuntaVecinosConnector,
            'veeduria_ciudadana': VeeduriaConnector,
        }
        self.initialized: Dict[str, BaseDRGovConnector] = {}
    
    async def initialize_all(self, auth_configs: Dict[str, AuthConfig]):
        """Initialize all connectors with their auth configs"""
        for name, connector_class in self.connectors.items():
            if name in auth_configs:
                connector = connector_class(auth_configs[name])
                await connector.__aenter__()
                self.initialized[name] = connector
    
    async def fetch_all_participation_data(self, citizen_id: str, cedula: str) -> Dict[str, Any]:
        """Fetch participation data from all platforms in parallel"""
        
        tasks = {}
        for name, connector in self.initialized.items():
            if name == 'superate':
                tasks[name] = connector.check_social_participation_for_merits(cedula)
            elif name == 'adess':
                tasks[name] = connector.check_subsidy_compliance(cedula)
            elif name == 'siuben':
                tasks[name] = connector.get_household_index(cedula)
            elif name == 'infotep':
                tasks[name] = connector.get_training_records(citizen_id)
            elif name == 'junta_vecinos':
                tasks[name] = connector.get_participation_record(citizen_id)
            elif name == 'veeduria_ciudadana':
                tasks[name] = connector.get_oversight_record(citizen_id)
        
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        return dict(zip(tasks.keys(), results))
    
    async def calculate_social_merits(self, citizen_id: str, cedula: str) -> SocialMeritCalculation:
        """Calculate total social merits from all platforms"""
        
        data = await self.fetch_all_participation_data(citizen_id, cedula)
        
        total_merits = 0
        breakdown = {}
        
        # SUPÉRATE participation
        if 'superate' in data and not isinstance(data['superate'], Exception):
            sp = data['superate']
            if sp.participating:
                merits = sp.months_active * 30  # 30 merits/month
                total_merits += merits
                breakdown['superate'] = merits
        
        # ADESS subsidy compliance
        if 'adess' in data and not isinstance(data['adess'], Exception):
            adess = data['adess']
            if adess.compliant:
                merits = adess.months_compliant * 20
                total_merits += merits
                breakdown['adess'] = merits
        
        # SIUBEN vulnerability index (lower index = more vulnerable = more merits for participation)
        if 'siuben' in data and not isinstance(data['siuben'], Exception):
            siuben = data['siuben']
            if siuben.registered:
                # Bonus for keeping SIUBEN updated
                merits = 10 if siuben.updated_recently else 0
                total_merits += merits
                breakdown['siuben'] = merits
        
        # INFOTEP training
        if 'infotep' in data and not isinstance(data['infotep'], Exception):
            infotep = data['infotep']
            merits = infotep.courses_completed * 150
            total_merits += merits
            breakdown['infotep'] = merits
        
        # Junta de Vecinos participation
        if 'junta_vecinos' in data and not isinstance(data['junta_vecinos'], Exception):
            junta = data['junta_vecinos']
            merits = junta.meetings_attended * 20
            total_merits += merits
            breakdown['junta_vecinos'] = merits
        
        # Veeduría Ciudadana (high value)
        if 'veeduria_ciudadana' in data and not isinstance(data['veeduria_ciudadana'], Exception):
            veeduria = data['veeduria_ciudadana']
            merits = veeduria.projects_monitored * 100
            total_merits += merits
            breakdown['veeduria_ciudadana'] = merits
        
        return SocialMeritCalculation(
            citizen_id=citizen_id,
            total_merits=total_merits,
            breakdown=breakdown,
            source_data=data,
            calculated_at=datetime.now()
        )

class INFOTEPConnector(BaseDRGovConnector):
    """INFOTEP Training Records Connector"""
    
    def __init__(self, auth_config: AuthConfig, use_sandbox: bool = False):
        super().__init__(DRGovAPI.INFOTEP, auth_config, use_sandbox)
    
    async def get_training_records(self, citizen_id: str) -> TrainingRecordResult:
        # INFOTEP uses citizen_id (not cédula) for training records
        resp = await self.request("training_records", params={"citizen_id": citizen_id})
        if not resp.success:
            return TrainingRecordResult(courses_completed=0, certifications=0)
        
        courses = resp.data.get("cursos", [])
        certs = resp.data.get("certificaciones", [])
        
        return TrainingRecordResult(
            courses_completed=len([c for c in courses if c.get("estado") == "APROBADO"]),
            certifications=len([c for c in certs if c.get("vigente", False)]),
            details=resp.data
        )

class JuntaVecinosConnector:
    """Community Board Participation Connector (local government platforms)"""
    
    def __init__(self, api_base: str = "https://api.juntas.gob.do"):
        self.api_base = api_base
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    async def get_participation_record(self, citizen_id: str) -> ParticipationRecord:
        # Query municipal platform for Junta de Vecinos participation
        async with self.session.get(f"{self.api_base}/v1/participacion/{citizen_id}") as resp:
            if resp.status != 200:
                return ParticipationRecord(meetings_attended=0)
            
            data = await resp.json()
            return ParticipationRecord(
                meetings_attended=data.get("reuniones_asistidas", 0),
                positions_held=data.get("cargos_ocupados", []),
                projects_participated=data.get("proyectos_participados", []),
                details=data
            )

class VeeduriaConnector:
    """Citizen Oversight (Veeduría) Participation Connector"""
    
    def __init__(self, api_base: str = "https://api.veeduria.gob.do"):
        self.api_base = api_base
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    async def get_oversight_record(self, citizen_id: str) -> OversightRecord:
        async with self.session.get(f"{self.api_base}/v1/veedores/{citizen_id}") as resp:
            if resp.status != 200:
                return OversightRecord(projects_monitored=0)
            
            data = await resp.json()
            return OversightRecord(
                projects_monitored=len(data.get("proyectos", [])),
                reports_filed=data.get("reportes_presentados", 0),
                anomalies_detected=data.get("anomalias_detectadas", 0),
                details=data
            )
```

---

## 7. INSTANT API APPLICATION AUTOMATION ENGINE

### 7.1 Event-Driven Automation

```python
# automation/instant_api_engine.py
"""
Instant API Application Engine.
Event-driven automation that instantly applies APIs when conditions are met.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
import asyncio
from datetime import datetime
import json

class TriggerType(Enum):
    MERIT_THRESHOLD_REACHED = "merit_threshold_reached"
    RELOCATION_VERIFIED = "relocation_verified"
    UTILITY_BILL_DUE = "utility_bill_due"
    HOUSING_ASSIGNED = "housing_assigned"
    APPLIANCE_VOUCHER_READY = "appliance_voucher_ready"
    CONTEXT_FILING_DUE = "context_filing_due"
    SCHEDULED = "scheduled"
    MANUAL = "manual"

class AutomationStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class AutomationTrigger:
    trigger_id: str
    trigger_type: TriggerType
    citizen_id: str
    conditions: Dict[str, Any]
    priority: int = 1
    created_at: datetime = datetime.now()
    metadata: Dict = None

@dataclass
class AutomationExecution:
    execution_id: str
    trigger_id: str
    citizen_id: str
    actions: List[AutomationAction]
    status: AutomationStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    results: List[ActionResult] = None
    error: str = ""

@dataclass
class AutomationAction:
    action_id: str
    action_type: str              # "api_call", "fund_transfer", "notification", "record_update"
    target_api: str               # API endpoint identifier
    parameters: Dict[str, Any]
    depends_on: List[str] = None  # Other action_ids this depends on
    retry_policy: RetryPolicy = None
    timeout_seconds: int = 30

@dataclass
class RetryPolicy:
    max_retries: int = 3
    base_delay_seconds: int = 5
    max_delay_seconds: int = 300
    exponential_base: float = 2.0

class InstantAPIApplicationEngine:
    """
    Event-driven automation engine for instant API application.
    Triggers: Merit thresholds, relocation verification, bill due dates, etc.
    Actions: API calls, fund transfers, notifications, record updates.
    """
    
    def __init__(self):
        self.triggers: Dict[str, AutomationTrigger] = {}
        self.executions: Dict[str, AutomationExecution] = {}
        self.action_handlers: Dict[str, Callable] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        
        # Register default action handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register built-in action handlers"""
        self.action_handlers.update({
            'utility_payment': self._handle_utility_payment,
            'housing_fund_release': self._handle_housing_fund_release,
            'appliance_voucher_issue': self._handle_appliance_voucher,
            'context_filing': self._handle_context_filing,
            'notification_send': self._handle_notification,
            'merit_deduction': self._handle_merit_deduction,
            'record_update': self._handle_record_update,
            'blockchain_anchor': self._handle_blockchain_anchor,
        })
    
    def register_trigger(self, trigger: AutomationTrigger):
        """Register a new automation trigger"""
        self.triggers[trigger.trigger_id] = trigger
    
    async def fire_trigger(self, trigger_id: str, context: Dict = None):
        """Fire a trigger immediately"""
        trigger = self.triggers.get(trigger_id)
        if not trigger:
            raise ValueError(f"Trigger not found: {trigger_id}")
        
        # Merge context
        execution_context = {**trigger.conditions, **(context or {})}
        
        # Create execution
        execution = AutomationExecution(
            execution_id=f"exec_{trigger_id}_{int(datetime.now().timestamp())}",
            trigger_id=trigger_id,
            citizen_id=trigger.citizen_id,
            actions=self._build_actions_for_trigger(trigger, execution_context),
            status=AutomationStatus.PENDING,
            started_at=datetime.now()
        )
        
        self.executions[execution.execution_id] = execution
        
        # Execute asynchronously
        asyncio.create_task(self._execute_automation(execution))
    
    def _build_actions_for_trigger(self, trigger: AutomationTrigger, context: Dict) -> List[AutomationAction]:
        """Build action sequence based on trigger type"""
        
        action_builders = {
            TriggerType.MERIT_THRESHOLD_REACHED: self._build_merit_threshold_actions,
            TriggerType.RELOCATION_VERIFIED: self._build_relocation_actions,
            TriggerType.UTILITY_BILL_DUE: self._build_utility_bill_actions,
            TriggerType.HOUSING_ASSIGNED: self._build_housing_assignment_actions,
            TriggerType.APPLIANCE_VOUCHER_READY: self._build_appliance_voucher_actions,
            TriggerType.CONTEXT_FILING_DUE: self._build_context_filing_actions,
        }
        
        builder = action_builders.get(trigger.trigger_type)
        if builder:
            return builder(trigger, context)
        return []
    
    def _build_merit_threshold_actions(self, trigger: AutomationTrigger, context: Dict) -> List[AutomationAction]:
        """Build actions for merit threshold reached"""
        citizen_id = trigger.citizen_id
        front = context.get('front', 'UTILITY_FUND')
        amount = context.get('amount_dop', 0)
        
        return [
            AutomationAction(
                action_id="reserve_funds",
                action_type="api_call",
                target_api="CENTRAL_AI_FUND",
                parameters={
                    "operation": "reserve_funds",
                    "citizen_id": citizen_id,
                    "front": front,
                    "amount_dop": amount
                }
            ),
            AutomationAction(
                action_id="notify_citizen",
                action_type="notification",
                target_api="NOTIFICATION_SERVICE",
                parameters={
                    "citizen_id": citizen_id,
                    "type": "MERIT_ALLOCATION_READY",
                    "front": front,
                    "amount": amount
                },
                depends_on=["reserve_funds"]
            ),
        ]
    
    def _build_utility_bill_actions(self, trigger: AutomationTrigger, context: Dict) -> List[AutomationAction]:
        """Build actions for utility bill payment"""
        citizen_id = trigger.citizen_id
        utility_type = context.get('utility_type')  # electricity, water
        account_number = context.get('account_number')
        amount = context.get('amount_dop')
        
        api_map = {
            'electricity': 'EDE_PAYMENT',
            'water': 'WATER_PAYMENT'
        }
        
        return [
            AutomationAction(
                action_id="verify_funds",
                action_type="api_call",
                target_api="CENTRAL_AI_FUND",
                parameters={
                    "operation": "verify_available",
                    "citizen_id": citizen_id,
                    "front": "UTILITY_FUND",
                    "amount_dop": amount
                }
            ),
            AutomationAction(
                action_id="pay_bill",
                action_type="api_call",
                target_api=api_map.get(utility_type, 'UTILITY_PAYMENT'),
                parameters={
                    "operation": "pay_utility_bill",
                    "citizen_id": citizen_id,
                    "account_number": account_number,
                    "amount_dop": amount,
                    "reference": f"AUTO_{citizen_id}_{int(datetime.now().timestamp())}"
                },
                depends_on=["verify_funds"]
            ),
            AutomationAction(
                action_id="deduct_merits",
                action_type="merit_deduction",
                target_api="MERIT_LEDGER",
                parameters={
                    "citizen_id": citizen_id,
                    "amount_dop": amount,
                    "front": "UTILITY_FUND"
                },
                depends_on=["pay_bill"]
            ),
            AutomationAction(
                action_id="file_context",
                action_type="context_filing",
                target_api="CONTEXT_FILING_ENGINE",
                parameters={
                    "citizen_id": citizen_id,
                    "event_type": "UTILITY_PAYMENT",
                    "details": {"utility": utility_type, "amount": str(amount), "account": account_number}
                },
                depends_on=["deduct_merits"]
            ),
        ]
    
    async def _execute_automation(self, execution: AutomationExecution):
        """Execute automation with dependency resolution"""
        execution.status = AutomationStatus.RUNNING
        
        # Build dependency graph
        action_map = {a.action_id: a for a in execution.actions}
        completed = set()
        results = []
        
        # Execute in topological order
        while len(completed) < len(execution.actions):
            progress = False
            
            for action in execution.actions:
                if action.action_id in completed:
                    continue
                
                # Check dependencies
                deps = action.depends_on or []
                if not all(d in completed for d in deps):
                    continue
                
                # Execute action
                try:
                    result = await self._execute_action(action, execution.citizen_id)
                    results.append(result)
                    
                    if result.success:
                        completed.add(action.action_id)
                        progress = True
                    else:
                        # Handle failure
                        if action.retry_policy:
                            await self._retry_action(action, execution)
                        else:
                            execution.status = AutomationStatus.FAILED
                            execution.error = f"Action {action.action_id} failed: {result.error}"
                            execution.completed_at = datetime.now()
                            return
                
                except Exception as e:
                    execution.status = AutomationStatus.FAILED
                    execution.error = f"Action {action.action_id} exception: {str(e)}"
                    execution.completed_at = datetime.now()
                    return
            
            if not progress:
                # Circular dependency or stuck
                execution.status = AutomationStatus.FAILED
                execution.error = "Dependency resolution failed"
                execution.completed_at = datetime.now()
                return
        
        execution.status = AutomationStatus.COMPLETED
        execution.completed_at = datetime.now()
        execution.results = results
    
    async def _execute_action(self, action: AutomationAction, citizen_id: str) -> ActionResult:
        """Execute a single action"""
        handler = self.action_handlers.get(action.action_type)
        if not handler:
            return ActionResult(success=False, error=f"No handler for action type: {action.action_type}")
        
        try:
            result = await handler(action.parameters, citizen_id)
            return ActionResult(success=True, data=result)
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    # Action Handlers
    
    async def _handle_utility_payment(self, params: Dict, citizen_id: str) -> Dict:
        # This would use the utility connectors
        # Implementation depends on specific utility
        pass
    
    async def _handle_housing_fund_release(self, params: Dict, citizen_id: str) -> Dict:
        # Release housing funds via Central AI
        pass
    
    async def _handle_appliance_voucher(self, params: Dict, citizen_id: str) -> Dict:
        # Issue appliance voucher
        pass
    
    async def _handle_context_filing(self, params: Dict, citizen_id: str) -> Dict:
        # File context report
        pass
    
    async def _handle_notification(self, params: Dict, citizen_id: str) -> Dict:
        # Send notification (WhatsApp, SMS, email, app)
        pass
    
    async def _handle_merit_deduction(self, params: Dict, citizen_id: str) -> Dict:
        # Deduct merits from available balance
        pass
    
    async def _handle_record_update(self, params: Dict, citizen_id: str) -> Dict:
        # Update database records
        pass
    
    async def _handle_blockchain_anchor(self, params: Dict, citizen_id: str) -> Dict:
        # Anchor to blockchain
        pass
```

### 7.2 Scheduled Automation (Cron-like)

```python
# automation/scheduler.py
"""
Scheduled automation for recurring tasks:
- Daily utility bill checks
- Weekly merit threshold evaluations
- Monthly context filing
- Quarterly housing eligibility reviews
"""

class AutomationScheduler:
    def __init__(self, engine: InstantAPIApplicationEngine):
        self.engine = engine
        self.jobs: Dict[str, ScheduledJob] = {}
        self.running = False
    
    def add_job(self, job: ScheduledJob):
        self.jobs[job.job_id] = job
    
    async def start(self):
        self.running = True
        asyncio.create_task(self._scheduler_loop())
    
    async def _scheduler_loop(self):
        while self.running:
            now = datetime.now()
            
            for job in self.jobs.values():
                if job.should_run(now):
                    # Create trigger context
                    context = await job.build_context()
                    
                    # Fire automation
                    await self.engine.fire_trigger(job.trigger_id, context)
                    
                    job.last_run = now
            
            await asyncio.sleep(60)  # Check every minute
    
    # Pre-defined scheduled jobs
    
    def setup_default_jobs(self):
        """Setup default scheduled automation jobs"""
        
        # Daily utility bill check (6 AM)
        self.add_job(ScheduledJob(
            job_id="daily_utility_check",
            trigger_id="utility_bill_check",
            cron="0 6 * * *",  # Daily at 6 AM
            build_context=self._build_utility_check_context
        ))
        
        # Weekly merit evaluation (Monday 8 AM)
        self.add_job(ScheduledJob(
            job_id="weekly_merit_evaluation",
            trigger_id="merit_evaluation",
            cron="0 8 * * 1",  # Monday 8 AM
            build_context=self._build_merit_evaluation_context
        ))
        
        # Monthly context filing (1st of month 9 AM)
        self.add_job(ScheduledJob(
            job_id="monthly_context_filing",
            trigger_id="context_filing_batch",
            cron="0 9 1 * *",  # 1st of month 9 AM
            build_context=self._build_context_filing_context
        ))
        
        # Quarterly housing review (quarterly)
        self.add_job(ScheduledJob(
            job_id="quarterly_housing_review",
            trigger_id="housing_eligibility_review",
            cron="0 10 1 */3 *",  # 1st of quarter 10 AM
            build_context=self._build_housing_review_context
        ))
    
    async def _build_utility_check_context(self) -> Dict:
        # Fetch citizens with due utility bills
        # This would query the utility APIs for due bills
        return {"check_type": "daily_utility_bills"}
    
    async def _build_merit_evaluation_context(self) -> Dict:
        return {"evaluation_type": "weekly_threshold_check"}
    
    async def _build_context_filing_context(self) -> Dict:
        return {"filing_type": "monthly_status_report"}
    
    async def _build_housing_review_context(self) -> Dict:
        return {"review_type": "quarterly_eligibility"}
```

---

## 8. CONTEXT FILING ENGINE

### 8.1 Multi-Source Context Aggregation

```python
# core/context_filing.py
"""
Context Filing Engine - Aggregates attendance, housing status, and other data sources
for automated reporting and compliance verification.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio

class ContextEventType(Enum):
    HOUSING_STATUS = "housing_status"
    UTILITY_PAYMENT = "utility_payment"
    RELOCATION_PROGRESS = "relocation_progress"
    MERIT_ALLOCATION = "merit_allocation"
    ATTENDANCE_REPORT = "attendance_report"
    COMPLIANCE_CHECK = "compliance_check"
    LIFECYCLE_EVENT = "lifecycle_event"

@dataclass
class ContextReport:
    report_id: str
    citizen_id: str
    event_type: ContextEventType
    timestamp: datetime
    data_sources: List[str]
    aggregated_data: Dict[str, Any]
    verification_status: str  # VERIFIED, PARTIAL, UNVERIFIED
    blockchain_hash: str = ""
    filed_at: datetime = None
    
    def __post_init__(self):
        if self.filed_at is None:
            self.filed_at = datetime.now()

class ContextFilingEngine:
    """
    Automated context filing from multiple data sources.
    Fetches: housing status, utility payments, attendance, compliance, merits.
    Files: Consolidated reports for audit, governance, and AI decision-making.
    """
    
    def __init__(self):
        self.data_fetchers: Dict[str, DataFetcher] = {}
        self.report_store = ReportStore()
        self.blockchain_anchor = BlockchainAnchor()
        self.verification_engine = VerificationEngine()
    
    def register_fetcher(self, source_name: str, fetcher: 'DataFetcher'):
        self.data_fetchers[source_name] = fetcher
    
    async def file_context_report(self, 
                                  citizen_id: str, 
                                  event_type: ContextEventType,
                                  required_sources: List[str] = None,
                                  custom_data: Dict = None) -> ContextReport:
        """File a context report by fetching from multiple sources"""
        
        # Determine sources to fetch
        sources = required_sources or self._get_default_sources(event_type)
        
        # Fetch from all sources in parallel
        fetch_tasks = {}
        for source in sources:
            if source in self.data_fetchers:
                fetch_tasks[source] = self.data_fetchers[source].fetch(citizen_id, event_type)
        
        results = await asyncio.gather(*fetch_tasks.values(), return_exceptions=True)
        source_data = dict(zip(fetch_tasks.keys(), results))
        
        # Aggregate data
        aggregated = self._aggregate_data(event_type, source_data, custom_data)
        
        # Verify
        verification = await self.verification_engine.verify(aggregated, source_data)
        
        # Create report
        report = ContextReport(
            report_id=self._generate_report_id(citizen_id, event_type),
            citizen_id=citizen_id,
            event_type=event_type,
            timestamp=datetime.now(),
            data_sources=list(source_data.keys()),
            aggregated_data=aggregated,
            verification_status=verification.status
        )
        
        # Blockchain anchor
        report.blockchain_hash = await self.blockchain_anchor.anchor_report(report)
        
        # Store
        await self.report_store.save(report)
        
        return report
    
    def _get_default_sources(self, event_type: ContextEventType) -> List[str]:
        mapping = {
            ContextEventType.HOUSING_STATUS: ['mivhed', 'property_registry', 'geospatial', 'utility_providers'],
            ContextEventType.UTILITY_PAYMENT: ['utility_provider', 'central_ai_fund', 'merit_ledger'],
            ContextEventType.RELOCATION_PROGRESS: ['mivhed', 'geospatial', 'community_verification'],
            ContextEventType.MERIT_ALLOCATION: ['merit_ledger', 'central_ai_fund', 'selecting_front'],
            ContextEventType.ATTENDANCE_REPORT: ['junta_vecinos', 'veeduria', 'infotep', 'superate'],
            ContextEventType.COMPLIANCE_CHECK: ['dgii', 'dgcp', 'superate', 'adess'],
            ContextEventType.LIFECYCLE_EVENT: ['jce', 'civil_registry'],
        }
        return mapping.get(event_type, [])
    
    def _aggregate_data(self, event_type: ContextEventType, source_data: Dict, custom_data: Dict) -> Dict:
        """Aggregate data from multiple sources based on event type"""
        
        aggregators = {
            ContextEventType.HOUSING_STATUS: self._aggregate_housing_status,
            ContextEventType.UTILITY_PAYMENT: self._aggregate_utility_payment,
            ContextEventType.RELOCATION_PROGRESS: self._aggregate_relocation_progress,
            ContextEventType.MERIT_ALLOCATION: self._aggregate_merit_allocation,
            ContextEventType.ATTENDANCE_REPORT: self._aggregate_attendance,
            ContextEventType.COMPLIANCE_CHECK: self._aggregate_compliance,
        }
        
        aggregator = aggregators.get(event_type, self._aggregate_generic)
        return aggregator(source_data, custom_data)
    
    def _aggregate_housing_status(self, source_data: Dict, custom: Dict) -> Dict:
        aggregated = {
            "citizen_id": custom.get("citizen_id"),
            "current_housing": {},
            "relocation_status": {},
            "utility_connections": {},
            "compliance": {}
        }
        
        # MIVHED data
        if 'mivhed' in source_data and not isinstance(source_data['mivhed'], Exception):
            mivhed = source_data['mivhed']
            aggregated["relocation_status"] = {
                "case_id": mivhed.get("case_id"),
                "status": mivhed.get("status"),
                "assigned_unit": mivhed.get("assigned_unit"),
                "relocation_date": mivhed.get("relocation_date")
            }
        
        # Property registry
        if 'property_registry' in source_data and not isinstance(source_data['property_registry'], Exception):
            prop = source_data['property_registry']
            aggregated["current_housing"] = {
                "owns_property": prop.get("owns_property"),
                "property_type": prop.get("property_type"),
                "habitable": prop.get("habitable"),
                "location": prop.get("location")
            }
        
        # Utility connections
        if 'utility_providers' in source_data and not isinstance(source_data['utility_providers'], Exception):
            utils = source_data['utility_providers']
            aggregated["utility_connections"] = {
                "electricity": utils.get("electricity_connected"),
                "water": utils.get("water_connected"),
                "internet": utils.get("internet_connected")
            }
        
        return aggregated
    
    def _aggregate_utility_payment(self, source_data: Dict, custom: Dict) -> Dict:
        return {
            "payment": {
                "utility_type": custom.get("utility_type"),
                "amount_dop": custom.get("amount_dop"),
                "account_number": custom.get("account_number"),
                "transaction_id": custom.get("transaction_id"),
                "status": "COMPLETED"
            },
            "funding": {
                "source": "MERIT_UTILITY_FUND",
                "merits_used": custom.get("merits_used"),
                "central_ai_reservation": custom.get("reservation_id")
            },
            "verification": {
                "utility_confirmed": source_data.get('utility_provider', {}).get('confirmed', False),
                "fund_deducted": source_data.get('central_ai_fund', {}).get('deducted', False),
                "merits_deducted": source_data.get('merit_ledger', {}).get('deducted', False)
            }
        }
    
    async def generate_periodic_report(self, citizen_id: str, period: str = "monthly") -> ContextReport:
        """Generate comprehensive periodic status report"""
        
        # Fetch all current statuses
        report = await self.file_context_report(
            citizen_id=citizen_id,
            event_type=ContextEventType.ATTENDANCE_REPORT,
            required_sources=[
                'mivhed', 'utility_providers', 'merit_ledger', 
                'junta_vecinos', 'veeduria', 'infotep', 'superate', 'adess'
            ]
        )
        
        # Add period metadata
        report.aggregated_data["period"] = period
        report.aggregated_data["generated_at"] = datetime.now().isoformat()
        
        return report

class DataFetcher(ABC):
    """Abstract base for data fetchers"""
    
    @abstractmethod
    async def fetch(self, citizen_id: str, event_type: ContextEventType) -> Dict:
        pass

class MIVHEDDataFetcher(DataFetcher):
    def __init__(self, connector: MIVHEDConnector):
        self.connector = connector
    
    async def fetch(self, citizen_id: str, event_type: ContextEventType) -> Dict:
        # Fetch housing/relocation status from MIVHED
        resp = await self.connector.get_citizen_status(citizen_id)
        return resp.data if resp.success else {}

class UtilityDataFetcher(DataFetcher):
    def __init__(self, connectors: Dict[str, UtilityPaymentConnector]):
        self.connectors = connectors
    
    async def fetch(self, citizen_id: str, event_type: ContextEventType) -> Dict:
        # Fetch utility status from all providers
        results = {}
        for name, connector in self.connectors.items():
            # Would need citizen's account numbers
            resp = await connector.get_account_status(citizen_id)
            results[name] = resp.data if resp.success else {}
        return {"providers": results}

class MeritLedgerFetcher(DataFetcher):
    def __init__(self, ledger: MeritLedger):
        self.ledger = ledger
    
    async def fetch(self, citizen_id: str, event_type: ContextEventType) -> Dict:
        profile = await self.ledger.get_profile(citizen_id)
        return {
            "total_merits": profile.total_merits,
            "tier": profile.tier.value,
            "front_assignment": profile.front_assignment,
            "category_breakdown": {k.value: v for k, v in profile.category_breakdown.items()}
        }
```

---

## 9. COMPLETE INTEGRATION EXAMPLE

### 9.1 End-to-End Flow: Citizen Merit → Utility Payment

```python
# integration/complete_flow.py
"""
Complete end-to-end integration example:
Citizen accumulates merits → Selecting Front → Central AI → Utility Payment → Context Filing
"""

class TaxMeritToUtilityFlow:
    """
    Orchestrates the complete flow from tax merit accumulation to utility payment.
    """
    
    def __init__(self):
        # Initialize all components
        self.merit_calculator = MeritCalculator(blockchain_anchor=BlockchainAnchor())
        self.merit_ledger = MeritLedger(db=Database(), blockchain=BlockchainAnchor())
        self.selecting_front = SelectingFrontDistributor(
            merit_ledger=self.merit_ledger,
            central_ai_fund=CentralAIFundManager()
        )
        self.central_ai = CentralAIFundManager()
        self.automation_engine = InstantAPIApplicationEngine()
        self.scheduler = AutomationScheduler(self.automation_engine)
        self.context_filing = ContextFilingEngine()
        
        # Initialize API connectors
        self._init_connectors()
        
        # Register data fetchers for context filing
        self._init_context_fetchers()
    
    def _init_connectors(self):
        # DGII for tax compliance
        self.dgii = DGIIConnector(
            auth_config=AuthConfig(
                auth_type="oauth2",
                client_id=os.getenv("DGII_CLIENT_ID"),
                client_secret=os.getenv("DGII_CLIENT_SECRET"),
                token_url="https://api.dgii.gov.do/oauth/token",
                scope="taxpayer_read"
            )
        )
        
        # SUPÉRATE for social participation
        self.superate = SUPÉRATEConnector(
            auth_config=AuthConfig(
                auth_type="oauth2",
                client_id=os.getenv("SUPÉRATE_CLIENT_ID"),
                client_secret=os.getenv("SUPÉRATE_CLIENT_SECRET"),
                token_url="https://api.superate.gob.do/oauth/token",
                scope="beneficiary_read"
            )
        )
        
        # Utility connectors
        self.ede_norte = EDEConnector("norte", AuthConfig(
            auth_type="api_key",
            api_key=os.getenv("EDE_NORTE_API_KEY")
        ))
        
        self.coraasan = WaterUtilityConnector("coraasan", AuthConfig(
            auth_type="api_key",
            api_key=os.getenv("CORAASAN_API_KEY")
        ))
        
        # MIVHED for housing
        self.mivhed = MIVHEDConnector(
            auth_config=AuthConfig(
                auth_type="oauth2",
                client_id=os.getenv("MIVHED_CLIENT_ID"),
                client_secret=os.getenv("MIVHED_CLIENT_SECRET"),
                token_url="https://api.mivhed.gob.do/oauth/token",
                scope="housing_read housing_write"
            )
        )
        
        # Social platform connector
        self.social_platforms = MeritedSocialPlatformConnector()
    
    def _init_context_fetchers(self):
        self.context_filing.register_fetcher('mivhed', MIVHEDDataFetcher(self.mivhed))
        self.context_filing.register_fetcher('utility_providers', UtilityDataFetcher({
            'ede_norte': self.ede_norte,
            'coraasan': self.coraasan
        }))
        self.context_filing.register_fetcher('merit_ledger', MeritLedgerFetcher(self.merit_ledger))
    
    async def process_citizen_tax_payment(self, citizen_id: str, rnc: str, payment_data: Dict) -> FlowResult:
        """Process tax payment and trigger merit accumulation"""
        
        # 1. Verify payment with DGII
        compliance = await self.dgii.check_tax_compliance_for_merits(rnc)
        
        if not compliance.compliant:
            return FlowResult(success=False, reason="Tax compliance not met")
        
        # 2. Calculate merits for tax compliance
        merit_event = await self.merit_calculator.calculate_merits(
            citizen_id=citizen_id,
            category=MeritCategory.TAX_COMPLIANCE,
            action="quarterly_on_time",
            evidence={
                "source_system": "DGII",
                "reference_id": payment_data.get("transaction_id"),
                "rnc": rnc,
                "amount": payment_data.get("amount"),
                "period": payment_data.get("period")
            }
        )
        
        # 3. Record in merit ledger
        recording = await self.merit_ledger.record_merit_event(merit_event)
        
        # 4. Check if selecting front threshold reached
        profile = recording.profile
        if profile.selecting_front_eligible and profile.front_assignment == "UTILITY_FUND":
            # 5. Trigger selecting front distribution
            distribution = await self.selecting_front.evaluate_and_distribute(citizen_id)
            
            if distribution.eligible:
                # 6. Automation will handle the rest via triggers
                await self.automation_engine.fire_trigger(
                    "merit_threshold_reached",
                    context={
                        "citizen_id": citizen_id,
                        "front": "UTILITY_FUND",
                        "amount_dop": float(distribution.total_funding_reserved)
                    }
                )
        
        return FlowResult(
            success=True,
            merit_event=merit_event,
            profile=profile,
            distribution=distribution if 'distribution' in locals() else None
        )
    
    async def process_utility_bill_payment(self, citizen_id: str, utility_type: str, 
                                           account_number: str, amount_dop: Decimal) -> FlowResult:
        """Process utility bill payment via merit funding"""
        
        # 1. Check merit balance and reserve funds
        reservation = await self.central_ai.reserve_funds(
            citizen_id=citizen_id,
            front=SelectingFront.UTILITY_FUND,
            amount_dop=amount_dop,
            merits_backing=int(amount_dop * 20)  # 1 merit = 50 DOP, so 20 merits per 1000 DOP
        )
        
        if not reservation.success:
            return FlowResult(success=False, reason=f"Fund reservation failed: {reservation.reason}")
        
        # 2. Execute payment via appropriate utility API
        if utility_type == "electricity":
            payment_result = await self.ede_norte.pay_utility_bill(
                account_number=account_number,
                amount_dop=amount_dop,
                reference=f"MERIT_{citizen_id}_{int(datetime.now().timestamp())}",
                citizen_id=citizen_id
            )
        elif utility_type == "water":
            payment_result = await self.coraasan.pay_utility_bill(
                account_number=account_number,
                amount_dop=amount_dop,
                reference=f"MERIT_{citizen_id}_{int(datetime.now().timestamp())}",
                citizen_id=citizen_id
            )
        else:
            return FlowResult(success=False, reason=f"Unknown utility type: {utility_type}")
        
        if not payment_result.success:
            # Release reservation
            await self.central_ai.release_reservation(reservation.reservation.reservation_id)
            return FlowResult(success=False, reason=f"Payment failed: {payment_result.error}")
        
        # 3. Deduct merits
        await self.merit_ledger.deduct_available_merits(
            citizen_id, 
            reservation.reservation.merits_backing
        )
        
        # 4. File context report
        context_report = await self.context_filing.file_context_report(
            citizen_id=citizen_id,
            event_type=ContextEventType.UTILITY_PAYMENT,
            custom_data={
                "citizen_id": citizen_id,
                "utility_type": utility_type,
                "amount_dop": amount_dop,
                "account_number": account_number,
                "transaction_id": payment_result.transaction_id,
                "merits_used": reservation.reservation.merits_backing,
                "reservation_id": reservation.reservation.reservation_id
            }
        )
        
        return FlowResult(
            success=True,
            payment_result=payment_result,
            context_report=context_report,
            reservation=reservation.reservation
        )
```

### 9.2 Configuration & Deployment

```python
# config/system_config.py
"""
System configuration for deployment.
"""

import os
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class SystemConfig:
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/governance")
    
    # Blockchain
    blockchain_rpc_url: str = os.getenv("BLOCKCHAIN_RPC", "http://localhost:8545")
    blockchain_contract_address: str = os.getenv("MERIT_CONTRACT", "0x...")
    
    # API Keys (loaded from environment/secrets manager)
    dgii_client_id: str = os.getenv("DGII_CLIENT_ID")
    dgii_client_secret: str = os.getenv("DGII_CLIENT_SECRET")
    
    superate_client_id: str = os.getenv("SUPÉRATE_CLIENT_ID")
    superate_client_secret: str = os.getenv("SUPÉRATE_CLIENT_SECRET")
    
    adess_client_id: str = os.getenv("ADESS_CLIENT_ID")
    adess_client_secret: str = os.getenv("ADESS_CLIENT_SECRET")
    
    ede_norte_api_key: str = os.getenv("EDE_NORTE_API_KEY")
    ede_sur_api_key: str = os.getenv("EDE_SUR_API_KEY")
    ede_este_api_key: str = os.getenv("EDE_ESTE_API_KEY")
    
    coraasan_api_key: str = os.getenv("CORAASAN_API_KEY")
    coraamoca_api_key: str = os.getenv("CORAAMOCA_API_KEY")
    inapa_api_key: str = os.getenv("INAPA_API_KEY")
    caasd_api_key: str = os.getenv("CAASD_API_KEY")
    
    mivhed_client_id: str = os.getenv("MIVHED_CLIENT_ID")
    mivhed_client_secret: str = os.getenv("MIVHED_CLIENT_SECRET")
    
    jce_cert_path: str = os.getenv("JCE_CERT_PATH")
    jce_cert_password: str = os.getenv("JCE_CERT_PASSWORD")
    
    infotep_client_id: str = os.getenv("INFOTEP_CLIENT_ID")
    infotep_client_secret: str = os.getenv("INFOTEP_CLIENT_SECRET")
    
    # Merit System Parameters
    merit_to_dop_rates: Dict = {
        "UTILITY_FUND": Decimal('50.0'),
        "HOUSING_RELOCATION": Decimal('100.0'),
        "APPLIANCE_FUND": Decimal('75.0'),
    }
    
    minimum_merits: Dict = {
        "UTILITY_FUND": 500,
        "HOUSING_RELOCATION": 2000,
        "APPLIANCE_FUND": 1000,
    }
    
    # Central AI Fund Parameters
    fund_initial_balances: Dict = {
        "UTILITY_FUND": Decimal('100000000'),      # 100M DOP
        "HOUSING_RELOCATION_FUND": Decimal('500000000'),  # 500M DOP
        "APPLIANCE_FUND": Decimal('50000000'),     # 50M DOP
        "EMERGENCY_RESERVE": Decimal('10000000'),  # 10M DOP
    }
    
    # Automation
    automation_check_interval_seconds: int = 60
    max_concurrent_executions: int = 100
    default_retry_policy: Dict = {
        "max_retries": 3,
        "base_delay": 5,
        "max_delay": 300
    }
    
    # Monitoring
    metrics_port: int = 9090
    health_check_port: int = 8080
    log_level: str = "INFO"

# Docker Compose for deployment
DOCKER_COMPOSE = """
version: '3.8'
services:
  governance-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/governance
      - BLOCKCHAIN_RPC=http://blockchain:8545
      - DGII_CLIENT_ID=${DGII_CLIENT_ID}
      - DGII_CLIENT_SECRET=${DGII_CLIENT_SECRET}
      # ... all other env vars
    depends_on:
      - db
      - redis
      - blockchain
  
  automation-engine:
    build: .
    command: python -m automation.engine
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/governance
    depends_on:
      - db
      - redis
  
  scheduler:
    build: .
    command: python -m automation.scheduler
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/governance
    depends_on:
      - db
      - redis
  
  context-filing:
    build: .
    command: python -m core.context_filing
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/governance
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=governance
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
  
  blockchain:
    image: hyperledger/fabric-ca:latest
    # Or ganache for development
  
  monitoring:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

volumes:
  postgres_data:
"""

# Kubernetes deployment manifests would go here for production
```

---

## 10. MONITORING & OBSERVABILITY

```python
# monitoring/metrics.py
"""
Prometheus metrics for system observability.
"""

from prometheus_client import Counter, Histogram, Gauge, Summary

# Merit System Metrics
MERITS_CALCULATED = Counter('merits_calculated_total', 'Total merits calculated', ['category', 'action'])
MERITS_RECORDED = Counter('merits_recorded_total', 'Total merits recorded', ['tier'])
MERIT_THRESHOLD_REACHED = Counter('merit_threshold_reached_total', 'Threshold reached', ['front'])

# Selecting Front Metrics
FRONT_DISTRIBUTION = Counter('front_distribution_total', 'Distributions to fronts', ['front', 'status'])
FUNDING_RESERVED = Summary('funding_reserved_dop', 'Funding reserved in DOP', ['front'])

# Central AI Fund Metrics
FUND_RESERVATIONS = Counter('fund_reservations_total', 'Fund reservations', ['fund_type', 'status'])
FUND_BALANCE = Gauge('fund_balance_dop', 'Current fund balance', ['fund_type'])
AI_APPROVAL_RATE = Gauge('ai_approval_rate', 'AI approval rate', ['fund_type'])
RISK_SCORE_DISTRIBUTION = Histogram('risk_score', 'Risk score distribution', ['fund_type'])

# Automation Metrics
AUTOMATION_EXECUTIONS = Counter('automation_executions_total', 'Automation executions', ['trigger_type', 'status'])
AUTOMATION_DURATION = Histogram('automation_duration_seconds', 'Automation execution time', ['trigger_type'])
API_CALL_DURATION = Histogram('api_call_duration_seconds', 'API call duration', ['api', 'operation', 'status'])
API_CALL_ERRORS = Counter('api_call_errors_total', 'API call errors', ['api', 'operation', 'error_type'])

# Context Filing Metrics
CONTEXT_REPORTS_FILED = Counter('context_reports_filed_total', 'Context reports filed', ['event_type', 'verification_status'])
CONTEXT_FILING_DURATION = Histogram('context_filing_duration_seconds', 'Context filing duration', ['event_type'])

# Utility Payment Metrics
UTILITY_PAYMENTS = Counter('utility_payments_total', 'Utility payments', ['utility_type', 'provider', 'status'])
UTILITY_PAYMENT_AMOUNT = Summary('utility_payment_amount_dop', 'Payment amounts', ['utility_type'])

# Housing Metrics
HOUSING_RELOCATIONS = Counter('housing_relocations_total', 'Housing relocations', ['reason', 'status'])
HOUSING_FUNDING = Summary('housing_funding_dop', 'Housing funding amounts')

# System Health
SYSTEM_HEALTH = Gauge('system_health', 'System health status', ['component'])
ACTIVE_CITIZENS = Gauge('active_citizens', 'Citizens with active merit profiles')
PENDING_AUTOMATIONS = Gauge('pending_automations', 'Pending automation executions')
```

---

## 11. SECURITY & COMPLIANCE

```python
# security/compliance.py
"""
Security and compliance framework.
"""

class SecurityCompliance:
    """Security and compliance controls"""
    
    # Data Protection
    ENCRYPTION_AT_REST = "AES-256-GCM"
    ENCRYPTION_IN_TRANSIT = "TLS 1.3"
    PII_HASHING = "bcrypt + salt"
    CEDULA_TOKENIZATION = "Format-preserving encryption"
    
    # Access Control
    RBAC_ROLES = [
        "SYSTEM_ADMIN",
        "FUND_MANAGER", 
        "COMPLIANCE_OFFICER",
        "AUTOMATION_OPERATOR",
        "AUDITOR",
        "CITIZEN_SUPPORT"
    ]
    
    # Audit Requirements
    AUDIT_LOG_RETENTION_YEARS = 7
    BLOCKCHAIN_ANCHOR_ALL_TRANSACTIONS = True
    MULTISIG_THRESHOLD = 3  # Of 5 signers for >100k DOP
    
    # API Security
    API_RATE_LIMITS = {
        "dgii": 60,      # per minute
        "superate": 100,
        "adess": 100,
        "ede": 120,
        "coraasan": 60,
        "mivhed": 50,
        "jce": 200,
    }
    
    # Compliance Standards
    STANDARDS = [
        "ISO 27001",           # Information Security
        "ISO 27701",           # Privacy Information Management
        "PCI DSS",             # Payment Card Industry (for utility payments)
        "SOX",                 # Financial Controls
        "GDPR",                # Data Protection (for Haitian migrants etc.)
        "DR_LAW_172-13",       # Data Protection Law
        "DR_LAW_53-07",        # High-Tech Crimes
    ]
```

---

## 12. TESTING STRATEGY

```python
# tests/test_integration.py
"""
Integration tests for the complete system.
"""

import pytest
from decimal import Decimal

class TestTaxMeritToUtilityFlow:
    
    @pytest.fixture
    async def flow(self):
        flow = TaxMeritToUtilityFlow()
        await flow.initialize()
        yield flow
        await flow.cleanup()
    
    @pytest.mark.asyncio
    async def test_tax_payment_creates_merits(self, flow):
        """Test that tax payment generates merits"""
        result = await flow.process_citizen_tax_payment(
            citizen_id="CIT_001",
            rnc="130000000",
            payment_data={
                "transaction_id": "TXN_123",
                "amount": Decimal('50000'),
                "period": "2026-Q1"
            }
        )
        
        assert result.success
        assert result.merit_event.category == MeritCategory.TAX_COMPLIANCE
        assert result.merit_event.total_merits > 0
    
    @pytest.mark.asyncio
    async def test_merit_threshold_triggers_utility_fund(self, flow):
        """Test that reaching threshold triggers utility fund allocation"""
        # Setup citizen with enough merits
        await flow.merit_ledger.add_test_merits("CIT_001", 600)
        
        result = await flow.process_citizen_tax_payment(
            citizen_id="CIT_001",
            rnc="130000000",
            payment_data={"transaction_id": "TXN_124", "amount": Decimal('10000'), "period": "2026-Q2"}
        )
        
        assert result.distribution is not None
        assert result.distribution.eligible
        assert "UTILITY_FUND" in [a.front.value for a in result.distribution.allocations]
    
    @pytest.mark.asyncio
    async def test_utility_payment_e2e(self, flow):
        """Test complete utility payment flow"""
        # Reserve funds
        reservation = await flow.central_ai.reserve_funds(
            citizen_id="CIT_001",
            front=SelectingFront.UTILITY_FUND,
            amount_dop=Decimal('5000'),
            merits_backing=100
        )
        
        assert reservation.success
        
        # Execute payment (mocked)
        with patch('connectors.specific_connectors.EDEConnector.pay_utility_bill') as mock_pay:
            mock_pay.return_value = PaymentResult(success=True, transaction_id="PAY_123")
            
            result = await flow.process_utility_bill_payment(
                citizen_id="CIT_001",
                utility_type="electricity",
                account_number="ACC_12345",
                amount_dop=Decimal('5000')
            )
        
        assert result.success
        assert result.payment_result.transaction_id == "PAY_123"
        assert result.context_report.verification_status == "VERIFIED"
    
    @pytest.mark.asyncio
    async def test_relocation_housing_only_under_relocation(self, flow):
        """Test housing only allocated under verified relocation"""
        allocator = RelocationHousingAllocator(...)
        
        # Try without relocation reason - should fail
        case = RelocationCase(
            citizen_id="CIT_001",
            household_size=4,
            current_address="Calle Falsa 123",
            current_coordinates=(19.45, -70.70),
            relocation_reason=None,  # No reason
            reason_evidence={}
        )
        
        result = await allocator.submit_relocation_request(case)
        assert not result.success
        assert "relocation reason" in result.reason.lower()
        
        # With valid disaster declaration - should succeed
        case.relocation_reason = RelocationReason.NATURAL_DISASTER
        case.reason_evidence = {"coe_declaration_id": "COE_2026_001"}
        
        with patch.object(allocator, '_fetch_coe_declaration') as mock_coe:
            mock_coe.return_value = CoEDeclaration(active=True, event="Hurricane Franklin")
            
            result = await allocator.submit_relocation_request(case)
            assert result.success
            assert result.case.status == HousingStatus.VERIFIED
```

---

## 13. DEPLOYMENT CHECKLIST

### Phase 1: Infrastructure (Week 1-2)
- [ ] PostgreSQL database with schema
- [ ] Redis for caching/queues
- [ ] Blockchain node (Hyperledger Fabric or Polygon)
- [ ] Kubernetes cluster (or Docker Compose for dev)
- [ ] Monitoring stack (Prometheus, Grafana, Loki)

### Phase 2: Core Services (Week 3-4)
- [ ] Merit Calculator & Ledger deployed
- [ ] Selecting Front Distributor deployed
- [ ] Central AI Fund Manager deployed
- [ ] Database migrations run
- [ ] Blockchain contracts deployed

### Phase 3: API Connectors (Week 5-6)
- [ ] DGII connector configured with credentials
- [ ] SUPÉRATE connector configured
- [ ] ADESS connector configured
- [ ] EDE Norte/Sur/Este connectors configured
- [ ] CORAASAN/CAASD/INAPA connectors configured
- [ ] MIVHED connector configured
- [ ] JCE connector configured (certificate-based)
- [ ] INFOTEP connector configured
- [ ] All connectors tested in sandbox

### Phase 4: Automation & Context (Week 7-8)
- [ ] Instant API Application Engine deployed
- [ ] Scheduler configured with default jobs
- [ ] Context Filing Engine deployed
- [ ] Data fetchers registered
- [ ] End-to-end flow tested

### Phase 5: Security & Compliance (Week 9-10)
- [ ] RBAC configured
- [ ] Audit logging verified
- [ ] Blockchain anchoring working
- [ ] Multi-signature treasury tested
- [ ] Penetration testing completed
- [ ] Compliance review passed

### Phase 6: Production Launch (Week 11-12)
- [ ] Pilot with 100 citizens in Santiago
- [ ] Monitor metrics, adjust parameters
- [ ] Scale to 1,000 citizens
- [ ] Full production launch
- [ ] 24/7 support established

---

*Document Version: 1.0 | Date: 2026-11-10*
*System: Tax Merit Distribution & Central AI Fund Management for Dominican Republic*
*Integrates: Japanese Agile Governance + DR Government APIs + Automated Execution*
*Location: F:\managements\tax_merit_central_ai_fund_system.md*