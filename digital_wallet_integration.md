# Apple Pay & Google Pay Integration
## Digital Wallet Payments for Dominican Republic Governance Platform
### Seamless integration with existing minimal-info payment system

---

## 1. DESIGN PRINCIPLES

| Principle | Implementation |
|-----------|----------------|
| **Zero additional friction** | User selects Apple/Google Pay → biometric auth → done |
| **Same auto-fill engine** | Government APIs populate amount, recipient, metadata |
| **Unified traceability** | Same hash-chained audit log as other payments |
| **Merit-integrated** | Digital wallet payments earn same merit rewards |
| **Offline-capable** | Works with cached payment methods when offline |
| **DR-specific cards** | Supports local cards (Banreservas, Popular, BHD, Scotia, etc.) |

---

## 2. ARCHITECTURE

### 2.1 Payment Flow Comparison

```
TRADITIONAL CARD          APPLE PAY / GOOGLE PAY
─────────────────         ──────────────────────
Enter card number         Select wallet
Enter expiry              FaceID / TouchID / Fingerprint
Enter CVV                 Done
Enter billing address     (Auto-filled from gov APIs)
Enter name                (Auto-filled from merit profile)
Submit                    → Central AI Fund → Gov APIs
```

### 2.2 Integration Points

```python
class DigitalWalletPaymentGateway:
    """
    Unified gateway for Apple Pay + Google Pay
    Routes to: Central AI Fund → Government APIs (EDE, CORAASAN, ADESS, MIVHED)
    """
    
    SUPPORTED_NETWORKS = {
        "visa": {"apple_pay": True, "google_pay": True, "dr_banks": ["Banreservas", "Popular", "BHD", "Scotia", "Banesco", "Caribe", "Ademi", "Promerica"]},
        "mastercard": {"apple_pay": True, "google_pay": True, "dr_banks": ["Banreservas", "Popular", "BHD", "Scotia", "Banesco", "Caribe", "Ademi", "Promerica"]},
        "amex": {"apple_pay": True, "google_pay": True, "dr_banks": ["Popular", "BHD"]},
        "discover": {"apple_pay": True, "google_pay": False, "dr_banks": []},
        "unionpay": {"apple_pay": True, "google_pay": True, "dr_banks": ["Banreservas"]},
        "jcb": {"apple_pay": True, "google_pay": True, "dr_banks": []}
    }
    
    # Dominican Republic specific
    DR_CARD_BINS = {
        "456789": "Banreservas Visa",
        "456790": "Banreservas Mastercard",
        "512345": "Popular Mastercard",
        "523456": "BHD Mastercard",
        "534567": "Scotia Mastercard",
        "545678": "Banesco Mastercard",
        "556789": "Caribe Mastercard",
        "567890": "Ademi Mastercard",
        "578901": "Promerica Mastercard",
        "498765": "Banreservas Visa Débito",
        "487654": "Popular Visa Débito"
    }
```

---

## 3. APPLE PAY INTEGRATION

### 3.1 Server-Side (Payment Processing)

