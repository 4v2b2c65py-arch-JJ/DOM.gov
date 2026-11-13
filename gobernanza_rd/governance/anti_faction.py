# Anti-Faction Governance Layer - FGA, Audit Trail, Circuit Breakers
import asyncio
import hashlib
import json
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, List, Any, Set
from dataclasses import dataclass, field
from enum import Enum

import structlog
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import get_settings
from models import (
    AuditRecord, ConsensusDecision, ModelRotationLog, CircuitBreakerEvent, FGAGovernanceAction,
    AuditEventType, AccountabilityLayer, User, ConsensusDecision, CircuitBreakerEvent
)
from consensus.engine import ConsensusEngine, ProposalSeverity, ConsensusResult
from services.trace_logger import TraceLogger

settings = get_settings()
logger = structlog.get_logger()


class CircuitBreakerTrigger(str, Enum):
    CONSENSUS_FAILURE = "consensus_failure"
    FAIRNESS_COLLAPSE = "fairness_collapse"
    MODEL_CAPTURE = "model_capture"
    CONSTITUTIONAL_CRISIS = "constitutional_crisis"


class CircuitBreakerAction(str, Enum):
    FREEZE = "freeze"
    REDISTRIBUTE = "redistribute"
    ROTATE = "rotate"
    STAY = "stay"


class FGAAuditService:
    """FGA (Fundación de Gobernanza Algorítmica) audit and governance operations"""
    
    def __init__(self, db: AsyncSession, consensus_engine: ConsensusEngine, trace_logger: TraceLogger):
        self.db = db
        self.consensus_engine = consensus_engine
        self.trace_logger = trace_logger
    
    async def initiate_model_audit(self, trigger: str, scope: List[str] = None) -> str:
        """Initiate algorithmic audit (quarterly mandatory or trigger-based)"""
        
        audit_id = f"audit_{trigger}_{int(datetime.utcnow().timestamp())}"
        
        # Log audit initiation
        await self.trace_logger.log_event(
            event_type=AuditEventType.FGA_ACTION,
            event_data={
                "audit_id": audit_id,
                "trigger": trigger,
                "scope": scope or ["all_families"],
                "status": "initiated"
            },
            actor_user_id=None
        )
        
        # In production, this would trigger external auditor engagement
        # For now, log and return
        return audit_id
    
    async def review_model_rotation(self, rotation_log_id: uuid.UUID, approved: bool, reviewer_id: uuid.UUID, notes: str = "") -> bool:
        """Review and approve/reject model rotation"""
        
        result = await self.db.execute(
            select(ModelRotationLog).where(ModelRotationLog.id == rotation_log_id)
        )
        rotation = result.scalar_one_or_none()
        
        if not rotation:
            return False
        
        rotation.fga_approval = approved
        rotation.approved_by = reviewer_id
        rotation.approved_at = datetime.utcnow()
        
        if approved:
            rotation.deployed = True
            rotation.deployed_at = datetime.utcnow()
        else:
            rotation.rollback_at = datetime.utcnow()
            rotation.rollback_reason = notes or "FGA rejected"
        
        await self.db.flush()
        
        # Log
        await self.trace_logger.log_event(
            event_type=AuditEventType.MODEL_ROTATION,
            event_data={
                "rotation_id": str(rotation_log_id),
                "family": rotation.family,
                "old_model": rotation.old_model,
                "new_model": rotation.new_model,
                "approved": approved,
                "reviewer": str(reviewer_id)
            },
            actor_user_id=reviewer_id
        )
        
        return True
    
    async def propose_governance_action(self, action_type: str, target_type: str, target_id: uuid.UUID,
                                         description: str, rationale: str, legal_basis: str,
                                         proposer_id: uuid.UUID) -> FGAGovernanceAction:
        """Propose FGA governance action"""
        
        action = FGAGovernanceAction(
            action_number=f"FGA-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
            action_type=action_type,
            target_type=target_type,
            target_id=target_id,
            description=description,
            rationale=rationale,
            legal_basis=legal_basis,
            decided_by={"proposer": str(proposer_id), "board": []},
            votes_for=1,
            votes_against=0,
            votes_abstain=0,
            quorum_met=False,
            status="proposed"
        )
        
        self.db.add(action)
        await self.db.flush()
        
        # Log
        await self.trace_logger.log_event(
            event_type=AuditEventType.FGA_ACTION,
            event_data={
                "action_number": action.action_number,
                "action_type": action_type,
                "target": f"{target_type}:{target_id}",
                "status": "proposed"
            },
            actor_user_id=proposer_id
        )
        
        return action
    
    async def vote_on_action(self, action_id: uuid.UUID, voter_id: uuid.UUID, vote: str) -> bool:
        """Board member votes on FGA action"""
        
        result = await self.db.execute(
            select(FGAGovernanceAction).where(FGAGovernanceAction.id == action_id)
        )
        action = result.scalar_one_or_none()
        
        if not action or action.status != "proposed":
            return False
        
        # Update vote counts
        if vote == "for":
            action.votes_for += 1
        elif vote == "against":
            action.votes_against += 1
        elif vote == "abstain":
            action.votes_abstain += 1
        
        # Check quorum (4 of 7 board members)
        total_votes = action.votes_for + action.votes_against + action.votes_abstain
        action.quorum_met = total_votes >= 4
        
        # Check if passed (simple majority with quorum)
        if action.quorum_met and action.votes_for > action.votes_against:
            action.status = "approved"
        elif action.quorum_met and action.votes_for <= action.votes_against:
            action.status = "rejected"
        
        await self.db.flush()
        return True


