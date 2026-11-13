# DOM.gov - GobernanzaRD Platform

Dominican Republic governance platform implementing Japanese Society 5.0 / Agile Governance models with DR-specific adaptations.

## 🌐 Live Portal

**Live now:** https://frontend-amber-alpha-84.vercel.app

The citizen portal is deployed on Vercel (Vue 3 + Vite). The Python FastAPI backend, Telecaster service, and local AI models run separately as described below.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DOM.gov Platform                         │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (Vercel)           │  Backend (Local/Docker)          │
│  ┌─────────────────────┐     │  ┌─────────────────────────────┐ │
│  │ Vue 3 + Vite        │◄───►│  │ Python FastAPI (8000)       │ │
│  │ - Citizen Portal    │     │  │ - Auth / Identity           │ │
│  │ - Admin Dashboard   │     │  │ - Merits / Payments         │ │
│  │ - Quest / Veeduría  │     │  │ - Governance / Consensus    │ │
│  │ - Airport Easy Pass │     │  │ - Audit Trail               │ │
│  └─────────────────────┘     │  └─────────────────────────────┘ │
│                              │  ┌─────────────────────────────┐ │
│                              │  │ Node.js Telecaster (3001)   │ │
│                              │  │ - WhatsApp / SMS / USSD     │ │
│                              │  │ - Push / WebSocket          │ │
│                              │  │ - Airport Clearance         │ │
│                              │  └─────────────────────────────┘ │
│                              │  ┌─────────────────────────────┐ │
│                              │  │ Local AI Models             │ │
│                              │  │ - Ollama (llama3.1:70b)     │ │
│                              │  │ - llama.cpp                 │ │
│                              │  │ - vLLM (Nemotron-3-Ultra)   │ │
│                              │  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## ✨ Features

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

### Cédula Identity & Banking
- **Cédula validation**: Accepts 11-12 digits (formatted `3-3-3-2`, e.g. `001-1234567-8`)
- **Tokenized storage**: Cédula is stored as a hashed token, never in plain text
- **Progressive identity**: Cédula verification unlocks Level 2 (Méritos Vinculados)
- **Bank linking**: 10 Dominican banks (Banreservas, Popular, BHD, Scotiabank, BDI, Santa Cruz, Caribe, Cibao, La Nacional, La Vega Real)

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

## 🚀 Quick Start

### 1. Frontend (Vercel) - Live Deployment

**Production URL:** https://frontend-amber-alpha-84.vercel.app

```bash
# Option A: One-click deploy (recommended)
# Click "Deploy with Vercel" button below or visit:
# https://vercel.com/new/clone?repository-url=https://github.com/4v2b2c65py-arch-JJ/DOM.gov&project-name=dom-gov&repository-name=DOM.gov

# Option B: Vercel CLI
cd frontend
npm i -g vercel
vercel login
vercel --prod
```

**Required Vercel Environment Variables:**
```bash
VITE_API_URL=https://api.dom.gov          # Your Python backend URL
VITE_WS_URL=wss://ws.dom.gov/ws           # Your Telecaster WebSocket URL
VITE_TELECASTER_URL=https://ws.dom.gov    # Your Telecaster REST URL
```

### 2. Backend (Local/Server) - Docker

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
# Frontend: https://frontend-amber-alpha-84.vercel.app
# Python API: http://localhost:8000
# Telecaster: http://localhost:3001
# Grafana: http://localhost:3000 (admin/gobernanza_grafana_2024)
# Prometheus: http://localhost:9090
```

### 3. Local Development

```bash
# Frontend
cd frontend
npm install
npm run dev          # http://localhost:5173

