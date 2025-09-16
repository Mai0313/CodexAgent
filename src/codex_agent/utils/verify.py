import hmac
import hashlib

from fastapi import HTTPException


class Verification:
    @staticmethod
    def verify_github(payload_body: bytes, secret_token: str, signature_header: str) -> None:
        if not signature_header:
            raise HTTPException(status_code=403, detail="x-hub-signature-256 header is missing!")
        hash_object = hmac.new(
            secret_token.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256
        )
        expected_signature = "sha256=" + hash_object.hexdigest()
        if not hmac.compare_digest(expected_signature, signature_header):
            raise HTTPException(status_code=403, detail="Request signatures didn't match!")
