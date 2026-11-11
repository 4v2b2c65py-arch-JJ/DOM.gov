# Multi-Source Institutional Accountability Framework
## Real-Time Monitoring, Global API Integration & Citizen-Oversight Accountability
### Integrated with Japanese Meta-Governance & Integrated Liability-Redress Models

---

## 1. EXECUTIVE SUMMARY

### 1.1 Core Problem
Institutions in the Dominican Republic lack real-time, multi-source accountability. Corruption, inefficiency, and service failures persist because:
- No automated cross-referencing of internal performance data with external benchmarks
- Global standards (UN, OECD, OAS, IDB) are not integrated into daily governance
- Citizen oversight is disconnected from institutional decision-making
- Accountability is retrospective, not preventive

### 1.2 Solution: Accountability Data Fusion Engine
A real-time accountability system that fuses:
1. **Internal Model Data** - From all 6 governance layers (Technical, Organizational, Soft Law, Hard Law, Market, Social Norm)
2. **Global Establishment APIs** - UN SDG, OECD Governance, OAS Democracy, IDB/WB Performance, IMF Fiscal, WHO Health, UNESCO Education, ILO Labor
3. **Citizen Oversight** - Merit-weighted Veeduría, Quest engagement, Mutual Aid feedback
4. **Automated Accountability Scoring** - Real-time institutional health dashboards
5. **Integrated Liability-Redress** - Japanese model: no-fault compensation + proportional accountability

---

## 2. ACCOUNTABILITY DATA ARCHITECTURE

### 2.1 Multi-Source Data Fusion Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    ACCOUNTABILITY DATA FUSION ENGINE                                │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  INTERNAL SOURCES (6 Governance Layers)          GLOBAL ESTABLISHMENT APIs          │
│  ┌─────────────────────────────────────────┐    ┌─────────────────────────────────┐ │
│  │ Layer 1: Technical (CPS/SoS)            │    │ UN SDG API                      │ │
│  │   - Infrastructure health               │    │   - Goal 16: Institutions       │ │
│  │   - Service delivery metrics            │    │   - Goal 11: Cities             │ │
│  │   - Digital twin status                 │    │   - Goal 6: Water               │ │
│  ├─────────────────────────────────────────┤    ├─────────────────────────────────┤ │
│  │ Layer 2: Organizational                 │    │ OECD Governance API             │ │
│  │   - Integrity unit performance          │    │   - Budget transparency         │ │
│  │   - Merit-based hiring compliance       │    │   - Procurement integrity       │ │
│  │   - Training completion                 │    │   - Regulatory quality          │ │
│  ├─────────────────────────────────────────┤    ├─────────────────────────────────┤ │
│  │ Layer 3: Soft Law (Guidelines)          │    │ OAS Democracy API               │ │
│  │   - Sandbox graduation rates            │    │   - Electoral integrity         │ │
│  │   - Guideline adoption                  │    │   - Human rights compliance     │ │
│  │   - Participatory policy making         │    │   - Anti-corruption measures    │ │
│  ├─────────────────────────────────────────┤    ├─────────────────────────────────┤ │
│  │ Layer 4: Hard Law (Legislation)         │    │ IDB/World Bank API              │ │
│  │   - Law enforcement rates               │    │   - Project performance         │ │
│  │   - Judicial efficiency                 │    │   - Fiscal sustainability       │ │
│  │   - Rights protection                   │    │   - Climate resilience          │ │
│  ├─────────────────────────────────────────┤    ├─────────────────────────────────┤ │
│  │ Layer 5: Market (Incentives)            │    │ IMF Fiscal API                  │ │
│  │   - Performance bonus distribution      │    │   - Revenue mobilization        │ │
│  │   - Procurement fairness                │    │   - Expenditure efficiency      │ │
│  │   - Transparency scores                 │    │   - Debt sustainability         │ │
│  ├─────────────────────────────────────────┤    ├─────────────────────────────────┤ │
│  │ Layer 6: Social Norm (Convivencia)      │    │ WHO/UNESCO/ILO APIs             │ │
│  │   - Kindness/cleanliness indices        │    │   - Health system performance   │ │
│  │   - Quest engagement rates              │    │   - Education quality           │ │
│  │   - Mutual aid coverage                 │    │   - Labor standards             │ │
│  └─────────────────────────────────────────┘    └─────────────────────────────────┘ │
│                                    │                              │                  │
│                                    └──────────────┬───────────────┘                  │
│                                                   ▼                                  │
│                                    ┌─────────────────────────────────┐               │
│                                    │      DATA FUSION LAYER         │               │
│                                    │  • Entity resolution           │               │
│                                    │  • Temporal alignment          │               │
│                                    │  • Cross-source validation     │               │
│                                    │  • Anomaly detection           │               │
│                                    │  • Blockchain anchoring        │               │
│                                    └──────────────┬────────────────┘               │
│                                                   ▼                                  │
│                                    ┌─────────────────────────────────┐               │
│                                    │    ACCOUNTABILITY ENGINE       │               │
│                                    │  • Real-time scoring           │               │
│                                    │  • Predictive risk             │               │
│                                    │  • Automated alerts            │               │
│                                    │  • Liability-redress triggers  │               │
│                                    └──────────────┬────────────────┘               │
│                                                   ▼                                  │
│                          ┌──────────────┬──────────────┬──────────────┐            │
│                          ▼              ▼              ▼              ▼            │
│                   ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐      │
│                   │ INSTITUTIONAL│ │  CITIZEN  │ │  GLOBAL   │ │  LIABILITY │      │
│                   │  DASHBOARD  │  │ OVERSIGHT │  │ REPORTING │  │  REDRESS   │      │
│                   │             │  │  PORTAL   │  │  ENGINE   │  │  ENGINE   │      │
│                   └───────────┘  └───────────┘  └───────────┘  └───────────┘      │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Core Data Models

