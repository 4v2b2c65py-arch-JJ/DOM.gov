# Zero Shipping Address Issues System
## Address-Free Delivery via Government APIs + Geo-Location + Community Networks
### For Dominican Republic Governance Platform

---

## 1. PROBLEM ELIMINATION STRATEGY

| Traditional Problem | Our Solution |
|---------------------|--------------|
| User enters wrong address | **Zero manual entry** — auto-filled from JCE/MIVHED/SUPÉRATE |
| Address doesn't exist in maps | **Geo-coordinates + community reference** — GPS + "casa de Doña María, esquina colmado" |
| Courier can't find location | **Quest visitor pre-verification** — Quest visitor confirms location day before |
| No one home to receive | **Mutual aid neighbor network** — Designated neighbor + digital signature |
| Rural/informal settlements | **Geo-fenced delivery zones** + community pickup points |
| Address changes not updated | **Real-time gov API sync** — JCE/MIVHED/SUPÉRATE auto-update |

---

## 2. ADDRESS RESOLUTION ENGINE

### 2.1 Multi-Source Address Aggregator

```python
class AddressResolutionEngine:
    """
    Resolves delivery location WITHOUT user entering address
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
    
    async def resolve_delivery_location(self, cedula: str, 
                                        delivery_type: DeliveryType) -> DeliveryLocation:
        """Get verified delivery location from government sources"""
        
        # Parallel fetch from all sources
        tasks = {
            "jce": self.jce.get_domicilio(cedula),
            "mivhed": self.mivhed.get_assigned_address(cedula),
            "superate": self.superate.get_hogar_location(cedula),
            "ede": self.ede.get_service_address(cedula),
            "coraasan": self.coraasan.get_service_address(cedula),
            "dgii": self.dgii.get_fiscal_domicile(cedula),
            "quest": self.quest.get_last_verified_location(cedula)
        }
        
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        source_data = dict(zip(tasks.keys(), results))
        
        # Resolve conflicts using priority + recency + verification
        resolved = self._resolve_conflicts(source_data, delivery_type)
        
        # Enhance with geo-coordinates and community references
        enhanced = await self._enhance_with_geo(resolved)
        
        return enhanced
    
    def _resolve_conflicts(self, sources: Dict, delivery_type: DeliveryType) -> ResolvedAddress:
        """Priority-based conflict resolution with delivery-type weighting"""
        
        # Delivery-type specific priority adjustments
        type_weights = {
            DeliveryType.HOUSING_KEYS: {"mivhed": 10, "jce": 8, "quest": 9},
            DeliveryType.APPLIANCE: {"ede": 9, "coraasan": 8, "superate": 7, "quest": 8},
            DeliveryType.UTILITY_EQUIPMENT: {"ede": 10, "coraasan": 10, "jce": 6},
            DeliveryType.FOOD_PACKAGE: {"superate": 10, "quest": 9, "community": 8},
            DeliveryType.EMERGENCY_SUPPLIES: {"quest": 10, "community": 9, "jce": 7},
            DeliveryType.MUTUAL_AID: {"quest": 9, "community": 10, "superate": 7}
        }
        
        weights = type_weights.get(delivery_type, {})
        
        scored = []
        for source_name, data in sources.items():
            if isinstance(data, Exception) or not data:
                continue
            base_priority = len(self.SOURCE_PRIORITY) - self.SOURCE_PRIORITY.index(source_name) if source_name in self.SOURCE_PRIORITY else 0
            type_bonus = weights.get(source_name, 0)
            recency_score = self._calculate_recency_score(data.timestamp)
            verification_score = 10 if data.verified else 5
            
            total = base_priority + type_bonus + recency_score + verification_score
            scored.append((total, source_name, data))
        
        scored.sort(reverse=True, key=lambda x: x[0])
        return scored[0][2] if scored else None
```

### 2.2 Enhanced Location Object