```python
class ApplePayProcessor:
    """
    Processes Apple Pay payments via Payment Service Provider (PSP)
    Supported PSPs in DR: PayPal/Braintree, Stripe, MercadoPago, 2Checkout, PayU
    """
    
    def __init__(self, config: ApplePayConfig):
        self.config = config
        self.psp = self._init_psp(config.psp_provider)
        self.merchant_id = config.merchant_id
        self.certificate = config.merchant_certificate
    
    async def process_payment(self, request: ApplePayPaymentRequest) -> PaymentResult:
        """
        1. Validate Apple Pay token
        2. Decrypt payment data
        3. Route to Central AI Fund
        4. Execute via government APIs
        """
        
        # 1. Verify Apple Pay session
        session_valid = await self._verify_apple_pay_session(request.session_data)
        if not session_valid:
            return PaymentResult(success=False, reason="Invalid Apple Pay session")
        
        # 2. Decrypt payment token
        payment_data = await self._decrypt_payment_token(
            request.payment_token,
            request.payment_method
        )
        
        # 3. Extract card info (tokenized)
        card_info = self._extract_card_info(payment_data)
        
        # 4. Verify DR bank support
        if not self._is_dr_bank_supported(card_info):
            return PaymentResult(success=False, reason="Card issuer not supported in DR")
        
        # 5. Build payment with auto-fill
        auto_filled = await self.auto_fill_engine.build_payment(
            payment_type=request.payment_type,
            user_session=request.user_session,
            provided={"digital_wallet": "apple_pay", "card_token": card_info.token}
        )
        
        # 6. Fraud check
        risk = await self.fraud_detector.assess_digital_wallet_payment(
            request.user_session, auto_filled, "apple_pay"
        )
        if risk.blocked:
            return PaymentResult(success=False, reason="Fraud check failed")
        
        # 7. Execute via Central AI Fund
        result = await self.central_ai_fund.execute(auto_filled)
        
        # 8. Trace log
        await self.trace_logger.log(TraceEvent(
            event_type="digital_wallet_payment",
            wallet_type="apple_pay",
            payment_id=result.payment_id,
            card_token=card_info.token,
            card_network=card_info.network,
            card_issuer=card_info.issuer,
            amount=auto_filled["monto"],
            session_id=request.user_session.id,
            biometric_verified=True,
            timestamp=datetime.utcnow()
        ))
        
        return result
    
    def _extract_card_info(self, payment_data: dict) -> CardInfo:
        """Extract tokenized card info from Apple Pay payment data"""
        # Apple Pay returns tokenized data - no raw PAN
        return CardInfo(
            token=payment_data["applicationData"],
            network=payment_data["paymentMethod"]["network"],  # visa, mastercard, amex
            type=payment_data["paymentMethod"]["type"],  # debit, credit, prepaid
            issuer=self._identify_issuer(payment_data["paymentMethod"]["displayName"]),
            last4=payment_data["paymentMethod"]["displayName"][-4:],
            device_account_number=payment_data["token"]["transactionIdentifier"]
        )
```

### 3.2 Client-Side (iOS/macOS/Safari)

```swift
// iOS/macOS Implementation
import PassKit

class ApplePayManager: NSObject, PKPaymentAuthorizationControllerDelegate {
    
    let merchantIdentifier = "merchant.gob.do.gobernanza"
    let supportedNetworks: [PKPaymentNetwork] = [.visa, .masterCard, .amex, .discover, .unionPay, .JCB]
    let merchantCapabilities: PKMerchantCapability = [.capability3DS, .capabilityDebit, .capabilityCredit]
    
    func presentPayment(for paymentRequest: GovernancePaymentRequest) {
        let request = PKPaymentRequest()
        request.merchantIdentifier = merchantIdentifier
        request.supportedNetworks = supportedNetworks
        request.merchantCapabilities = merchantCapabilities
        request.countryCode = "DO"
        request.currencyCode = "DOP"
        
        // Amount auto-filled from government APIs
        request.paymentSummaryItems = [
            PKPaymentSummaryItem(label: paymentRequest.description, amount: NSDecimalNumber(string: paymentRequest.amount)),
            PKPaymentSummaryItem(label: "Gobierno de RD", amount: NSDecimalNumber(string: paymentRequest.amount))
        ]
        
        // Required billing contact fields (auto-filled)
        request.requiredBillingContactFields = [.name, .phoneNumber, .emailAddress, .postalAddress]
        
        // Shipping contact NOT needed - we use Quest-verified GPS location
        // request.requiredShippingContactFields = []  // Empty!
        
        let controller = PKPaymentAuthorizationController(paymentRequest: request)
        controller.delegate = self
        controller.present(completion: nil)
    }
    
    func paymentAuthorizationController(_ controller: PKPaymentAuthorizationController,
                                         didAuthorizePayment payment: PKPayment,
                                         handler completion: @escaping (PKPaymentAuthorizationResult) -> Void) {
        
        // Send token to backend
        let token = payment.token
        let paymentData = [
            "token": token.paymentData,
            "paymentMethod": [
                "network": token.paymentMethod.network?.rawValue ?? "",
                "type": token.paymentMethod.type.rawValue,
                "displayName": token.paymentMethod.displayName ?? ""
            ],
            "transactionIdentifier": token.transactionIdentifier
        ]
        
        // Call backend API
        Task {
            let result = await backend.processApplePay(paymentData, paymentRequest)
            completion(PKPaymentAuthorizationResult(status: result.success ? .success : .failure, errors: nil))
        }
    }
}
```