```python
# accountability/data_models.py
"""
Core data models for multi-source institutional accountability.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

class InstitutionType(Enum):
    EXECUTIVE_MINISTRY = "executive_ministry"
    AUTONOMOUS_INSTITUTE = "autonomous_institute"
    MUNICIPALITY = "municipality"
    REGULATORY_BODY = "regulatory_body"
    JUDICIAL = "judicial"
    LEGISLATIVE = "legislative"
    STATE_OWNED_ENTERPRISE = "state_owned_enterprise"
    PUBLIC_UTILITY = "public_utility"
    SOCIAL_PROGRAM = "social_program"

class AccountabilityDimension(Enum):
    TRANSPARENCY = "transparency"
    INTEGRITY = "integrity"
    EFFECTIVENESS = "effectiveness"
    EFFICIENCY = "efficiency"
    RESPONSIVENESS = "responsiveness"
    EQUITY = "equity"
    SUSTAINABILITY = "sustainability"
    PARTICIPATION = "participation"
    RULE_OF_LAW = "rule_of_law"
    HUMAN_RIGHTS = "human_rights"

class DataSource(Enum):
    # Internal
    TECHNICAL_LAYER = "technical_layer"
    ORGANIZATIONAL_LAYER = "organizational_layer"
    SOFT_LAW_LAYER = "soft_law_layer"
    HARD_LAW_LAYER = "hard_law_layer"
    MARKET_LAYER = "market_layer"
    SOCIAL_NORM_LAYER = "social_norm_layer"
    
    # Global Establishments
    UN_SDG = "un_sdg"
    OECD_GOVERNANCE = "oecd_governance"
    OAS_DEMOCRACY = "oas_democracy"
    IDB_PROJECTS = "idb_projects"
    WORLD_BANK = "world_bank"
    IMF_FISCAL = "imf_fiscal"
    WHO_HEALTH = "who_health"
    UNESCO_EDUCATION = "unesco_education"
    ILO_LABOR = "ilo_labor"
    TRANSPARENCY_INTERNATIONAL = "transparency_international"
    
    # Citizen
    VEEDURIA_CIUDADANA = "veeduria_ciudadana"
    QUEST_ENGAGEMENT = "quest_engagement"
    MUTUAL_AID_FEEDBACK = "mutual_aid_feedback"
    RP_CREDENTIALS = "rp_credentials"

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class AccountabilityIndicator:
    """Single accountability metric from a specific source"""
    indicator_id: str
    institution_id: str
    dimension: AccountabilityDimension
    source: DataSource
    source_metric_id: str  # Original metric ID from source
    value: float
    normalized_value: float  # 0-1 scale
    unit: str
    timestamp: datetime
    confidence: float  # 0-1
    metadata: Dict[str, Any] = field(default_factory=dict)
    blockchain_hash: str = ""

@dataclass
class InstitutionAccountabilityProfile:
    """Complete accountability profile for an institution"""
    institution_id: str
    institution_name: str
    institution_type: InstitutionType
    territory_code: str
    responsible_roles: List[str]  # Role IDs from governance system
    
    # Dimension scores (0-1)
    dimension_scores: Dict[AccountabilityDimension, float] = field(default_factory=dict)
    
    # Composite score
    composite_score: float = 0.0
    percentile_rank: float = 0.0  # National percentile
    
    # Trend
    trend: str = "stable"  # improving, stable, declining
    trend_confidence: float = 0.0
    
    # Source breakdown
    internal_score: float = 0.0
    global_score: float = 0.0
    citizen_score: float = 0.0
    
    # Risk flags
    active_alerts: List[AccountabilityAlert] = field(default_factory=list)
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
    
    # Liability-Redress
    liability_exposure: Decimal = Decimal('0')
    redress_obligations: List[str] = field(default_factory=list)
    
    # Metadata
    last_updated: datetime = datetime.now()
    data_completeness: float = 0.0  # % of expected indicators received
    blockchain_anchor: str = ""

@dataclass
class AccountabilityAlert:
    """Real-time accountability alert"""
    alert_id: str
    institution_id: str
    dimension: AccountabilityDimension
    severity: AlertSeverity
    title: str
    description: str
    triggering_indicators: List[str]  # indicator_ids
    threshold_breached: Dict[str, Any]
    detected_at: datetime
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolution_status: str = "OPEN"  # OPEN, INVESTIGATING, RESOLVED, ESCALATED
    liability_triggered: bool = False
    redress_required: bool = False
    blockchain_hash: str = ""

@dataclass
class GlobalBenchmark:
    """Benchmark from global establishment"""
    benchmark_id: str
    source: DataSource
    dimension: AccountabilityDimension
    country: str = "DOM"
    year: int
    value: float
    ranking: Optional[int] = None  # Global ranking
    percentile: Optional[float] = None
    trend: str = "stable"
    metadata: Dict = field(default_factory=dict)
```

---

## 3. GLOBAL ESTABLISHMENT API INTEGRATION

### 3.1 API Connector Framework

```python
# accountability/global_apis.py
"""
Global Establishment API Connectors for Accountability Benchmarking.
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

class GlobalEstablishmentConnector:
    """Base connector for global establishment APIs"""
    
    def __init__(self, api_config: 'APIConfig'):
        self.config = api_config
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, tuple] = {}  # key -> (data, timestamp)
        self.cache_ttl = 3600  # 1 hour default
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    async def fetch_indicators(self, country: str = "DOM", 
                               dimensions: List[AccountabilityDimension] = None) -> List[AccountabilityIndicator]:
        """Fetch and normalize indicators from this establishment"""
        raise NotImplementedError
    
    async def fetch_benchmarks(self, country: str = "DOM") -> List[GlobalBenchmark]:
        """Fetch benchmark data for comparison"""
        raise NotImplementedError

class UN_SDG_Connector(GlobalEstablishmentConnector):
    """UN SDG API - Sustainable Development Goals indicators"""
    
    BASE_URL = "https://unstats.un.org/SDGAPI/v1/sdg"
    
    # Goal 16 (Institutions) + Goal 11 (Cities) + Goal 6 (Water) + Goal 7 (Energy) + Goal 4 (Education)
    RELEVANT_INDICATORS = {
        AccountabilityDimension.TRANSPARENCY: ["16.6.1", "16.6.2"],
        AccountabilityDimension.INTEGRITY: ["16.5.1", "16.5.2"],
        AccountabilityDimension.EFFECTIVENESS: ["16.6.1", "16.6.2", "11.3.1"],
        AccountabilityDimension.RULE_OF_LAW: ["16.3.1", "16.3.2", "16.3.3"],
        AccountabilityDimension.HUMAN_RIGHTS: ["16.1.1", "16.1.2", "16.1.3", "16.1.4"],
        AccountabilityDimension.PARTICIPATION: ["16.7.1", "16.7.2"],
        AccountabilityDimension.EQUITY: ["10.3.1", "16.b.1"],
        AccountabilityDimension.SUSTAINABILITY: ["11.6.1", "11.6.2", "6.1.1", "7.1.1"],
    }
    
    async def fetch_indicators(self, country: str = "DOM", 
                               dimensions: List[AccountabilityDimension] = None) -> List[AccountabilityIndicator]:
        indicators = []
        target_dims = dimensions or list(self.RELEVANT_INDICATORS.keys())
        
        for dimension in target_dims:
            sdg_codes = self.RELEVANT_INDICATORS.get(dimension, [])
            for code in sdg_codes:
                data = await self._fetch_sdg_indicator(country, code)
                if data:
                    indicator = self._normalize_sdg_data(data, dimension, code)
                    indicators.append(indicator)
        
        return indicators
    
    async def _fetch_sdg_indicator(self, country: str, code: str) -> Optional[Dict]:
        url = f"{self.BASE_URL}/Indicator/{code}/GeoArea/{self._get_country_code(country)}"
        async with self.session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
        return None

class OECD_Governance_Connector(GlobalEstablishmentConnector):
    """OECD Government at a Glance / OECD Anti-Corruption indicators"""
    
    BASE_URL = "https://stats.oecd.org/SDMX-JSON/data"
    
    DATASETS = {
        "GOV_GLAG": "Government at a Glance",
        "GOV_BUDGET": "Budget Transparency",
        "GOV_PROCUREMENT": "Public Procurement",
        "GOV_INTEGRITY": "Public Integrity",
        "GOV_REGULATORY": "Regulatory Quality",
        "GOV_DIGITAL": "Digital Government",
    }
    
    async def fetch_indicators(self, country: str = "DOM", 
                               dimensions: List[AccountabilityDimension] = None) -> List[AccountabilityIndicator]:
        indicators = []
        
        # OECD doesn't always include DR - use regional averages or LAC group
        for dataset_code, dataset_name in self.DATASETS.items():
            data = await self._fetch_oecd_dataset(dataset_code, country)
            if data:
                normalized = self._normalize_oecd_data(data, dataset_code)
                indicators.extend(normalized)
        
        return indicators
    
    async def _fetch_oecd_dataset(self, dataset: str, country: str) -> Optional[Dict]:
        # OECD SDMX-JSON query
        url = f"{self.BASE_URL}/{dataset}/A.{country}..../all?startTime=2020&endTime=2024"
        async with self.session.get(url, headers={"Accept": "application/json"}) as resp:
            if resp.status == 200:
                return await resp.json()
        return None

class OAS_Democracy_Connector(GlobalEstablishmentConnector):
    """OAS Inter-American Democratic Charter compliance indicators"""
    
    BASE_URL = "https://www.oas.org/en/sap/democ/indicators"
    
    INDICATORS = {
        AccountabilityDimension.RULE_OF_LAW: ["judicial_independence", "due_process", "access_to_justice"],
        AccountabilityDimension.HUMAN_RIGHTS: ["freedom_expression", "assembly", "association"],
        AccountabilityDimension.PARTICIPATION: ["electoral_integrity", "civic_participation"],
        AccountabilityDimension.TRANSPARENCY: ["access_to_information", "asset_declaration"],
        AccountabilityDimension.INTEGRITY: ["anti_corruption_bodies", "whistleblower_protection"],
    }

class IDB_Projects_Connector(GlobalEstablishmentConnector):
    """Inter-American Development Bank project performance data"""
    
    BASE_URL = "https://api.iadb.org/projects/v1"
    
    async def fetch_institution_projects(self, institution_name: str) -> List[Dict]:
        """Fetch all IDB projects for a Dominican institution"""
        url = f"{self.BASE_URL}/projects?country=DR&executing_agency={institution_name}"
        async with self.session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
        return []

class WorldBank_Governance_Connector(GlobalEstablishmentConnector):
    """World Bank Worldwide Governance Indicators (WGI)"""
    
    BASE_URL = "https://api.worldbank.org/v2/country/DOM/indicator"
    
    WGI_INDICATORS = {
        "CC.EST": AccountabilityDimension.INTEGRITY,           # Control of Corruption
        "GE.EST": AccountabilityDimension.EFFECTIVENESS,       # Government Effectiveness
        "PV.EST": AccountabilityDimension.HUMAN_RIGHTS,        # Political Stability/Violence
        "RQ.EST": AccountabilityDimension.RULE_OF_LAW,         # Regulatory Quality
        "RL.EST": AccountabilityDimension.RULE_OF_LAW,         # Rule of Law
        "VA.EST": AccountabilityDimension.PARTICIPATION,       # Voice and Accountability
    }
    
    async def fetch_indicators(self, country: str = "DOM", 
                               dimensions: List[AccountabilityDimension] = None) -> List[AccountabilityIndicator]:
        indicators = []
        target_codes = [code for code, dim in self.WGI_INDICATORS.items() 
                       if not dimensions or dim in dimensions]
        
        for code in target_codes:
            data = await self._fetch_wgi_indicator(code)
            if data:
                indicators.append(self._normalize_wgi_data(data, code))
        
        return indicators

class IMF_Fiscal_Connector(GlobalEstablishmentConnector):
    """IMF Fiscal Transparency and Government Finance Statistics"""
    
    BASE_URL = "https://data.imf.org/api/v1/data"
    
    DATASETS = {
        "GFS": "Government Finance Statistics",
        "FT": "Fiscal Transparency",
    }

class WHO_Health_Connector(GlobalEstablishmentConnector):
    """WHO Global Health Observatory - Health system performance"""
    
    BASE_URL = "https://ghoapi.azureedge.net/api"

class UNESCO_Education_Connector(GlobalEstablishmentConnector):
    """UNESCO Institute for Statistics - Education quality"""
    
    BASE_URL = "http://data.uis.unesco.org/api"

class ILO_Labor_Connector(GlobalEstablishmentConnector):
    """ILOSTAT - Labor standards and decent work"""
    
    BASE_URL = "https://www.ilo.org/ilostat-api"

class TransparencyInternational_Connector(GlobalEstablishmentConnector):
    """Transparency International CPI and bribery data"""
    
    BASE_URL = "https://api.transparency.org/v1"
```

