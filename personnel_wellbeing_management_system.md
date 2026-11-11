# Personnel Well-Being Management System
## Sub-Categorized Accounting, Attendant-Citizen Support & Continuous Care
### Integrated with Merit System, Central AI Fund & Convivencia Limpia

---

## 1. EXECUTIVE SUMMARY

### 1.1 Core Philosophy

> **"El bienestar del personal es el bienestar de la sociedad. Cada persona que cuida, merece ser cuidada. El sistema contabiliza, anticipa y provee sin burocracia, con la misma bondad que se espera del personal hacia la ciudadanía."**

### 1.2 Key Requirements Addressed

| Requirement | Solution |
|-------------|----------|
| **Sub-categories for personnel types** | 8-tier personnel classification with differentiated support |
| **Attendant-citizen accounting** | Bidirectional support tracking (attendant→citizen, system→attendant) |
| **Appliances, housing, food support** | Unified Support Wallet with category-specific funds |
| **Pending purchases for aging needs** | Predictive Life-Stage Procurement Engine |
| **Personnel leave continuity** | Zero-Gap Coverage Protocol with merit-weighted substitutes |
| **System→personnel communication** | Direct Well-Being Channel (not top-down orders) |

---

## 2. PERSONNEL SUB-CATEGORIZATION FRAMEWORK

### 2.1 Eight Personnel Tiers (Capas de Personal)

```python
# personnel/sub_categories.py
"""
Eight-tier personnel classification with differentiated well-being support.
Based on role, risk, responsibility, and relational intensity.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal

class PersonnelTier(Enum):
    TIER_1_QUEST_GUIDES = "quest_guides"           # Quest visitors, community connectors
    TIER_2_ATTENDANTS = "attendants"               # Direct citizen care (health, social, elderly)
    TIER_3_FIELD_OPERATORS = "field_operators"     # Infrastructure, utilities, environment
    TIER_4_KNOWLEDGE_WORKERS = "knowledge_workers" # Analysts, planners, engineers, educators
    TIER_5_COORDINATORS = "coordinators"           # Team leads, project managers, supervisors
    TIER_6_SPECIALISTS = "specialists"             # Doctors, engineers, legal, technical experts
    TIER_7_STRATEGIC = "strategic"                 # Directors, policy makers, governance roles
    TIER_8_FOUNDATIONAL = "foundational"           # Maintenance, cleaning, logistics, security

class PersonnelCategory(Enum):
    # Functional categories within tiers
    CARE = "care"                    # Direct human care
    TECHNICAL = "technical"          # Infrastructure, systems
    ANALYTICAL = "analytical"        # Data, planning, policy
    COORDINATION = "coordination"    # People/process management
    STRATEGIC = "strategic"          # Governance, direction
    OPERATIONAL = "operational"      # Execution, maintenance
    COMMUNITY = "community"          # Quest, veeduría, mutual aid
    SUPPORT = "support"              # Logistics, admin, facilities

@dataclass
class PersonnelProfile:
    personnel_id: str
    national_id_hash: str  # Cédula hashed
    
    # Classification
    tier: PersonnelTier
    category: PersonnelCategory
    role_title: str
    institution_id: str
    territory_code: str
    
    # Relational intensity (0-1): How much direct citizen interaction
    relational_intensity: float
    
    # Risk exposure (0-1): Physical, psychological, environmental
    risk_exposure: float
    
    # Responsibility level (0-1): Decision impact scope
    responsibility_level: float
    
    # Tenure
    hire_date: datetime
    tier_history: List[TierTransition] = field(default_factory=list)
    
    # Well-being tracking
    well_being_score: float = 1.0  # 0-1, updated monthly
    stress_indicators: Dict[str, float] = field(default_factory=dict)
    last_well_being_check: datetime = datetime.now()
    
    # Support wallet
    support_wallet: 'SupportWallet' = None
    
    # Leave management
    leave_balance: 'LeaveBalance' = None
    leave_history: List[LeaveRecord] = field(default_factory=list)
    
    # Merit integration
    merit_profile: 'CitizenMeritProfile' = None
    
    # Aging/life-stage
    life_stage: 'LifeStage' = None
    anticipated_needs: List['AnticipatedNeed'] = field(default_factory=list)

@dataclass
class TierConfiguration:
    """Support configuration per tier"""
    tier: PersonnelTier
    
    # Base support allocations (monthly DOP)
    base_wellbeing_allowance: Decimal
    appliance_fund_annual: Decimal
    housing_support_annual: Decimal
    food_security_annual: Decimal
    pending_purchase_reserve: Decimal
    
    # Leave coverage
    leave_substitute_tier: PersonnelTier  # Who covers during leave
    leave_coverage_rate: float  # % of salary covered
    max_concurrent_leave_days: int
    
    # Relational support
    supervision_frequency_days: int  # How often check-in
    peer_support_group_size: int
    mandatory_rest_days_per_quarter: int
    
    # Aging anticipation
    life_stage_review_age: int
    anticipatory_funding_start_age: int

# Default configurations (governance-adjustable)
TIER_CONFIGS = {
    PersonnelTier.TIER_1_QUEST_GUIDES: TierConfiguration(
        tier=PersonnelTier.TIER_1_QUEST_GUIDES,
        base_wellbeing_allowance=Decimal('8000'),
        appliance_fund_annual=Decimal('50000'),
        housing_support_annual=Decimal('120000'),
        food_security_annual=Decimal('60000'),
        pending_purchase_reserve=Decimal('30000'),
        leave_substitute_tier=PersonnelTier.TIER_2_ATTENDANTS,
        leave_coverage_rate=1.0,
        max_concurrent_leave_days=30,
        supervision_frequency_days=14,
        peer_support_group_size=8,
        mandatory_rest_days_per_quarter=5,
        life_stage_review_age=35,
        anticipatory_funding_start_age=40
    ),
    PersonnelTier.TIER_2_ATTENDANTS: TierConfiguration(
        tier=PersonnelTier.TIER_2_ATTENDANTS,
        base_wellbeing_allowance=Decimal('12000'),
        appliance_fund_annual=Decimal('80000'),
        housing_support_annual=Decimal('180000'),
        food_security_annual=Decimal('90000'),
        pending_purchase_reserve=Decimal('50000'),
        leave_substitute_tier=PersonnelTier.TIER_1_QUEST_GUIDES,
        leave_coverage_rate=1.0,
        max_concurrent_leave_days=45,
        supervision_frequency_days=7,
        peer_support_group_size=6,
        mandatory_rest_days_per_quarter=7,
        life_stage_review_age=30,
        anticipatory_funding_start_age=35
    ),
    PersonnelTier.TIER_3_FIELD_OPERATORS: TierConfiguration(
        tier=PersonnelTier.TIER_3_FIELD_OPERATORS,
        base_wellbeing_allowance=Decimal('10000'),
        appliance_fund_annual=Decimal('60000'),
        housing_support_annual=Decimal('150000'),
        food_security_annual=Decimal('72000'),
        pending_purchase_reserve=Decimal('40000'),
        leave_substitute_tier=PersonnelTier.TIER_8_FOUNDATIONAL,
        leave_coverage_rate=0.9,
        max_concurrent_leave_days=30,
        supervision_frequency_days=14,
        peer_support_group_size=10,
        mandatory_rest_days_per_quarter=5,
        life_stage_review_age=35,
        anticipatory_funding_start_age=40
    ),
    PersonnelTier.TIER_4_KNOWLEDGE_WORKERS: TierConfiguration(
        tier=PersonnelTier.TIER_4_KNOWLEDGE_WORKERS,
        base_wellbeing_allowance=Decimal('8000'),
        appliance_fund_annual=Decimal('50000'),
        housing_support_annual=Decimal('120000'),
        food_security_annual=Decimal('60000'),
        pending_purchase_reserve=Decimal('30000'),
        leave_substitute_tier=PersonnelTier.TIER_4_KNOWLEDGE_WORKERS,
        leave_coverage_rate=0.85,
        max_concurrent_leave_days=60,
        supervision_frequency_days=30,
        peer_support_group_size=12,
        mandatory_rest_days_per_quarter=3,
        life_stage_review_age=40,
        anticipatory_funding_start_age=45
    ),
    PersonnelTier.TIER_5_COORDINATORS: TierConfiguration(
        tier=PersonnelTier.TIER_5_COORDINATORS,
        base_wellbeing_allowance=Decimal('10000'),
        appliance_fund_annual=Decimal('70000'),
        housing_support_annual=Decimal('150000'),
        food_security_annual=Decimal('72000'),
        pending_purchase_reserve=Decimal('40000'),
        leave_substitute_tier=PersonnelTier.TIER_5_COORDINATORS,
        leave_coverage_rate=0.85,
        max_concurrent_leave_days=45,
        supervision_frequency_days=21,
        peer_support_group_size=8,
        mandatory_rest_days_per_quarter=5,
        life_stage_review_age=40,
        anticipatory_funding_start_age=45
    ),
    PersonnelTier.TIER_6_SPECIALISTS: TierConfiguration(
        tier=PersonnelTier.TIER_6_SPECIALISTS,
        base_wellbeing_allowance=Decimal('15000'),
        appliance_fund_annual=Decimal('100000'),
        housing_support_annual=Decimal('240000'),
        food_security_annual=Decimal('120000'),
        pending_purchase_reserve=Decimal('80000'),
        leave_substitute_tier=PersonnelTier.TIER_6_SPECIALISTS,
        leave_coverage_rate=0.9,
        max_concurrent_leave_days=30,
        supervision_frequency_days=14,
        peer_support_group_size=5,
        mandatory_rest_days_per_quarter=7,
        life_stage_review_age=40,
        anticipatory_funding_start_age=45
    ),
    PersonnelTier.TIER_7_STRATEGIC: TierConfiguration(
        tier=PersonnelTier.TIER_7_STRATEGIC,
        base_wellbeing_allowance=Decimal('20000'),
        appliance_fund_annual=Decimal('150000'),
        housing_support_annual=Decimal('300000'),
        food_security_annual=Decimal('180000'),
        pending_purchase_reserve=Decimal('100000'),
        leave_substitute_tier=PersonnelTier.TIER_5_COORDINATORS,
        leave_coverage_rate=0.8,
        max_concurrent_leave_days=60,
        supervision_frequency_days=30,
        peer_support_group_size=4,
        mandatory_rest_days_per_quarter=10,
        life_stage_review_age=45,
        anticipatory_funding_start_age=50
    ),
    PersonnelTier.TIER_8_FOUNDATIONAL: TierConfiguration(
        tier=PersonnelTier.TIER_8_FOUNDATIONAL,
        base_wellbeing_allowance=Decimal('6000'),
        appliance_fund_annual=Decimal('40000'),
        housing_support_annual=Decimal('100000'),
        food_security_annual=Decimal('48000'),
        pending_purchase_reserve=Decimal('20000'),
        leave_substitute_tier=PersonnelTier.TIER_8_FOUNDATIONAL,
        leave_coverage_rate=0.95,
        max_concurrent_leave_days=30,
        supervision_frequency_days=21,
        peer_support_group_size=15,
        mandatory_rest_days_per_quarter=5,
        life_stage_review_age=35,
        anticipatory_funding_start_age=40
    ),
}
```

