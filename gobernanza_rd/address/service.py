# Address Resolution Engine - Zero Shipping Address Issues
import asyncio
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum

import structlog
from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config.settings import get_settings
from models import (
    DeliveryLocation, CommunityReference, DesignatedNeighbor, PickupPoint,
    AddressCorrection, QuestVisit, User, Delivery, DeliveryType,
    CommunityReferenceType, AuditRecord, AuditEventType
)
from services.gov_api_connectors import GovAPIConnectorManager
from services.quest_service import QuestService
from services.trace_logger import TraceLogger

settings = get_settings()
logger = structlog.get_logger()


@dataclass
class ResolvedLocation:
    """Complete delivery location with GPS and community references"""
    latitud: Decimal
    longitud: Decimal
    precision_metros: int
    nombre_completo: str
    telefono: str
    email: Optional[str]
    provincia: Optional[str]
    municipio: Optional[str]
    sector: Optional[str]
    calle_principal: Optional[str]
    numero_casa: Optional[str]
    referencia_catastral: Optional[str]
    community_references: List[Dict]
    designated_neighbor: Optional[Dict]
    instrucciones_acceso: Optional[str]
    codigo_acceso: Optional[str]
    horarios_disponibles: List[Dict]
    requiere_autorizacion: bool
    fuente_principal: str
    ultima_verificacion: datetime
    verificado_por_quest: bool
    quest_verificador_id: Optional[str]
    quest_verificacion_fecha: Optional[datetime]
    confidence_score: Decimal
    delivery_constraints: Dict