### 3.2 Global API Orchestrator

```python
# accountability/api_orchestrator.py
"""
Orchestrates all global establishment API connectors.
Manages rate limits, caching, normalization, and scheduling.
"""

class GlobalAPIOrchestrator:
    def __init__(self):
        self.connectors: Dict[DataSource, GlobalEstablishmentConnector] = {}
        self.scheduler = APIScheduler()
        self.normalizer = IndicatorNormalizer()
        self.benchmark_store = BenchmarkStore()
        
    def register_connector(self, source: DataSource, connector: GlobalEstablishmentConnector):
        self.connectors[source] = connector
    
    async def fetch_all_global_indicators(self, 
                                          institution_id: str,
                                          institution_type: InstitutionType,
                                          territory: str) -> GlobalIndicatorResult:
        """Fetch indicators from all global establishments for an institution"""
        
        # Determine relevant connectors based on institution type
        relevant_connectors = self._get_relevant_connectors(institution_type)
        
        # Fetch in parallel
        tasks = {}
        for source, connector in relevant_connectors.items():
            tasks[source] = connector.fetch_indicators(country="DOM")
        
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        # Process results
        all_indicators = []
        errors = {}
        
        for source, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                errors[source.value] = str(result)
            elif isinstance(result, list):
                # Tag with institution context
                for indicator in result:
                    indicator.institution_id = institution_id
                    indicator.metadata['global_source'] = source.value
                    indicator.metadata['institution_type'] = institution_type.value
                all_indicators.extend(result)
        
        # Fetch benchmarks for comparison
        benchmarks = await self._fetch_all_benchmarks()
        
        return GlobalIndicatorResult(
            institution_id=institution_id,
            indicators=all_indicators,
            benchmarks=benchmarks,
            errors=errors,
            fetched_at=datetime.now()
        )
    
    def _get_relevant_connectors(self, institution_type: InstitutionType) -> Dict[DataSource, GlobalEstablishmentConnector]:
        """Map institution type to relevant global connectors"""
        
        type_mapping = {
            InstitutionType.EXECUTIVE_MINISTRY: [
                DataSource.OECD_GOVERNANCE, DataSource.OAS_DEMOCRACY,
                DataSource.WORLD_BANK, DataSource.IMF_FISCAL,
                DataSource.TRANSPARENCY_INTERNATIONAL
            ],
            InstitutionType.MUNICIPALITY: [
                DataSource.UN_SDG, DataSource.OECD_GOVERNANCE,
                DataSource.WORLD_BANK, DataSource.IDB_PROJECTS
            ],
            InstitutionType.PUBLIC_UTILITY: [
                DataSource.UN_SDG, DataSource.IDB_PROJECTS,
                DataSource.WORLD_BANK
            ],
            InstitutionType.SOCIAL_PROGRAM: [
                DataSource.UN_SDG, DataSource.WHO_HEALTH,
                DataSource.UNESCO_EDUCATION, DataSource.ILO_LABOR,
                DataSource.WORLD_BANK
            ],
            InstitutionType.REGULATORY_BODY: [
                DataSource.OECD_GOVERNANCE, DataSource.WORLD_BANK,
                DataSource.OAS_DEMOCRACY
            ],
        }
        
        sources = type_mapping.get(institution_type, list(DataSource))
        return {s: self.connectors[s] for s in sources if s in self.connectors}
    
    async def _fetch_all_benchmarks(self) -> List[GlobalBenchmark]:
        """Fetch benchmarks from all connectors"""
        benchmarks = []
        for source, connector in self.connectors.items():
            try:
                bm = await connector.fetch_benchmarks("DOM")
                benchmarks.extend(bm)
            except Exception as e:
                logger.warning(f"Benchmark fetch failed for {source}: {e}")
        return benchmarks
```

---

## 4. ACCOUNTABILITY ENGINE: REAL-TIME SCORING

### 4.1 Multi-Source Scoring Engine