### 2.2 Attendant-Citizen Bidirectional Accounting

```python
# personnel/attendant_accounting.py
"""
Bidirectional accounting: Attendant supports Citizen ↔ System supports Attendant.
Tracks care given and care received in unified ledger.
"""

class AttendantCitizenAccounting:
    """
    Every attendant-citizen interaction creates dual entry:
    1. Care Provided (attendant → citizen) - builds attendant's merit
    2. Support Received (system → attendant) - builds attendant's well-being
    """
    
    def __init__(self, merit_system: 'MeritLedger', wellbeing_system: 'WellBeingSystem'):
        self.merit_system = merit_system
        self.wellbeing = wellbeing_system
        self.interactions: Dict[str, List[CareInteraction]] = {}
        self.support_flows: Dict[str, SupportFlow] = {}
        
    async def record_care_interaction(self, interaction: CareInteraction) -> InteractionRecord:
        """Record care interaction with dual accounting"""
        
        interaction.interaction_id = f"CARE_{interaction.attendant_id}_{interaction.citizen_id}_{uuid.uuid4().hex[:8]}"
        interaction.timestamp = datetime.now()
        
        # 1. VALIDATE: Both parties exist and are active
        attendant = await self._get_attendant(interaction.attendant_id)
        citizen = await self._get_citizen(interaction.citizen_id)
        
        if not attendant or not citizen:
            return InteractionRecord(success=False, reason="Invalid parties")
        
        # 2. ACCOUNT: Care Provided → Attendant's Merit
        care_merit = self._calculate_care_merit(interaction, attendant)
        merit_event = MeritEvent(
            event_id=f"MERIT_CARE_{interaction.interaction_id}",
            citizen_id=interaction.attendant_id,
            category=MeritCategory.CIVIC_PARTICIPATION,
            base_merits=care_merit.base_merits,
            multiplier=care_merit.multiplier,
            total_merits=0,
            source_system="ATTENDANT_CARE",
            source_reference=interaction.interaction_id,
            timestamp=datetime.now(),
            verified=True
        )
        merit_event.__post_init__()  # Calculate total_merits
        
        await self.merit_system.ledger.record_merit_event(merit_event)
        
        # 3. ACCOUNT: System Support → Attendant's Well-Being Wallet
        support_amount = self._calculate_wellbeing_support(interaction, attendant)
        await self.wellbeing.credit_wallet(
            attendant_id=interaction.attendant_id,
            amount=support_amount,
            category=SupportCategory.RELATIONAL_CARE,
            reference=interaction.interaction_id
        )
        
        # 4. TRACK: Bidirectional flow
        flow = SupportFlow(
            flow_id=f"FLOW_{interaction.interaction_id}",
            attendant_id=interaction.attendant_id,
            citizen_id=interaction.citizen_id,
            care_provided=interaction,
            merit_earned=merit_event.total_merits,
            wellbeing_credited=support_amount,
            timestamp=datetime.now()
        )
        
        self.support_flows.setdefault(interaction.attendant_id, []).append(flow)
        self.interactions.setdefault(interaction.attendant_id, []).append(interaction)
        
        # 5. CHECK: Attendant well-being thresholds
        await self._check_attendant_wellbeing(attendant)
        
        return InteractionRecord(
            success=True,
            interaction=interaction,
            merit_earned=merit_event.total_merits,
            wellbeing_credited=support_amount,
            flow=flow
        )
    
    def _calculate_care_merit(self, interaction: CareInteraction, attendant: PersonnelProfile) -> CareMeritCalculation:
        """Calculate merit for care provided based on tier and intensity"""
        
        config = TIER_CONFIGS[attendant.tier]
        
        # Base merits by interaction type
        base_by_type = {
            CareType.DIRECT_PHYSICAL: 50,
            CareType.EMOTIONAL_SUPPORT: 30,
            CareType.NAVIGATION_ASSISTANCE: 25,
            CareType.ADVOCACY: 40,
            CareType.SKILL_TEACHING: 35,
            CareType.CRISIS_INTERVENTION: 75,
            CareType.DAILY_CHECK_IN: 15,
            CareType.RESOURCE_CONNECTION: 20,
        }
        
        base = base_by_type.get(interaction.care_type, 20)
        
        # Multipliers
        relational_mult = 1.0 + attendant.relational_intensity  # Up to 2x
        risk_mult = 1.0 + attendant.risk_exposure * 0.5  # Up to 1.5x
        duration_mult = min(interaction.duration_minutes / 60, 2.0)  # Up to 2x for 2+ hours
        
        # Vulnerability bonus (caring for more vulnerable citizens)
        vulnerability_bonus = interaction.citizen_vulnerability_score * 0.3  # Up to 30%
        
        total_multiplier = relational_mult * risk_mult * duration_mult * (1 + vulnerability_bonus)
        
        return CareMeritCalculation(
            base_merits=base,
            multiplier=total_multiplier,
            relational_multiplier=relational_mult,
            risk_multiplier=risk_mult,
            duration_multiplier=duration_mult,
            vulnerability_bonus=vulnerability_bonus
        )
    
    def _calculate_wellbeing_support(self, interaction: CareInteraction, attendant: PersonnelProfile) -> Decimal:
        """Calculate well-being support credited to attendant"""
        
        config = TIER_CONFIGS[attendant.tier]
        
        # Base support per interaction
        base_support = config.base_wellbeing_allowance / Decimal('30') / Decimal('4')  # Daily/4 interactions
        
        # Intensity adjustment
        intensity_factor = Decimal(str(1.0 + interaction.intensity_score * 0.5))
        
        # Reciprocity factor (citizen's capacity to reciprocate via mutual aid)
        reciprocity_factor = Decimal(str(1.0 + interaction.citizen_reciprocity_score * 0.3))
        
        total = base_support * intensity_factor * reciprocity_factor
        
        return total.quantize(Decimal('0.01'))
```