class AddressResolutionEngine:
    """
    Resolves delivery location WITHOUT user entering address.
    Sources (priority order):
    1. JCE Cédula registry (official domicile)
    2. MIVHED housing assignment (if subsidized housing)
    3. SUPÉRATE beneficiary registry (household location)
    4. EDE/CORAASAN utility account (service address)
    5. DGII tax domicile (fiscal address)
    6. Quest visit logs (verified physical location)
    7. Community reference points (colmado, iglesia, escuela)
    """
    
    SOURCE_PRIORITY = [
        "jce_cedula",
        "mivhed_assignment",
        "superate_hogar",
        "ede_service",
        "coraasan_service",
        "dgii_fiscal",
        "quest_verified",
        "community_reference"
    ]
    
    # Delivery-type specific priority adjustments
    TYPE_WEIGHTS = {
        DeliveryType.HOUSING_KEYS: {"mivhed": 10, "jce": 8, "quest": 9},
        DeliveryType.APPLIANCE: {"ede": 9, "coraasan": 8, "superate": 7, "quest": 8},
        DeliveryType.UTILITY_EQUIPMENT: {"ede": 10, "coraasan": 10, "jce": 6},
        DeliveryType.FOOD_PACKAGE: {"superate": 10, "quest": 9, "community": 8},
        DeliveryType.EMERGENCY_SUPPLIES: {"quest": 10, "community": 9, "jce": 7},
        DeliveryType.MUTUAL_AID: {"quest": 9, "community": 10, "superate": 7},
        DeliveryType.SELECTING_FRONT: {"mivhed": 9, "jce": 8, "quest": 8},
    }
    
    def __init__(self, gov_connector: GovAPIConnectorManager, quest_service: QuestService, trace_logger: TraceLogger):
        self.gov_connector = gov_connector
        self.quest_service = quest_service
        self.trace_logger = trace_logger
    
    async def resolve_delivery_location(self, cedula: str, delivery_type: DeliveryType) -> Optional[ResolvedLocation]:
        """Get verified delivery location from government sources"""
        
        # Parallel fetch from all sources
        tasks = {
            "jce": self._get_jce_domicilio(cedula),
            "mivhed": self._get_mivhed_assignment(cedula),
            "superate": self._get_superate_hogar(cedula),
            "ede": self._get_ede_service(cedula),
            "coraasan": self._get_coraasan_service(cedula),
            "dgii": self._get_dgii_fiscal(cedula),
            "quest": self._get_quest_verified(cedula)
        }
        
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        source_data = dict(zip(tasks.keys(), results))
        
        # Resolve conflicts using priority + recency + verification
        resolved = self._resolve_conflicts(source_data, delivery_type, cedula)
        
        if not resolved:
            return None
        
        # Enhance with community references
        enhanced = await self._enhance_with_community(cedula, resolved)
        
        return enhanced
    
    async def _get_jce_domicilio(self, cedula: str) -> Optional[Dict]:
        """Get domicile from JCE"""
        try:
            result = await self.gov_connector.call("jce", "get_domicilio", {"cedula": cedula})
            if result.success and result.data:
                return {
                    "source": "jce_cedula",
                    "data": result.data,
                    "timestamp": result.timestamp,
                    "verified": True
                }
        except Exception:
            pass
        return None
    
    async def _get_mivhed_assignment(self, cedula: str) -> Optional[Dict]:
        """Get housing assignment from MIVHED"""
        try:
            result = await self.gov_connector.call("mivhed", "get_assigned_address", {"cedula": cedula})
            if result.success and result.data:
                return {
                    "source": "mivhed_assignment",
                    "data": result.data,
                    "timestamp": result.timestamp,
                    "verified": True
                }
        except Exception:
            pass
        return None
    
    async def _get_superate_hogar(self, cedula: str) -> Optional[Dict]:
        """Get household location from SUPÉRATE"""
        try:
            result = await self.gov_connector.call("superate", "get_hogar_location", {"cedula": cedula})
            if result.success and result.data:
                return {
                    "source": "superate_hogar",
                    "data": result.data,
                    "timestamp": result.timestamp,
                    "verified": result.data.get("verified", False)
                }
        except Exception:
            pass
        return None
    
    async def _get_ede_service(self, cedula: str) -> Optional[Dict]:
        """Get service address from EDE (tries all three)"""
        for ede in ["ede_norte", "ede_sur", "ede_este"]:
            try:
                result = await self.gov_connector.call(ede, "get_service_address", {"cedula": cedula})
                if result.success and result.data:
                    return {
                        "source": f"ede_service_{ede}",
                        "data": result.data,
                        "timestamp": result.timestamp,
                        "verified": True
                    }
            except Exception:
                continue
        return None
    
    async def _get_coraasan_service(self, cedula: str) -> Optional[Dict]:
        """Get service address from CORAASAN/CAASD/INAPA"""
        for api in ["coraasan", "caasd", "inapa"]:
            try:
                result = await self.gov_connector.call(api, "get_service_address", {"cedula": cedula})
                if result.success and result.data:
                    return {
                        "source": f"water_service_{api}",
                        "data": result.data,
                        "timestamp": result.timestamp,
                        "verified": True
                    }
            except Exception:
                continue
        return None
    
    async def _get_dgii_fiscal(self, cedula: str) -> Optional[Dict]:
        """Get fiscal domicile from DGII"""
        try:
            result = await self.gov_connector.call("dgii", "get_fiscal_domicile", {"cedula": cedula})
            if result.success and result.data:
                return {
                    "source": "dgii_fiscal",
                    "data": result.data,
                    "timestamp": result.timestamp,
                    "verified": True
                }
        except Exception:
            pass
        return None
    
    async def _get_quest_verified(self, cedula: str) -> Optional[Dict]:
        """Get last Quest-verified location"""
        try:
            result = await self.quest_service.get_last_verified_location(cedula)
            if result:
                return {
                    "source": "quest_verified",
                    "data": result,
                    "timestamp": datetime.utcnow(),
                    "verified": True
                }
        except Exception:
            pass
        return None
    
    def _resolve_conflicts(self, sources: Dict, delivery_type: DeliveryType, cedula: str) -> Optional[Dict]:
        """Priority-based conflict resolution with delivery-type weighting"""
        
        weights = self.TYPE_WEIGHTS.get(delivery_type, {})
        
        scored = []
        for source_name, source_result in sources.items():
            if isinstance(source_result, Exception) or not source_result:
                continue
            
            base_priority = len(self.SOURCE_PRIORITY) - self.SOURCE_PRIORITY.index(source_name) if source_name in self.SOURCE_PRIORITY else 0
            type_bonus = weights.get(source_name.split("_")[0], 0)  # e.g., "mivhed" from "mivhed_assignment"
            recency_score = self._calculate_recency_score(source_result["timestamp"])
            verification_score = 10 if source_result.get("verified") else 5
            
            total = base_priority + type_bonus + recency_score + verification_score
            scored.append((total, source_name, source_result))
        
        scored.sort(reverse=True, key=lambda x: x[0])
        return scored[0][2] if scored else None
    
    def _calculate_recency_score(self, timestamp: datetime) -> int:
        """Score based on recency (0-10)"""
        age_days = (datetime.utcnow() - timestamp).days
        if age_days <= 1: return 10
        if age_days <= 7: return 8
        if age_days <= 30: return 6
        if age_days <= 90: return 4
        if age_days <= 180: return 2
        return 0
    
    async def _enhance_with_community(self, cedula: str, resolved: Dict) -> ResolvedLocation:
        """Enhance with community references and GPS"""
        
        data = resolved["data"]
        source = resolved["source"]
        
        # Get community references for this location
        community_refs = await self._get_community_references(data.get("lat"), data.get("lng"), data.get("sector"))
        
        # Get designated neighbor
        designated_neighbor = await self._get_designated_neighbor(cedula)
        
        # Build delivery constraints
        constraints = self._build_delivery_constraints(data, community_refs)
        
        return ResolvedLocation(
            latitud=Decimal(str(data.get("lat", data.get("latitud", 0)))),
            longitud=Decimal(str(data.get("lng", data.get("longitud", 0)))),
            precision_metros=data.get("precision", data.get("precision_metros", 10)),
            nombre_completo=data.get("nombre", data.get("nombre_completo", "")),
            telefono=data.get("telefono", data.get("phone", "")),
            email=data.get("email"),
            provincia=data.get("provincia"),
            municipio=data.get("municipio"),
            sector=data.get("sector"),
            calle_principal=data.get("calle"),
            numero_casa=data.get("numero"),
            referencia_catastral=data.get("referencia_catastral"),
            community_references=community_refs,
            designated_neighbor=designated_neighbor,
            instrucciones_acceso=data.get("instrucciones_acceso"),
            codigo_acceso=data.get("codigo_acceso"),
            horarios_disponibles=data.get("horarios", []),
            requiere_autorizacion=data.get("requiere_autorizacion", False),
            fuente_principal=source,
            ultima_verificacion=resolved["timestamp"],
            verificado_por_quest=source == "quest_verified",
            quest_verificador_id=data.get("quest_verificador_id"),
            quest_verificacion_fecha=data.get("quest_verificacion_fecha"),
            confidence_score=Decimal(str(self._calculate_confidence(resolved))),
            delivery_constraints=constraints
        )
    
    def _calculate_confidence(self, resolved: Dict) -> float:
        """Calculate confidence score 0.0-1.0"""
        base = 0.5
        if resolved.get("verified"):
            base += 0.2
        if resolved["source"] in ["jce_cedula", "mivhed_assignment"]:
            base += 0.2
        elif resolved["source"] == "quest_verified":
            base += 0.3
        return min(base, 1.0)
    
    def _build_delivery_constraints(self, data: Dict, community_refs: List) -> Dict:
        """Build delivery constraints"""
        return {
            "requires_signature": data.get("requires_signature", True),
            "requires_id": data.get("requires_id", True),
            "allows_neighbor": data.get("allows_neighbor", True),
            "allows_pickup": data.get("allows_pickup", False),
            "time_windows": data.get("horarios", []),
            "special_instructions": data.get("instrucciones_especiales")
        }
    
    async def _get_community_references(self, lat: float, lng: float, sector: str) -> List[Dict]:
        """Get community reference points near location"""
        # Would query community reference database
        # For now, return empty
        return []
    
    async def _get_designated_neighbor(self, cedula: str) -> Optional[Dict]:
        """Get designated neighbor for delivery backup"""
        # Would query designated neighbor database
        return None