```python
# accountability/scoring_engine.py
"""
Real-time institutional accountability scoring.
Fuses internal, global, and citizen data with weighted aggregation.
"""

class AccountabilityScoringEngine:
    def __init__(self, 
                 blockchain: 'BlockchainAnchor',
                 liability_engine: 'IntegratedLiabilityRedressSystem'):
        self.blockchain = blockchain
        self.liability_engine = liability_engine
        
        # Dimension weights (configurable via governance)
        self.dimension_weights = {
            AccountabilityDimension.INTEGRITY: 0.20,
            AccountabilityDimension.TRANSPARENCY: 0.15,
            AccountabilityDimension.EFFECTIVENESS: 0.15,
            AccountabilityDimension.RULE_OF_LAW: 0.15,
            AccountabilityDimension.RESPONSIVENESS: 0.10,
            AccountabilityDimension.EQUITY: 0.10,
            AccountabilityDimension.HUMAN_RIGHTS: 0.05,
            AccountabilityDimension.PARTICIPATION: 0.05,
            AccountabilityDimension.EFFICIENCY: 0.03,
            AccountabilityDimension.SUSTAINABILITY: 0.02,
        }
        
        # Source weights
        self.source_weights = {
            DataSource.TECHNICAL_LAYER: 0.20,
            DataSource.ORGANIZATIONAL_LAYER: 0.15,
            DataSource.SOCIAL_NORM_LAYER: 0.15,  # High weight for citizen voice
            DataSource.HARD_LAW_LAYER: 0.15,
            DataSource.SOFT_LAW_LAYER: 0.10,
            DataSource.MARKET_LAYER: 0.10,
            # Global sources
            DataSource.WORLD_BANK: 0.15,
            DataSource.OECD_GOVERNANCE: 0.10,
            DataSource.OAS_DEMOCRACY: 0.10,
            DataSource.UN_SDG: 0.10,
            DataSource.IDB_PROJECTS: 0.05,
            DataSource.IMF_FISCAL: 0.05,
            DataSource.TRANSPARENCY_INTERNATIONAL: 0.05,
            DataSource.WHO_HEALTH: 0.03,
            DataSource.UNESCO_EDUCATION: 0.03,
            DataSource.ILO_LABOR: 0.03,
            # Citizen sources
            DataSource.VEEDURIA_CIUDADANA: 0.20,
            DataSource.QUEST_ENGAGEMENT: 0.10,
            DataSource.MUTUAL_AID_FEEDBACK: 0.10,
            DataSource.RP_CREDENTIALS: 0.05,
        }
        
        self.profiles: Dict[str, InstitutionAccountabilityProfile] = {}
    
    async def compute_accountability_profile(self, 
                                             institution_id: str,
                                             internal_data: InternalDataBundle,
                                             global_data: GlobalIndicatorResult,
                                             citizen_data: CitizenOversightData) -> InstitutionAccountabilityProfile:
        """Compute complete accountability profile"""
        
        # 1. Aggregate indicators by dimension
        dimension_indicators = self._group_by_dimension(
            internal_data.indicators + global_data.indicators + citizen_data.indicators
        )
        
        # 2. Compute dimension scores
        dimension_scores = {}
        for dimension, indicators in dimension_indicators.items():
            score = self._compute_dimension_score(dimension, indicators)
            dimension_scores[dimension] = score
        
        # 3. Compute composite score
        composite = sum(
            dimension_scores.get(dim, 0) * weight 
            for dim, weight in self.dimension_weights.items()
        )
        
        # 4. Compute source breakdown
        internal_score = self._compute_source_score(internal_data.indicators)
        global_score = self._compute_source_score(global_data.indicators)
        citizen_score = self._compute_source_score(citizen_data.indicators)
        
        # 5. Determine trend
        trend, trend_confidence = self._compute_trend(institution_id, composite)
        
        # 6. Check for alerts
        alerts = await self._check_thresholds(institution_id, dimension_scores, dimension_indicators)
        
        # 7. Calculate risk level
        risk_level = self._calculate_risk_level(composite, alerts)
        
        # 8. Compute liability exposure
        liability = await self._compute_liability_exposure(institution_id, alerts)
        
        # 9. Create profile
        profile = InstitutionAccountabilityProfile(
            institution_id=institution_id,
            institution_name=internal_data.institution_name,
            institution_type=internal_data.institution_type,
            territory_code=internal_data.territory_code,
            responsible_roles=internal_data.responsible_roles,
            dimension_scores=dimension_scores,
            composite_score=composite,
            internal_score=internal_score,
            global_score=global_score,
            citizen_score=citizen_score,
            trend=trend,
            trend_confidence=trend_confidence,
            active_alerts=alerts,
            risk_level=risk_level,
            liability_exposure=liability,
            data_completeness=self._calculate_completeness(dimension_indicators),
            last_updated=datetime.now()
        )
        
        # 10. Blockchain anchor
        profile.blockchain_anchor = await self.blockchain.anchor_accountability_profile(profile)
        
        # 11. Store and return
        self.profiles[institution_id] = profile
        return profile
    
    def _compute_dimension_score(self, dimension: AccountabilityDimension, 
                                 indicators: List[AccountabilityIndicator]) -> float:
        """Compute weighted score for a dimension from multiple sources"""
        
        if not indicators:
            return 0.0
        
        # Group by source
        by_source = {}
        for ind in indicators:
            by_source.setdefault(ind.source, []).append(ind)
        
        # Weighted average across sources
        total_weight = 0.0
        weighted_sum = 0.0
        
        for source, source_indicators in by_source.items():
            source_weight = self.source_weights.get(source, 0.01)
            
            # Average within source (confidence-weighted)
            source_avg = sum(
                ind.normalized_value * ind.confidence 
                for ind in source_indicators
            ) / sum(ind.confidence for ind in source_indicators)
            
            weighted_sum += source_avg * source_weight
            total_weight += source_weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    async def _check_thresholds(self, institution_id: str,
                                dimension_scores: Dict[AccountabilityDimension, float],
                                dimension_indicators: Dict[AccountabilityDimension, List]) -> List[AccountabilityAlert]:
        """Check for threshold breaches and generate alerts"""
        
        alerts = []
        
        # Critical thresholds (Japanese "safety boundaries")
        critical_thresholds = {
            AccountabilityDimension.INTEGRITY: 0.3,
            AccountabilityDimension.TRANSPARENCY: 0.4,
            AccountabilityDimension.RULE_OF_LAW: 0.35,
            AccountabilityDimension.HUMAN_RIGHTS: 0.4,
        }
        
        warning_thresholds = {
            AccountabilityDimension.INTEGRITY: 0.5,
            AccountabilityDimension.TRANSPARENCY: 0.6,
            AccountabilityDimension.EFFECTIVENESS: 0.5,
            AccountabilityDimension.RESPONSIVENESS: 0.5,
        }
        
        for dimension, score in dimension_scores.items():
            # Critical alert
            if dimension in critical_thresholds and score < critical_thresholds[dimension]:
                alert = AccountabilityAlert(
                    alert_id=f"ALERT_{institution_id}_{dimension.value}_{uuid.uuid4().hex[:8]}",
                    institution_id=institution_id,
                    dimension=dimension,
                    severity=AlertSeverity.CRITICAL,
                    title=f"Critical {dimension.value} threshold breached",
                    description=f"{dimension.value} score {score:.2f} below critical threshold {critical_thresholds[dimension]}",
                    triggering_indicators=[i.indicator_id for i in dimension_indicators.get(dimension, [])],
                    threshold_breached={"critical": critical_thresholds[dimension], "actual": score},
                    detected_at=datetime.now(),
                    liability_triggered=True,
                    redress_required=True
                )
                alerts.append(alert)
            
            # Warning alert
            elif dimension in warning_thresholds and score < warning_thresholds[dimension]:
                alert = AccountabilityAlert(
                    alert_id=f"ALERT_{institution_id}_{dimension.value}_{uuid.uuid4().hex[:8]}",
                    institution_id=institution_id,
                    dimension=dimension,
                    severity=AlertSeverity.HIGH,
                    title=f"{dimension.value} below warning threshold",
                    description=f"{dimension.value} score {score:.2f} below warning threshold {warning_thresholds[dimension]}",
                    triggering_indicators=[i.indicator_id for i in dimension_indicators.get(dimension, [])],
                    threshold_breached={"warning": warning_thresholds[dimension], "actual": score},
                    detected_at=datetime.now()
                )
                alerts.append(alert)
        
        # Cross-source anomaly detection
        anomaly_alerts = await self._detect_cross_source_anomalies(institution_id, dimension_indicators)
        alerts.extend(anomaly_alerts)
        
        return alerts
    
    async def _detect_cross_source_anomalies(self, institution_id: str,
                                             dimension_indicators: Dict) -> List[AccountabilityAlert]:
        """Detect discrepancies between internal, global, and citizen data"""
        
        alerts = []
        
        for dimension, indicators in dimension_indicators.items():
            # Group by source category
            internal = [i for i in indicators if i.source in [
                DataSource.TECHNICAL_LAYER, DataSource.ORGANIZATIONAL_LAYER,
                DataSource.SOFT_LAW_LAYER, DataSource.HARD_LAW_LAYER,
                DataSource.MARKET_LAYER, DataSource.SOCIAL_NORM_LAYER
            ]]
            global_src = [i for i in indicators if i.source in [
                DataSource.WORLD_BANK, DataSource.OECD_GOVERNANCE,
                DataSource.OAS_DEMOCRACY, DataSource.UN_SDG,
                DataSource.IDB_PROJECTS, DataSource.IMF_FISCAL,
                DataSource.TRANSPARENCY_INTERNATIONAL, DataSource.WHO_HEALTH,
                DataSource.UNESCO_EDUCATION, DataSource.ILO_LABOR
            ]]
            citizen = [i for i in indicators if i.source in [
                DataSource.VEEDURIA_CIUDADANA, DataSource.QUEST_ENGAGEMENT,
                DataSource.MUTUAL_AID_FEEDBACK, DataSource.RP_CREDENTIALS
            ]]
            
            if internal and global_src:
                internal_avg = sum(i.normalized_value for i in internal) / len(internal)
                global_avg = sum(i.normalized_value for i in global_src) / len(global_src)
                gap = abs(internal_avg - global_avg)
                
                if gap > 0.3:  # 30% discrepancy
                    alerts.append(AccountabilityAlert(
                        alert_id=f"ANOMALY_{institution_id}_{dimension.value}_{uuid.uuid4().hex[:8]}",
                        institution_id=institution_id,
                        dimension=dimension,
                        severity=AlertSeverity.HIGH,
                        title=f"Internal-Global data discrepancy in {dimension.value}",
                        description=f"Internal score {internal_avg:.2f} vs Global benchmark {global_avg:.2f} (gap: {gap:.2f})",
                        triggering_indicators=[i.indicator_id for i in internal + global_src],
                        threshold_breached={"discrepancy": gap, "threshold": 0.3},
                        detected_at=datetime.now()
                    ))
            
            if citizen and (internal or global_src):
                citizen_avg = sum(i.normalized_value for i in citizen) / len(citizen)
                official_avg = sum(i.normalized_value for i in (internal + global_src)) / len(internal + global_src)
                gap = abs(citizen_avg - official_avg)
                
                if gap > 0.4:  # 40% discrepancy (citizen voice often differs)
                    alerts.append(AccountabilityAlert(
                        alert_id=f"CITIZEN_GAP_{institution_id}_{dimension.value}_{uuid.uuid4().hex[:8]}",
                        institution_id=institution_id,
                        dimension=dimension,
                        severity=AlertSeverity.WARNING,
                        title=f"Citizen perception gap in {dimension.value}",
                        description=f"Citizen score {citizen_avg:.2f} vs Official {official_avg:.2f} (gap: {gap:.2f})",
                        triggering_indicators=[i.indicator_id for i in citizen + internal + global_src],
                        threshold_breached={"citizen_gap": gap, "threshold": 0.4},
                        detected_at=datetime.now()
                    ))
        
        return alerts
```