# Backend (requires Docker for databases)
docker-compose up -d postgres redis ollama llama-cpp vllm
cd gobernanza_rd
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Telecaster
cd node-telecaster
npm install
npm run dev          # http://localhost:3001
```

## 📁 Project Structure

```
DOM.gov/
├── frontend/                    # Vue 3 + Vite (Vercel)
│   ├── src/
│   │   ├── api/                 # API client
│   │   ├── components/          # Header, Footer, UI components
│   │   ├── stores/              # Pinia stores (auth, merits, airport)
│   │   ├── views/               # Pages (Home, Dashboard, Merits, Airport, etc.)
│   │   ├── router/              # Vue Router
│   │   ├── App.vue              # Root component
│   │   └── main.ts              # Entry point
│   ├── public/                  # Static assets (manifest, favicon)
│   ├── tailwind.config.js       # Tailwind CSS config
│   ├── vercel.json              # Vercel deployment config
│   └── package.json
│
├── gobernanza_rd/               # Python FastAPI Backend
│   ├── app/                     # FastAPI application
│   ├── models/                  # SQLAlchemy models
│   ├── consensus/               # Multi-model consensus engine
│   ├── auth/                    # Magic link auth, progressive identity
│   ├── payments/                # Auto-fill payments, wallet service
│   ├── address/                 # Zero-address delivery resolution
│   ├── telecom/                 # DR telecom integration
│   ├── governance/              # Anti-faction, FGA, circuit breakers
│   ├── local_models/            # Ollama, llama.cpp, vLLM runners
│   └── Dockerfile.python
│
├── node-telecaster/             # Node.js Communication Service
│   ├── src/
│   │   ├── services/            # Broadcast, Alert, Notification, WS, Airport
│   │   ├── routes/              # API endpoints
│   │   ├── utils/               # Logger, Redis, BullMQ
│   │   ├── config.js            # All configuration
│   │   └── index.js             # Entry point
│   └── Dockerfile
│
├── docker-compose.yml           # Full stack orchestration
├── .github/workflows/           # CI/CD pipelines
└── README.md
```

## 🔧 Environment Variables

### Frontend (.env.local for local, Vercel dashboard for production)
```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:3001/ws
VITE_TELECASTER_URL=http://localhost:3001
VITE_APP_NAME=DOM.gov
VITE_APP_VERSION=1.0.0
```

### Backend (.env)
```bash
# Database
POSTGRES_PASSWORD=secure_password
DATABASE_URL=postgresql+asyncpg://gobernanza:password@localhost:5432/gobernanza_rd

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET=your_jwt_secret_change_in_production
PYTHON_API_KEY=python_backend_key

# Local AI Models
OLLAMA_URL=http://localhost:11434
LLAMA_CPP_URL=http://localhost:8080
VLLM_URL=http://localhost:8000

# Telecom (DR)
NP_API_KEY=indotel_np_key
CLARO_USERNAME=xxx
CLARO_PASSWORD=xxx
ALTICE_API_KEY=xxx
VIVA_API_KEY=xxx
TWILIO_ACCOUNT_SID=xxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_FROM_NUMBER=xxx
TWILIO_WHATSAPP_FROM=xxx
WHATSAPP_VERIFY_TOKEN=xxx
AT_USERNAME=xxx
AT_API_KEY=xxx

# Digital Wallets
APPLE_PAY_MERCHANT_ID=xxx
GOOGLE_PAY_MERCHANT_ID=xxx

# Airport
AIRPORT_QR_SECRET=xxx
DGII_API_URL=https://api.dgii.gob.do
JCE_API_URL=https://api.jce.gob.do
MIGRATION_API_URL=https://api.migracion.gob.do

# Monitoring
GRAFANA_PASSWORD=secure_password
```

## 🌐 Deployment

### Vercel (Frontend)
1. Connect GitHub repo to Vercel
2. Set Framework Preset: **Vite**
3. Build Command: `npm run build`
4. Output Directory: `dist`
5. Add Environment Variables (see above)
4. Deploy

### Custom Domain
```bash
# In Vercel dashboard → Settings → Domains
# Add: dom.gov, www.dom.gov, api.dom.gov, ws.dom.gov

# DNS Records (at your registrar)
# Type    Name    Value
# A       @       76.76.21.21          # Vercel IP
# CNAME   www     cname.vercel-dns.com
# CNAME   api     your-server.com      # Your backend server
# CNAME   ws      your-server.com      # Your backend server
```

### Backend Server (VPS/EC2/DigitalOcean)
```bash
# 1. Provision server (Ubuntu 22.04+, 4GB+ RAM, 50GB+ SSD)
# 2. Install Docker & Docker Compose
# 3. Clone repo and configure .env
# 4. Run docker-compose up -d
# 5. Setup Nginx reverse proxy with SSL (Let's Encrypt)
# 6. Configure firewall (ufw allow 80,443,22)

# Nginx config example:
server {
    listen 80;
    server_name api.dom.gov ws.dom.gov;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.dom.gov;
    ssl_certificate /etc/letsencrypt/live/api.dom.gov/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.dom.gov/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 443 ssl http2;
    server_name ws.dom.gov;
    ssl_certificate /etc/letsencrypt/live/ws.dom.gov/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ws.dom.gov/privkey.pem;
    
    location /ws {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
    
    location / {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔌 API Endpoints

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

## 🏛️ Governance Model

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

## 📄 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Contact

- **Repository**: https://github.com/4v2b2c65py-arch-JJ/DOM.gov
- **Issues**: GitHub Issues
- **Governance**: FGA (Fundación de Gobernanza Algorítmica)
- **Email**: soporte@dom.gov

---

**Built with ❤️ for República Dominicana** 🇩🇴

*Society 5.0 • Anti-Facción • Meritocracia • Identidad Soberana*