class CircuitBreakerService:
    """Circuit breaker system for catastrophic scenarios"""
    
    TRIGGER_CONFIGS = {
        CircuitBreakerTrigger.CONSENSUS_FAILURE: {
            "condition": "No consensus reached after 3 rounds",
            "action": CircuitBreakerAction.FREEZE,
            "timeout_hours": 72,
            "authority": "system",
            "auto_resolve": False
        },
        CircuitBreakerTrigger.FAIRNESS_COLLAPSE: {
            "condition": "Gini > 0.50 OR geographic disparity > 10x",
            "action": CircuitBreakerAction.REDISTRIBUTE,
            "timeout_hours": 24,
            "authority": "fga",
            "auto_resolve": True
        },
        CircuitBreakerTrigger.MODEL_CAPTURE: {
            "condition": "Single provider > 50% weight OR model agreement > 99%",
            "action": CircuitBreakerAction.ROTATE,
            "timeout_hours": 48,
            "authority": "fga_veeduria",
            "auto_resolve": False
        },
        CircuitBreakerTrigger.CONSTITUTIONAL_CRISIS: {
            "condition": "AI decision challenged in Constitutional Court",
            "action": CircuitBreakerAction.STAY,
            "timeout_hours": None,  # Until Court resolves
            "authority": "constitutional_court",
            "auto_resolve": False
        }
    }
    
    def __init__(self, db: AsyncSession, consensus_engine: ConsensusEngine, trace_logger: TraceLogger):
        self.db = db
        self.consensus_engine = consensus_engine
        self.trace_logger = trace_logger
        self.active_breakers: Dict[str, CircuitBreakerEvent] = {}
    
    async def check_triggers(self) -> List[CircuitBreakerEvent]:
        """Check all circuit breaker triggers"""
        triggered = []
        
        for trigger_type, config in self.TRIGGER_CONFIGS.items():
            if await self._evaluate_trigger(trigger_type, config):
                event = await self._activate_breaker(trigger_type, config)
                triggered.append(event)
        
        return triggered
    
    async def _evaluate_trigger(self, trigger: CircuitBreakerTrigger, config: Dict) -> bool:
        """Evaluate if trigger condition is met"""
        
        if trigger == CircuitBreakerTrigger.CONSENSUS_FAILURE:
            # Check recent consensus failures
            result = await self.db.execute(
                select(func.count(ConsensusDecision.id)).where(
                    and_(
                        ConsensusDecision.consensus_achieved == False,
                        ConsensusDecision.created_at > datetime.utcnow() - timedelta(hours=1)
                    )
                )
            )
            failure_count = result.scalar() or 0
            return failure_count >= 3
        
        elif trigger == CircuitBreakerTrigger.FAIRNESS_COLLAPSE:
            # Check fairness metrics
            from services.fairness_monitor import FairnessMonitor
            monitor = FairnessMonitor(self.db)
            metrics = await monitor.compute_all_metrics()
            
            gini = metrics.get("gini_coefficient", 0)
            geo_disparity = metrics.get("geographic_disparity", 0)
            
            return gini > 0.50 or geo_disparity > 10
        
        elif trigger == CircuitBreakerTrigger.MODEL_CAPTURE:
            # Check model diversity
            enforcer = ModelDiversityEnforcer(self.consensus_engine.runner_pool, self.db, self.trace_logger)
            provider_weights = await enforcer._calculate_provider_weights()
            
            max_weight = max(provider_weights.values()) if provider_weights else 0
            
            # Check model agreement
            recent_decisions = await self.db.execute(
                select(ConsensusDecision).where(
                    ConsensusDecision.created_at > datetime.utcnow() - timedelta(hours=24)
                ).order_by(desc(ConsensusDecision.created_at)).limit(100)
            )
            decisions = recent_decisions.scalars().all()
            
            if decisions:
                unanimous_count = sum(1 for d in decisions if d.consensus_score > 0.99)
                agreement_rate = unanimous_count / len(decisions)
                return max_weight > 0.5 or agreement_rate > 0.95
            
            return max_weight > 0.5
        
        elif trigger == CircuitBreakerTrigger.CONSTITUTIONAL_CRISIS:
            # Would check for active constitutional court cases
            # For now, manual trigger only
            return False
        
        return False
    
    async def _activate_breaker(self, trigger: CircuitBreakerTrigger, config: Dict) -> CircuitBreakerEvent:
        """Activate circuit breaker"""
        
        event = CircuitBreakerEvent(
            trigger=trigger.value,
            trigger_data={"condition": config["condition"]},
            action=config["action"].value,
            action_details={"timeout_hours": config["timeout_hours"]},
            authorized_by=config["authority"],
            expires_at=datetime.utcnow() + timedelta(hours=config["timeout_hours"]) if config["timeout_hours"] else None
        )
        
        self.db.add(event)
        await self.db.flush()
        
        # Execute action
        await self._execute_action(event)
        
        # Log
        await self.trace_logger.log_event(
            event_type=AuditEventType.CIRCUIT_BREAKER,
            event_data={
                "event_id": str(event.id),
                "trigger": trigger.value,
                "action": config["action"].value,
                "authority": config["authority"]
            },
            actor_user_id=None
        )
        
        self.active_breakers[trigger.value] = event
        return event
    
    async def _execute_action(self, event: CircuitBreakerEvent):
        """Execute circuit breaker action"""
        
        action = CircuitBreakerAction(event.action)
        
        if action == CircuitBreakerAction.FREEZE:
            # Freeze all non-emergency decisions
            await self.consensus_engine.freeze_non_emergency()
        
        elif action == CircuitBreakerAction.REDISTRIBUTE:
            # Trigger fairness redistribution
            from services.fairness_monitor import FairnessMonitor
            monitor = FairnessMonitor(self.db)
            await monitor.trigger_emergency_redistribution()
        
        elif action == CircuitBreakerAction.ROTATE:
            # Force model rotation
            enforcer = ModelDiversityEnforcer(self.consensus_engine.runner_pool, self.db, self.trace_logger)
            await enforcer.force_rotation()
        
        elif action == CircuitBreakerAction.STAY:
            # Stay all decisions on constitutional matters
            await self.consensus_engine.stay_constitutional()
    
    async def resolve_breaker(self, trigger: CircuitBreakerTrigger, resolver_id: uuid.UUID, resolution: str) -> bool:
        """Manually resolve circuit breaker"""
        
        if trigger.value not in self.active_breakers:
            return False
        
        event = self.active_breakers[trigger.value]
        event.resolved_at = datetime.utcnow()
        event.resolution = resolution
        event.resolution_details = {"resolved_by": str(resolver_id)}
        
        # Reverse action
        await self._reverse_action(event)
        
        await self.db.flush()
        
        # Log
        await self.trace_logger.log_event(
            event_type=AuditEventType.CIRCUIT_BREAKER,
            event_data={
                "event_id": str(event.id),
                "trigger": trigger.value,
                "resolution": resolution,
                "resolved_by": str(resolver_id)
            },
            actor_user_id=resolver_id
        )
        
        del self.active_breakers[trigger.value]
        return True
    
    async def _reverse_action(self, event: CircuitBreakerEvent):
        """Reverse circuit breaker action"""
        action = CircuitBreakerAction(event.action)
        
        if action == CircuitBreakerAction.FREEZE:
            await self.consensus_engine.unfreeze()
        elif action == CircuitBreakerAction.STAY:
            await self.consensus_engine.unstay()


