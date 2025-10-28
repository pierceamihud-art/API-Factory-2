import hashlib
import time
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.auth import get_api_key

router = APIRouter()

# In-memory stores (MVP, process-local)
_CONSENT_REQUESTS: Dict[str, Dict] = {}
_VAULT_STORE: Dict[str, Dict] = {}
_RECORDS: Dict[str, Dict] = {}
_IDENTITIES: Dict[str, Dict] = {}
_WALLETS: Dict[str, Dict] = {}


class ConsentRequest(BaseModel):
    requester: str = Field(..., description="Who is requesting consent")
    purpose: str = Field(..., description="Purpose for data access")
    scope: Optional[Dict[str, bool]] = Field(None, description="Requested consent flags")


class VaultStoreRequest(BaseModel):
    owner_id: str
    doc_name: str
    content: str
    encrypted: Optional[bool] = True


class RecordStoreRequest(BaseModel):
    event: str
    payload: Optional[Dict] = None


class IdentityVerifyRequest(BaseModel):
    identity: Dict
    disclose: Optional[list] = None


class IdentityExportRequest(BaseModel):
    identity_id: str
    format: Optional[str] = "portable"


class WalletMigrateRequest(BaseModel):
    wallet_id: str
    target_app: str


def _make_id(seed: str) -> str:
    return hashlib.sha256(seed.encode()).hexdigest()


@router.post("/consent/request")
async def consent_request(req: ConsentRequest, api_key: str = Depends(get_api_key)):
    """Create a consent request record and return an ID so the client can present it to a user."""
    rid = _make_id(f"consent:{req.requester}:{time.time()}")
    _CONSENT_REQUESTS[rid] = {
        "requester": req.requester,
        "purpose": req.purpose,
        "scope": req.scope or {},
        "created_at": time.time(),
        "status": "pending",
    }
    return {"consent_id": rid, "status": "pending"}


@router.post("/vault/store")
async def vault_store(req: VaultStoreRequest, api_key: str = Depends(get_api_key)):
    """Store a document in the vault. Returns a document id and hash.

    This is an in-memory MVP. `content` should be encrypted by the client in real deployments.
    """
    # Compute a content hash to enable tamper-proof verification later
    h = _make_id(f"vault:{req.owner_id}:{req.doc_name}:{req.content}")
    doc_id = _make_id(f"doc:{time.time()}:{req.owner_id}:{req.doc_name}")
    _VAULT_STORE[doc_id] = {
        "owner_id": req.owner_id,
        "doc_name": req.doc_name,
        "content": req.content,
        "encrypted": bool(req.encrypted),
        "hash": h,
        "created_at": time.time(),
    }
    return {"doc_id": doc_id, "hash": h}


@router.post("/record/store")
async def record_store(req: RecordStoreRequest, api_key: str = Depends(get_api_key)):
    """Store a timestamped record (proof/event). Returns a record id and hash."""
    payload_str = repr(req.payload) if req.payload is not None else ""
    h = _make_id(f"record:{req.event}:{payload_str}:{time.time()}")
    rec_id = _make_id(f"rec:{time.time()}:{req.event}")
    _RECORDS[rec_id] = {
        "event": req.event,
        "payload": req.payload,
        "hash": h,
        "timestamp": time.time(),
    }
    return {"record_id": rec_id, "hash": h}


@router.get("/record/verify/{record_id}")
async def record_verify(record_id: str, api_key: str = Depends(get_api_key)):
    """Verify a record exists and return its stored hash and timestamp."""
    rec = _RECORDS.get(record_id)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return {"record_id": record_id, "hash": rec["hash"], "timestamp": rec["timestamp"]}


@router.post("/identity/verify")
async def identity_verify(req: IdentityVerifyRequest, api_key: str = Depends(get_api_key)):
    """Generate a selective disclosure proof for provided identity data.

    This is an MVP: the proof is a deterministic hash of disclosed fields.
    """
    identity = req.identity
    disclose = req.disclose or list(identity.keys())
    disclosed = {k: identity.get(k) for k in disclose}
    proof_raw = repr(sorted(disclosed.items()))
    proof = _make_id(f"proof:{proof_raw}")
    # Store a lightweight identity record for reference
    iid = _make_id(f"identity:{time.time()}:{proof}")
    _IDENTITIES[iid] = {"full": identity, "disclosed": disclosed, "proof": proof, "created_at": time.time()}
    return {"identity_id": iid, "proof": proof, "disclosed": disclosed}


@router.post("/identity/export")
async def identity_export(req: IdentityExportRequest, api_key: str = Depends(get_api_key)):
    rec = _IDENTITIES.get(req.identity_id)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Identity not found")
    # For MVP, a portable package is just the disclosed fields + proof
    package = {"disclosed": rec["disclosed"], "proof": rec["proof"], "exported_at": time.time()}
    return {"package": package, "format": req.format}


@router.post("/wallet/migrate")
async def wallet_migrate(req: WalletMigrateRequest, api_key: str = Depends(get_api_key)):
    """Simulate migration of a wallet to another app. Returns new mapping info."""
    new_id = _make_id(f"wallet_migrate:{req.wallet_id}:{req.target_app}:{time.time()}")
    _WALLETS[new_id] = {"origin": req.wallet_id, "target_app": req.target_app, "created_at": time.time()}
    return {"status": "migrated", "new_wallet_id": new_id}