---

## 5. AUTOMATED REPORTING & ALERT SYSTEM

### 5.1 Real-Time Alert Distribution

```python
# accountability/alert_system.py
"""
Automated multi-channel alert distribution for accountability.
"""

class AccountabilityAlertSystem:
    def __init__(self):
        self.channels = {
            'institutional': InstitutionalAlertChannel(),
            'citizen': CitizenAlertChannel(),
            'global': GlobalReportingChannel(),
            'liability': LiabilityRedressChannel(),
            'media': MediaTransparencyChannel(),
            'emergency': EmergencyChannel(),
        }
        self.alert_rules = AlertRulesEngine()
        self.escalation_engine = EscalationEngine()
        
    async def process_alert(self, alert: AccountabilityAlert):
        """Process alert through all channels with appropriate routing"""
        
        # Determine routing based on severity and dimension
        routing = self.alert_rules.determine_routing(alert)
        
        # Send to channels in parallel
        tasks = []
        for channel_name in routing.channels:
            channel = self.channels.get(channel_name)
            if channel:
                tasks.append(channel.send(alert, routing.context))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check if escalation needed
        if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
            await self.escalation_engine.initiate_escalation(alert)
        
        # Trigger liability-redress if flagged
        if alert.liability_triggered:
            await self.channels['liability'].trigger_redress(alert)
        
        return AlertProcessingResult(
            alert_id=alert.alert_id,
            channels_notified=routing.channels,
            results={c: r for c, r in zip(routing.channels, results) if not isinstance(r, Exception)},
            escalated=alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]
        )

class InstitutionalAlertChannel:
    """Direct alerts to responsible roles within institution"""
    
    async def send(self, alert: AccountabilityAlert, context: Dict):
        # Get responsible roles from governance registry
        roles = await self._get_responsible_roles(alert.institution_id, alert.dimension)
        
        for role_id in roles:
            # Send via governance platform (Discord, dashboard, email)
            await self._send_to_role(role_id, {
                'type': 'ACCOUNTABILITY_ALERT',
                'alert': alert,
                'required_action': self._determine_action(alert),
                'deadline': self._calculate_deadline(alert),
                'support_resources': self._get_support_resources(alert)
            })

class CitizenAlertChannel:
    """Alerts to citizen oversight (Veeduría, Quest participants)"""
    
    async def send(self, alert: AccountabilityAlert, context: Dict):
        # Merit-weighted notification
        oversight_members = await self._get_oversight_members(alert.institution_id)
        
        for member in oversight_members:
            weight = await self._get_merit_weight(member.citizen_id)
            if weight > 0.5:  # Only notify sufficiently engaged citizens
                await self._send_notification(member.citizen_id, {
                    'type': 'COMMUNITY_ALERT',
                    'institution': alert.institution_name,
                    'issue': alert.title,
                    'severity': alert.severity.value,
                    'what_this_means': self._explain_in_plain_language(alert),
                    'how_to_help': self._suggest_citizen_actions(alert),
                    'quest_followup': True  # Trigger Quest visit
                })

class GlobalReportingChannel:
    """Automated reporting to global establishments"""
    
    async def send(self, alert: AccountabilityAlert, context: Dict):
        # Generate standardized report for each relevant establishment
        reports = self._generate_global_reports(alert)
        
        for establishment, report in reports.items():
            await self._submit_to_establishment(establishment, report)

class LiabilityRedressChannel:
    """Triggers Japanese-style integrated liability-redress"""
    
    async def send(self, alert: AccountabilityAlert, context: Dict):
        if not alert.liability_triggered:
            return
        
        # Create liability incident
        incident = GovernanceIncident(
            incident_id=f"LIAB_{alert.alert_id}",
            institution_id=alert.institution_id,
            trigger_alert=alert.alert_id,
            dimension=alert.dimension,
            severity=alert.severity,
            victims_identified=await self._identify_victims(alert),
            occurred_at=alert.detected_at
        )
        
        # Trigger redress process (no-fault compensation + proportional liability)
        await self.liability_engine.process_incident(incident)
        
        # Notify affected parties
        await self._notify_victims(incident)

class EscalationEngine:
    """Automated escalation based on severity and response time"""
    
    ESCALATION_MATRIX = {
        AlertSeverity.INFO: {"hours": 168, "level": "MONITOR"},  # 1 week
        AlertSeverity.WARNING: {"hours": 72, "level": "REVIEW"},  # 3 days
        AlertSeverity.HIGH: {"hours": 24, "level": "ACT"},  # 1 day
        AlertSeverity.CRITICAL: {"hours": 4, "level": "INTERVENE"},  # 4 hours
        AlertSeverity.EMERGENCY: {"hours": 1, "level": "EMERGENCY_POWERS"},  # 1 hour
    }
    
    async def initiate_escalation(self, alert: AccountabilityAlert):
        escalation = self.ESCALATION_MATRIX[alert.severity]
        
        # Schedule escalation check
        await self._schedule_escalation_check(alert, escalation['hours'])
        
        # Immediate notifications for CRITICAL/EMERGENCY
        if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
            await self._immediate_escalation(alert, escalation['level'])
    
    async def _immediate_escalation(self, alert: AccountabilityAlert, level: str):
        """Immediate escalation actions"""
        
        if level == "INTERVENE":
            # Direct intervention: Central AI Fund freeze, emergency oversight
            await self._freeze_institution_funds(alert.institution_id)
            await self._activate_emergency_oversight(alert.institution_id)
            await self._notify_presidential_office(alert)
        
        elif level == "EMERGENCY_POWERS":
            # Constitutional emergency powers
            await self._invoke_emergency_powers(alert.institution_id)
            await self._activate_transitional_governance(alert.institution_id)
            await self._notify_congress_and_courts(alert)
```