### 3.3 Web (Safari) - Apple Pay JS API

```javascript
// Frontend: Apple Pay on Web
class ApplePayWeb {
    constructor() {
        this.session = null;
        this.merchantId = 'merchant.gob.do.gobernanza';
        this.supportedNetworks = ['visa', 'mastercard', 'amex', 'discover', 'unionpay', 'jcb'];
    }
    
    async canMakePayments() {
        if (!window.ApplePaySession) return false;
        return ApplePaySession.canMakePaymentsWithActiveCard(this.merchantId);
    }
    
    async startPayment(paymentRequest) {
        // 1. Create session
        this.session = new ApplePaySession(3, this.buildPaymentRequest(paymentRequest));
        
        // 2. Handle events
        this.session.onvalidatemerchant = this.validateMerchant.bind(this);
        this.session.onpaymentauthorized = this.paymentAuthorized.bind(this);
        this.session.onpaymentmethodselected = this.paymentMethodSelected.bind(this);
        this.session.onshippingcontactselected = this.shippingContactSelected.bind(this);
        this.session.oncancel = () => this.cleanup();
        
        // 3. Begin
        this.session.begin();
    }
    
    buildPaymentRequest(request) {
        return {
            countryCode: 'DO',
            currencyCode: 'DOP',
            supportedNetworks: this.supportedNetworks,
            merchantCapabilities: ['supports3DS', 'supportsDebit', 'supportsCredit'],
            total: {
                label: 'Gobierno de RD',
                amount: request.amount,
                type: 'final'
            },
            lineItems: [
                { label: request.description, amount: request.amount, type: 'final' }
            ],
            requiredBillingContactFields: ['name', 'phone', 'email', 'postalAddress'],
            // NO shipping contact - we use Quest-verified location
        };
    }
    
    async validateMerchant(event) {
        // Call backend to get merchant session
        const merchantSession = await fetch('/api/apple-pay/merchant-session', {
            method: 'POST',
            body: JSON.stringify({ validationURL: event.validationURL })
        });
        this.session.completeMerchantValidation(await merchantSession.json());
    }
    
    async paymentAuthorized(event) {
        // Send payment token to backend
        const result = await fetch('/api/payments/apple-pay', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                payment_token: event.payment.token,
                payment_method: event.payment.paymentMethod,
                payment_type: this.currentRequest.type,
                session_id: this.currentSessionId
            })
        });
        
        const response = await result.json();
        this.session.completePayment(response.success ? ApplePaySession.STATUS_SUCCESS : ApplePaySession.STATUS_FAILURE);
    }
}
```

---

## 4. GOOGLE PAY INTEGRATION

### 4.1 Server-Side

