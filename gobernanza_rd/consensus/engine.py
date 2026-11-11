# Multi-Model Consensus Engine
import asyncio
import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from collections import defaultdict

import structlog

from config.settings import get_settings
from local_models.runner import ModelRunnerPool, ModelConfig, ModelProvider, ModelResponse, create_runner
from models import ConsensusDecision, AuditRecord, AuditEventType, ModelRotationLog, CircuitBreakerEvent

settings = get_settings()
logger = structlog.get_logger()


class ProposalSeverity(str, Enum):
    ROUTINE = "routine"
    SIGNIFICANT = "significant"
    CONSTITUTIONAL = "constitutional"
    EMERGENCY = "emergency"


class ConsensusResult(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    ESCALATED = "escalated"


@dataclass
class ModelVote:
    family: str
    model_id: str
    provider: ModelProvider
    role: str
    vote: ConsensusResult
    confidence: float
    reasoning: str
    raw_response: ModelResponse
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FamilyConsensus:
    family: str
    votes: List[ModelVote]
    consensus: ConsensusResult
    confidence: float
    reasoning: str
    dissenting_votes: List[ModelVote]
    adversarial_challenge: Optional[ModelVote] = None


@dataclass
class ConsensusOutcome:
    decision_id: str
    proposal_type: str
    proposal_id: str
    severity: ProposalSeverity
    family_consensus: Dict[str, FamilyConsensus]
    final_decision: ConsensusResult
    consensus_score: float
    threshold_met: bool
    required_threshold: float
    families_participated: int
    families_required: int
    dissenting_families: List[str]
    adversarial_challenges: List[ModelVote]
    threshold_signature: Optional[str] = None
    proof_hash: Optional[str] = None


class AdversarialChallenger:
    """Generates adversarial challenges for each family"""
    
    CHALLENGE_PROMPTS = {
        "constitutional": """You are a constitutional adversarial reviewer. Your role is to find flaws in the reasoning.
        Challenge the proposal on: constitutional violations, rights infringements, precedent conflicts, 
        separation of powers, due process, equal protection, judicial review standards.""",
        
        "economic": """You are an economic adversarial reviewer. Challenge on: allocation efficiency, 
        Pareto optimality, incentive compatibility, market distortion, distributional effects, 
        fiscal sustainability, moral hazard, adverse selection, game-theoretic vulnerabilities.""",
        
        "social": """You are a social dynamics adversarial reviewer. Challenge on: community impact, 
        cultural sensitivity, exclusionary effects, power dynamics, social cohesion, 
        trust erosion, manipulation vulnerability, unintended consequences on vulnerable groups.""",
        
        "security": """You are a security adversarial reviewer. Challenge on: attack vectors, 
        fraud vulnerabilities, system integrity, data poisoning, model extraction, 
        adversarial examples, privilege escalation, audit trail manipulation, consensus capture.""",
        
        "arbitration": """You are a legal arbitration adversarial reviewer. Challenge on: 
        procedural fairness, evidence standards, burden of proof, precedent consistency, 
        conflict of interest, jurisdictional issues, enforcement feasibility, appeal rights."""
    }
    
    def __init__(self, runner_pool: ModelRunnerPool):
        self.runner_pool = runner_pool
    
    async def challenge(self, family: str, proposal_data: Dict, family_consensus: FamilyConsensus) -> Optional[ModelVote]:
        """Generate adversarial challenge from a different provider"""
        prompt = f"""
        {self.CHALLENGE_PROMPTS.get(family, "Challenge this proposal critically.")}
        
        Proposal: {json.dumps(proposal_data, indent=2)}
        
        Family Consensus: {family_consensus.consensus.value} (confidence: {family_consensus.confidence:.2f})
        Family Reasoning: {family_consensus.reasoning}
        
        Individual Votes:
        {json.dumps([{"model": v.model_id, "vote": v.vote.value, "confidence": v.confidence, "reasoning": v.reasoning} for v in family_consensus.votes], indent=2)}
        
        Provide your adversarial challenge as JSON:
        {{
            "challenge_valid": true/false,
            "concerns": ["concern1", "concern2"],
            "counter_arguments": ["arg1", "arg2"],
            "recommended_action": "approve/reject/defer/escalate",
            "confidence": 0.0-1.0
        }}
        """
        
        # Use adversarial model from different provider
        adversarial_runner = await self.runner_pool.get_runner(f"{family}_adversarial")
        if not adversarial_runner:
            return None
        
        try:
            response = await adversarial_runner.generate(prompt)
            challenge_data = json.loads(response.content)
            
            if challenge_data.get("challenge_valid"):
                return ModelVote(
                    family=family,
                    model_id=f"{family}_adversarial",
                    provider=adversarial_runner.config.provider,
                    role="adversarial",
                    vote=ConsensusResult(challenge_data.get("recommended_action", "defer")),
                    confidence=challenge_data.get("confidence", 0.5),
                    reasoning=f"Adversarial: {', '.join(challenge_data.get('concerns', []))}",
                    raw_response=response
                )
        except Exception as e:
            logger.error(f"Adversarial challenge failed for {family}", error=str(e))
        
        return None


class ConsensusEngine:
    """Multi-model consensus engine with 5 families, adversarial validation, threshold signatures"""
    
    def __init__(self, runner_pool: ModelRunnerPool, db_session, audit_logger):
        self.runner_pool = runner_pool
        self.db = db_session
        self.audit_logger = audit_logger
        self.adversarial = AdversarialChallenger(runner_pool)
        
        # Load family configurations from settings
        self.families = settings.MODEL_FAMILIES
        self.consensus_rules = settings.CONSENSUS_THRESHOLDS
    
    async def decide(self, proposal_type: str, proposal_id: str, proposal_data: Dict, 
                     severity: ProposalSeverity = ProposalSeverity.ROUTINE) -> ConsensusOutcome:
        """Execute full consensus decision process"""
        
        decision_id = f"consensus_{proposal_type}_{proposal_id}_{int(time.time())}"
        start_time = time.time()
        
        logger.info(f"Starting consensus decision", decision_id=decision_id, severity=severity.value)
        
        # 1. Determine relevant families
        relevant_families = self._select_families(proposal_type, severity)
        
        # 2. Query each family in parallel
        family_results = await asyncio.gather(*[
            self._query_family(family, proposal_data, proposal_type)
            for family in relevant_families
        ], return_exceptions=True)
        
        # 3. Process family results
        family_consensus = {}
        for family, result in zip(relevant_families, family_results):
            if isinstance(result, Exception):
                logger.error(f"Family {family} failed", error=str(result))
                # Create failed consensus
                family_consensus[family] = FamilyConsensus(
                    family=family,
                    votes=[],
                    consensus=ConsensusResult.DEFERRED,
                    confidence=0.0,
                    reasoning=f"Family query failed: {str(result)}",
                    dissenting_votes=[]
                )
            else:
                family_consensus[family] = result
        
        # 4. Generate adversarial challenges
        adversarial_challenges = []
        for family, consensus in family_consensus.items():
            challenge = await self.adversarial.challenge(family, proposal_data, consensus)
            if challenge:
                adversarial_challenges.append(challenge)
                consensus.adversarial_challenge = challenge
        
        # 5. Compute inter-family consensus
        outcome = self._compute_inter_family_consensus(
            decision_id, proposal_type, proposal_id, severity,
            family_consensus, adversarial_challenges
        )
        
        # 6. Generate cryptographic proof
        outcome.threshold_signature = await self._generate_threshold_signature(outcome)
        outcome.proof_hash = self._generate_proof_hash(outcome)
        
        # 7. Persist to database
        await self._persist_decision(outcome, family_consensus, adversarial_challenges, time.time() - start_time)
        
        # 8. Log to audit trail
        await self._audit_decision(outcome, family_consensus)
        
        logger.info(f"Consensus completed", decision_id=decision_id, decision=outcome.final_decision.value, score=outcome.consensus_score)
        
        return outcome
    
    def _select_families(self, proposal_type: str, severity: ProposalSeverity) -> List[str]:
        """Select which families should participate based on proposal type and severity"""
        # All families participate in constitutional decisions
        if severity == ProposalSeverity.CONSTITUTIONAL:
            return list(self.families.keys())
        
        # Map proposal types to relevant families
        type_family_map = {
            "merit_allocation": ["economic", "constitutional", "social"],
            "payment_authorization": ["economic", "security", "constitutional"],
            "housing_decision": ["economic", "social", "constitutional"],
            "infrastructure_project": ["economic", "security", "constitutional"],
            "contractor_approval": ["security", "economic", "constitutional"],
            "identity_escalation": ["constitutional", "security", "social"],
            "veeduria_escalation": ["constitutional", "social", "security"],
            "circuit_breaker": ["constitutional", "security", "arbitration"],
            "model_rotation": ["constitutional", "security", "arbitration"],
            "policy_change": ["constitutional", "economic", "social"],
            "emergency_response": ["security", "constitutional", "arbitration"],
        }
        
        families = type_family_map.get(proposal_type, list(self.families.keys()))
        
        # Ensure minimum families per severity
        min_families = self.consensus_rules[severity.value]["families_required"]
        if len(families) < min_families:
            # Add highest-weighted families not already included
            all_families = sorted(self.families.keys(), key=lambda f: self.families[f]["weight"], reverse=True)
            for f in all_families:
                if f not in families:
                    families.append(f)
                if len(families) >= min_families:
                    break
        
        return families
    
    async def _query_family(self, family: str, proposal_data: Dict, proposal_type: str) -> FamilyConsensus:
        """Query all models in a family and compute intra-family consensus"""
        
        family_config = self.families[family]
        models = family_config["models"]
        
        # Build prompt for this family
        prompt = self._build_family_prompt(family, proposal_data, proposal_type)
        system_prompt = self._get_family_system_prompt(family)
        
        # Query all models in parallel
        model_tasks = []
        for model_config in models:
            provider = ModelProvider(model_config["provider"])
            config = ModelConfig(
                provider=provider,
                model_name=model_config["model"],
                role=model_config["role"],
                base_url=self._get_provider_base_url(provider),
                api_key=self._get_provider_api_key(provider)
            )
            runner = create_runner(config)
            model_tasks.append(self._query_single_model(runner, model_config, prompt, system_prompt))
        
        model_responses = await asyncio.gather(*model_tasks, return_exceptions=True)
        
        # Process responses into votes
        votes = []
        for model_config, response in zip(models, model_responses):
            if isinstance(response, Exception):
                logger.error(f"Model {model_config['model']} failed", error=str(response))
                continue
            
            vote = self._parse_model_vote(response, model_config, family)
            if vote:
                votes.append(vote)
        
        # Compute intra-family consensus
        return self._compute_intra_family_consensus(family, votes)
    
    async def _query_single_model(self, runner: BaseModelRunner, model_config: Dict, prompt: str, system_prompt: str) -> ModelResponse:
        """Query a single model"""
        async with runner:
            return await runner.generate(prompt, system_prompt)
    
    def _build_family_prompt(self, family: str, proposal_data: Dict, proposal_type: str) -> str:
        """Build family-specific prompt"""
        family_specialties = {
            "constitutional": "constitutional law, rights analysis, legal precedent, due process",
            "economic": "resource allocation, mechanism design, welfare economics, fiscal policy",
            "social": "community dynamics, cultural anthropology, social psychology, participatory governance",
            "security": "threat modeling, fraud detection, system integrity, adversarial robustness",
            "arbitration": "legal arbitration, dispute resolution, precedent analysis, procedural fairness"
        }
        
        specialty = family_specialties.get(family, "governance analysis")
        
        return f"""
        You are a {specialty} expert participating in a multi-model governance consensus.
        
        Proposal Type: {proposal_type}
        Proposal Data: {json.dumps(proposal_data, indent=2, default=str)}
        
        Your family specialty: {specialty}
        Your role: Provide expert analysis and vote on this proposal.
        
        Respond with JSON:
        {{
            "analysis": "Your detailed analysis from your specialty perspective",
            "vote": "approved/rejected/deferred/escalated",
            "confidence": 0.0-1.0,
            "key_concerns": ["concern1", "concern2"],
            "conditions": ["condition1"] // if vote is approved with conditions
        }}
        """
    
    def _get_family_system_prompt(self, family: str) -> str:
        """Get system prompt for family"""
        prompts = {
            "constitutional": "You are a constitutional law expert. Analyze proposals for constitutionality, rights protection, separation of powers, due process, and legal precedent. Be rigorous and cite principles.",
            "economic": "You are a welfare economics and mechanism design expert. Analyze for efficiency, equity, incentive compatibility, Pareto optimality, and fiscal sustainability. Use mathematical reasoning.",
            "social": "You are a community governance and social dynamics expert. Analyze for social cohesion, cultural appropriateness, power dynamics, inclusion, and trust-building. Center vulnerable voices.",
            "security": "You are a security and adversarial robustness expert. Analyze for attack vectors, fraud, integrity violations, consensus capture, and system vulnerabilities. Think like an attacker.",
            "arbitration": "You are a legal arbitration expert. Analyze for procedural fairness, evidence standards, precedent consistency, conflict of interest, and enforceability. Be impartial and precedent-bound."
        }
        return prompts.get(family, "You are a governance expert. Provide rigorous analysis.")
    
    def _parse_model_vote(self, response: ModelResponse, model_config: Dict, family: str) -> Optional[ModelVote]:
        """Parse model response into vote"""
        try:
            # Try to extract JSON from response
            content = response.content.strip()
            
            # Find JSON in response
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                data = json.loads(json_str)
            else:
                # Fallback: assume entire response is the analysis
                data = {
                    "analysis": content,
                    "vote": "deferred",
                    "confidence": 0.5,
                    "key_concerns": ["Could not parse structured vote"],
                    "conditions": []
                }
            
            vote_str = data.get("vote", "deferred").lower()
            vote_map = {
                "approved": ConsensusResult.APPROVED,
                "reject": ConsensusResult.REJECTED,
                "rejected": ConsensusResult.REJECTED,
                "defer": ConsensusResult.DEFERRED,
                "deferred": ConsensusResult.DEFERRED,
                "escalate": ConsensusResult.ESCALATED,
                "escalated": ConsensusResult.ESCALATED
            }
            vote = vote_map.get(vote_str, ConsensusResult.DEFERRED)
            
            return ModelVote(
                family=family,
                model_id=model_config["model"],
                provider=ModelProvider(model_config["provider"]),
                role=model_config["role"],
                vote=vote,
                confidence=float(data.get("confidence", 0.5)),
                reasoning=data.get("analysis", "")[:2000],
                raw_response=response
            )
        except Exception as e:
            logger.error(f"Failed to parse vote from {model_config['model']}", error=str(e))
            return None
    
    def _compute_intra_family_consensus(self, family: str, votes: List[ModelVote]) -> FamilyConsensus:
        """Compute consensus within a family"""
        if not votes:
            return FamilyConsensus(
                family=family,
                votes=[],
                consensus=ConsensusResult.DEFERRED,
                confidence=0.0,
                reasoning="No valid votes",
                dissenting_votes=[]
            )
        
        # Weight votes by confidence
        vote_weights = defaultdict(float)
        total_weight = 0
        
        for vote in votes:
            weight = vote.confidence
            vote_weights[vote.vote] += weight
            total_weight += weight
        
        # Normalize
        for v in vote_weights:
            vote_weights[v] /= total_weight
        
        # Determine consensus
        sorted_votes = sorted(vote_weights.items(), key=lambda x: x[1], reverse=True)
        winning_vote, winning_weight = sorted_votes[0]
        
        # Dissenting votes
        dissenting = [v for v in votes if v.vote != winning_vote]
        
        # Average confidence of winning votes
        winning_votes = [v for v in votes if v.vote == winning_vote]
        avg_confidence = sum(v.confidence for v in winning_votes) / len(winning_votes) if winning_votes else 0
        
        # Reasoning synthesis
        reasoning_parts = [v.reasoning for v in winning_votes[:3]]
        reasoning = " | ".join(reasoning_parts)[:2000]
        
        return FamilyConsensus(
            family=family,
            votes=votes,
            consensus=winning_vote,
            confidence=winning_weight * avg_confidence,
            reasoning=reasoning,
            dissenting_votes=dissenting
        )
    
    def _compute_inter_family_consensus(self, decision_id: str, proposal_type: str, proposal_id: str,
                                         severity: ProposalSeverity, family_consensus: Dict[str, FamilyConsensus],
                                         adversarial_challenges: List[ModelVote]) -> ConsensusOutcome:
        """Compute consensus across families"""
        
        rule = self.consensus_rules[severity.value]
        required_threshold = rule["threshold"]
        families_required = rule["families_required"]
        
        # Weight families by their configured weight
        family_weights = {f: self.families[f]["weight"] for f in family_consensus.keys()}
        total_weight = sum(family_weights.values())
        normalized_weights = {f: w/total_weight for f, w in family_weights.items()}
        
        # Compute weighted consensus
        decision_weights = defaultdict(float)
        for family, consensus in family_consensus.items():
            weight = normalized_weights.get(family, 0)
            decision_weights[consensus.consensus] += weight * consensus.confidence
        
        # Normalize decision weights
        total_decision_weight = sum(decision_weights.values())
        if total_decision_weight > 0:
            for d in decision_weights:
                decision_weights[d] /= total_decision_weight
        
        # Check adversarial challenges
        adversarial_weight = 0
        for challenge in adversarial_challenges:
            adversarial_weight += challenge.confidence * 0.1  # Adversarial has 10% weight
        
        # Determine final decision
        if not decision_weights:
            final_decision = ConsensusResult.DEFERRED
            consensus_score = 0.0
        else:
            sorted_decisions = sorted(decision_weights.items(), key=lambda x: x[1], reverse=True)
            final_decision, consensus_score = sorted_decisions[0]
            
            # Apply adversarial penalty
            if adversarial_challenges:
                # If strong adversarial challenge opposes, reduce confidence
                for challenge in adversarial_challenges:
                    if challenge.vote != final_decision and challenge.confidence > 0.7:
                        consensus_score *= (1 - challenge.confidence * 0.2)
        
        # Check threshold
        threshold_met = consensus_score >= required_threshold
        families_participated = len([f for f, c in family_consensus.items() if c.votes])
        
        # Check family participation requirement
        if families_participated < families_required:
            threshold_met = False
            final_decision = ConsensusResult.DEFERRED
        
        # Dissenting families
        dissenting_families = [f for f, c in family_consensus.items() if c.consensus != final_decision]
        
        return ConsensusOutcome(
            decision_id=decision_id,
            proposal_type=proposal_type,
            proposal_id=proposal_id,
            severity=severity,
            family_consensus=family_consensus,
            final_decision=final_decision,
            consensus_score=consensus_score,
            threshold_met=threshold_met,
            required_threshold=required_threshold,
            families_participated=families_participated,
            families_required=families_required,
            dissenting_families=dissenting_families,
            adversarial_challenges=adversarial_challenges
        )
    
    async def _generate_threshold_signature(self, outcome: ConsensusOutcome) -> str:
        """Generate FROST threshold signature (placeholder - would use actual FROST implementation)"""
        # In production, this would use a proper FROST threshold signature scheme
        # For now, create a deterministic hash-based proof
        data = f"{outcome.decision_id}:{outcome.final_decision.value}:{outcome.consensus_score:.4f}:{sorted(outcome.family_consensus.keys())}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _generate_proof_hash(self, outcome: ConsensusOutcome) -> str:
        """Generate proof hash for audit trail"""
        proof_data = {
            "decision_id": outcome.decision_id,
            "proposal_type": outcome.proposal_type,
            "proposal_id": outcome.proposal_id,
            "final_decision": outcome.final_decision.value,
            "consensus_score": outcome.consensus_score,
            "family_results": {
                f: {"consensus": c.consensus.value, "confidence": c.confidence}
                for f, c in outcome.family_consensus.items()
            },
            "adversarial_challenges": len(outcome.adversarial_challenges),
            "threshold_met": outcome.threshold_met
        }
        return hashlib.sha256(json.dumps(proof_data, sort_keys=True).encode()).hexdigest()
    
    async def _persist_decision(self, outcome: ConsensusOutcome, family_consensus: Dict[str, FamilyConsensus],
                                 adversarial_challenges: List[ModelVote], duration_ms: float):
        """Persist consensus decision to database"""
        
        # Family votes for storage
        family_votes_json = {}
        for family, consensus in family_consensus.items():
            family_votes_json[family] = {
                "consensus": consensus.consensus.value,
                "confidence": consensus.confidence,
                "reasoning": consensus.reasoning,
                "votes": [
                    {
                        "model": v.model_id,
                        "provider": v.provider.value,
                        "role": v.role,
                        "vote": v.vote.value,
                        "confidence": v.confidence,
                        "reasoning": v.reasoning
                    }
                    for v in consensus.votes
                ],
                "dissenting_votes": [
                    {"model": v.model_id, "vote": v.vote.value}
                    for v in consensus.dissenting_votes
                ],
                "adversarial_challenge": {
                    "model": consensus.adversarial_challenge.model_id,
                    "vote": consensus.adversarial_challenge.vote.value,
                    "concerns": consensus.adversarial_challenge.reasoning
                } if consensus.adversarial_challenge else None
            }
        
        # Create consensus decision record
        decision_record = ConsensusDecision(
            decision_id=outcome.decision_id,
            proposal_type=outcome.proposal_type,
            proposal_id=uuid.UUID(outcome.proposal_id) if outcome.proposal_id else None,
            proposal_data={"data": outcome.proposal_data} if hasattr(outcome, 'proposal_data') else {},
            severity=outcome.severity.value,
            family_votes=family_votes_json,
            decision=outcome.final_decision.value,
            consensus_achieved=outcome.threshold_met,
            consensus_score=outcome.consensus_score,
            threshold_met=outcome.threshold_met,
            required_threshold=outcome.required_threshold,
            families_participated=outcome.families_participated,
            families_required=outcome.families_required,
            dissenting_families=outcome.dissenting_families,
            adversarial_challenges=[
                {
                    "family": c.family,
                    "model": c.model_id,
                    "vote": c.vote.value,
                    "confidence": c.confidence,
                    "reasoning": c.reasoning
                }
                for c in outcome.adversarial_challenges
            ],
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_ms=int(duration_ms * 1000),
            threshold_signature=outcome.threshold_signature,
            proof_hash=outcome.proof_hash
        )
        
        self.db.add(decision_record)
        await self.db.flush()
    
    async def _audit_decision(self, outcome: ConsensusOutcome, family_consensus: Dict[str, FamilyConsensus]):
        """Log to immutable audit trail"""
        
        event_data = {
            "decision_id": outcome.decision_id,
            "proposal_type": outcome.proposal_type,
            "proposal_id": outcome.proposal_id,
            "final_decision": outcome.final_decision.value,
            "consensus_score": float(outcome.consensus_score),
            "threshold_met": outcome.threshold_met,
            "families": {
                f: {"consensus": c.consensus.value, "confidence": float(c.confidence)}
                for f, c in outcome.family_consensus.items()
            },
            "adversarial_challenges": len(outcome.adversarial_challenges)
        }
        
        await self.audit_logger.log_event(
            event_type=AuditEventType.CONSENSUS_DECISION,
            event_data=event_data,
            actor_user_id=None,  # System action
            target_type="consensus",
            target_id=uuid.UUID(outcome.decision_id.replace("consensus_", "")[:36]) if "consensus_" in outcome.decision_id else None
        )
    
    def _get_provider_base_url(self, provider: ModelProvider) -> str:
        urls = {
            ModelProvider.OLLAMA: settings.OLLAMA_BASE_URL,
            ModelProvider.LLAMA_CPP: settings.LLAMA_CPP_SERVER_URL,
            ModelProvider.VLLM: settings.VLLM_BASE_URL,
            ModelProvider.ANTHROPIC: "https://api.anthropic.com/v1",
            ModelProvider.OPENAI: "https://api.openai.com/v1",
            ModelProvider.GOOGLE: "https://generativelanguage.googleapis.com/v1beta",
            ModelProvider.MISTRAL: "https://api.mistral.ai/v1",
            ModelProvider.COHERE: "https://api.cohere.ai/v1",
        }
        return urls.get(provider, "")
    
    def _get_provider_api_key(self, provider: ModelProvider) -> Optional[str]:
        keys = {
            ModelProvider.ANTHROPIC: settings.ANTHROPIC_API_KEY,
            ModelProvider.OPENAI: settings.OPENAI_API_KEY,
            ModelProvider.GOOGLE: settings.GOOGLE_API_KEY,
            ModelProvider.MISTRAL: settings.MISTRAL_API_KEY,
            ModelProvider.COHERE: settings.COHERE_API_KEY,
        }
        return keys.get(provider)


class ModelDiversityEnforcer:
    """Enforces model diversity and rotation policies"""
    
    def __init__(self, runner_pool: ModelRunnerPool, db_session, audit_logger):
        self.runner_pool = runner_pool
        self.db = db_session
        self.audit_logger = audit_logger
        self.policies = {
            "provider_max_share": 0.35,
            "model_max_share": 0.20,
            "family_provider_diversity": 3,
            "rotation_interval_days": 90,
            "emergency_new_model_days": 7
        }
    
    async def check_and_enforce(self) -> List[ModelRotationLog]:
        """Check diversity constraints and enforce if needed"""
        rotations = []
        
        # Check provider concentration
        provider_weights = await self._calculate_provider_weights()
        for provider, weight in provider_weights.items():
            if weight > self.policies["provider_max_share"]:
                rotation = await self._trigger_rebalance(provider, "overconcentration")
                if rotation:
                    rotations.append(rotation)
        
        # Check model staleness
        for runner_id, runner in self.runner_pool.runners.items():
            # Would check last rotation date from DB
            pass
        
        return rotations
    
    async def _calculate_provider_weights(self) -> Dict[str, float]:
        """Calculate current provider weight distribution"""
        weights = defaultdict(float)
        total = 0
        
        for family, config in settings.MODEL_FAMILIES.items():
            family_weight = config["weight"]
            for model in config["models"]:
                provider = model["provider"]
                weights[provider] += family_weight / len(config["models"])
                total += family_weight / len(config["models"])
        
        # Normalize
        if total > 0:
            for p in weights:
                weights[p] /= total
        
        return dict(weights)
    
    async def _trigger_rebalance(self, provider: str, reason: str) -> Optional[ModelRotationLog]:
        """Trigger model rebalance for overconcentrated provider"""
        # Would implement actual rotation logic
        logger.warning(f"Provider overconcentration detected: {provider} - {reason}")
        return None