---

## 3. UNIFIED SUPPORT WALLET SYSTEM

### 3.1 Multi-Category Support Wallet

```python
# personnel/support_wallet.py
"""
Unified Support Wallet: Appliances, Housing, Food, Pending Purchases.
Single wallet, category-specific allocations, automatic replenishment.
"""

class SupportWallet:
    """
    Personnel's well-being wallet with category sub-accounts.
    Auto-replenished from Central AI Fund based on tier config.
    """
    
    def __init__(self, personnel_id: str, tier: PersonnelTier, central_ai: 'CentralAIFundManager'):
        self.personnel_id = personnel_id
        self.tier = tier
        self.config = TIER_CONFIGS[tier]
        self.central_ai = central_ai
        
        # Category balances (DOP)
        self.balances: Dict[SupportCategory, Decimal] = {
            SupportCategory.APPLIANCES: Decimal('0'),
            SupportCategory.HOUSING: Decimal('0'),
            SupportCategory.FOOD: Decimal('0'),
            SupportCategory.PENDING_PURCHASES: Decimal('0'),
            SupportCategory.WELLBEING_GENERAL: Decimal('0'),
            SupportCategory.EMERGENCY: Decimal('0'),
            SupportCategory.LEAVE_COVERAGE: Decimal('0'),
            SupportCategory.AGING_ANTICIPATION: Decimal('0'),
        }
        
        # Annual allocation tracking
        self.annual_allocations: Dict[SupportCategory, Decimal] = {}
        self.spent_this_year: Dict[SupportCategory, Decimal] = {cat: Decimal('0') for cat in SupportCategory}
        
        # Transaction history
        self.transactions: List[WalletTransaction] = []
        
        # Auto-replenishment rules
        self.replenishment_rules: Dict[SupportCategory, ReplenishmentRule] = {}
        
    async def initialize_wallet(self):
        """Initialize with annual allocations from Central AI Fund"""
        
        allocations = {
            SupportCategory.APPLIANCES: self.config.appliance_fund_annual,
            SupportCategory.HOUSING: self.config.housing_support_annual,
            SupportCategory.FOOD: self.config.food_security_annual,
            SupportCategory.PENDING_PURCHASES: self.config.pending_purchase_reserve,
            SupportCategory.WELLBEING_GENERAL: self.config.base_wellbeing_allowance * Decimal('12'),
            SupportCategory.EMERGENCY: self.config.base_wellbeing_allowance * Decimal('3'),
            SupportCategory.LEAVE_COVERAGE: self.config.base_wellbeing_allowance * Decimal('2'),
            SupportCategory.AGING_ANTICIPATION: Decimal('0'),  # Filled by anticipation engine
        }
        
        for category, amount in allocations.items():
            if amount > 0:
                await self.credit(category, amount, WalletTransactionType.ANNUAL_ALLOCATION)
        
        # Set up monthly replenishment for general wellbeing
        self.replenishment_rules[SupportCategory.WELLBEING_GENERAL] = ReplenishmentRule(
            category=SupportCategory.WELLBEING_GENERAL,
            trigger=ReplenishmentTrigger.MONTHLY,
            amount=self.config.base_wellbeing_allowance,
            min_threshold=self.config.base_wellbeing_allowance * Decimal('0.2')
        )
        
        # Request Central AI Fund commitment
        total_annual = sum(allocations.values())
        await self.central_ai.commit_personnel_funds(
            personnel_id=self.personnel_id,
            annual_amount=total_annual,
            tier=self.tier
        )
    
    async def credit(self, category: SupportCategory, amount: Decimal, 
                     tx_type: WalletTransactionType, reference: str = "") -> WalletTransaction:
        """Credit wallet category"""
        
        self.balances[category] += amount
        self.annual_allocations[category] = self.annual_allocations.get(category, Decimal('0')) + amount
        
        tx = WalletTransaction(
            transaction_id=f"TXN_{self.personnel_id}_{category.value}_{uuid.uuid4().hex[:8]}",
            personnel_id=self.personnel_id,
            category=category,
            type=tx_type,
            amount=amount,
            balance_after=self.balances[category],
            reference=reference,
            timestamp=datetime.now()
        )
        
        self.transactions.append(tx)
        
        # Check if this triggers any pending purchases
        if category in [SupportCategory.APPLIANCES, SupportCategory.HOUSING, SupportCategory.PENDING_PURCHASES]:
            await self._check_pending_purchases(category)
        
        return tx
    
    async def debit(self, category: SupportCategory, amount: Decimal,
                    purpose: str, reference: str = "") -> DebitResult:
        """Debit wallet category with validation"""
        
        if self.balances[category] < amount:
            # Try emergency fund transfer
            if category != SupportCategory.EMERGENCY and self.balances[SupportCategory.EMERGENCY] >= amount - self.balances[category]:
                shortfall = amount - self.balances[category]
                await self.transfer(SupportCategory.EMERGENCY, category, shortfall, "EMERGENCY_TRANSFER")
            else:
                return DebitResult(success=False, reason=f"Insufficient balance in {category.value}")
        
        self.balances[category] -= amount
        self.spent_this_year[category] += amount
        
        tx = WalletTransaction(
            transaction_id=f"TXN_{self.personnel_id}_{category.value}_{uuid.uuid4().hex[:8]}",
            personnel_id=self.personnel_id,
            category=category,
            type=WalletTransactionType.EXPENDITURE,
            amount=-amount,
            balance_after=self.balances[category],
            reference=reference,
            timestamp=datetime.now(),
            purpose=purpose
        )
        
        self.transactions.append(tx)
        
        # Auto-replenish if below threshold
        await self._check_replenishment(category)
        
        return DebitResult(success=True, transaction=tx, new_balance=self.balances[category])
    
    async def transfer(self, from_cat: SupportCategory, to_cat: SupportCategory, 
                       amount: Decimal, reason: str) -> TransferResult:
        """Transfer between categories (with governance rules)"""
        
        # Check transfer rules
        allowed = self._check_transfer_allowed(from_cat, to_cat, amount)
        if not allowed:
            return TransferResult(success=False, reason="Transfer not allowed")
        
        await self.debit(from_cat, amount, f"Transfer to {to_cat.value}: {reason}")
        await self.credit(to_cat, amount, WalletTransactionType.TRANSFER_IN, f"Transfer from {from_cat.value}: {reason}")
        
        return TransferResult(success=True, from_balance=self.balances[from_cat], to_balance=self.balances[to_cat])

class SupportCategory(Enum):
    APPLIANCES = "appliances"              # Energy-efficient appliances, repairs
    HOUSING = "housing"                    # Rent, repairs, relocation, accessibility
    FOOD = "food"                          # Nutritional security, special diets
    PENDING_PURCHASES = "pending_purchases" # Pre-approved future needs
    WELLBEING_GENERAL = "wellbeing_general" # General well-being, mental health, recreation
    EMERGENCY = "emergency"                # Unexpected crises
    LEAVE_COVERAGE = "leave_coverage"      # Leave substitute costs
    AGING_ANTICIPATION = "aging_anticipation" # Predictive life-stage needs

class ReplenishmentRule:
    category: SupportCategory
    trigger: ReplenishmentTrigger
    amount: Decimal
    min_threshold: Decimal
    max_per_month: Decimal

class ReplenishmentTrigger(Enum):
    MONTHLY = "monthly"
    THRESHOLD = "threshold"
    QUARTERLY = "quarterly"
    ON_DEMAND = "on_demand"
```