```python
class GooglePayProcessor:
    """
    Processes Google Pay payments via PSP
    Uses Google Pay API v2 with gateway tokenization
    """
    
    def __init__(self, config: GooglePayConfig):
        self.config = config
        self.gateway = config.gateway  # "braintree", "stripe", "mercadopago", etc.
        self.gateway_merchant_id = config.gateway_merchant_id
    
    async def process_payment(self, request: GooglePayPaymentRequest) -> PaymentResult:
        """
        1. Validate Google Pay token
        2. Verify signature
        3. Extract payment method
        4. Route to Central AI Fund
        """
        
        # 1. Parse payment token
        payment_token = json.loads(request.payment_token)
        
        # 2. Verify signature (Google Pay uses JWS)
        if not await self._verify_google_pay_signature(payment_token):
            return PaymentResult(success=False, reason="Invalid signature")
        
        # 3. Decrypt if using DIRECT tokenization
        if self.config.tokenization == "DIRECT":
            payment_data = await self._decrypt_google_pay_token(payment_token)
        else:
            # GATEWAY tokenization - PSP handles decryption
            payment_data = payment_token
        
        # 4. Extract card info
        card_info = self._extract_card_info(payment_data)
        
        # 5. Verify DR bank support
        if not self._is_dr_bank_supported(card_info):
            return PaymentResult(success=False, reason="Card issuer not supported in DR")
        
        # 6. Build payment with auto-fill
        auto_filled = await self.auto_fill_engine.build_payment(
            payment_type=request.payment_type,
            user_session=request.user_session,
            provided={"digital_wallet": "google_pay", "card_token": card_info.token}
        )
        
        # 7. Fraud check
        risk = await self.fraud_detector.assess_digital_wallet_payment(
            request.user_session, auto_filled, "google_pay"
        )
        if risk.blocked:
            return PaymentResult(success=False, reason="Fraud check failed")
        
        # 8. Execute via Central AI Fund
        result = await self.central_ai_fund.execute(auto_filled)
        
        # 9. Trace log
        await self.trace_logger.log(TraceEvent(
            event_type="digital_wallet_payment",
            wallet_type="google_pay",
            payment_id=result.payment_id,
            card_token=card_info.token,
            card_network=card_info.network,
            card_issuer=card_info.issuer,
            amount=auto_filled["monto"],
            session_id=request.user_session.id,
            biometric_verified=payment_data.get("authMethod") == "CRYPTOGRAM_3DS",
            timestamp=datetime.utcnow()
        ))
        
        return result
```

### 4.2 Client-Side (Android/Chrome)

```kotlin
// Android Implementation
class GooglePayManager(private val context: Context) {
    
    private val paymentsClient = PaymentsClient.create(
        context,
        WalletOptions.Builder()
            .setEnvironment(WalletConstants.ENVIRONMENT_PRODUCTION)
            .build()
    )
    
    fun requestPayment(paymentRequest: GovernancePaymentRequest, callback: PaymentCallback) {
        val request = buildPaymentDataRequest(paymentRequest)
        
        val task = paymentsClient.loadPaymentData(request)
        task.addOnCompleteListener { task ->
            if (task.isSuccessful) {
                val paymentData = task.result
                // Send to backend
                backend.processGooglePay(paymentData, paymentRequest, callback)
            } else {
                callback.onError(task.exception)
            }
        }
    }
    
    private fun buildPaymentDataRequest(request: GovernancePaymentRequest): PaymentDataRequest {
        return PaymentDataRequest.Builder()
            .setTransactionInfo(TransactionInfo.Builder()
                .setTotalPrice(request.amount)
                .setTotalPriceStatus(WalletConstants.TOTAL_PRICE_FINAL)
                .setCurrencyCode("DOP")
                .setCountryCode("DO")
                .build())
            .addAllowedPaymentMethod(buildCardPaymentMethod())
            .setMerchantInfo(MerchantInfo.Builder()
                .setMerchantName("Gobierno de RD")
                .setMerchantId(config.merchantId)
                .build())
            .setShippingAddressRequired(false)  // We use Quest-verified GPS
            .setBillingAddressRequired(true)
            .setBillingAddressFormat(WalletConstants.BILLING_ADDRESS_FORMAT_FULL)
            .setEmailRequired(true)
            .setPhoneNumberRequired(true)
            .build()
    }
    
    private fun buildCardPaymentMethod(): JSONObject {
        return JSONObject().apply {
            put("type", "CARD")
            put("parameters", JSONObject().apply {
                put("allowedAuthMethods", JSONArray().put("PAN_ONLY").put("CRYPTOGRAM_3DS"))
                put("allowedCardNetworks", JSONArray().put("VISA").put("MASTERCARD").put("AMEX").put("DISCOVER").put("JCB").put("UNIONPAY"))
                put("billingAddressRequired", true)
                put("billingAddressParameters", JSONObject().put("format", "FULL"))
            })
            put("tokenizationSpecification", JSONObject().apply {
                put("type", "PAYMENT_GATEWAY")
                put("parameters", JSONObject().apply {
                    put("gateway", "braintree")  // or stripe, mercadopago, etc.
                    put("gatewayMerchantId", config.gatewayMerchantId)
                })
            })
        }
    }
}
```

