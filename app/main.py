import asyncio
import hashlib
import logging
import os
from typing import Dict, Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, status, Response
from pydantic import BaseModel, Field

from app.model_adapter import ModelAdapter
from app.safety import content_validator
from app.security import security_validator
from app.legal import legal_validator, DataRegion
from app.data_retention import retention_manager, DataCategory, RetentionPolicy
from app.privacy import privacy_manager, PrivacyTier, AnonymizationLevel
from app.audit import audit_trail
from app import auth as auth_module
from app.metrics import (
    init_metrics, REQUESTS_TOTAL, LATENCY_SECONDS,
    MODEL_ERRORS, SAFETY_BLOCKS, RATE_LIMITS
)
# Auth dependency (uses Redis or in-memory fallback)
from app.auth import get_api_key  # noqa: E402

# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
}

load_dotenv("SafeNow.env")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("api-factory")

# Guardrail configuration (tunable via env)
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "1000"))
MAX_OUTPUT_CHARS = int(os.getenv("MAX_OUTPUT_CHARS", "2000"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "20"))
API_KEY = os.getenv("API_KEY", "devkey")
# Model / behavior config
PREDICT_TIMEOUT = float(os.getenv("PREDICT_TIMEOUT", "5.0"))
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "claude-sonnet-3.5")
ALLOWED_MODELS = set(["claude-sonnet-3.5", "mvp-placeholder"])
# When true, force DEFAULT_MODEL for all clients regardless of client request
FORCE_MODEL_FOR_ALL = os.getenv("FORCE_MODEL_FOR_ALL", "true").lower() in ("1", "true", "yes")

# Ensure DEFAULT_MODEL is permitted (avoid misconfiguration when env overrides defaults)
if DEFAULT_MODEL:
    ALLOWED_MODELS.add(DEFAULT_MODEL)

# Basic profanity list (MVP). Replace with a vetted classifier for production.
BAD_WORDS = {"badword", "evil", "malware", "terror"}

app = FastAPI(
    title="API-Factory MVP with Guardrails",
    description="API service with safety guardrails, metrics, and LLM integration",
    version="1.0.0"
)

# Initialize Prometheus metrics
init_metrics(app)

# Include routers
from app.daily_intention import router as intention_router  # noqa: E402
from app.batch import router as batch_router  # noqa: E402
from app.safenow import router as safenow_router  # noqa: E402

app.include_router(intention_router, prefix="/v1")
app.include_router(batch_router, prefix="/v1")
app.include_router(safenow_router, prefix="/v1")

