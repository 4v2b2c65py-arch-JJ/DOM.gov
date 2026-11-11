# DOM.gov - GobernanzaRD Platform

Dominican Republic governance platform implementing Japanese Society 5.0 / Agile Governance models with DR-specific adaptations.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DOM.gov Platform                         │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (Vercel)          │  Backend (Local/Docker)          │
│  ┌─────────────────────┐    │  ┌─────────────────────────────┐ │
│  │ Next.js App         │◄───│  │ Python FastAPI (8000)       │ │
│  │ - Citizen Portal    │    │  │ - Auth / Identity           │ │
│  │ - Admin Dashboard   │    │  │ - Merits / Payments         │ │
│  │ - Quest / Veeduría  │    │  │ - Governance / Consensus    │ │
│  │ - Airport Easy Pass │    │  │ - Audit Trail               │ │
│  └─────────────────────┘    │  └─────────────────────────────┘ │
│                             │  ┌─────────────────────────────┐ │
│                             │  │ Node.js Telecaster (3001)   │ │
│                             │  │ - WhatsApp / SMS / USSD     │ │
│                             │  │ - Push / WebSocket          │ │
│                             │  │ - Airport Clearance         │ │
│                             │  └─────────────────────────────┘ │
│                             │  ┌─────────────────────────────┐ │
│                             │  │ Local AI Models             │ │
│                             │  │ - Ollama (llama3.1:70b)     │ │
│                             │  │ - llama.cpp                 │ │
│                             │  │ - vLLM (Nemotron-3-Ultra)   │ │
│                             │  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Features

### Core Governance
- **CARACOL Dual-Loop**: Quarterly strategic + daily tactical governance
- **6-Layer Framework**: Technical → Organizational → Soft Law → Hard Law → Market → Social Norm
- **5 Domains**: Anti-corruption, Environment, Infrastructure, Employment, Participation
- **Multi-Model AI Consensus**: 5 heterogeneous model families with adversarial validation
- **FGA Legal Entity**: Fundación de Gobernanza Algorítmica with constitutional mandate

### Identity & Access
- **Progressive Identity**: Level 0 (Anonymous) → Level 5 (Authorized/Sovereign)
- **Capability-Gated**: Each level unlocks specific governance capabilities
- **Biometric Integration**: Level 3+ for high-trust operations

### Merit Economy
- **Accumulation**: Quest participation, Veeduría filing, Mutual aid
- **Selecting Front**: Utility/Housing/Appliance redemption via Central AI Fund
- **Auto-Filled Payments**: 8 Government APIs (DGII, SUPÉRATE, ADESS, EDE, CORAASAN, MIVHED, JCE, INFOTEP)

### Zero-Address Delivery
- **GPS + Community References**: Colmado, Iglesia, Escuela from JCE/MIVHED/SUPÉRATE/EDE/CORAASAN
- **Quest Pre-Verification**: Community-based address validation
- **Neighbor Chain Fallback**: Community pickup points

### Digital Wallets
- **Apple Pay / Google Pay**: Unified processor interface
- **DR Bank Support**: 10 major banks with BIN prefix detection

### Telecom Integration
- **DR Carriers**: Claro (45%), Altice (35%), Viva (18%)
- **Number Portability**: INDOTEL lookup with caching
- **WhatsApp BSP**: Twilio/Vonage/MessageBird/Gupshup
- **USSD**: *462# (*GOB#) via Africa's Talking
- **Cell Broadcast**: Emergency alerts via INDOTEL

### Airport Easy Pass
- **6 Clearance Grades**: Standard → PreCheck → Trusted → Biometric → Executive → Sovereign
- **5 DR Airports**: SDQ, PUJ, STI, LRM, AZS
- **QR/NFC Verification**: Offline-capable validation
- **eGate Integration**: Biometric gates at major airports

### Anti-Faction Guarantees
- **5 Model Families**: Constitutional, Economic, Social, Security, Arbitration
- **Provider Diversity**: Max 35% per provider, 90-day rotation
- **Circuit Breakers**: Automatic intervention on anomalies
- **Fairness Monitor**: Real-time equity metrics across 5 domains
- **Audit Trail**: Hash-chained logs anchored to Supreme Court, UN OICT, ICC, Bitcoin, Ethereum, Polygon

## Quick Start

### Local Development (Docker)
```bash
# Clone and configure
git clone https://github.com/4v2b2c65py-arch-JJ/DOM.gov.git
cd DOM.gov

# Create .env with required secrets
cp .env.example .env
# Edit .env with your API keys

# Start full stack
docker-compose up -d

# Access services
# Frontend: http://localhost:3000 (after Vercel deploy)
# Python API: http://localhost:8000
# Telecaster: http://localhost:3001
# Grafana: http://localhost:3000 (admin/gobernanza_grafana_2024)
# Prometheus: http://localhost:9090
```