```python
@dataclass
class DeliveryLocation:
    """Complete delivery location - no manual address needed"""
    
    # Core identification
    cedula: str
    nombre_completo: str
    telefono: str
    
    # Geo-coordinates (PRIMARY for courier)
    latitud: Decimal
    longitud: Decimal
    precision_metros: int  # GPS accuracy
    
    # Structured address (from gov APIs)
    provincia: str
    municipio: str
    sector: str
    calle_principal: str = None
    numero_casa: str = None
    referencia_catastral: str = None  # MIVHED catastro reference
    
    # Community references (for human navigation)
    referencias_comunitarias: List[CommunityReference] = field(default_factory=list)
    # e.g., "Esquina colmado 'El Buen Precio'", "Frente a escuela Juan Pablo Duarte"
    
    # Access instructions
    instrucciones_acceso: str = None  # "Portón azul, tocar timbre 2 veces"
    codigo_acceso: str = None  # Building/condo access code
    vecino_designado: DesignatedNeighbor = None  # Backup recipient
    
    # Verification metadata
    fuente_principal: str  # Which gov API provided this
    ultima_verificacion: datetime
    verificado_por_quest: bool = False
    quest_verificador_id: str = None
    quest_verificacion_fecha: datetime = None
    
    # Delivery constraints
    horarios_disponibles: List[TimeWindow] = field(default_factory=list)
    requiere_autorizacion: bool = False
    instrucciones_especiales: str = None

@dataclass
class CommunityReference:
    tipo: Literal["colmado", "iglesia", "escuela", "parada", "parque", "otro"]
    nombre: str
    distancia_metros: int
    direccion_cardinal: str  # "norte", "sur", "este", "oeste"

@dataclass
class DesignatedNeighbor:
    nombre: str
    telefono: str
    cedula: str  # For verification
    relacion: str  # "vecino", "familiar", "lider_comunitario"
    verificado: bool = False
```

---

## 3. DELIVERY EXECUTION SYSTEM

### 3.1 Courier App (Zero Address Entry)

```python
class CourierDeliveryApp:
    """
    Courier sees ONLY:
    - Map with GPS pin
    - Community references
    - Recipient name + phone
    - Access instructions
    - Designated neighbor (backup)
    NO manual address typing
    """
    
    async def get_delivery_route(self, courier_id: str, deliveries: List[DeliveryTask]) -> OptimizedRoute:
        """Optimize route using GPS coordinates only"""
        
        # All deliveries have lat/long - no geocoding needed
        waypoints = [
            {"lat": d.location.latitud, "lng": d.location.longitud, 
             "task_id": d.id, "priority": d.priority}
            for d in deliveries
        ]
        
        # Use OSRM/GraphHopper for routing
        route = await self.routing_engine.optimize(
            start=self.courier_location(courier_id),
            waypoints=waypoints,
            constraints={
                "time_windows": [d.location.horarios_disponibles for d in deliveries],
                "vehicle_capacity": self.courier_capacity(courier_id)
            }
        )
        
        return route
    
    async def execute_delivery(self, task: DeliveryTask, courier: Courier) -> DeliveryResult:
        """Execute with photo + GPS + digital signature"""
        
        # 1. Navigate to GPS coordinates
        await self.navigation.start(task.location.latitud, task.location.longitud)
        
        # 2. Verify location (GPS proximity check)
        if not await self._verify_proximity(courier.location, task.location):
            return DeliveryResult(success=False, reason="Location mismatch")
        
        # 3. Attempt recipient delivery
        recipient_result = await self._attempt_recipient_delivery(task)
        
        if not recipient_result.success:
            # 4. Fallback to designated neighbor
            neighbor_result = await self._attempt_neighbor_delivery(task)
            if neighbor_result.success:
                return DeliveryResult(
                    success=True, 
                    delivered_to="neighbor",
                    neighbor_name=task.location.vecino_designado.nombre,
                    photo=neighbor_result.photo,
                    gps=courier.location,
                    signature=neighbor_result.signature
                )
            
            # 5. Fallback to community pickup point
            pickup_result = await self._defer_to_pickup_point(task)
            return DeliveryResult(
                success=True,
                delivered_to="pickup_point",
                pickup_location=pickup_result.location,
                notification_sent=True
            )
        
        return DeliveryResult(
            success=True,
            delivered_to="recipient",
            photo=recipient_result.photo,
            gps=courier.location,
            signature=recipient_result.signature
        )

    async def _attempt_recipient_delivery(self, task: DeliveryTask) -> DeliveryAttempt:
        """Try to deliver to recipient directly"""
        
        # Call recipient
        call_result = await self.voice.call(task.location.telefono)
        
        if call_result.answered:
            # Verify identity (name confirmation)
            verified = await self._verify_recipient_identity(task.location.nombre_completo)
            
            if verified:
                # Photo evidence
                photo = await self.camera.capture(
                    metadata={"task_id": task.id, "gps": courier.location}
                )
                
                # Digital signature
                signature = await self.signature.capture(
                    prompt=f"Firma para recibir: {task.descripcion}"
                )
                
                return DeliveryAttempt(success=True, photo=photo, signature=signature)
        
        return DeliveryAttempt(success=False, reason="No answer / not verified")
```