---

## 6. CITIZEN OVERSIGHT ACCOUNTABILITY INTERFACE

### 6.1 Veeduría Digital Dashboard

```python
# accountability/citizen_interface.py
"""
Citizen-facing accountability interface.
Merit-weighted, accessible, actionable.
"""

class CitizenAccountabilityPortal:
    def __init__(self, merit_system: 'MeritLedger', scoring_engine: 'AccountabilityScoringEngine'):
        self.merit_system = merit_system
        self.scoring_engine = scoring_engine
        self.portal_state: Dict[str, CitizenPortalState] = {}
        
    async def get_citizen_dashboard(self, citizen_id: str) -> CitizenDashboard:
        """Personalized accountability dashboard for a citizen"""
        
        # Get citizen's merit profile
        merit_profile = await self.merit_system.get_profile(citizen_id)
        
        # Determine relevant institutions (territory + interests)
        relevant_institutions = await self._get_relevant_institutions(citizen_id)
        
        # Get accountability profiles
        profiles = []
        for inst_id in relevant_institutions:
            profile = self.scoring_engine.profiles.get(inst_id)
            if profile:
                profiles.append(await self._enrich_for_citizen(profile, citizen_id))
        
        # Get active quests for this citizen
        quests = await self._get_citizen_quests(citizen_id)
        
        # Get mutual aid network status
        mutual_aid = await self._get_mutual_aid_status(citizen_id)
        
        # Personalized alerts
        alerts = await self._get_personalized_alerts(citizen_id, profiles)
        
        return CitizenDashboard(
            citizen_id=citizen_id,
            merit_tier=merit_profile.tier,
            merit_weight=merit_profile.total_merits,
            institutions=profiles,
            active_quests=quests,
            mutual_aid_status=mutual_aid,
            personalized_alerts=alerts,
            recommended_actions=self._generate_recommendations(profiles, merit_profile),
            last_updated=datetime.now()
        )
    
    async def _enrich_for_citizen(self, profile: InstitutionAccountabilityProfile, 
                                  citizen_id: str) -> EnrichedInstitutionView:
        """Enrich institutional profile with citizen-relevant context"""
        
        # Translate scores to plain language
        dimension_explanations = {}
        for dim, score in profile.dimension_scores.items():
            dimension_explanations[dim.value] = self._explain_score(dim, score)
        
        # Highlight citizen-relevant dimensions
        citizen_priority_dimensions = [
            AccountabilityDimension.RESPONSIVENESS,
            AccountabilityDimension.EQUITY,
            AccountabilityDimension.PARTICIPATION,
            AccountabilityDimension.HUMAN_RIGHTS
        ]
        
        # Show trend in human terms
        trend_explanation = self._explain_trend(profile.trend, profile.trend_confidence)
        
        # Actionable items for this citizen
        actions = []
        if profile.citizen_score < 0.5:
            actions.append(CitizenAction(
                action_type="JOIN_VEEDURIA",
                description="Únete a la veeduría ciudadana para esta institución",
                impact="high",
                time_commitment="2 horas/semana"
            ))
        
        if profile.active_alerts:
            for alert in profile.active_alerts:
                if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                    actions.append(CitizenAction(
                        action_type="QUEST_FOLLOWUP",
                        description=f"Participa en Quest de seguimiento: {alert.title}",
                        impact="high",
                        time_commitment="30 min"
                    ))
        
        return EnrichedInstitutionView(
            institution_id=profile.institution_id,
            name=profile.institution_name,
            composite_score=profile.composite_score,
            percentile=profile.percentile_rank,
            dimension_scores={k.value: v for k, v in profile.dimension_scores.items()},
            dimension_explanations=dimension_explanations,
            trend=profile.trend,
            trend_explanation=trend_explanation,
            risk_level=profile.risk_level,
            citizen_score=profile.citizen_score,
            active_alerts=[self._enrich_alert(a) for a in profile.active_alerts],
            recommended_actions=actions,
            last_quest_visit=await self._get_last_quest_visit(profile.institution_id, citizen_id),
            mutual_aid_connection=await self._get_mutual_aid_connection(profile.institution_id, citizen_id)
        )
    
    def _explain_score(self, dimension: AccountabilityDimension, score: float) -> str:
        """Translate score to plain language"""
        
        explanations = {
            AccountabilityDimension.INTEGRITY: {
                (0.8, 1.0): "Muy íntegra: Pocos casos de corrupción, transparencia alta",
                (0.6, 0.8): "Integridad aceptable: Algunos riesgos pero controles funcionan",
                (0.4, 0.6): "Integridad preocupante: Casos de corrupción, controles débiles",
                (0.0, 0.4): "Integridad crítica: Corrupción sistémica, impunidad"
            },
            AccountabilityDimension.RESPONSIVENESS: {
                (0.8, 1.0): "Muy receptiva: Responde rápido a necesidades ciudadanas",
                (0.6, 0.8): "Receptiva: Responde en tiempo razonable",
                (0.4, 0.6): "Poco receptiva: Respuestas lentas o incompletas",
                (0.0, 0.4): "No receptiva: Ignora solicitudes ciudadanas"
            },
            AccountabilityDimension.EQUITY: {
                (0.8, 1.0): "Muy equitativa: Servicios justos para todos",
                (0.6, 0.8): "Equitativa: Algunas disparidades menores",
                (0.4, 0.6): "Desigual: Diferencias notables en acceso",
                (0.0, 0.4): "Muy desigual: Discriminación en servicios"
            },
        }
        
        dim_explanations = explanations.get(dimension, {})
        for (low, high), text in dim_explanations.items():
            if low <= score < high:
                return text
        return "Sin datos suficientes"
```

### 6.2 Quest-Integrated Accountability Follow-up

```python
# accountability/quest_integration.py
"""
Quest system integration for accountability follow-up.
When alerts trigger, Quest visits become targeted follow-ups.
"""

class QuestAccountabilityIntegration:
    def __init__(self, quest_engine: 'QuestEngine', alert_system: 'AccountabilityAlertSystem'):
        self.quest_engine = quest_engine
        self.alert_system = alert_system
        self.followup_quests: Dict[str, FollowupQuest] = {}
        
    async def trigger_accountability_quest(self, alert: AccountabilityAlert) -> FollowupQuestResult:
        """Trigger a targeted Quest follow-up for an accountability alert"""
        
        # Create specialized Quest protocol for accountability
        protocol = QuestProtocol(
            approach="knock_and_greet",
            opening=f"Buenos días, vengo de parte de la comunidad para conversar sobre {alert.title}",
            explanation=f"Hay una alerta sobre {alert.dimension.value} en {alert.institution_name}. Queremos saber su experiencia directa.",
            affirmation="Su voz importa. No está fallando. La comunidad quiere escucharle.",
            listening_first=True,
            no_clipboards=True,
            no_uniforms=True,
            small_gift=True,
            departure="Gracias por compartir. Su experiencia ayuda a mejorar las cosas para todos."
        )
        
        # Select Questers with relevant experience
        questers = await self._select_accountability_questers(alert)
        
        # Target homes in affected area
        target_homes = await self._get_affected_homes(alert)
        
        followup_quest = FollowupQuest(
            quest_id=f"FOLLOWUP_{alert.alert_id}",
            parent_alert_id=alert.alert_id,
            institution_id=alert.institution_id,
            dimension=alert.dimension,
            protocol=protocol,
            questers=questers,
            target_homes=target_homes,
            created_at=datetime.now(),
            status="ACTIVE",
            required_visits=len(target_homes)
        )
        
        self.followup_quests[followup_quest.quest_id] = followup_quest
        
        # Initiate
        initiation = await self.quest_engine.initiate_quest_custom(followup_quest)
        
        return FollowupQuestResult(
            success=True,
            quest=followup_quest,
            initiation=initiation
        )
    
    async def process_accountability_visit(self, visit: QuestVisit) -> AccountabilityVisitResult:
        """Process Quest visit with accountability context"""
        
        followup_quest = self.followup_quests.get(visit.quest_id)
        if not followup_quest:
            return AccountabilityVisitResult(success=False, reason="Not an accountability followup")
        
        # Extract accountability-relevant information
        accountability_data = self._extract_accountability_data(visit, followup_quest.dimension)
        
        # Update alert with citizen evidence
        await self.alert_system.update_alert_with_citizen_evidence(
            followup_quest.parent_alert_id,
            accountability_data
        )
        
        # Check if visit resolves alert
        resolution = self._assess_alert_resolution(accountability_data, followup_quest.dimension)
        
        if resolution.resolved:
            await self.alert_system.resolve_alert(followup_quest.parent_alert_id, resolution)
        
        return AccountabilityVisitResult(
            success=True,
            accountability_data=accountability_data,
            alert_updated=True,
            resolution=resolution
        )
```