### 4.3 Web - Google Pay API

```javascript
// Frontend: Google Pay on Web
class GooglePayWeb {
    constructor() {
        this.paymentsClient = new google.payments.api.PaymentsClient({
            environment: 'PRODUCTION'
        });
    }
    
    async isReadyToPay() {
        const request = this.getIsReadyToPayRequest();
        const response = await this.paymentsClient.isReadyToPay(request);
        return response.result;
    }
    
    async startPayment(paymentRequest) {
        const paymentDataRequest = this.getPaymentDataRequest(paymentRequest);
        
        try {
            const paymentData = await this.paymentsClient.loadPaymentData(paymentDataRequest);
            // Send to backend
            const result = await fetch('/api/payments/google-pay', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    payment_token: JSON.stringify(paymentData.paymentMethodData.tokenizationData.token),
                    payment_method: paymentData.paymentMethodData.info,
                    payment_type: paymentRequest.type,
                    session_id: this.currentSessionId
                })
            });
            return await result.json();
        } catch (error) {
            if (error.statusCode !== 'CANCELED') {
                throw error;
            }
        }
    }
    
    getPaymentDataRequest(request) {
        return {
            apiVersion: 2,
            apiVersionMinor: 0,
            allowedPaymentMethods: [{
                type: 'CARD',
                parameters: {
                    allowedAuthMethods: ['PAN_ONLY', 'CRYPTOGRAM_3DS'],
                    allowedCardNetworks: ['VISA', 'MASTERCARD', 'AMEX', 'DISCOVER', 'JCB', 'UNIONPAY'],
                    billingAddressRequired: true,
                    billingAddressParameters: { format: 'FULL' }
                },
                tokenizationSpecification: {
                    type: 'PAYMENT_GATEWAY',
                    parameters: {
                        gateway: 'braintree',
                        gatewayMerchantId: 'your_merchant_id'
                    }
                }
            }],
            merchantInfo: {
                merchantId: 'merchant_id_from_google',
                merchantName: 'Gobierno de RD'
            },
            transactionInfo: {
                totalPriceStatus: 'FINAL',
                totalPrice: request.amount,
                currencyCode: 'DOP',
                countryCode: 'DO'
            },
            // NO shipping address - Quest-verified GPS
            emailRequired: true,
            phoneNumberRequired: true
        };
    }
}
```

---

## 5. UNIFIED DIGITAL WALLET SERVICE

### 5.1 Abstraction Layer

```python
class DigitalWalletService:
    """
    Unified interface for Apple Pay + Google Pay
    Automatically detects best available option
    """
    
    def __init__(self, config):
        self.apple_pay = ApplePayProcessor(config.apple_pay) if config.apple_pay.enabled else None
        self.google_pay = GooglePayProcessor(config.google_pay) if config.google_pay.enabled else None
        self.auto_fill = PaymentAutoFillEngine()
        self.fraud = FraudDetector()
        self.trace = TraceLogger()
        self.fund = CentralAIFundExecutor()
    
    async def get_available_wallets(self, session: Session, platform: Platform) -> List[WalletOption]:
        """Detect which wallets user can use"""
        
        options = []
        
        if platform in [Platform.IOS, Platform.MACOS, Platform.SAFARI]:
            if self.apple_pay and await self.apple_pay.can_user_pay(session):
                options.append(WalletOption(
                    type="apple_pay",
                    label="Apple Pay",
                    icon="apple_pay",
                    supported_cards=await self._get_user_cards(session, "apple_pay")
                ))
        
        if platform in [Platform.ANDROID, Platform.CHROME, Platform.WEB]:
            if self.google_pay and await self.google_pay.can_user_pay(session):
                options.append(WalletOption(
                    type="google_pay",
                    label="Google Pay",
                    icon="google_pay",
                    supported_cards=await self._get_user_cards(session, "google_pay")
                ))
        
        return options
    
    async def process_payment(self, request: DigitalWalletPaymentRequest) -> PaymentResult:
        """Route to correct processor"""
        
        if request.wallet_type == "apple_pay":
            return await self.apple_pay.process_payment(request.apple_pay_request)
        elif request.wallet_type == "google_pay":
            return await self.google_pay.process_payment(request.google_pay_request)
        else:
            return PaymentResult(success=False, reason="Unsupported wallet type")
```