### 3.2 Quest Pre-Verification (Day Before Delivery)

```python
class QuestDeliveryPreVerification:
    """
    Quest visitor confirms delivery location 24h before
    Eliminates "address not found" failures
    """
    
    async def schedule_pre_verification(self, delivery: DeliveryTask) -> PreVerificationResult:
        """Quest visitor visits day before to confirm"""
        
        # Find Quest visitor in same territory
        quester = await self.quest_engine.get_available_quester(
            territory=delivery.location.sector,
            date=delivery.scheduled_date - timedelta(days=1)
        )
        
        if not quester:
            # Auto-assign to nearest Quest visitor
            quester = await self.quest_engine.assign_nearest_quester(delivery.location)
        
        # Create verification task
        verification_task = QuestVerificationTask(
            quester_id=quester.id,
            delivery_id=delivery.id,
            location=delivery.location,
            tasks=[
                "Confirm GPS coordinates match physical location",
                "Verify recipient lives at location",
                "Confirm access instructions accurate",
                "Verify designated neighbor available",
                "Photo: building entrance + street reference",
                "Note any changes (new construction, road work, etc.)"
            ],
            scheduled_for=delivery.scheduled_date - timedelta(days=1)
        )
        
        # Notify Quest visitor via Discord
        await self.discord.notify_quest_verification(quester.discord_id, verification_task)
        
        return PreVerificationResult(
            quester_id=quester.id,
            scheduled_date=verification_task.scheduled_for,
            tasks=verification_task.tasks
        )
    
    async def process_verification_result(self, result: QuestVerificationInput) -> DeliveryLocation:
        """Update delivery location with Quest-verified data"""
        
        location = await self.address_engine.get_location(result.delivery_id)
        
        # Update with verified data
        location.verificado_por_quest = True
        location.quest_verificador_id = result.quester_id
        location.quest_verificacion_fecha = datetime.utcnow()
        location.latitud = result.gps_latitud
        location.longitud = result.gps_longitud
        location.precision_metros = result.gps_precision
        location.referencias_comunitarias = result.referencias_comunitarias
        location.instrucciones_acceso = result.instrucciones_acceso
        location.vecino_designado = result.vecino_designado
        
        # Save updated location
        await self.address_engine.update_location(location)
        
        # Notify delivery system
        await self.delivery_system.update_location(result.delivery_id, location)
        
        return location
```

---

## 4. COMMUNITY-BASED DELIVERY NETWORK

### 4.1 Mutual Aid Delivery (Neighbor-to-Neighbor)