# Add admin endpoints
@app.get("/admin/stats")
async def get_stats(api_key: str = Depends(get_api_key)):
    """Get basic usage statistics (requires API key)."""
    if not api_key.startswith("admin_"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return {
        "requests": {str(k): v._value.get() for k, v in REQUESTS_TOTAL._metrics.items()},
        "blocks": {str(k): v._value.get() for k, v in SAFETY_BLOCKS._metrics.items()},
        "errors": {str(k): v._value.get() for k, v in MODEL_ERRORS._metrics.items()}
    }

@app.get("/admin/health/deep")
async def deep_health():
    """Deep health check that verifies all subsystems."""
    checks = {
        "api": True,
        "rate_limiter": await _check_rate_limiter(),
        "model": await _check_model()
    }
    is_healthy = all(checks.values())
    return {
        "status": "healthy" if is_healthy else "degraded",
        "checks": checks
    }

async def _check_rate_limiter() -> bool:
    """Verify rate limiter is working."""
    try:
        test_key = f"health_check_{int(asyncio.get_event_loop().time())}"
        await _rate_limiter.is_rate_limited(test_key)
        return True
    except Exception:
        return False

async def _check_model() -> bool:
    """Verify model access is working."""
    try:
        await _model_adapter.generate("test", {"system": "Reply with 'ok'"})
        return True
    except Exception:
        return False

# rate limiter import placed after app/router to avoid circular import error
from app.rate_limiter import get_rate_limiter  # noqa: E402

# Rate limiter (async, pluggable memory or redis)
_rate_limiter = get_rate_limiter()


class PredictRequest(BaseModel):
    """Request schema for the predict endpoint."""
    input: str = Field(
        ..., 
        description="Text input to process",
        min_length=1,
    )
    context: Optional[Dict] = Field(
        None,
        description="Optional context dictionary for the model"
    )
    user_consent: Optional[Dict[str, bool]] = Field(
        None,
        description="User consent flags for data processing"
    )
    region: str = Field(
        "global",
        description="Processing region (eu/us/global)"
    )
    retention_policy: Optional[str] = Field(
        None,
        description="Data retention policy (transient/short_term/standard/extended/permanent)"
    )
    privacy_level: Optional[str] = Field(
        None,
        description="Privacy level for data handling (none/partial/full/synthetic)"
    )
    retention_justification: Optional[str] = Field(
        None,
        description="Required justification if retention_policy is 'permanent'"
    )


class PredictResponse(BaseModel):
    """Response schema with model output and debug info."""
    output: str = Field(..., description="Generated text response")
    debug: Dict = Field(
        default_factory=dict,
        description="Debug information about the request"
    )


# Global model adapter instance (lazy-initialized to avoid heavy imports at module import time)
_model_adapter = None


async def get_api_key(
    x_api_key: str | None = Header(None),
    x_real_ip: str | None = Header(None, alias="X-Real-IP")
) -> str:
    if not x_api_key:
        logger.debug("missing API key")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API Key")
    # Rate limit by both API key and IP if available
    rate_key = f"{x_api_key}:{x_real_ip}" if x_real_ip else x_api_key

    # Allow the default dev key to bypass strict API key format checks (convenience for tests/dev)
    if x_api_key == API_KEY and API_KEY == "devkey":
        return rate_key

    # Validate API key format and strength for non-dev keys
    is_valid, issues = security_validator.validate_api_key(x_api_key)
    if not is_valid:
        logger.warning(f"API key validation failed: {issues}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key Format")

    if x_api_key != API_KEY:
        logger.debug("invalid API key")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")

    return rate_key


@app.get("/health")
async def health(x_api_key: str | None = Header(None, alias="X-API-Key")):
    """Health endpoint.

    - If called without API key, returns basic public health.
    - If called with API key, validates the key and returns 200 only if key is valid.
    """
    if not x_api_key:
        return {"status": "ok"}

    # Validate provided API key using auth store; raises 401 if invalid
    meta = await auth_module._get_metadata(x_api_key)
    if not meta or meta.get("disabled") == "1":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")

    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
async def predict(
    req: PredictRequest,
    api_key: str = Depends(get_api_key),
    x_model: str | None = Header(None, alias="X-Model", description="Optional model override"),
    response: Response = None
):
    # Apply security headers
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    """Generate text using the configured LLM with safety guards.
    
    - Requires API key authentication
    - Rate limited per API key
    - Input length and content filtered
    - Configurable model selection
    - Timeout protection
    """
    # Track latency
    with LATENCY_SECONDS.labels(endpoint="/predict").time():
        # Rate limiting (async)
        if await _rate_limiter.is_rate_limited(api_key):
            RATE_LIMITS.labels(
                api_key_hash=hashlib.sha256(api_key.encode()).hexdigest()[:8]
            ).inc()
            logger.info("rate limit exceeded for key=%s", api_key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )

        text = req.input or ""
        text_stripped = text.strip()

        # Security validation
        is_safe, security_issues = security_validator.validate_input(text_stripped)
        if not is_safe:
            logger.warning(f"Security validation failed: {security_issues}")
            SAFETY_BLOCKS.labels(rule_type="security_validation").inc()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"security_validation: {', '.join(security_issues)}"
            )

        # Profanity check (simple word-list based guardrail)
        lowered = text_stripped.lower()
        for bw in BAD_WORDS:
            if bw in lowered:
                SAFETY_BLOCKS.labels(rule_type="profanity").inc()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content validation failed: profanity detected")

        # Input size guardrail 
        if len(text_stripped) > MAX_INPUT_CHARS:
            logger.info("input too large: %d chars", len(text_stripped))
            SAFETY_BLOCKS.labels(rule_type="input_too_long").inc()
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Input too large (max {MAX_INPUT_CHARS})"
            )
        # Legal compliance validation (run before generic content validation so
        # PII detection can be handled as a legal/consent issue rather than a
        # generic safety block).
        try:
            region = DataRegion(req.region.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid region specified"
            )

        is_compliant, legal_issues = legal_validator.validate_request_compliance(
            text_stripped,
            region,
            req.user_consent
        )
        if not is_compliant:
            logger.warning(f"Legal compliance issues: {legal_issues}")
            SAFETY_BLOCKS.labels(rule_type="legal_compliance").inc()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Legal compliance check failed: {', '.join(legal_issues)}"
            )

        # Enhanced content validation (generic safety patterns)
        is_safe, issues = content_validator.validate(text_stripped)
        if not is_safe:
            logger.info("content issues detected: %s", issues)
            for issue in issues:
                SAFETY_BLOCKS.labels(rule_type=issue).inc()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Content validation failed: {', '.join(issues)}"
            )

        # Privacy tier classification and handling
        privacy_tier, sensitive_elements = privacy_manager.classify_privacy_tier(text_stripped)
        if privacy_tier in [PrivacyTier.RESTRICTED, PrivacyTier.SENSITIVE] and not req.user_consent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Enhanced consent required for {privacy_tier.value} data"
            )

        # Apply privacy controls
        try:
            anonymization_level = AnonymizationLevel(req.privacy_level) if req.privacy_level else AnonymizationLevel.NONE
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid privacy level specified"
            )

        # Anonymize input if required
        if anonymization_level != AnonymizationLevel.NONE:
            text_stripped, anon_stats = privacy_manager.anonymize_data(text_stripped, anonymization_level)
            logger.info("Applied anonymization: %s", anon_stats)

        # Data retention handling
        try:
            retention_policy = RetentionPolicy(req.retention_policy) if req.retention_policy else RetentionPolicy.STANDARD
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid retention policy specified"
            )

        # Register data for retention tracking
        try:
            retention_manager.register_data(
                data_id=response.headers.get("X-Request-ID", "unknown"),
                category=DataCategory.USER_INPUT,
                policy=retention_policy,
                justification=req.retention_justification
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        # Create detailed audit trail
        user_id = hashlib.sha256(api_key.encode()).hexdigest()[:8]
        audit_trail.add_entry(
            action="predict",
            user_id=user_id,
            resource_id=response.headers.get("X-Request-ID", "unknown"),
            details={
                "region": region.value,
                "privacy_tier": privacy_tier.value,
                "sensitive_elements": sensitive_elements,
                "anonymization_level": anonymization_level.value,
                "retention_policy": retention_policy.value,
                "input_length": len(text_stripped),
                "has_user_consent": bool(req.user_consent)
            }
        )

        # Get toxicity score
        toxicity = content_validator.get_toxicity_score(text_stripped)
        if toxicity > 0.7:  # Configurable threshold
            SAFETY_BLOCKS.labels(rule_type="high_toxicity").inc()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content appears unsafe"
            )

    # Determine which model to use
    requested_model = (x_model or "").strip()
    if FORCE_MODEL_FOR_ALL:
        model_to_use = DEFAULT_MODEL
    else:
        model_to_use = requested_model or DEFAULT_MODEL

    if model_to_use not in ALLOWED_MODELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested model not allowed"
        )

    # Run model call with timeout guard and metrics
    try:
        # Lazily initialize the model adapter to avoid heavy/third-party client
        # initialization at import time (helps tests and short-circuit imports).
        global _model_adapter
        if _model_adapter is None:
            # Initialize adapter with the resolved model name so debug shows the
            # expected configured DEFAULT_MODEL when FORCE_MODEL_FOR_ALL is set.
            _model_adapter = ModelAdapter(model=model_to_use)

        output = await asyncio.wait_for(
            _model_adapter.generate(text_stripped, req.context),
            timeout=PREDICT_TIMEOUT
        )
        REQUESTS_TOTAL.labels(endpoint="/predict", status="success").inc()
    except asyncio.TimeoutError:
        logger.warning("model call timed out")
        MODEL_ERRORS.labels(model=model_to_use, error_type="timeout").inc()
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Model processing timed out"
        )
    except Exception as e:
        logger.error("model error: %s", str(e))
        MODEL_ERRORS.labels(model=model_to_use, error_type="error").inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Model processing error"
        )

    # Output size cap
    debug = {"method": model_to_use}
    if len(output) > MAX_OUTPUT_CHARS:
        output = output[:MAX_OUTPUT_CHARS]
        debug["truncated"] = True

    logger.info("request processed for key=%s len_in=%d len_out=%d", api_key, len(text_stripped), len(output))
    return PredictResponse(output=output, debug=debug)