### 5.2 Frontend Wallet Selector

```jsx
// React Component: Wallet Payment Button
function WalletPaymentButton({ paymentRequest, onSuccess, onError }) {
    const [availableWallets, setAvailableWallets] = useState([]);
    const [selectedWallet, setSelectedWallet] = useState(null);
    
    useEffect(() => {
        detectWallets();
    }, []);
    
    const detectWallets = async () => {
        const platform = getPlatform(); // 'ios', 'android', 'web'
        const response = await fetch('/api/wallets/available', {
            method: 'POST',
            body: JSON.stringify({ platform, session_id: getSessionId() })
        });
        const wallets = await response.json();
        setAvailableWallets(wallets);
    };
    
    const handleWalletPayment = async (wallet) => {
        setSelectedWallet(wallet);
        
        try {
            let result;
            if (wallet.type === 'apple_pay') {
                result = await applePayWeb.startPayment(paymentRequest);
            } else if (wallet.type === 'google_pay') {
                result = await googlePayWeb.startPayment(paymentRequest);
            }
            
            if (result.success) {
                onSuccess(result);
                // Merit notification
                showMeritEarned(result.merit_earned);
            } else {
                onError(result.reason);
            }
        } catch (err) {
            onError(err.message);
        }
    };
    
    return (
        <div className="wallet-payment-options">
            {availableWallets.map(wallet => (
                <button
                    key={wallet.type}
                    onClick={() => handleWalletPayment(wallet)}
                    className="wallet-button"
                    disabled={selectedWallet !== null}
                >
                    <img src={wallet.icon} alt={wallet.label} />
                    <span>Pagar con {wallet.label}</span>
                    {wallet.supported_cards.length > 0 && (
                        <span className="cards">
                            {wallet.supported_cards.map(c => <CardBadge key={c} brand={c} />)}
                        </span>
                    )}
                </button>
            ))}
        </div>
    );
}
```

---

## 6. DOMINICAN REPUBLIC SPECIFIC CONFIGURATION

### 6.1 Supported Local Cards

```python
DR_DIGITAL_WALLET_CARDS = {
    "Banreservas": {
        "visa_credit": {"bin_ranges": ["456789", "456790"], "apple_pay": True, "google_pay": True},
        "visa_debit": {"bin_ranges": ["498765"], "apple_pay": True, "google_pay": True},
        "mastercard_credit": {"bin_ranges": ["556789"], "apple_pay": True, "google_pay": True},
        "mastercard_debit": {"bin_ranges": ["556790"], "apple_pay": True, "google_pay": True}
    },
    "Banco Popular": {
        "visa_credit": {"bin_ranges": ["487654"], "apple_pay": True, "google_pay": True},
        "visa_debit": {"bin_ranges": ["487655"], "apple_pay": True, "google_pay": True},
        "mastercard_credit": {"bin_ranges": ["512345"], "apple_pay": True, "google_pay": True},
        "mastercard_debit": {"bin_ranges": ["512346"], "apple_pay": True, "google_pay": True}
    },
    "BHD León": {
        "mastercard_credit": {"bin_ranges": ["523456"], "apple_pay": True, "google_pay": True},
        "mastercard_debit": {"bin_ranges": ["523457"], "apple_pay": True, "google_pay": True}
    },
    "Scotiabank": {
        "mastercard_credit": {"bin_ranges": ["534567"], "apple_pay": True, "google_pay": True},
        "visa_credit": {"bin_ranges": ["434567"], "apple_pay": True, "google_pay": True}
    },
    "Banesco": {
        "mastercard_credit": {"bin_ranges": ["545678"], "apple_pay": True, "google_pay": True}
    },
    "Banco Caribe": {
        "mastercard_credit": {"bin_ranges": ["556789"], "apple_pay": True, "google_pay": True}
    },
    "Banco Ademi": {
        "mastercard_credit": {"bin_ranges": ["567890"], "apple_pay": True, "google_pay": True}
    },
    "Banco Promerica": {
        "mastercard_credit": {"bin_ranges": ["578901"], "apple_pay": True, "google_pay": True}
    }
}
```