---

## 4. PENDING PURCHASES & AGING NEEDS MANAGEMENT

### 4.1 Predictive Life-Stage Procurement Engine

```python
# personnel/anticipation_engine.py
"""
Predictive engine for life-stage needs.
Anticipates: aging appliances, housing accessibility, health equipment, dietary needs.
"""

class AnticipationEngine:
    """
    Analyzes personnel life-stage, usage patterns, and environmental factors
    to predict and pre-fund future needs before they become urgent.
    """
    
    def __init__(self, wallet: SupportWallet, central_ai: 'CentralAIFundManager'):
        self.wallet = wallet
        self.central_ai = central_ai
        self.predictions: Dict[str, List[AnticipatedNeed]] = {}
        self.pending_purchases: Dict[str, PendingPurchase] = {}
        self.approval_workflows: Dict[str, ApprovalWorkflow] = {}
        
    async def analyze_and_predict(self, personnel: PersonnelProfile) -> AnticipationReport:
        """Comprehensive life-stage needs analysis"""
        
        # 1. AGE-BASED PREDICTIONS
        age_predictions = self._predict_by_age(personnel)
        
        # 2. ROLE-BASED PREDICTIONS
        role_predictions = self._predict_by_role(personnel)
        
        # 3. USAGE PATTERN ANALYSIS
        usage_predictions = await self._predict_by_usage(personnel)
        
        # 4. ENVIRONMENTAL FACTORS
        env_predictions = self._predict_by_environment(personnel)
        
        # 5. HEALTH TRAJECTORY (if available)
        health_predictions = await self._predict_by_health(personnel)
        
        # Combine and prioritize
        all_predictions = age_predictions + role_predictions + usage_predictions + env_predictions + health_predictions
        
        # Deduplicate and prioritize
        prioritized = self._prioritize_predictions(all_predictions)
        
        # Store
        self.predictions[personnel.personnel_id] = prioritized
        
        # Create pending purchases for high-priority items
        for pred in prioritized:
            if pred.priority >= Priority.HIGH and pred.confidence > 0.7:
                await self._create_pending_purchase(personnel, pred)
        
        # Update wallet's aging anticipation fund
        total_anticipated = sum(p.estimated_cost for p in prioritized if p.priority >= Priority.MEDIUM)
        await self.wallet.credit(
            SupportCategory.AGING_ANTICIPATION,
            total_anticipated * Decimal('0.3'),  # Pre-fund 30%
            WalletTransactionType.ANTICIPATION_FUNDING
        )
        
        return AnticipationReport(
            personnel_id=personnel.personnel_id,
            predictions=prioritized,
            total_anticipated_cost=total_anticipated,
            funding_recommended=total_anticipated * Decimal('0.3'),
            generated_at=datetime.now()
        )
    
    def _predict_by_age(self, personnel: PersonnelProfile) -> List[AnticipatedNeed]:
        """Predict needs based on age milestones"""
        
        predictions = []
        age = (datetime.now() - personnel.hire_date).days / 365.25
        current_age = personnel.life_stage.current_age if personnel.life_stage else 30
        
        # Age milestones with typical needs
        milestones = {
            30: [
                AnticipatedNeedCategory.ERGONOMIC_EQUIPMENT,
                AnticipatedNeedCategory.PREVENTIVE_HEALTH,
            ],
            35: [
                AnticipatedNeedCategory.VISION_CARE,
                AnticipatedNeedCategory.DENTAL_MAJOR,
                AnticipatedNeedCategory.HOME_OFFICE_UPGRADE,
            ],
            40: [
                AnticipatedNeedCategory.CARDIOVASCULAR_SCREENING,
                AnticipatedNeedCategory.JOINT_SUPPORT,
                AnticipatedNeedCategory.HOUSING_ACCESSIBILITY_PREP,
            ],
            45: [
                AnticipatedNeedCategory.COMPREHENSIVE_HEALTH_SCREENING,
                AnticipatedNeedCategory.HEARING_AIDS,
                AnticipatedNeedCategory.MOBILITY_AIDS_PREP,
            ],
            50: [
                AnticipatedNeedCategory.COLORECTAL_SCREENING,
                AnticipatedNeedCategory.BONE_DENSITY,
                AnticipatedNeedCategory.HOME_MODIFICATIONS,
            ],
            55: [
                AnticipatedNeedCategory.RETIREMENT_TRANSITION,
                AnticipatedNeedCategory.LONG_TERM_CARE_INSURANCE,
                AnticipatedNeedCategory.ASSISTED_LIVING_PREP,
            ],
            60: [
                AnticipatedNeedCategory.FULL_ACCESSIBILITY_HOME,
                AnticipatedNeedCategory.PERSONAL_CARE_ASSISTANCE,
                AnticipatedNeedCategory.MEDICAL_ALERT_SYSTEM,
            ],
        }
        
        for milestone_age, categories in milestones.items():
            years_until = milestone_age - current_age
            if 0 < years_until <= 5:  # Within 5 years
                for category in categories:
                    predictions.append(AnticipatedNeed(
                        need_id=f"AGE_{category.value}_{milestone_age}",
                        personnel_id=personnel.personnel_id,
                        category=category,
                        trigger=AnticipationTrigger.AGE_MILESTONE,
                        trigger_value=milestone_age,
                        years_until=years_until,
                        estimated_cost=self._estimate_cost(category, personnel),
                        confidence=0.85,
                        priority=self._priority_by_urgency(years_until),
                        description=f"Age {milestone_age} milestone: {category.value}",
                        recommended_action="Pre-fund and schedule"
                    ))
        
        return predictions
    
    def _predict_by_role(self, personnel: PersonnelProfile) -> List[AnticipatedNeed]:
        """Predict needs based on role wear-and-tear"""
        
        predictions = []
        config = TIER_CONFIGS[personnel.tier]
        
        # High physical demand roles
        if personnel.category in [PersonnelCategory.CARE, PersonnelCategory.OPERATIONAL, PersonnelCategory.COMMUNITY]:
            predictions.extend([
                AnticipatedNeed(
                    need_id=f"ROLE_PHYSICAL_{personnel.personnel_id}",
                    personnel_id=personnel.personnel_id,
                    category=AnticipatedNeedCategory.PHYSICAL_THERAPY,
                    trigger=AnticipationTrigger.ROLE_WEAR,
                    estimated_cost=Decimal('120000'),
                    confidence=0.8,
                    priority=Priority.HIGH,
                    description="Physical therapy for role-related strain",
                    recommended_action="Annual sessions pre-funded"
                ),
                AnticipatedNeed(
                    need_id=f"ROLE_FOOTWEAR_{personnel.personnel_id}",
                    personnel_id=personnel.personnel_id,
                    category=AnticipatedNeedCategory.ORTHOPEDIC_FOOTWEAR,
                    trigger=AnticipationTrigger.ROLE_WEAR,
                    estimated_cost=Decimal('15000'),
                    confidence=0.9,
                    priority=Priority.MEDIUM,
                    description="Annual orthopedic footwear replacement",
                    recommended_action="Auto-replace every 12 months"
                ),
            ])
        
        # High cognitive demand roles
        if personnel.category in [PersonnelCategory.ANALYTICAL, PersonnelCategory.STRATEGIC, PersonnelCategory.COORDINATION]:
            predictions.extend([
                AnticipatedNeed(
                    need_id=f"ROLE_VISION_{personnel.personnel_id}",
                    personnel_id=personnel.personnel_id,
                    category=AnticipatedNeedCategory.VISION_CARE,
                    trigger=AnticipationTrigger.ROLE_WEAR,
                    estimated_cost=Decimal('40000'),
                    confidence=0.85,
                    priority=Priority.MEDIUM,
                    description="Annual eye exam + blue-light lenses",
                    recommended_action="Annual vision benefit"
                ),
                AnticipatedNeed(
                    need_id=f"ROLE_ERGONOMICS_{personnel.personnel_id}",
                    personnel_id=personnel.personnel_id,
                    category=AnticipatedNeedCategory.ERGONOMIC_EQUIPMENT,
                    trigger=AnticipationTrigger.ROLE_WEAR,
                    estimated_cost=Decimal('80000'),
                    confidence=0.75,
                    priority=Priority.MEDIUM,
                    description="Standing desk, ergonomic chair, monitor arms",
                    recommended_action="Upgrade every 3 years"
                ),
            ])
        
        # High emotional demand roles
        if personnel.category == PersonnelCategory.CARE:
            predictions.append(
                AnticipatedNeed(
                    need_id=f"ROLE_MENTAL_{personnel.personnel_id}",
                    personnel_id=personnel.personnel_id,
                    category=AnticipatedNeedCategory.MENTAL_HEALTH_SUPPORT,
                    trigger=AnticipationTrigger.ROLE_WEAR,
                    estimated_cost=Decimal('60000'),
                    confidence=0.9,
                    priority=Priority.HIGH,
                    description="Quarterly psychological support sessions",
                    recommended_action="Pre-funded therapy/coaching"
                )
            )
        
        return predictions
    
    async def _predict_by_usage(self, personnel: PersonnelProfile) -> List[AnticipatedNeed]:
        """Predict based on actual appliance/equipment usage patterns"""
        
        # Get usage data from smart home/appliance monitoring
        usage_data = await self._get_usage_data(personnel.personnel_id)
        predictions = []
        
        for appliance, data in usage_data.items():
            # Predict replacement based on usage hours
            if data['hours_used'] > data['rated_life_hours'] * 0.8:
                years_remaining = (data['rated_life_hours'] - data['hours_used']) / data['annual_hours']
                
                if years_remaining <= 2:
                    predictions.append(AnticipatedNeed(
                        need_id=f"USAGE_{appliance}_{personnel.personnel_id}",
                        personnel_id=personnel.personnel_id,
                        category=AnticipatedNeedCategory.APPLIANCE_REPLACEMENT,
                        trigger=AnticipationTrigger.USAGE_PATTERN,
                        trigger_value=data['hours_used'],
                        years_until=years_remaining,
                        estimated_cost=self._estimate_appliance_cost(appliance),
                        confidence=0.9,
                        priority=Priority.HIGH if years_remaining < 1 else Priority.MEDIUM,
                        description=f"{appliance} at {data['hours_used']:.0f}h of {data['rated_life_hours']:.0f}h rated life",
                        recommended_action="Pre-order replacement"
                    ))
        
        return predictions
    
    async def _create_pending_purchase(self, personnel: PersonnelProfile, prediction: AnticipatedNeed):
        """Create pending purchase with auto-approval workflow"""
        
        pending = PendingPurchase(
            purchase_id=f"PEND_{prediction.need_id}",
            personnel_id=personnel.personnel_id,
            prediction=prediction,
            status=PendingStatus.PRE_APPROVED,  # Pre-approved by anticipation engine
            estimated_cost=prediction.estimated_cost,
            allocated_from=SupportCategory.PENDING_PURCHASES,
            backup_category=SupportCategory.AGING_ANTICIPATION,
            created_at=datetime.now(),
            target_date=datetime.now() + timedelta(days=int(prediction.years_until * 365)),
            auto_execute=True,
            approval_workflow=self._get_approval_workflow(prediction)
        )
        
        self.pending_purchases[pending.purchase_id] = pending
        
        # Reserve funds in wallet
        await self.wallet.debit(
            SupportCategory.PENDING_PURCHASES,
            prediction.estimated_cost * Decimal('0.5'),  # Reserve 50% now
            f"Reserve for {prediction.description}",
            pending.purchase_id
        )
        
        # Schedule remaining reservation
        if prediction.years_until > 1:
            await self._schedule_future_reservation(pending, prediction.estimated_cost * Decimal('0.5'))
```