class QuestPreVerificationService:
    """Quest visitor confirms delivery location 24h before"""
    
    def __init__(self, quest_service: QuestService, address_engine: AddressResolutionEngine, trace_logger: TraceLogger):
        self.quest_service = quest_service
        self.address_engine = address_engine
        self.trace_logger = trace_logger
    
    async def schedule_pre_verification(self, delivery: Delivery) -> Optional[Dict]:
        """Schedule Quest pre-verification for delivery"""
        
        # Find Quest visitor in same territory
        quester = await self.quest_service.get_available_quester(
            territory=delivery.delivery_location.sector,
            date=delivery.scheduled_at - timedelta(days=1) if delivery.scheduled_at else None
        )
        
        if not quester:
            # Auto-assign nearest
            quester = await self.quest_service.assign_nearest_quester(delivery.delivery_location)
        
        if not quester:
            return None
        
        # Create verification task
        verification_data = {
            "quester_id": str(quester.id),
            "delivery_id": str(delivery.id),
            "location": {
                "lat": float(delivery.delivery_location.latitud),
                "lng": float(delivery.delivery_location.longitud),
                "address": delivery.delivery_location.instrucciones_acceso
            },
            "tasks": [
                "Confirm GPS coordinates match physical location",
                "Verify recipient lives at location",
                "Confirm access instructions accurate",
                "Verify designated neighbor available",
                "Photo: building entrance + street reference",
                "Note any changes (new construction, road work, etc.)"
            ],
            "scheduled_for": delivery.scheduled_at - timedelta(days=1) if delivery.scheduled_at else datetime.utcnow()
        }
        
        # Notify Quest visitor via Discord/WhatsApp
        await self._notify_quester(quester, verification_data)
        
        return verification_data
    
    async def process_verification_result(self, verification_result: Dict) -> Optional[ResolvedLocation]:
        """Update delivery location with Quest-verified data"""
        
        delivery_id = verification_result.get("delivery_id")
        delivery = await self._get_delivery(delivery_id)
        
        if not delivery:
            return None
        
        location = delivery.delivery_location
        
        # Update with verified data
        location.verificado_por_quest = True
        location.quest_verificador_id = uuid.UUID(verification_result["quester_id"])
        location.quest_verificacion_fecha = datetime.utcnow()
        location.latitud = Decimal(str(verification_result["gps_lat"]))
        location.longitud = Decimal(str(verification_result["gps_lng"]))
        location.precision_metros = verification_result.get("gps_precision", 5)
        location.community_references = verification_result.get("community_references", [])
        location.instrucciones_acceso = verification_result.get("instrucciones_acceso")
        location.confidence_score = Decimal("0.95")  # High confidence after Quest verification
        
        # Update delivery location version
        location.version += 1
        location.ultima_verificacion = datetime.utcnow()
        
        await self._save_location(location)
        
        # Log trace event
        await self.trace_logger.log_event(
            event_type=AuditEventType.DELIVERY_PRE_VERIFICATION,
            event_data={
                "delivery_id": delivery_id,
                "quester_id": verification_result["quester_id"],
                "gps_updated": True,
                "confidence": 0.95
            },
            actor_user_id=uuid.UUID(verification_result["quester_id"])
        )
        
        return location
    
    async def _notify_quester(self, quester: User, verification_data: Dict):
        """Notify Quest visitor via preferred channel"""
        # Would integrate with notification service
        pass
    
    async def _get_delivery(self, delivery_id: str) -> Optional[Delivery]:
        pass
    
    async def _save_location(self, location: DeliveryLocation):
        pass