```python
class CommunityDeliveryNetwork:
    """
    When courier can't deliver → neighbor network activates
    Built on Convivencia Limpia mutual aid relationships
    """
    
    async def activate_neighbor_delivery(self, delivery: DeliveryTask) -> DeliveryResult:
        """Activate community delivery chain"""
        
        # 1. Check designated neighbor first
        if delivery.location.vecino_designado and delivery.location.vecino_designado.verificado:
            return await self._deliver_to_neighbor(delivery, delivery.location.vecino_designado)
        
        # 2. Find mutual aid connections in same sector
        connections = await self.convivencia.get_mutual_aid_connections(
            cedula=delivery.location.cedula,
            radius_km=0.5,
            min_trust_level=TrustLevel.CONOCIDO
        )
        
        # 3. Filter for availability + verification
        available = []
        for conn in connections:
            neighbor = await self.merit_service.get_profile(conn.vecino_cedula)
            if neighbor.identity_level >= IdentityLevel.MERIT_LINKED:
                if await self._check_availability(neighbor, delivery.scheduled_date):
                    available.append(neighbor)
        
        # 4. Select best (highest trust + closest)
        if available:
            best = max(available, key=lambda n: (n.trust_score, -n.distance))
            return await self._deliver_to_neighbor(delivery, best)
        
        # 5. Fallback: community pickup point
        return await self._defer_to_community_pickup(delivery)
    
    async def _deliver_to_neighbor(self, delivery: DeliveryTask, neighbor: Profile) -> DeliveryResult:
        """Execute neighbor delivery with full traceability"""
        
        # Notify neighbor via Discord/WhatsApp
        await self.messaging.send(
            to=neighbor.telefono,
            template="neighbor_delivery_request",
            data={
                "recipient_name": delivery.location.nombre_completo,
                "item_description": delivery.descripcion,
                "pickup_location": "Courier will bring to your address",
                "delivery_deadline": delivery.scheduled_date + timedelta(hours=4)
            }
        )
        
        # Courier delivers to neighbor
        courier_result = await self.courier_app.deliver_to_address(
            lat=neighbor.location.latitud,
            lng=neighbor.location.longitud,
            recipient_name=neighbor.nombre_completo,
            package=delivery.package
        )
        
        if courier_result.success:
            # Neighbor confirms receipt + will deliver
            confirmation = await self._wait_for_neighbor_confirmation(neighbor, delivery)
            
            if confirmation:
                # Track neighbor-to-recipient delivery
                await self.trace_logger.log(TraceEvent(
                    event_type="community_delivery_chain",
                    original_delivery_id=delivery.id,
                    courier_delivered_to=neighbor.cedula,
                    neighbor_confirmed=confirmation.timestamp,
                    final_delivery_pending=True
                ))
                
                return DeliveryResult(
                    success=True,
                    delivered_to="neighbor_chain",
                    neighbor_cedula=neighbor.cedula,
                    chain_initiated=True
                )
        
        return DeliveryResult(success=False, reason="Neighbor delivery failed")
```

### 4.2 Community Pickup Points (Automated)

```python
class CommunityPickupNetwork:
    """Pre-registered, trusted pickup locations in every sector"""
    
    PICKUP_TYPES = {
        "colmado": {"hours": "6:00-22:00", "capacity": "small", "trust": "high"},
        "iglesia": {"hours": "8:00-18:00", "capacity": "medium", "trust": "high"},
        "escuela": {"hours": "7:00-16:00", "capacity": "large", "trust": "high"},
        "junta_vecinos": {"hours": "9:00-17:00", "capacity": "medium", "trust": "high"},
        "centro_comunal": {"hours": "8:00-20:00", "capacity": "large", "trust": "high"},
        "farmacia": {"hours": "7:00-22:00", "capacity": "small", "trust": "medium"}
    }
    
    async def get_nearest_pickup(self, location: DeliveryLocation, 
                                  package_size: str) -> PickupPoint:
        """Find optimal pickup point for failed delivery"""
        
        # Query registered pickup points in sector
        points = await self.db.query("""
            SELECT * FROM pickup_points 
            WHERE sector = $1 AND active = true
            AND capacity >= $2
            ORDER BY ST_Distance(geom, ST_MakePoint($3, $4))
            LIMIT 5
        """, location.sector, package_size, location.longitud, location.latitud)
        
        # Score by: distance, hours match, trust, capacity
        scored = []
        for p in points:
            score = self._score_pickup_point(p, location, package_size)
            scored.append((score, p))
        
        scored.sort(reverse=True)
        return scored[0][1] if scored else None
    
    async def register_pickup_delivery(self, delivery: DeliveryTask, 
                                        pickup: PickupPoint, courier: Courier) -> DeliveryResult:
        """Deliver to pickup point + notify recipient"""
        
        # Courier delivers to pickup point
        result = await self.courier_app.deliver_to_pickup(pickup, delivery.package)
        
        if result.success:
            # Notify recipient via multiple channels
            await self._notify_recipient_pickup(delivery, pickup)
            
            # Log for traceability
            await self.trace_logger.log(TraceEvent(
                event_type="pickup_point_delivery",
                delivery_id=delivery.id,
                pickup_point_id=pickup.id,
                pickup_name=pickup.nombre,
                courier_id=courier.id,
                gps=courier.location,
                photo=result.photo,
                notification_sent=True
            ))
            
            return DeliveryResult(
                success=True,
                delivered_to="pickup_point",
                pickup_point=pickup,
                recipient_notified=True
            )
        
        return result
```

---

## 5. ADDRESS SYNC & MAINTENANCE

### 5.1 Real-Time Government API Sync