### Environment Variables
```bash
# Required for production
POSTGRES_PASSWORD=secure_password
JWT_SECRET=your_jwt_secret
PYTHON_API_KEY=python_backend_key

# Telecom
NP_API_KEY=indotel_np_key
CLARO_USERNAME=xxx
CLARO_PASSWORD=xxx
ALTICE_API_KEY=xxx
VIVA_API_KEY=xxx
TWILIO_ACCOUNT_SID=xxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_FROM_NUMBER=xxx

# WhatsApp
WHATSAPP_VERIFY_TOKEN=xxx

# USSD
AT_USERNAME=xxx
AT_API_KEY=xxx

# Digital Wallets
APPLE_PAY_MERCHANT_ID=xxx
GOOGLE_PAY_MERCHANT_ID=xxx

# Airport
AIRPORT_QR_SECRET=xxx
DGII_API_URL=https://api.dgii.gob.do
JCE_API_URL=https://api.jce.gob.do

# Monitoring
GRAFANA_PASSWORD=secure_password
```

## Project Structure

```
DOM.gov/
├── gobernanza_rd/              # Python FastAPI Backend
│   ├── app/                    # FastAPI application
│   ├── models/                 # SQLAlchemy models
│   ├── consensus/              # Multi-model consensus engine
│   ├── auth/                   # Magic link auth, progressive identity
│   ├── payments/               # Auto-fill payments, wallet service
│   ├── address/                # Zero-address delivery resolution
│   ├── telecom/                # DR telecom integration
│   ├── governance/             # Anti-faction, FGA, circuit breakers
│   ├── local_models/           # Ollama, llama.cpp, vLLM runners
│   └── Dockerfile.python
│
├── node-telecaster/            # Node.js Communication Service
│   ├── src/
│   │   ├── services/           # Broadcast, Alert, Notification, WS, Airport
│   │   ├── routes/             # API endpoints
│   │   ├── utils/              # Logger, Redis, BullMQ
│   │   ├── config.js           # All configuration
│   │   └── index.js            # Entry point
│   └── Dockerfile
│
├── docker-compose.yml          # Full stack orchestration
├── .github/workflows/          # CI/CD pipelines
└── README.md
```

## API Endpoints

### Python Backend (8000)
```
POST   /api/auth/magic-link           # Request magic link
POST   /api/auth/verify               # Verify magic link
GET    /api/users/me                  # Current user profile
POST   /api/merits/earn               # Earn merits
GET    /api/merits/balance            # Check merit balance
POST   /api/payments/initiate         # Initiate auto-filled payment
POST   /api/payments/confirm          # Confirm payment
GET    /api/quests/assigned           # Get assigned quests
POST   /api/quests/pre-verify         # Pre-verify delivery
POST   /api/veeduria/file             # File veeduría report
POST   /api/governance/consensus      # Request consensus decision
GET    /api/audit/trail               # Get audit trail
```

### Telecaster (3001)
```
POST   /api/auth/token                # Get JWT for WebSocket
POST   /api/broadcast                 # Send broadcast
POST   /api/broadcast/emergency       # Emergency broadcast
POST   /api/alerts                    # Create alert
POST   /api/alerts/emergency          # Emergency alert (hurricane/flood/etc)
POST   /api/notifications             # Send notification
GET    /api/websocket/state           # WebSocket service state
POST   /api/airport/clearance         # Request airport clearance
POST   /api/airport/clearance/:id/checkpoint  # Process checkpoint
POST   /api/airport/verify/qr         # Verify QR code
WS     /ws                            # WebSocket connection
```

## Deployment

### Vercel (Frontend)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy frontend
cd frontend  # (create Next.js app in separate repo or subfolder)
vercel --prod
```

### Local/Server (Backend)
```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or manual
cd gobernanza_rd && pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port 8000
cd node-telecaster && npm install && node src/index.js
```

## Governance Model

### Identity Levels
| Level | Name | Capabilities |
|-------|------|--------------|
| 0 | Anonymous | Public info, basic browsing |
| 1 | Email Verified | Notifications, airport pre-check |
| 2 | Merit Linked | Selecting Front, Quest, Veeduría, trusted traveler |
| 3 | Biometric | Biometric auth, eGate, governance voting |
| 4 | Trusted | VIP airport, FGA oversight, policy proposal |
| 5 | Authorized | Sovereign protocol, constitutional action |

### Merit Thresholds (Selecting Front)
- **Utility**: 1,000 merits (electricity, water, internet)
- **Housing**: 50,000 merits (MIVHED subsidy)
- **Appliance**: 5,000 merits (INFOTEP certified)

## License

MIT License - See LICENSE file for details.

## Contact

- **Repository**: https://github.com/4v2b2c65py-arch-JJ/DOM.gov
- **Issues**: GitHub Issues
- **Governance**: FGA (Fundación de Gobernanza Algorítmica)