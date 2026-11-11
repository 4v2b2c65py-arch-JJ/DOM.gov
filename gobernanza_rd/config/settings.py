# Core Configuration for GobernanzaRD Platform
from functools import lru_cache
from typing import List, Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "GobernanzaRD"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = Field(default="dev-secret-change-in-production", min_length=32)
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/gobernanza_rd"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600
    
    # Local Models (Ollama, llama.cpp, vLLM)
    LOCAL_MODEL_ENABLED: bool = True
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLAMA_CPP_SERVER_URL: str = "http://localhost:8080"
    VLLM_BASE_URL: str = "http://localhost:8001"
    LOCAL_MODEL_TIMEOUT: int = 120
    
    # External AI Providers (fallback)
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    MISTRAL_API_KEY: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None
    
    # Model Configuration
    MODEL_FAMILIES: Dict[str, Dict[str, Any]] = {
        "constitutional": {
            "weight": 0.30,
            "models": [
                {"provider": "local", "model": "llama3.1:70b", "role": "primary_reasoner"},
                {"provider": "local", "model": "nemotron-3-ultra", "role": "validator"},
                {"provider": "anthropic", "model": "claude-opus-4", "role": "cross_check"},
                {"provider": "openai", "model": "o1-pro", "role": "adversarial"}
            ]
        },
        "economic": {
            "weight": 0.25,
            "models": [
                {"provider": "local", "model": "nemotron-3-ultra", "role": "primary_allocator"},
                {"provider": "local", "model": "llama3.1:70b", "role": "fairness_check"},
                {"provider": "mistral", "model": "large-2", "role": "efficiency_optimizer"},
                {"provider": "cohere", "model": "command-r-plus", "role": "distribution_validator"}
            ]
        },
        "social": {
            "weight": 0.20,
            "models": [
                {"provider": "local", "model": "llama3.1:70b", "role": "community_analyst"},
                {"provider": "local", "model": "mistral:7b", "role": "cultural_validator"},
                {"provider": "anthropic", "model": "claude-haiku-3.5", "role": "rapid_assessment"},
                {"provider": "google", "model": "gemini-2.5-flash", "role": "sentiment_check"}
            ]
        },
        "security": {
            "weight": 0.15,
            "models": [
                {"provider": "openai", "model": "o1-pro", "role": "threat_modeler"},
                {"provider": "anthropic", "model": "claude-opus-4", "role": "adversarial_tester"},
                {"provider": "google", "model": "gemini-2.5-pro", "role": "anomaly_detector"},
                {"provider": "local", "model": "dr-fraud-specialist", "role": "domain_expert"}
            ]
        },
        "arbitration": {
            "weight": 0.10,
            "models": [
                {"provider": "anthropic", "model": "claude-opus-4", "role": "chief_arbitrator"},
                {"provider": "openai", "model": "o1-pro", "role": "dissenting_opinion"},
                {"provider": "google", "model": "gemini-2.5-pro", "role": "precedent_analyst"},
                {"provider": "local", "model": "dr-constitutional-court-ai", "role": "dr_law_expert"}
            ]
        }
    }
    
    CONSENSUS_THRESHOLDS: Dict[str, Dict[str, Any]] = {
        "routine": {"threshold": 0.66, "families_required": 3},
        "significant": {"threshold": 0.75, "families_required": 4},
        "constitutional": {"threshold": 0.85, "families_required": 5},
        "emergency": {"threshold": 0.51, "families_required": 2, "timeout": 300}
    }
    
    # DR Government APIs
    DGII_BASE_URL: str = "https://api.dgii.gov.do/v1"
    DGII_CLIENT_ID: Optional[str] = None
    DGII_CLIENT_SECRET: Optional[str] = None
    
    SUPERATE_BASE_URL: str = "https://api.superate.gob.do/v1"
    SUPERATE_CLIENT_ID: Optional[str] = None
    SUPERATE_CLIENT_SECRET: Optional[str] = None
    
    ADESS_BASE_URL: str = "https://api.adess.gob.do/v1"
    ADESS_CLIENT_ID: Optional[str] = None
    ADESS_CLIENT_SECRET: Optional[str] = None
    
    EDE_NORTE_BASE_URL: str = "https://api.edenorte.com.do/v1"
    EDE_NORTE_API_KEY: Optional[str] = None
    
    EDE_SUR_BASE_URL: str = "https://api.edesur.com.do/v1"
    EDE_SUR_API_KEY: Optional[str] = None
    
    EDE_ESTE_BASE_URL: str = "https://api.edeeste.com.do/v1"
    EDE_ESTE_API_KEY: Optional[str] = None
    
    CORAASAN_BASE_URL: str = "https://api.coraasan.gob.do/v1"
    CORAASAN_API_KEY: Optional[str] = None
    
    CAASD_BASE_URL: str = "https://api.caasd.gob.do/v1"
    CAASD_API_KEY: Optional[str] = None
    
    INAPA_BASE_URL: str = "https://api.inapa.gob.do/v1"
    INAPA_API_KEY: Optional[str] = None
    
    MIVHED_BASE_URL: str = "https://api.mivhed.gob.do/v1"
    MIVHED_CLIENT_ID: Optional[str] = None
    MIVHED_CLIENT_SECRET: Optional[str] = None
    
    JCE_BASE_URL: str = "https://api.jce.gob.do/v1"
    JCE_CERT_PATH: Optional[str] = None
    JCE_CERT_PASSWORD: Optional[str] = None
    
    DGCP_BASE_URL: str = "https://api.dgcp.gob.do/v1"
    DGCP_CLIENT_ID: Optional[str] = None
    DGCP_CLIENT_SECRET: Optional[str] = None
    
    COE_BASE_URL: str = "https://api.coe.gob.do/v1"
    
    INDRHI_BASE_URL: str = "https://api.indrhi.gob.do/v1"
    INDRHI_API_KEY: Optional[str] = None
    
    BANCO_CENTRAL_BASE_URL: str = "https://api.bancentral.gov.do/v1"
    BANCO_CENTRAL_CLIENT_ID: Optional[str] = None
    BANCO_CENTRAL_CLIENT_SECRET: Optional[str] = None
    
    # DR Telecom
    INDOTEL_NP_API_URL: str = "https://np.indotel.gob.do/api"
    INDOTEL_NP_API_KEY: Optional[str] = None
    
    CLARO_SMS_API_URL: str = "https://api.claro.com.do/sms/v1"
    CLARO_SMS_TOKEN: Optional[str] = None
    
    ALTICE_SMS_API_URL: str = "https://api.altice.com.do/sms/v1"
    ALTICE_SMS_TOKEN: Optional[str] = None
    
    VIVA_SMS_API_URL: str = "https://api.viva.com.do/sms/v1"
    VIVA_SMS_TOKEN: Optional[str] = None
    
    # WhatsApp Business API
    WHATSAPP_BSP: str = "twilio"  # twilio, vonage, messagebird, gupshup, wati
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_WHATSAPP_NUMBER: Optional[str] = None
    
    VONAGE_API_KEY: Optional[str] = None
    VONAGE_API_SECRET: Optional[str] = None
    VONAGE_WHATSAPP_NUMBER: Optional[str] = None
    
    # Digital Wallets
    APPLE_PAY_MERCHANT_ID: Optional[str] = None
    APPLE_PAY_CERT_PATH: Optional[str] = None
    APPLE_PAY_KEY_PATH: Optional[str] = None
    
    GOOGLE_PAY_MERCHANT_ID: Optional[str] = None
    GOOGLE_PAY_GATEWAY: str = "braintree"
    GOOGLE_PAY_GATEWAY_MERCHANT_ID: Optional[str] = None
    
    # Payment Service Providers
    BRAINTREE_MERCHANT_ID: Optional[str] = None
    BRAINTREE_PUBLIC_KEY: Optional[str] = None
    BRAINTREE_PRIVATE_KEY: Optional[str] = None
    BRAINTREE_ENVIRONMENT: str = "sandbox"
    
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    MERCADOPAGO_ACCESS_TOKEN: Optional[str] = None
    MERCADOPAGO_PUBLIC_KEY: Optional[str] = None
    
    # Translation (NICT TexTra / Commercial)
    NICT_TEX_TRA_API_KEY: Optional[str] = None
    NICT_TEX_TRA_BASE_URL: str = "https://mt-auto-minhon-mlt.ucri.jgn-x.jp/api"
    GOOGLE_TRANSLATE_API_KEY: Optional[str] = None
    
    # Email (Magic Links)
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = False
    EMAIL_FROM: str = "noreply@gobierna.do"
    MAGIC_LINK_EXPIRY_MINUTES: int = 15
    MAGIC_LINK_DOMAIN: str = "localhost:8000"
    
    # Temp Email Domains (accepted)
    TEMP_EMAIL_DOMAINS: List[str] = [
        "10minutemail.com", "10minutemail.net", "guerrillamail.com",
        "tempmail.com", "temp-mail.org", "fakeinbox.com",
        "throwawaymail.com", "yopmail.com", "mailinator.com",
        "trashmail.com", "getnada.com", "dispostable.com"
    ]
    
    # Device Fingerprinting
    DEVICE_FINGERPRINT_SECRET: str = "dev-fingerprint-secret-change-in-production"
    DEVICE_FINGERPRINT_TTL_DAYS: int = 90
    
    # Fraud Detection
    FRAUD_RISK_THRESHOLDS: Dict[str, float] = {
        "allow": 0.3,
        "challenge": 0.5,
        "require_merit_link": 0.7,
        "require_biometric": 0.9,
        "block": 1.0
    }
    
    # Merit System
    MERIT_DAILY_ACTION_LIMITS: Dict[int, int] = {
        0: 5,    # Anonymous
        1: 20,   # Email Verified
        2: 100,  # Merit Linked
        3: 500,  # Biometric
        4: 2000, # Trusted
        5: -1    # Authorized (unlimited)
    }
    
    MERIT_MULTIPLIERS: Dict[int, float] = {
        0: 0.0,
        1: 1.0,
        2: 1.0,
        3: 1.5,
        4: 2.0,
        5: 3.0
    }
    
    # Identity Levels
    IDENTITY_LEVELS: Dict[int, str] = {
        0: "ANONYMOUS",
        1: "EMAIL_VERIFIED",
        2: "MERIT_LINKED",
        3: "BIOMETRIC",
        4: "TRUSTED",
        5: "AUTHORIZED"
    }
    
    # Central AI Fund
    CENTRAL_AI_FUND_WALLET: Optional[str] = None
    CENTRAL_AI_FUND_API_URL: str = "http://localhost:8002"
    
    # Audit Trail
    AUDIT_CHAIN_ALGORITHM: str = "FROST"
    AUDIT_CURVE: str = "secp256k1"
    AUDIT_ANCHORS: List[str] = [
        "dr_supreme_court",
        "un_oict",
        "icc",
        "bitcoin",
        "ethereum",
        "polygon"
    ]
    
    # FGA (Fundación de Gobernanza Algorítmica)
    FGA_ENABLED: bool = True
    FGA_FUNDING_PERCENTAGE: float = 0.005  # 0.5% of Fund yield
    FGA_REDRESS_FUND_PERCENTAGE: float = 0.01  # 1% of Fund yield
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    GRAFANA_ENABLED: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Rate Limiting
    RATE_LIMIT_DEFAULT: int = 100
    RATE_LIMIT_AUTH: int = 20
    RATE_LIMIT_PAYMENT: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()