class CommunityDeliveryNetwork:
    """When courier can't deliver → neighbor network activates"""
    
    def __init__(self, address_engine: AddressResolutionEngine, trace_logger: TraceLogger):
        self.address_engine = address_engine
        self.trace_logger = trace_logger
    
    async def attempt_neighbor_delivery(self, delivery: Delivery) -> Dict:
        """Attempt delivery via designated neighbor or mutual aid network"""
        
        location = delivery.delivery_location
        
        # 1. Try designated neighbor
        if location.designated_neighbor and location.designated_neighbor.get("verificado"):
            result = await self._deliver_to_neighbor(delivery, location.designated_neighbor)
            if result["success"]:
                return result
        
        # 2. Try mutual aid connections
        connections = await self._get_mutual_aid_connections(
            cedula=location.cedula_token,
            radius_km=0.5,
            min_trust=0.7
        )
        
        for conn in connections:
            result = await self._deliver_to_neighbor(delivery, conn)
            if result["success"]:
                return result
        
        # 3. Fallback to community pickup point
        return await self._defer_to_pickup_point(delivery)
    
    async def _deliver_to_neighbor(self, delivery: Delivery, neighbor: Dict) -> Dict:
        """Execute neighbor delivery with full traceability"""
        
        # Notify neighbor
        await self._notify_neighbor(neighbor, delivery)
        
        # Courier delivers to neighbor
        courier_result = await self._courier_deliver_to_address(
            lat=neighbor["lat"],
            lng=neighbor["lng"],
            recipient_name=neighbor["nombre"],
            package=delivery.package_description
        )
        
        if courier_result["success"]:
            # Track neighbor-to-recipient delivery
            await self.trace_logger.log_event(
                event_type=AuditEventType.DELIVERY_NEIGHBOR_CHAIN,
                event_data={
                    "delivery_id": str(delivery.id),
                    "courier_delivered_to": neighbor.get("cedula"),
                    "neighbor_confirmed": True,
                    "final_delivery_pending": True
                },
                actor_user_id=delivery.courier_id
            )
            
            return {
                "success": True,
                "delivered_to": "neighbor_chain",
                "neighbor": neighbor["nombre"],
                "chain_initiated": True
            }
        
        return {"success": False, "reason": "Courier delivery to neighbor failed"}
    
    async def _defer_to_pickup_point(self, delivery: Delivery) -> Dict:
        """Defer to nearest community pickup point"""
        
        location = delivery.delivery_location
        pickup = await self._find_nearest_pickup(
            lat=float(location.latitud),
            lng=float(location.longitud),
            sector=location.sector,
            package_size="medium"
        )
        
        if pickup:
            # Deliver to pickup point
            courier_result = await self._courier_deliver_to_pickup(pickup, delivery)
            
            if courier_result["success"]:
                # Notify recipient
                await self._notify_pickup_ready(delivery, pickup)
                
                await self.trace_logger.log_event(
                    event_type=AuditEventType.DELIVERY_PICKUP_POINT,
                    event_data={
                        "delivery_id": str(delivery.id),
                        "pickup_point_id": str(pickup.id),
                        "pickup_name": pickup.nombre,
                        "recipient_notified": True
                    },
                    actor_user_id=delivery.courier_id
                )
                
                return {
                    "success": True,
                    "delivered_to": "pickup_point",
                    "pickup_point": {"id": str(pickup.id), "nombre": pickup.nombre, "direccion": pickup.direccion_detallada}
                }
        
        return {"success": False, "reason": "No available pickup point"}
    
    async def _get_mutual_aid_connections(self, cedula: str, radius_km: float, min_trust: float) -> List[Dict]:
        """Get mutual aid connections in radius"""
        # Would query convivencia service
        return []
    
    async def _find_nearest_pickup(self, lat: float, lng: float, sector: str, package_size: str) -> Optional[PickupPoint]:
        """Find nearest active pickup point"""
        # Would query pickup point database with PostGIS
        return None
    
    async def _courier_deliver_to_address(self, lat: float, lng: float, recipient_name: str, package: str) -> Dict:
        """Courier delivers to GPS coordinates"""
        # Would integrate with courier system
        return {"success": True}
    
    async def _courier_deliver_to_pickup(self, pickup: PickupPoint, delivery: Delivery) -> Dict:
        return {"success": True}
    
    async def _notify_neighbor(self, neighbor: Dict, delivery: Delivery):
        pass
    
    async def _notify_pickup_ready(self, delivery: Delivery, pickup: PickupPoint):
        pass