---

## 7. INTEGRATED LIABILITY-REDRESS SYSTEM (JAPANESE MODEL)

### 7.1 Japanese Integrated Reform Adaptation

```python
# accountability/liability_redress.py
"""
Japanese "Regulation-Sanction-Liability Integrated Reform" (規制・制裁・責任の一体的改革)
Adapted for DR accountability system.
"""

class IntegratedLiabilityRedressSystem:
    """
    Three-pillar system:
    1. No-fault victim compensation (social insurance model)
    2. Proportional institutional liability (based on governance maturity)
    3. Algorithmic accountability + specialized tribunals
    """
    
    def __init__(self):
        self.compensation_fund = VictimCompensationFund()
        self.liability_calculator = ProportionalLiabilityCalculator()
        self.tribunal = AccountabilityTribunal()
        self.explainability_auditor = AlgorithmicExplainabilityAuditor()
        self.governance_maturity_assessor = GovernanceMaturityAssessor()
        
    async def process_accountability_incident(self, incident: AccountabilityIncident) -> RedressOutcome:
        """Process incident through integrated liability-redress"""
        
        # PILLAR 1: Immediate victim compensation (no-fault)
        compensation = await self.compensation_fund.compensate(incident.victims)
        
        # PILLAR 2: Determine institutional liability share
        governance_maturity = await self.governance_maturity_assessor.assess(incident.institution_id)
        liability_share = self.liability_calculator.calculate(incident, governance_maturity)
        
        # PILLAR 3: Algorithmic accountability check
        if incident.involves_algorithm:
            explainability = await self.explainability_auditor.audit(incident.algorithm)
            if not explainability.meets_standard:
                liability_share *= EXPLAINABILITY_PENALTY_MULTIPLIER  # 1.5x
        
        # Tribunal adjudication if disputed
        if incident.disputed:
            ruling = await self.tribunal.adjudicate(incident, liability_share)
            liability_share = ruling.final_liability
        
        # Recoup from institution
        await self.compensation_fund.recoup(incident.institution_id, liability_share)
        
        # Generate governance improvement signal
        improvement_signal = await self._generate_improvement_signal(incident, liability_share)
        
        # Feed back to accountability scoring
        await self._update_accountability_scores(incident, liability_share)
        
        return RedressOutcome(
            victim_compensation=compensation,
            institutional_liability=liability_share,
            governance_improvement_signal=improvement_signal,
            tribunal_ruling=ruling if incident.disputed else None,
            processed_at=datetime.now()
        )

class GovernanceMaturityAssessor:
    """Assesses institutional governance maturity for proportional liability"""
    
    MATURITY_LEVELS = {
        1: "AD_HOC",           # No systematic governance
        2: "REACTIVE",         # Responds to problems after they occur
        3: "DEFINED",          # Documented processes, some automation
        4: "MANAGED",          # Metrics-driven, predictive
        5: "OPTIMIZING",       # Continuous improvement, innovation
    }
    
    LIABILITY_MULTIPLIERS = {
        1: 2.0,   # Ad hoc: Double liability
        2: 1.5,   # Reactive: 50% more
        3: 1.0,   # Defined: Baseline
        4: 0.7,   # Managed: 30% reduction
        5: 0.5,   # Optimizing: 50% reduction
    }
    
    async def assess(self, institution_id: str) -> GovernanceMaturity:
        """Assess across 5 dimensions (CMMI-inspired)"""
        
        dimensions = {
            'transparency': await self._assess_transparency(institution_id),
            'integrity_systems': await self._assess_integrity_systems(institution_id),
            'performance_management': await self._assess_performance_management(institution_id),
            'risk_management': await self._assess_risk_management(institution_id),
            'citizen_engagement': await self._assess_citizen_engagement(institution_id),
            'learning_adaptation': await self._assess_learning_adaptation(institution_id),
        }
        
        # Overall maturity (weighted average)
        weights = {'transparency': 0.2, 'integrity_systems': 0.25, 'performance_management': 0.2,
                  'risk_management': 0.15, 'citizen_engagement': 0.1, 'learning_adaptation': 0.1}
        
        weighted_score = sum(dimensions[d] * weights[d] for d in dimensions)
        maturity_level = self._score_to_level(weighted_score)
        
        return GovernanceMaturity(
            institution_id=institution_id,
            overall_score=weighted_score,
            maturity_level=maturity_level,
            dimension_scores=dimensions,
            liability_multiplier=self.LIABILITY_MULTIPLIERS[maturity_level],
            assessed_at=datetime.now()
        )
```

### 7.2 Victim Compensation Fund

```python
# accountability/compensation_fund.py
"""
No-fault victim compensation fund (Japanese social insurance model).
Funded by: institutional contributions, liability recoveries, budget allocation.
"""

class VictimCompensationFund:
    def __init__(self):
        self.fund_balance = Decimal('0')
        self.contributions: List[FundContribution] = []
        self.claims: List[CompensationClaim] = []
        self.payouts: List[CompensationPayout] = []
        
    async def compensate(self, victims: List[Victim]) -> CompensationResult:
        """Immediate no-fault compensation"""
        
        total_compensation = Decimal('0')
        payouts = []
        
        for victim in victims:
            # Calculate compensation based on harm type
            amount = self._calculate_compensation(victim)
            
            # Check fund availability
            if self.fund_balance >= amount:
                payout = CompensationPayout(
                    payout_id=f"PAYOUT_{uuid.uuid4().hex[:12]}",
                    victim_id=victim.victim_id,
                    amount=amount,
                    harm_type=victim.harm_type,
                    paid_at=datetime.now(),
                    no_fault=True
                )
                
                self.fund_balance -= amount
                payouts.append(payout)
                total_compensation += amount
                
                # Notify victim
                await self._notify_victim(victim, payout)
            else:
                # Emergency funding trigger
                await self._trigger_emergency_funding(amount - self.fund_balance)
                # Retry
                return await self.compensate([victim])
        
        return CompensationResult(
            success=True,
            total_compensation=total_compensation,
            payouts=payouts,
            fund_balance_remaining=self.fund_balance
        )
    
    def _calculate_compensation(self, victim: Victim) -> Decimal:
        """Japanese-style compensation schedule"""
        
        base_amounts = {
            HarmType.PHYSICAL_INJURY: Decimal('500000'),      # 500K DOP base
            HarmType.PSYCHOLOGICAL_HARM: Decimal('300000'),
            HarmType.PROPERTY_DAMAGE: Decimal('200000'),
            HarmType.SERVICE_DENIAL: Decimal('100000'),
            HarmType.RIGHTS_VIOLATION: Decimal('400000'),
            HarmType.ENVIRONMENTAL_HARM: Decimal('1000000'),
            HarmType.FINANCIAL_LOSS: Decimal('100000'),  # Plus actual loss
        }
        
        base = base_amounts.get(victim.harm_type, Decimal('100000'))
        
        # Severity multipliers
        severity_multipliers = {
            SeverityLevel.MINOR: 1.0,
            SeverityLevel.MODERATE: 2.0,
            SeverityLevel.SEVERE: 5.0,
            SeverityLevel.CATASTROPHIC: 10.0,
        }
        
        multiplier = severity_multipliers.get(victim.severity, 1.0)
        
        # Vulnerability adjustments (elderly, disabled, children, poor)
        vulnerability_adjustment = self._calculate_vulnerability_adjustment(victim)
        
        return base * Decimal(str(multiplier)) * Decimal(str(vulnerability_adjustment))
```