class FairnessMonitor:
    """Real-time fairness monitoring with automatic correction"""
    
    METRICS_CONFIG = {
        "gini_coefficient": {"target": 0.35, "alert": 0.40, "critical": 0.50},
        "merit_concentration": {"target": 0.30, "alert": 0.35, "critical": 0.40},  # Top 10%
        "geographic_disparity": {"target": 3.0, "alert": 5.0, "critical": 10.0},  # Max/min ratio
        "demographic_parity": {"target": 0.10, "alert": 0.15, "critical": 0.20},  # Max difference
        "intergenerational_equity": {"target": (0.8, 1.2), "alert": (0.6, 1.5), "critical": (0.5, 2.0)}
    }
    
    def __init__(self, db: AsyncSession, trace_logger: TraceLogger):
        self.db = db
        self.trace_logger = trace_logger
    
    async def compute_all_metrics(self) -> Dict[str, float]:
        """Compute all fairness metrics"""
        metrics = {}
        
        # Gini coefficient for merit distribution
        metrics["gini_coefficient"] = await self._compute_gini()
        
        # Merit concentration (top 10%)
        metrics["merit_concentration"] = await self._compute_merit_concentration()
        
        # Geographic disparity
        metrics["geographic_disparity"] = await self._compute_geographic_disparity()
        
        # Demographic parity
        metrics["demographic_parity"] = await self._compute_demographic_parity()
        
        # Intergenerational equity
        metrics["intergenerational_equity"] = await self._compute_intergenerational_equity()
        
        return metrics
    
    async def _compute_gini(self) -> float:
        """Compute Gini coefficient for merit scores"""
        result = await self.db.execute(
            select(User.merit_score).where(User.is_deleted == False)
        )
        scores = [float(s[0]) for s in result.all() if s[0] > 0]
        
        if not scores:
            return 0.0
        
        scores.sort()
        n = len(scores)
        cumsum = sum((i + 1) * scores[i] for i in range(n))
        total = sum(scores)
        
        if total == 0:
            return 0.0
        
        gini = (2 * cumsum) / (n * total) - (n + 1) / n
        return max(0.0, min(1.0, gini))
    
    async def _compute_merit_concentration(self) -> float:
        """Compute top 10% merit share"""
        result = await self.db.execute(
            select(User.merit_score).where(User.is_deleted == False).order_by(desc(User.merit_score))
        )
        scores = [float(s[0]) for s in result.all() if s[0] > 0]
        
        if not scores:
            return 0.0
        
        top_10_count = max(1, len(scores) // 10)
        top_10_sum = sum(scores[:top_10_count])
        total_sum = sum(scores)
        
        return top_10_sum / total_sum if total_sum > 0 else 0.0
    
    async def _compute_geographic_disparity(self) -> float:
        """Compute max/min merit ratio across provinces"""
        result = await self.db.execute(
            select(User.province, func.avg(User.merit_score)).where(
                and_(User.is_deleted == False, User.province.isnot(None))
            ).group_by(User.province)
        )
        province_scores = {p: float(s) for p, s in result.all() if s > 0}
        
        if len(province_scores) < 2:
            return 1.0
        
        max_score = max(province_scores.values())
        min_score = min(province_scores.values())
        
        return max_score / min_score if min_score > 0 else float('inf')
    
    async def _compute_demographic_parity(self) -> float:
        """Compute max difference across demographic groups"""
        # Would need demographic data - placeholder
        return 0.05
    
    async def _compute_intergenerational_equity(self) -> float:
        """Compute youth/elderly merit ratio"""
        # Would need age data - placeholder
        return 1.0
    
    async def check_violations(self, metrics: Dict[str, float]) -> List[Dict]:
        """Check for threshold violations"""
        violations = []
        
        for metric, value in metrics.items():
            config = self.METRICS_CONFIG.get(metric, {})
            
            if "critical" in config and value >= config["critical"]:
                violations.append({
                    "metric": metric,
                    "value": value,
                    "threshold": config["critical"],
                    "level": "critical"
                })
            elif "alert" in config and value >= config["alert"]:
                violations.append({
                    "metric": metric,
                    "value": value,
                    "threshold": config["alert"],
                    "level": "alert"
                })
        
        return violations
    
    async def trigger_emergency_redistribution(self):
        """Trigger emergency fairness redistribution"""
        # Would implement redistribution logic
        await self.trace_logger.log_event(
            event_type=AuditEventType.CIRCUIT_BREAKER,
            event_data={"action": "emergency_redistribution_triggered"},
            actor_user_id=None
        )


class ModelDiversityEnforcer:
    """Enforces model diversity and rotation"""
    
    def __init__(self, runner_pool, db: AsyncSession, trace_logger: TraceLogger):
        self.runner_pool = runner_pool
        self.db = db
        self.trace_logger = trace_logger
        self.policies = {
            "provider_max_share": 0.35,
            "model_max_share": 0.20,
            "family_provider_diversity": 3,
            "rotation_interval_days": 90
        }
    
    async def check_and_enforce(self) -> List[ModelRotationLog]:
        rotations = []
        
        provider_weights = await self._calculate_provider_weights()
        for provider, weight in provider_weights.items():
            if weight > self.policies["provider_max_share"]:
                rotation = await self._trigger_rebalance(provider, "overconcentration")
                if rotation:
                    rotations.append(rotation)
        
        return rotations
    
    async def _calculate_provider_weights(self) -> Dict[str, float]:
        weights = {}
        total = 0
        
        for family, config in settings.MODEL_FAMILIES.items():
            family_weight = config["weight"]
            for model in config["models"]:
                provider = model["provider"]
                weights[provider] = weights.get(provider, 0) + family_weight / len(config["models"])
                total += family_weight / len(config["models"])
        
        if total > 0:
            for p in weights:
                weights[p] /= total
        
        return weights
    
    async def _trigger_rebalance(self, provider: str, reason: str) -> Optional[ModelRotationLog]:
        logger.warning(f"Provider overconcentration: {provider} - {reason}")
        return None
    
    async def force_rotation(self):
        """Force immediate model rotation for all overconcentrated providers"""
        provider_weights = await self._calculate_provider_weights()
        for provider, weight in provider_weights.items():
            if weight > self.policies["provider_max_share"]:
                await self._trigger_rebalance(provider, "forced_rotation")


class AuditTrailService:
    """Immutable audit trail with cryptographic chaining and multi-jurisdiction anchoring"""
    
    ANCHOR_CONFIGS = {
        "dr_supreme_court": {"endpoint": "https://audit.suprema.gob.do/anchor", "method": "POST"},
        "un_oict": {"endpoint": "https://oict.un.org/audit/anchor", "method": "POST"},
        "icc": {"endpoint": "https://icc-cpi.int/audit/anchor", "method": "POST"},
        "bitcoin": {"method": "op_return"},  # OpenTimestamps
        "ethereum": {"method": "contract_storage"},
        "polygon": {"method": "contract_storage"}
    }
    
    def __init__(self, db: Optional[AsyncSession] = None, trace_logger: Optional[TraceLogger] = None):
        self.db = db
        self.trace_logger = trace_logger
        self.last_hash = None
        self.sequence = 0
    
    async def log_event(self, event_type: AuditEventType, event_data: Dict,
                        actor_user_id: Optional[uuid.UUID] = None,
                        actor_session_id: Optional[uuid.UUID] = None,
                        actor_identity_level: Optional[int] = None,
                        actor_ip_hash: Optional[str] = None,
                        actor_device_fingerprint: Optional[str] = None,
                        target_type: Optional[str] = None,
                        target_id: Optional[uuid.UUID] = None) -> Optional[AuditRecord]:
        """Log event to immutable audit trail"""
        
        if self.db is None:
            logger.info(
                "audit_event",
                event_type=getattr(event_type, "value", event_type),
                event_data=event_data,
            )
            return None
        
        self.sequence += 1
        
        # Get previous hash
        if self.last_hash:
            previous_hash = self.last_hash
        else:
            # Get from database
            result = await self.db.execute(
                select(AuditRecord.record_hash).order_by(desc(AuditRecord.sequence)).limit(1)
            )
            previous_hash = result.scalar() or "genesis"
        
        # Create record
        record = AuditRecord(
            sequence=self.sequence,
            event_type=event_type,
            event_data=event_data,
            actor_user_id=actor_user_id,
            actor_session_id=actor_session_id,
            actor_identity_level=actor_identity_level,
            actor_ip_hash=actor_ip_hash,
            actor_device_fingerprint=actor_device_fingerprint,
            target_type=target_type,
            target_id=target_id,
            previous_hash=previous_hash,
            record_hash="",  # Will compute
            timestamp=datetime.utcnow()
        )
        
        # Compute hash
        record.record_hash = self._compute_hash(record, previous_hash)
        
        self.db.add(record)
        await self.db.flush()
        
        self.last_hash = record.record_hash
        
        # Anchor asynchronously
        asyncio.create_task(self._anchor_record(record))
        
        return record
    
    def _compute_hash(self, record: AuditRecord, previous_hash: str) -> str:
        """Compute cryptographic hash for chaining"""
        data = {
            "sequence": record.sequence,
            "event_type": record.event_type.value,
            "event_data": record.event_data,
            "actor_user_id": str(record.actor_user_id) if record.actor_user_id else None,
            "target_type": record.target_type,
            "target_id": str(record.target_id) if record.target_id else None,
            "previous_hash": previous_hash,
            "timestamp": record.timestamp.isoformat()
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    
    async def _anchor_record(self, record: AuditRecord):
        """Anchor record to multiple jurisdictions"""
        anchors = {}
        
        for name, config in self.ANCHOR_CONFIGS.items():
            try:
                if config["method"] == "op_return":
                    # Bitcoin OP_RETURN via OpenTimestamps
                    anchor_result = await self._anchor_bitcoin(record.record_hash)
                elif config["method"] == "contract_storage":
                    # Ethereum/Polygon contract storage
                    anchor_result = await self._anchor_ethereum(record.record_hash, name)
                else:
                    # HTTP POST to anchor service
                    anchor_result = await self._anchor_http(record.record_hash, config)
                
                anchors[name] = anchor_result
            except Exception as e:
                logger.error(f"Anchoring failed for {name}", error=str(e))
                anchors[name] = {"error": str(e)}
        
        # Update record with anchors
        record.anchors = anchors
        record.anchored = True
        record.anchored_at = datetime.utcnow()
        await self.db.flush()
    
    async def _anchor_bitcoin(self, hash_value: str) -> Dict:
        """Anchor via OpenTimestamps to Bitcoin"""
        # Would use OpenTimestamps library
        return {"method": "op_return", "status": "pending"}
    
    async def _anchor_ethereum(self, hash_value: str, network: str) -> Dict:
        """Anchor to Ethereum/Polygon"""
        # Would write to smart contract
        return {"method": "contract_storage", "network": network, "status": "pending"}
    
    async def _anchor_http(self, hash_value: str, config: Dict) -> Dict:
        """Anchor via HTTP POST"""
        async with aiohttp.ClientSession() as session:
            async with session.post(config["endpoint"], json={"hash": hash_value}) as resp:
                return {"status": resp.status, "response": await resp.text()}
    
    async def verify_chain(self, start_sequence: int = 1, end_sequence: int = None) -> Dict:
        """Verify audit chain integrity"""
        query = select(AuditRecord).where(AuditRecord.sequence >= start_sequence).order_by(AuditRecord.sequence)
        if end_sequence:
            query = query.where(AuditRecord.sequence <= end_sequence)
        
        result = await self.db.execute(query)
        records = result.scalars().all()
        
        errors = []
        previous_hash = "genesis"
        
        for record in records:
            expected_hash = self._compute_hash(record, previous_hash)
            if record.record_hash != expected_hash:
                errors.append({
                    "sequence": record.sequence,
                    "expected": expected_hash,
                    "actual": record.record_hash
                })
            previous_hash = record.record_hash
        
        return {
            "verified": len(errors) == 0,
            "records_checked": len(records),
            "errors": errors
        }