### 4.2 Pending Purchase Auto-Execution

```python
# personnel/pending_execution.py
"""
Automated execution of pending purchases when conditions met.
Integrates with vendor APIs, delivery tracking, satisfaction confirmation.
"""

class PendingPurchaseExecutor:
    def __init__(self, wallet: SupportWallet, vendor_registry: 'VendorRegistry'):
        self.wallet = wallet
        self.vendors = vendor_registry
        self.execution_queue: asyncio.Queue = asyncio.Queue()
        
    async def process_pending_purchases(self):
        """Main loop: check and execute due pending purchases"""
        
        for purchase_id, purchase in self.pending_purchases.items():
            if purchase.status == PendingStatus.PRE_APPROVED and purchase.target_date <= datetime.now():
                await self.execution_queue.put(purchase)
        
        # Process queue
        while not self.execution_queue.empty():
            purchase = await self.execution_queue.get()
            await self._execute_purchase(purchase)
    
    async def _execute_purchase(self, purchase: PendingPurchase):
        """Execute a pending purchase end-to-end"""
        
        try:
            # 1. Select best vendor
            vendor = await self._select_vendor(purchase)
            
            # 2. Place order
            order = await vendor.place_order(
                item=purchase.prediction.category,
                specifications=purchase.prediction.specifications,
                delivery_address=await self._get_delivery_address(purchase.personnel_id),
                billing_account=self.wallet
            )
            
            # 3. Transfer remaining funds
            remaining = purchase.estimated_cost - purchase.reserved_amount
            if remaining > 0:
                await self.wallet.debit(
                    purchase.backup_category,
                    remaining,
                    f"Complete payment for {purchase.prediction.description}",
                    purchase.purchase_id
                )
            
            # 4. Track delivery
            delivery_tracking = await self._track_delivery(order)
            
            # 5. Confirm receipt & satisfaction
            satisfaction = await self._confirm_satisfaction(purchase, delivery_tracking)
            
            # 6. Update status
            purchase.status = PendingStatus.COMPLETED
            purchase.order_id = order.order_id
            purchase.completed_at = datetime.now()
            purchase.satisfaction_score = satisfaction.score
            
            # 7. Learn for future predictions
            await self._update_prediction_model(purchase, satisfaction)
            
        except Exception as e:
            purchase.status = PendingStatus.FAILED
            purchase.failure_reason = str(e)
            await self._handle_execution_failure(purchase, e)
```

---

## 5. PERSONNEL LEAVE CONTINUITY SYSTEM

### 5.1 Zero-Gap Coverage Protocol