---

## 8. PREDICTIVE ACCOUNTABILITY & RISK FORECASTING

### 8.1 AI-Powered Predictive Engine

```python
# accountability/predictive_engine.py
"""
Predictive accountability: Forecast institutional risks before they materialize.
Japanese "Predictive Governance" (予測ガバナンス) concept.
"""

class PredictiveAccountabilityEngine:
    def __init__(self):
        self.risk_forecaster = RiskForecaster()
        self.early_warning = EarlyWarningSystem()
        self.scenario_simulator = ScenarioSimulator()
        self.intervention_optimizer = InterventionOptimizer()
        
    async def forecast_institutional_risk(self, institution_id: str, 
                                          horizon_days: int = 90) -> RiskForecast:
        """Forecast accountability risks for an institution"""
        
        # Get historical data
        historical = await self._get_historical_data(institution_id, days=365)
        
        # Get current profile
        current_profile = self.scoring_engine.profiles.get(institution_id)
        
        # Feature engineering
        features = self._engineer_features(institution_id, historical, current_profile)
        
        # Run forecasting models
        forecasts = await asyncio.gather(
            self.risk_forecaster.forecast_deterioration(features, horizon_days),
            self.risk_forecaster.forecast_corruption_risk(features, horizon_days),
            self.risk_forecaster.forecast_service_failure(features, horizon_days),
            self.risk_forecaster.forecast_citizen_unrest(features, horizon_days),
            self.risk_forecaster.forecast_fiscal_stress(features, horizon_days),
        )
        
        # Combine forecasts
        combined = self._combine_forecasts(forecasts)
        
        # Generate early warnings
        warnings = await self.early_warning.generate_warnings(combined, current_profile)
        
        # Simulate intervention scenarios
        scenarios = await self.scenario_simulator.simulate_interventions(
            institution_id, combined, warnings
        )
        
        # Optimize recommended interventions
        recommended = await self.intervention_optimizer.optimize(scenarios)
        
        return RiskForecast(
            institution_id=institution_id,
            forecast_horizon_days=horizon_days,
            risk_trajectories=combined,
            early_warnings=warnings,
            intervention_scenarios=scenarios,
            recommended_actions=recommended,
            confidence=self._calculate_forecast_confidence(forecasts),
            generated_at=datetime.now()
        )
    
    async def forecast_systemic_risk(self, territory_code: str) -> SystemicRiskForecast:
        """Forecast systemic risks across all institutions in a territory"""
        
        institutions = await self._get_territory_institutions(territory_code)
        
        # Parallel individual forecasts
        individual_forecasts = await asyncio.gather(*[
            self.forecast_institutional_risk(inst_id, 90) 
            for inst_id in institutions
        ])
        
        # Network contagion analysis
        contagion = await self._analyze_contagion_risk(institutions, individual_forecasts)
        
        # Critical infrastructure cascade
        cascade = await self._analyze_infrastructure_cascade(territory_code, individual_forecasts)
        
        # Fiscal contagion
        fiscal = await self._analyze_fiscal_contagion(institutions, individual_forecasts)
        
        return SystemicRiskForecast(
            territory_code=territory_code,
            individual_forecasts=individual_forecasts,
            contagion_risk=contagion,
            infrastructure_cascade=cascade,
            fiscal_contagion=fiscal,
            system_risk_level=self._calculate_system_risk(individual_forecasts, contagion),
            generated_at=datetime.now()
        )
```

---

## 9. IMPLEMENTATION ROADMAP

### Phase 1: Data Foundation (Months 1-2)
- [ ] Deploy Accountability Data Fusion Engine
- [ ] Implement 6-layer internal data connectors
- [ ] Deploy Global API Orchestrator with 10+ establishment connectors
- [ ] Build Indicator Normalizer & Benchmark Store
- [ ] Establish blockchain anchoring for all accountability records

### Phase 2: Scoring & Alerts (Months 3-4)
- [ ] Deploy Accountability Scoring Engine with weighted aggregation
- [ ] Implement real-time threshold checking
- [ ] Deploy Automated Alert System (6 channels)
- [ ] Build Escalation Engine with time-based triggers
- [ ] Integrate Liability-Redress Engine

### Phase 3: Citizen Interface (Months 5-6)
- [ ] Deploy Citizen Accountability Portal
- [ ] Integrate Quest follow-up system
- [ ] Build merit-weighted notification system
- [ ] Implement plain-language score explanations
- [ ] Deploy Veeduría digital tools

### Phase 4: Predictive & Systemic (Months 7-9)
- [ ] Deploy Predictive Accountability Engine
- [ ] Implement Early Warning System
- [ ] Build Scenario Simulator for interventions
- [ ] Deploy Systemic Risk Forecasting
- [ ] Integrate with Central AI Fund for preventive action

### Phase 5: Full Integration (Months 10-12)
- [ ] Connect with all 6 governance layers
- [ ] Integrate with Upfront Operations contractor monitoring
- [ ] Connect with Tax Merit & Central AI Fund systems
- [ ] Deploy institutional dashboards for all 158 municipalities
- [ ] National accountability dashboard for Presidency

---

## 10. KEY PERFORMANCE INDICATORS

| KPI | Target | Measurement |
|-----|--------|-------------|
| **Data Freshness** | < 1 hour lag | Pipeline timestamps |
| **Global API Coverage** | 100% relevant establishments | Connector health |
| **Indicator Normalization Accuracy** | > 95% | Validation sampling |
| **Alert Detection Time** | < 4 hours from threshold breach | Alert timestamps |
| **Alert Acknowledgment Rate** | > 90% within SLA | Institutional response |
| **Citizen Dashboard Adoption** | > 60% eligible citizens | Portal analytics |
| **Quest Follow-up Completion** | > 80% triggered quests | Quest engine |
| **Liability-Redress Resolution** | < 30 days average | Tribunal records |
| **Victim Compensation Time** | < 14 days | Fund records |
| **Predictive Accuracy** | > 75% for 90-day horizon | Forecast validation |
| **Systemic Risk Detection** | 100% critical cascades | Retrospective analysis |
| **Governance Maturity Improvement** | +0.5 level/year | Annual assessment |

---

## 11. LEGAL & INSTITUTIONAL FRAMEWORK

### 11.1 Required Legal Basis

| Legal Instrument | Accountability Provision |
|-----------------|-------------------------|
| **Constitución Art. 147** | Control de la gestión pública |
| **Ley 10-04** | Cámara de Cuentas - fiscalización |
| **Ley 340-06** | Compras - transparencia y veeduría |
| **Ley 200-04** | Libre acceso a la información pública |
| **Ley 172-13** | Protección de datos personales |
| **Ley 53-07** | Crímenes de alta tecnología |
| **Nueva Ley: Responsabilidad Institucional Integral** | Integrar: compensación sin culpa + responsabilidad proporcional + tribunal especializado |

### 11.2 International Commitments Alignment

| Commitment | Accountability Framework Alignment |
|------------|-----------------------------------|
| **UNCAC (Convención ONU vs Corrupción)** | Art. 5, 7, 10, 13 - Preventive bodies, transparency, reporting |
| **OAS Convención Interamericana vs Corrupción** | Art. III - Oversight bodies, citizen participation |
| **ODS 16.6** | Instituciones eficaces, responsables, transparentes |
| **ODS 16.7** | Toma de decisiones inclusiva, participativa, representativa |
| **OECD Recommendation on Public Integrity** | Whole-of-society approach, risk-based, accountability |
| **Extractive Industries Transparency Initiative (EITI)** | Sector-specific transparency standards |

---

*Document Version: 1.0 | Date: 2026-11-10*
*System: Multi-Source Institutional Accountability Framework*
*Integrates: Japanese Meta-Governance + Integrated Liability-Redress + Global Establishments + Citizen Oversight*
*Location: F:\managements\institutional_accountability_framework.md*