```python
class AddressSyncService:
    """Keep addresses current via government API webhooks/polling"""
    
    SYNC_SCHEDULE = {
        "jce_cedula": "daily",       # Civil registry changes
        "mivhed_assignment": "hourly", # New housing assignments
        "superate_hogar": "daily",   # Household composition changes
        "ede_service": "weekly",     # Utility service changes
        "coraasan_service": "weekly",
        "dgii_fiscal": "monthly",    # Tax domicile changes
        "quest_verified": "continuous" # Real-time from Quest visits
    }
    
    async def sync_all_sources(self, cedula: str) -> SyncResult:
        """Sync address from all government sources"""
        
        changes = []
        
        for source, schedule in self.SYNC_SCHEDULE.items():
            connector = getattr(self, f"{source}_connector")
            try:
                new_data = await connector.get_address(cedula)
                current = await self.address_store.get_current(cedula, source)
                
                if self._has_changed(current, new_data):
                    changes.append(AddressChange(
                        source=source,
                        old=current,
                        new=new_data,
                        detected_at=datetime.utcnow()
                    ))
                    
                    # Update store
                    await self.address_store.update(cedula, source, new_data)
                    
            except Exception as e:
                await self.logger.error(f"Sync failed for {source}: {e}")
        
        # Re-resolve canonical address if any changes
        if changes:
            await self.address_engine.re_resolve(cedula)
            
            # Notify affected deliveries
            await self._notify_pending_deliveries(cedula, changes)
        
        return SyncResult(cedula=cedula, changes=changes)
    
    async def webhook_jce_change(self, payload: JCEWebhookPayload):
        """Real-time JCE address change notification"""
        await self.sync_all_sources(payload.cedula)
```

### 5.2 Quest-Driven Address Corrections

```python
# Quest visitors continuously improve address data
class QuestAddressCorrection:
    """Quest visitors report address discrepancies during visits"""
    
    async def report_discrepancy(self, quester_id: str, cedula: str, 
                                  observed: ObservedLocation) -> CorrectionResult:
        """Quest visitor reports: 'GPS says X but house is actually Y'"""
        
        # Log discrepancy
        discrepancy = AddressDiscrepancy(
            cedula=cedula,
            reported_by=quester_id,
            system_location=await self.address_engine.get_location(cedula),
            observed_location=observed,
            reported_at=datetime.utcnow()
        )
        
        await self.discrepancy_log.insert(discrepancy)
        
        # Auto-correct if high confidence (Quest visitor + GPS + photo)
        if observed.confidence >= 0.8:
            await self.address_engine.apply_correction(cedula, observed)
            
            # Notify all systems
            await self._broadcast_correction(cedula, observed)
            
            return CorrectionResult(applied=True, confidence=observed.confidence)
        
        # Queue for manual review
        await self.review_queue.add(discrepancy)
        return CorrectionResult(applied=False, queued_for_review=True)
```

---

## 6. DELIVERY TYPES & WORKFLOWS

### 6.1 Delivery Type Configurations

```python
DELIVERY_CONFIGS = {
    DeliveryType.HOUSING_KEYS: {
        "requires_recipient": True,
        "requires_id_verification": True,
        "allows_neighbor": False,
        "allows_pickup": False,
        "pre_verification_required": True,
        "courier_training": "secure_handoff",
        "insurance": "high"
    },
    DeliveryType.APPLIANCE: {
        "requires_recipient": True,
        "requires_id_verification": True,
        "allows_neighbor": True,  # With authorization
        "allows_pickup": False,
        "pre_verification_required": True,
        "installation_included": True,
        "courier_training": "appliance_handling"
    },
    DeliveryType.UTILITY_EQUIPMENT: {
        "requires_recipient": False,
        "allows_neighbor": True,
        "allows_pickup": True,
        "pre_verification_required": False,
        "technician_required": True
    },
    DeliveryType.FOOD_PACKAGE: {
        "requires_recipient": False,
        "allows_neighbor": True,
        "allows_pickup": True,
        "pre_verification_required": False,
        "temperature_controlled": True
    },
    DeliveryType.EMERGENCY_SUPPLIES: {
        "requires_recipient": False,
        "allows_neighbor": True,
        "allows_pickup": True,
        "pre_verification_required": False,
        "priority": "critical",
        "community_distribution": True
    },
    DeliveryType.MUTUAL_AID: {
        "requires_recipient": False,
        "allows_neighbor": True,
        "allows_pickup": True,
        "peer_to_peer": True,
        "no_courier_needed": True
    }
}
```