```python
# personnel/leave_continuity.py
"""
Zero-Gap Coverage: No citizen left unattended during personnel leave.
Merit-weighted substitute system with automatic activation.
"""

class LeaveContinuitySystem:
    def __init__(self, personnel_registry: 'PersonnelRegistry', merit_system: 'MeritLedger'):
        self.registry = personnel_registry
        self.merit_system = merit_system
        self.active_leaves: Dict[str, ActiveLeave] = {}
        self.coverage_assignments: Dict[str, CoverageAssignment] = {}
        self.substitute_pool: Dict[PersonnelTier, List[SubstituteCandidate]] = {}
        
    async def request_leave(self, request: LeaveRequest) -> LeaveApproval:
        """Request leave with automatic coverage planning"""
        
        personnel = await self.registry.get_profile(request.personnel_id)
        config = TIER_CONFIGS[personnel.tier]
        
        # Validate leave request
        validation = self._validate_leave_request(personnel, request, config)
        if not validation.valid:
            return LeaveApproval(approved=False, reason=validation.reason)
        
        # Create leave record
        leave = ActiveLeave(
            leave_id=f"LEAVE_{request.personnel_id}_{uuid.uuid4().hex[:8]}",
            personnel_id=request.personnel_id,
            leave_type=request.leave_type,
            start_date=request.start_date,
            end_date=request.end_date,
            reason=request.reason,
            status=LeaveStatus.APPROVED,
            coverage_required=self._calculate_coverage_needs(personnel, request)
        )
        
        # Find substitutes
        substitutes = await self._find_substitutes(personnel, leave)
        
        if not substitutes and leave.coverage_required:
            return LeaveApproval(approved=False, reason="No qualified substitutes available")
        
        # Create coverage assignments
        for sub in substitutes:
            assignment = CoverageAssignment(
                assignment_id=f"COV_{leave.leave_id}_{sub.personnel_id}",
                leave_id=leave.leave_id,
                original_personnel_id=request.personnel_id,
                substitute_id=sub.personnel_id,
                duties_covered=leave.coverage_required.duties,
                start_date=request.start_date,
                end_date=request.end_date,
                compensation_rate=config.leave_coverage_rate,
                merit_bonus=self._calculate_merit_bonus(sub, leave)
            )
            
            self.coverage_assignments[assignment.assignment_id] = assignment
            
            # Notify substitute
            await self._notify_substitute(sub, assignment)
        
        # Activate coverage protocol
        leave.coverage_assignments = [a.assignment_id for a in self.coverage_assignments.values() 
                                      if a.leave_id == leave.leave_id]
        leave.status = LeaveStatus.COVERAGE_ACTIVE
        
        self.active_leaves[leave.leave_id] = leave
        
        # Fund leave coverage from wallet
        await self._fund_leave_coverage(personnel, leave)
        
        return LeaveApproval(
            approved=True,
            leave=leave,
            substitutes=[sub.personnel_id for sub in substitutes],
            coverage_details=[{
                'substitute_id': sub.personnel_id,
                'duties': a.duties_covered,
                'merit_bonus': a.merit_bonus
            } for sub, a in zip(substitutes, [ca for ca in self.coverage_assignments.values() if ca.leave_id == leave.leave_id])]
        )
    
    def _calculate_coverage_needs(self, personnel: PersonnelProfile, request: LeaveRequest) -> CoverageNeeds:
        """Calculate what coverage is needed based on role and duties"""
        
        # Get current citizen assignments
        citizen_assignments = self._get_attendant_assignments(personnel.personnel_id)
        
        # Get active projects/tasks
        active_tasks = self._get_active_tasks(personnel.personnel_id)
        
        # Determine criticality
        critical_citizens = [c for c in citizen_assignments if c.vulnerability_score > 0.7]
        critical_tasks = [t for t in active_tasks if t.priority == 'CRITICAL']
        
        return CoverageNeeds(
            citizen_assignments=citizen_assignments,
            critical_citizens=critical_citizens,
            active_tasks=active_tasks,
            critical_tasks=critical_tasks,
            duties=[
                DutyCoverage(
                    duty_type="CITIZEN_CARE",
                    targets=[c.citizen_id for c in critical_citizens],
                    frequency="DAILY",
                    skill_required="CARE_CERTIFICATION"
                ),
                DutyCoverage(
                    duty_type="QUEST_VISITS",
                    targets=[c.citizen_id for c in citizen_assignments if c.quest_scheduled],
                    frequency="PER_SCHEDULE",
                    skill_required="QUEST_PROTOCOL"
                ),
                DutyCoverage(
                    duty_type="EMERGENCY_RESPONSE",
                    targets=[],
                    frequency="ON_CALL",
                    skill_required="CRISIS_TRAINING"
                )
            ],
            requires_same_tier=len(critical_citizens) > 0
        )
    
    async def _find_substitutes(self, personnel: PersonnelProfile, leave: ActiveLeave) -> List[SubstituteCandidate]:
        """Find qualified substitutes using merit-weighted matching"""
        
        config = TIER_CONFIGS[personnel.tier]
        substitute_tier = config.leave_substitute_tier
        
        # Get candidates from substitute tier
        candidates = await self.registry.get_personnel_by_tier(substitute_tier)
        
        # Filter: same territory, available, qualified
        qualified = []
        for candidate in candidates:
            if candidate.personnel_id == personnel.personnel_id:
                continue
            
            # Check availability
            if not self._is_available(candidate, leave.start_date, leave.end_date):
                continue
            
            # Check qualifications
            if not self._has_required_skills(candidate, leave.coverage_required):
                continue
            
            # Check well-being capacity (not overloaded)
            if not self._has_capacity(candidate, leave.coverage_required):
                continue
            
            # Calculate merit-weighted suitability
            suitability = self._calculate_substitute_suitability(candidate, personnel, leave)
            
            qualified.append(SubstituteCandidate(
                personnel_id=candidate.personnel_id,
                tier=candidate.tier,
                suitability_score=suitability,
                merit_bonus_eligible=suitability > 0.7,
                current_load=self._get_current_load(candidate)
            ))
        
        # Sort by suitability
        qualified.sort(key=lambda c: c.suitability_score, reverse=True)
        
        # Return top candidates (max 2 per critical duty)
        max_needed = max(2, len(leave.coverage_required.critical_citizens))
        return qualified[:max_needed]
    
    def _calculate_substitute_suitability(self, candidate: PersonnelProfile, 
                                          original: PersonnelProfile, 
                                          leave: ActiveLeave) -> float:
        """Merit-weighted suitability score"""
        
        factors = {}
        
        # Merit score (0-1)
        merit_profile = self.merit_system.get_profile(candidate.personnel_id)
        factors['merit'] = merit_profile.total_merits / 10000  # Normalize
        
        # Relational continuity (knows the citizens)
        factors['continuity'] = self._calculate_continuity(candidate, leave.coverage_required.citizen_assignments)
        
        # Skill match
        factors['skills'] = self._calculate_skill_match(candidate, leave.coverage_required)
        
        # Well-being capacity
        factors['capacity'] = candidate.well_being_score
        
        # Proximity
        factors['proximity'] = self._calculate_proximity(candidate, original)
        
        # Weighted composite
        weights = {'merit': 0.25, 'continuity': 0.3, 'skills': 0.25, 'capacity': 0.1, 'proximity': 0.1}
        
        return sum(factors[k] * weights[k] for k in factors)
    
    def _calculate_merit_bonus(self, substitute: SubstituteCandidate, leave: ActiveLeave) -> MeritBonus:
        """Calculate merit bonus for covering leave"""
        
        base_bonus = 100  # Base merit for coverage
        
        # Multipliers
        criticality_mult = 1.0 + len(leave.coverage_required.critical_citizens) * 0.2
        duration_mult = 1.0 + (leave.end_date - leave.start_date).days / 30 * 0.1
        tier_mult = 1.0 + (substitute.tier.value == leave.original_personnel_tier) * 0.3
        
        total_bonus = int(base_bonus * criticality_mult * duration_mult * tier_mult)
        
        return MeritBonus(
            bonus_merits=total_bonus,
            bonus_type=MeritBonusType.LEAVE_COVERAGE,
            description=f"Covered leave for {leave.original_personnel_id}: {leave.coverage_required.duties}",
            paid_from=SupportCategory.LEAVE_COVERAGE
        )
```

### 5.2 Leave Continuity Monitoring