class AddressSyncService:
    """Keep addresses current via government API webhooks/polling"""
    
    SYNC_SCHEDULE = {
        "jce_cedula": "daily",
        "mivhed_assignment": "hourly",
        "superate_hogar": "daily",
        "ede_service": "weekly",
        "coraasan_service": "weekly",
        "dgii_fiscal": "monthly",
        "quest_verified": "continuous"
    }
    
    def __init__(self, gov_connector: GovAPIConnectorManager, address_engine: AddressResolutionEngine, trace_logger: TraceLogger):
        self.gov_connector = gov_connector
        self.address_engine = address_engine
        self.trace_logger = trace_logger
    
    async def sync_all_sources(self, cedula: str) -> Dict:
        """Sync address from all government sources"""
        
        changes = []
        
        for source in self.SYNC_SCHEDULE:
            connector = getattr(self.gov_connector, f"{source}_connector", None)
            if not connector:
                continue
            
            try:
                method = getattr(connector, f"get_{source.replace('_', '')}_address", None)
                if not method:
                    continue
                
                new_data = await method(cedula)
                current = await self._get_current_address(cedula, source)
                
                if self._has_changed(current, new_data):
                    changes.append({
                        "source": source,
                        "old": current,
                        "new": new_data,
                        "detected_at": datetime.utcnow()
                    })
                    
                    await self._update_address(cedula, source, new_data)
                    
            except Exception as e:
                logger.error(f"Sync failed for {source}", error=str(e))
        
        # Re-resolve if changes
        if changes:
            await self.address_engine.resolve_delivery_location(cedula, DeliveryType.DOCUMENTS)
            await self._notify_pending_deliveries(cedula, changes)
        
        return {"cedula": cedula, "changes": changes}
    
    def _has_changed(self, old: Dict, new: Dict) -> bool:
        if not old or not new:
            return old != new
        # Compare key fields
        key_fields = ["lat", "lng", "provincia", "municipio", "sector", "calle", "numero"]
        return any(old.get(f) != new.get(f) for f in key_fields)
    
    async def _get_current_address(self, cedula: str, source: str) -> Dict:
        return {}
    
    async def _update_address(self, cedula: str, source: str, data: Dict):
        pass
    
    async def _notify_pending_deliveries(self, cedula: str, changes: List):
        pass