### 6.2 End-to-End Flow Example: Appliance Delivery

```
1. MERIT THRESHOLD REACHED
   └─ User qualifies for "nevera" via Selecting Front

2. AUTO-RESOLVE LOCATION
   └─ AddressEngine resolves from JCE + MIVHED + Quest (last week's visit)
   └─ Result: GPS + "Esquina colmado Doña Rosa, portón verde"

3. SCHEDULE DELIVERY
   ├─ Quest pre-verification scheduled (day before)
   ├─ Courier route optimized via GPS
   └─ Delivery window: 9:00-12:00 (user's preferred from profile)

4. DAY BEFORE: QUEST PRE-VERIFICATION
   ├─ Quest visitor confirms GPS accurate
   ├─ Photos entrance + street reference
   ├─ Confirms recipient home + neighbor available
   └─ Updates location if needed

5. DELIVERY DAY
   ├─ Courier navigates to GPS (no address typing)
   ├─ Calls recipient → verified by name
   ├─ Photo: appliance in situ + recipient signature
   ├─ Installation technician follows (separate task)
   └─ Trace log: complete chain from merit → delivery → installation

6. POST-DELIVERY
   ├─ Merit: +50 for responsible receipt
   ├─ Quest visitor: +25 for pre-verification
   ├─ Courier: performance metric updated
   └─ Address confidence score increased
```

---

## 7. INTEGRATION WITH EXISTING SYSTEMS

### 7.1 Merit System
```python
# Delivery performance affects merit
DELIVERY_MERIT_EVENTS = {
    "successful_receipt": 10,
    "pre_verification_by_quester": 25,
    "neighbor_delivery_completed": 15,
    "pickup_point_collection": 5,
    "address_correction_reported": 20,
    "community_pickup_volunteer": 30
}
```

### 7.2 Central AI Fund
```python
# Fund pays for delivery logistics
DELIVERY_COSTS = {
    "standard_courier": 150,      # DOP
    "appliance_installation": 500,
    "emergency_express": 300,
    "community_pickup": 0,        # Volunteer
    "quest_pre_verification": 75  # Stipend
}
```

### 7.3 Convivencia Limpia
```python
# Mutual aid network = delivery network
# Trust levels determine neighbor delivery eligibility
# Quest visits = address verification layer
```

---

## 8. API SPECIFICATIONS

### 8.1 Delivery Endpoints

```yaml
# POST /deliveries/create
request:
  delivery_type: string
  recipient_cedula: string
  package_details: object
  preferred_window: TimeWindow (optional)
response:
  delivery_id: string
  location: DeliveryLocation (auto-resolved)
  pre_verification_scheduled: boolean
  estimated_delivery: datetime

# GET /deliveries/{id}/tracking
response:
  status: enum [pending, pre_verifying, scheduled, en_route, delivered, failed]
  location: DeliveryLocation
  courier: CourierInfo (if en_route)
  pre_verification: QuestVerificationResult
  chain: DeliveryChain (if neighbor/pickup)

# POST /deliveries/{id}/confirm-receipt
request:
  signature: string (base64)
  photo: string (base64, optional)
  gps: {lat, lng}
response:
  success: boolean
  merit_earned: integer
  trace_id: string

# POST /addresses/correction
request:
  cedula: string
  observed: ObservedLocation
  reporter_id: string (quester)
response:
  applied: boolean
  confidence: float
  new_location: DeliveryLocation
```

---

## 9. IMPLEMENTATION CHECKLIST

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **1. Address Engine** | 2 weeks | Multi-source resolver, conflict resolution, geo-enhancement |
| **2. Courier App** | 2 weeks | GPS-only navigation, photo/signature, neighbor fallback |
| **3. Quest Pre-Verification** | 1 week | Scheduling, verification tasks, location updates |
| **4. Community Network** | 2 weeks | Neighbor delivery, pickup points, mutual aid integration |
| **5. Sync Service** | 1 week | Gov API polling, webhooks, Quest corrections |
| **6. Integration** | 1 week | Merit, Central AI Fund, Convivencia, Quest |
| **7. Testing** | 1 week | Pilot in 3 sectors, measure failure rate < 1% |

---

*File: F:\managements\zero_shipping_address_system.md*
*Version: 1.0 | Date: 2026-11-10*