### 6.2 PSP Configuration for DR

```python
DR_PSP_CONFIG = {
    "braintree": {
        "supported": True,
        "apple_pay": True,
        "google_pay": True,
        "local_acquiring": True,  # Processes DR-issued cards locally
        "currencies": ["DOP", "USD"],
        "merchant_setup": "Requires DR entity or international"
    },
    "stripe": {
        "supported": True,
        "apple_pay": True,
        "google_pay": True,
        "local_acquiring": False,  # International processing
        "currencies": ["DOP", "USD"],
        "merchant_setup": "Atlas or international entity"
    },
    "mercadopago": {
        "supported": True,
        "apple_pay": True,
        "google_pay": True,
        "local_acquiring": True,  # Strong in LatAm
        "currencies": ["DOP"],
        "merchant_setup": "Local DR account"
    },
    "payu": {
        "supported": True,
        "apple_pay": True,
        "google_pay": True,
        "local_acquiring": True,
        "currencies": ["DOP"],
        "merchant_setup": "Local DR account"
    },
    "2checkout": {
        "supported": True,
        "apple_pay": True,
        "google_pay": True,
        "local_acquiring": False,
        "currencies": ["DOP", "USD"],
        "merchant_setup": "International"
    }
}
```

---

## 7. INTEGRATION WITH EXISTING SYSTEMS

### 7.1 Merit System Integration

```python
# Digital wallet payments earn same merit as other methods
DIGITAL_WALLET_MERIT = {
    "utility_payment": 10,      # Same as bank transfer
    "housing_subsidy": 0,       # Government to citizen
    "merit_reward": 0,          # System to citizen
    "quest_stipend": 0,         # System to quester
    "mutual_aid_sent": 15,      # Citizen to citizen
    "mutual_aid_received": 5,   # Receiving aid
    "emergency_relief": 0       # Government to citizen
}

# Bonus for digital adoption (first 3 payments)
DIGITAL_ADOPTION_BONUS = {
    "first_apple_pay": 25,
    "first_google_pay": 25,
    "wallet_diversity": 10  # Using both
}
```

### 7.2 Central AI Fund Integration

```python
# Fund executes digital wallet payments same as others
class CentralAIFundExecutor:
    async def execute_digital_wallet(self, payment: AutoFilledPayment) -> PaymentResult:
        # Route to correct government API
        executor = self.executors[payment.type]
        
        # Add digital wallet metadata
        payment.metadata.update({
            "payment_method": "digital_wallet",
            "wallet_type": payment.wallet_type,
            "card_token": payment.card_token,
            "biometric_verified": True
        })
        
        return await executor.execute(payment)
```

### 7.3 Traceability (Same as All Payments)

```python
# Digital wallet payments fully traceable
TRACE_EVENT = TraceEvent(
    event_type="payment_executed",
    payment_method="digital_wallet",
    wallet_type="apple_pay|google_pay",
    card_network="visa|mastercard|amex",
    card_issuer="Banreservas|Popular|BHD|...",
    card_last4="1234",  # Tokenized, not real PAN
    device_account_number="token_ref",
    biometric_verified=True,
    amount=1500.00,
    government_api="EDE|CORAASAN|ADESS|MIVHED",
    api_response={"transaction_id": "txn_123", "status": "approved"},
    merit_earned=10,
    hash_chain_link="previous_hash..."
)
```

---

## 8. SECURITY & COMPLIANCE

### 8.1 Data Handling

| Data | Apple Pay | Google Pay | Stored? |
|------|-----------|------------|---------|
| PAN (card number) | Never received | Never received | No |
| Device Account Number | Token reference | Token reference | Hash only |
| Cryptogram | Per-transaction | Per-transaction | No |
| Billing contact | Name, phone, email | Name, phone, email | Encrypted |
| Shipping address | NOT REQUESTED | NOT REQUESTED | N/A |
| Biometric data | On device only | On device only | Never |

### 8.2 PCI DSS Compliance