```python
# personnel/leave_monitoring.py
"""
Real-time monitoring of leave coverage quality.
Triggers interventions if coverage degrades.
"""

class LeaveCoverageMonitor:
    def __init__(self, continuity_system: LeaveContinuitySystem, quest_engine: 'QuestEngine'):
        self.continuity = continuity_system
        self.quest_engine = quest_engine
        self.monitoring_active = True
        
    async def monitor_active_leaves(self):
        """Continuous monitoring of all active leaves"""
        
        while self.monitoring_active:
            for leave_id, leave in self.continuity.active_leaves.items():
                if leave.status == LeaveStatus.COVERAGE_ACTIVE:
                    await self._check_coverage_quality(leave)
            
            await asyncio.sleep(3600)  # Check hourly
    
    async def _check_coverage_quality(self, leave: ActiveLeave):
        """Check if substitute is maintaining care quality"""
        
        for assignment_id in leave.coverage_assignments:
            assignment = self.continuity.coverage_assignments.get(assignment_id)
            if not assignment:
                continue
            
            # Check citizen well-being under substitute
            for citizen_id in assignment.duties_covered:
                if citizen_id.startswith('CITIZEN_'):
                    well_being = await self._check_citizen_wellbeing(citizen_id)
                    
                    if well_being.score < 0.6:  # Degradation threshold
                        await self._trigger_coverage_intervention(leave, assignment, citizen_id, well_being)
            
            # Check substitute well-being
            sub_wellbeing = await self._check_substitute_wellbeing(assignment.substitute_id)
            if sub_wellbeing.score < 0.5:
                await self._trigger_substitute_support(assignment)
            
            # Trigger Quest check-in for critical citizens
            critical_citizens = [c for c in leave.coverage_required.citizen_assignments if c.vulnerability_score > 0.7]
            for citizen in critical_citizens:
                await self.quest_engine.initiate_wellbeing_check(citizen.citizen_id, reason="LEAVE_COVERAGE_MONITORING")
```

---

## 6. DIRECT WELL-BEING COMMUNICATION CHANNEL

### 6.1 System→Personnel: Not Orders, But Care

```python
# personnel/wellbeing_channel.py
"""
Direct Well-Being Channel: System communicates care, not commands.
"How are you?" not "Do this."
"""

class WellBeingChannel:
    """
    Communication channel from governance system to personnel.
    Only sends: check-ins, resource offers, appreciation, rest reminders.
    Never sends: orders, deadlines, performance pressure.
    """
    
    def __init__(self, personnel_registry: 'PersonnelRegistry', merit_system: 'MeritLedger'):
        self.registry = personnel_registry
        self.merit_system = merit_system
        self.message_templates = self._load_templates()
        self.communication_log: Dict[str, List[WellBeingMessage]] = {}
        
    async def send_daily_checkin(self, personnel_id: str) -> CheckInResult:
        """Daily personalized check-in (not surveillance)"""
        
        personnel = await self.registry.get_profile(personnel_id)
        
        # Select template based on tier, recent context
        template = self._select_checkin_template(personnel)
        
        # Personalize
        message = self._personalize_message(template, personnel)
        
        # Send via preferred channel (WhatsApp, app, email, in-person via Quest)
        channel = self._get_preferred_channel(personnel)
        
        sent = await self._send_message(personnel_id, message, channel)
        
        if sent:
            # Log for relationship tracking (not compliance)
            self.communication_log.setdefault(personnel_id, []).append(WellBeingMessage(
                message_id=f"MSG_{personnel_id}_{uuid.uuid4().hex[:8]}",
                personnel_id=personnel_id,
                type=MessageType.DAILY_CHECKIN,
                content=message.content,
                channel=channel,
                sent_at=datetime.now(),
                response_received=False
            ))
        
        return CheckInResult(sent=sent, message=message, channel=channel)
    
    def _select_checkin_template(self, personnel: PersonnelProfile) -> MessageTemplate:
        """Select appropriate check-in template"""
        
        templates = {
            PersonnelTier.TIER_1_QUEST_GUIDES: [
                "¡Buenos días! ¿Cómo amaneció su caminata de hoy? ¿Necesita algo para el camino?",
                "Hola, pensando en usted y su labor de conectar. ¿Todo bien en los hogares que visita?",
            ],
            PersonnelTier.TIER_2_ATTENDANTS: [
                "Buenos días. ¿Cómo está su energía hoy? Recuerde: cuidar también es dejarse cuidar.",
                "Hola. Sus ciudadanos le aprecian. ¿Necesita algún apoyo para su jornada?",
            ],
            PersonnelTier.TIER_3_FIELD_OPERATORS: [
                "Buenos días. Trabajo duro el de hoy. ¿Tiene agua, sombra, descanso garantizado?",
                "Hola. Su labor sostiene la infraestructura. ¿Todo seguro en el campo?",
            ],
            PersonnelTier.TIER_4_KNOWLEDGE_WORKERS: [
                "Buenos días. ¿Mente clara para hoy? Recuerde pausas cada 90 minutos.",
                "Hola. Pensamiento profundo merece descanso profundo. ¿Cómo va la carga mental?",
            ],
            PersonnelTier.TIER_5_COORDINADORES: [
                "Buenos días. Liderar es servir. ¿Su equipo y usted tienen lo que necesitan?",
                "Hola. Coordinar cuida a otros. ¿Quién le cuida a usted hoy?",
            ],
            PersonnelTier.TIER_6_SPECIALISTS: [
                "Buenos días. Su expertise salva vidas. ¿Descansó bien? Su agudeza es vital.",
                "Hola. Especialista: la precisión requiere pausa. ¿Su bienestar está atendido?",
            ],
            PersonnelTier.TIER_7_STRATEGIC: [
                "Buenos días. Decidir por muchos pesa. ¿Tiene espacio para pensar y respirar?",
                "Hola. Su visión guía. ¿Necesita silencio, datos, o solo un café tranquilo?",
            ],
            PersonnelTier.TIER_8_FOUNDATIONAL: [
                "Buenos días. Lo invisible sostiene todo. ¿Su cuerpo, sus herramientas, su dignidad están bien?",
                "Hola. Base firme, todo arriba se sostiene. ¿Le falta algo hoy?",
            ],
        }
        
        tier_templates = templates.get(personnel.tier, templates[PersonnelTier.TIER_4_KNOWLEDGE_WORKERS])
        
        # Select based on day of week, recent stress
        import random
        return MessageTemplate(
            template_id=f"CHECKIN_{personnel.tier.value}_{random.randint(0, len(tier_templates)-1)}",
            content=random.choice(tier_templates),
            tone="caring",
            expects_reply=True,
            reply_options=["Todo bien", "Necesito apoyo", "Solo gracias", "Quiero hablar"]
        )
    
    async def send_rest_reminder(self, personnel_id: str, reason: RestReminderReason):
        """Send mandatory rest reminder (not as punishment, as care)"""
        
        personnel = await self.registry.get_profile(personnel_id)
        
        messages = {
            RestReminderReason.QUARTERLY_MANDATORY: [
                "Es hora de su descanso trimestral obligatorio. No es opcional: es cuidado. Disfrútelo sin culpa.",
                "Sus días de descanso obligatorio llegaron. El sistema se pauses por usted. Desconéctese."
            ],
            RestReminderReason.HIGH_STRESS_DETECTED: [
                "Notamos señales de fatiga. Por favor, tome un día. Su bienestar vale más que cualquier métrica.",
                "Su cuerpo pide pausa. Escúchelo. Le damos permiso oficial para descansar mañana."
            ],
            RestReminderReason.POST_CRISIS: [
                "Después de lo vivido, descanse es orden médica y humana. No regrese hasta estar listo.",
                "Lo que hizo fue extraordinario. Ahora lo ordinario: cuidarse. Tómese el tiempo."
            ],
        }
        
        message_options = messages.get(reason, ["Descanse, por favor. Lo necesita y lo merece."])
        
        template = MessageTemplate(
            template_id=f"REST_{reason.value}",
            content=random.choice(message_options),
            tone="protective",
            expects_reply=False,
            reply_options=["Entendido, gracias", "Ya estoy descansando", "Necesito más tiempo"]
        )
        
        message = self._personalize_message(template, personnel)
        await self._send_message(personnel_id, message, self._get_preferred_channel(personnel))
    
    async def send_appreciation(self, personnel_id: str, reason: AppreciationReason, details: str):
        """Send genuine appreciation (not performance review)"""
        
        personnel = await self.registry.get_profile(personnel_id)
        
        message = f"Queremos que sepa: {reason.value}. {details}. Gracias por ser quien es en este sistema."
        
        template = MessageTemplate(
            template_id=f"APPRECIATION_{reason.value}",
            content=message,
            tone="grateful",
            expects_reply=False,
            reply_options=["Gracias", "Significa mucho", "Seguimos"]
        )
        
        await self._send_message(personnel_id, template, self._get_preferred_channel(personnel))
```