- **SAQ A-EP** eligible (no card data touches our servers)
- Tokenization handled by PSP + Apple/Google
- Only encrypted billing contact stored
- Trace logs contain only token references

### 8.3 Ley 172-13 (Data Protection)

- Minimal personal data collected
- Encryption at rest (AES-256)
- Tokenization of all identifiers
- Right to deletion supported

---

## 9. API SPECIFICATIONS

### 9.1 Wallet Detection

```yaml
# POST /api/wallets/available
request:
  platform: "ios" | "android" | "web" | "macos" | "chrome" | "safari"
  session_id: string
response:
  wallets:
    - type: "apple_pay" | "google_pay"
      label: string
      icon: string
      supported_cards: ["visa", "mastercard", "amex"]
      can_pay: boolean
```

### 9.2 Apple Pay Endpoints

```yaml
# POST /api/apple-pay/merchant-session
request:
  validationURL: string
response:
  merchant_session: object (opaque)

# POST /api/payments/apple-pay
request:
  payment_token: object (PKPaymentToken)
  payment_method: object
  payment_type: string
  session_id: string
response:
  success: boolean
  payment_id: string
  trace_id: string
  receipt: object
  merit_earned: integer
```

### 9.3 Google Pay Endpoints

```yaml
# POST /api/payments/google-pay
request:
  payment_token: string (JWS)
  payment_method: object
  payment_type: string
  session_id: string
response:
  success: boolean
  payment_id: string
  trace_id: string
  receipt: object
  merit_earned: integer
```

---

## 10. IMPLEMENTATION CHECKLIST

| Phase | Duration | Tasks |
|-------|----------|-------|
| **1. PSP Setup** | 1 week | Configure Braintree/Stripe/MercadoPago for DR |
| **2. Apple Pay Certs** | 3 days | Merchant ID, certificates, domain verification |
| **3. Google Pay Config** | 2 days | Merchant ID, gateway config, domain verification |
| **4. Backend Processors** | 1 week | Apple/Google processors + unified service |
| **5. Frontend Integration** | 1 week | Web (Safari/Chrome) + iOS + Android |
| **6. Auto-fill Integration** | 3 days | Connect to existing government API auto-fill |
| **7. Fraud Rules** | 2 days | Digital wallet specific risk rules |
| **8. Testing** | 1 week | Sandbox testing with DR cards, end-to-end |
| **9. Production** | 3 days | Live certificates, monitoring, rollout |

---

## 11. USER EXPERIENCE FLOW

```
┌─────────────────────────────────────────────────────────────┐
│  USER QUALIFIES FOR NEVERA (MERIT THRESHOLD)                │
├─────────────────────────────────────────────────────────────┤
│  1. Opens Gobernanza app → "Mis Beneficios"                 │
│  2. Sees "Nevera disponible - RD$45,000"                    │
│  3. Taps "Solicitar y Pagar Envío"                          │
│  4. System shows:                                           │
│     ┌─────────────┐  ┌──────────────┐                       │
│     │  Apple Pay  │  │ Google Pay   │  ← Auto-detected     │
│     │  🍎 Visa ••••1234          │  │  🅶 Mastercard •••5678│
│     └─────────────┘  └──────────────┘                       │
│  5. Selects Apple Pay                                       │
│  6. FaceID confirms                                         │
│  7. Auto-filled (user sees read-only):                      │
│     - Monto: RD$45,000                                      │
│     - Destino: GPS verificado por Quest (ayer)              │
│     - Referencia: "Esquina colmado Doña Rosa"               │
│  8. Confirma → Pago instantáneo                             │
│  9. Recibe:                                                 │
│     ✅ Confirmación + Trace ID                              │
│     🏆 +55 méritos (pago responsable + adopción digital)   │
│     📱 Notificación Discord + Email                         │
│     🚚 Courier asignado con GPS + foto pre-verificación     │
└─────────────────────────────────────────────────────────────┘
```

---

*File: F:\managements\digital_wallet_integration.md*
*Version: 1.0 | Date: 2026-11-10*
*Integrates with: simple_auth_payment_system.md, zero_shipping_address_system.md*