---

## 7. INTEGRATION WITH CENTRAL AI FUND & MERIT SYSTEM

### 7.1 Personnel Fund Manager

```python
# personnel/fund_integration.py
"""
Integration with Central AI Fund Manager for personnel well-being funds.
"""

class PersonnelFundManager:
    def __init__(self, central_ai: 'CentralAIFundManager', personnel_registry: 'PersonnelRegistry'):
        self.central_ai = central_ai
        self.registry = personnel_registry
        self.personnel_wallets: Dict[str, SupportWallet] = {}
        
    async def initialize_all_wallets(self):
        """Initialize support wallets for all active personnel"""
        
        all_personnel = await self.registry.get_all_active()
        
        for personnel in all_personnel:
            wallet = SupportWallet(personnel.personnel_id, personnel.tier, self.central_ai)
            await wallet.initialize_wallet()
            self.personnel_wallets[personnel.personnel_id] = wallet
            
            # Link to personnel profile
            personnel.support_wallet = wallet
    
    async def monthly_replenishment(self):
        """Monthly replenishment of all wallets"""
        
        for personnel_id, wallet in self.personnel_wallets.items():
            personnel = await self.registry.get_profile(personnel_id)
            config = TIER_CONFIGS[personnel.tier]
            
            # Replenish general wellbeing
            await wallet.credit(
                SupportCategory.WELLBEING_GENERAL,
                config.base_wellbeing_allowance,
                WalletTransactionType.MONTHLY_REPLENISHMENT
            )
            
            # Check and replenish other categories
            for category, rule in wallet.replenishment_rules.items():
                if wallet.balances[category] < rule.min_threshold:
                    await wallet.credit(
                        category,
                        rule.amount,
                        WalletTransactionType.AUTO_REPLENISHMENT
                    )
    
    async def process_leave_funding(self, leave: ActiveLeave):
        """Fund leave coverage from original personnel's wallet"""
        
        original_wallet = self.personnel_wallets.get(leave.personnel_id)
        if not original_wallet:
            return
        
        config = TIER_CONFIGS[leave.original_tier]
        
        # Calculate coverage cost
        coverage_cost = self._calculate_coverage_cost(leave)
        
        # Debit from leave coverage category
        await original_wallet.debit(
            SupportCategory.LEAVE_COVERAGE,
            coverage_cost,
            f"Leave coverage for {leave.leave_id}",
            leave.leave_id
        )
        
        # Credit to substitutes' wallets
        for assignment_id in leave.coverage_assignments:
            assignment = self.continuity.coverage_assignments[assignment_id]
            sub_wallet = self.personnel_wallets.get(assignment.substitute_id)
            if sub_wallet:
                await sub_wallet.credit(
                    SupportCategory.WELLBEING_GENERAL,
                    coverage_cost / len(leave.coverage_assignments),
                    WalletTransactionType.LEAVE_COVERAGE_COMPENSATION,
                    assignment.assignment_id
                )
```

---

## 8. IMPLEMENTATION ROADMAP

### Phase 1: Classification & Wallet (Months 1-2)
- [ ] Deploy 8-tier personnel classification
- [ ] Build Support Wallet with 8 categories
- [ ] Integrate with Central AI Fund
- [ ] Initialize wallets for all personnel
- [ ] Deploy Attendant-Citizen bidirectional accounting

### Phase 2: Anticipation & Leave (Months 3-4)
- [ ] Deploy Anticipation Engine (age, role, usage predictions)
- [ ] Build Pending Purchase auto-execution
- [ ] Deploy Zero-Gap Leave Continuity System
- [ ] Implement merit-weighted substitute matching
- [ ] Deploy Leave Coverage Monitor

### Phase 3: Communication & Care (Months 5-6)
- [ ] Deploy Direct Well-Being Channel
- [ ] Implement daily check-ins (multi-channel)
- [ ] Build rest reminder system
- [ ] Deploy appreciation messaging
- [ ] Integrate with Quest for in-person check-ins

### Phase 4: Predictive & Systemic (Months 7-9)
- [ ] Advanced life-stage prediction models
- [ ] Cross-personnel well-being analytics
- [ ] Systemic risk forecasting for personnel burnout
- [ ] Integration with institutional accountability
- [ ] Caribbean regional personnel well-being standards

---

## 9. KEY PERFORMANCE INDICATORS

| KPI | Target | Measurement |
|-----|--------|-------------|
| **Wallet Funding Adequacy** | 100% categories funded | Wallet balances vs config |
| **Pending Purchase Fulfillment** | > 95% on time | Execution tracking |
| **Leave Coverage Continuity** | 100% zero-gap | Coverage monitor |
| **Substitute Suitability** | > 0.8 avg score | Post-leave surveys |
| **Daily Check-in Response Rate** | > 80% | Communication logs |
| **Rest Compliance** | 100% mandatory taken | Leave records |
| **Well-Being Score Stability** | > 0.7 avg | Monthly assessments |
| **Anticipation Accuracy** | > 80% predictions correct | Prediction validation |
| **Attendant-Citizen Continuity** | > 90% during leave | Citizen feedback |
| **Personnel Retention** | > 95% annual | HR records |

---

## 10. LEGAL & ETHICAL FRAMEWORK

### 10.1 Personnel Rights Charter

| Right | Implementation |
|-------|----------------|
| **Dignified Support** | Wallet funds are rights, not benefits |
| **Predictive Care** | Needs anticipated, not reacted to |
| **Leave Without Guilt** | Zero-gap coverage, merit bonuses |
| **Direct Communication** | Care messages, never orders |
| **Privacy in Well-Being** | Scores confidential, only trends shared |
| **Aging with Security** | Life-stage funds pre-allocated |
| **Mutual Care Reciprocity** | Care given = care received (accounting) |

### 10.2 Ethical Guardrails

```python
PERSONNEL_WELLBEING_ETHICS = {
    'no_surveillance': 'Well-being data never used for performance evaluation',
    'no_coercion': 'Check-ins are invitations, rest is mandatory not optional',
    'privacy_first': 'Individual scores encrypted, only aggregated trends visible',
    'care_not_control': 'Every system message: "How can we support you?"',
    'equity_in_support': 'Tier configs adjust for relational intensity, not hierarchy',
    'leave_as_right': 'Leave triggers care, not scrutiny',
    'anticipation_not_reaction': 'Funds ready before needs become crises',
}
```

---

*Document Version: 1.0 | Date: 2026-11-10*
*System: Personnel Well-Being Management System*
*Integrates: 8-Tier Classification + Bidirectional Accounting + Support Wallet + Anticipation Engine + Zero-Gap Leave + Direct Care Channel*
*Connected to: Merit System + Central AI Fund + Convivencia Limpia + Institutional Accountability*
*Location: F:\managements\personnel_wellbeing_management_system.md*