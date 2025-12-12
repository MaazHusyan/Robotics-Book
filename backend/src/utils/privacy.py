"""
Privacy utilities for RAG chatbot anonymization and data protection.
Provides IP hashing, user agent anonymization, and PII detection.
"""

import hashlib
import hmac
import re
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import ipaddress
from cryptography.fernet import Fernet
import base64

from ..utils.config import get_config

logger = logging.getLogger(__name__)


@dataclass
class PrivacyConfig:
    """Configuration for privacy features."""

    # Anonymization settings
    enable_ip_hashing: bool = True
    enable_user_agent_hashing: bool = True
    enable_query_anonymization: bool = True

    # Hash settings
    hash_salt: str = "rag-chatbot-salt-2025"
    hash_algorithm: str = "sha256"

    # PII detection
    enable_pii_detection: bool = True
    pii_patterns: Optional[List[str]] = None

    # Data retention
    session_retention_hours: int = 24
    log_retention_days: int = 30

    # Encryption settings
    enable_encryption: bool = False  # Disabled for anonymous system
    encryption_key: Optional[str] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.pii_patterns is None:
            self.pii_patterns = [
                # Email patterns
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                # Phone patterns (US)
                r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
                r"\b\+1[-.]?\d{3}[-.]?\d{3}[-.]?\d{4}\b",
                # SSN patterns
                r"\b\d{3}-\d{2}-\d{4}\b",
                r"\b\d{3}\s\d{2}\s\d{4}\b",
                # Credit card patterns
                r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
                r"\b\d{13,19}\b",
                # Address patterns
                r"\d+\s+[\w\s]+\s+(street|st|avenue|ave|road|rd|boulevard|blvd|lane|ln|drive|dr)",
                # API keys and tokens
                r"[A-Za-z0-9]{32,}",  # Long alphanumeric strings
                r"Bearer\s+[A-Za-z0-9\-._~+\/]+=*",  # Bearer tokens
                r'api[_-]?key["\']?\s*[:=]\s*["\']?[A-Za-z0-9\-._~+\/]+=*["\']?',
                # URLs with potential sensitive info
                r"https?://[^\s]*\?(?:[^&]*&)?(?:token|key|password|secret)=[^&\s]*",
                # Common PII indicators
                r'(?:name|email|phone|address|ssn|social.security|credit.card)\s*[:=]\s*["\']?[^"\'\s,;]+["\']?',
            ]


class PIIDetector:
    """Detects and handles personally identifiable information."""

    def __init__(self, config: PrivacyConfig):
        self.config = config
        patterns = config.pii_patterns or []
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in patterns
        ]

    def detect_pii(self, text: str) -> Dict[str, Any]:
        """Detect PII in text."""
        if not self.config.enable_pii_detection:
            return {"has_pii": False, "matches": [], "types": []}

        matches = []
        types = set()

        for i, pattern in enumerate(self.compiled_patterns):
            pattern_matches = pattern.finditer(text)
            for match in pattern_matches:
                pii_type = self._get_pii_type(i)
                matches.append(
                    {
                        "type": pii_type,
                        "text": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "pattern_index": i,
                    }
                )
                types.add(pii_type)

        return {
            "has_pii": len(matches) > 0,
            "matches": matches,
            "types": list(types),
            "count": len(matches),
        }

    def redact_pii(self, text: str, replacement: str = "[REDACTED]") -> str:
        """Redact PII from text."""
        if not self.config.enable_pii_detection:
            return text

        redacted_text = text

        # Apply patterns in reverse order to maintain indices
        for pattern in reversed(self.compiled_patterns):
            redacted_text = pattern.sub(replacement, redacted_text)

        return redacted_text

    def _get_pii_type(self, pattern_index: int) -> str:
        """Get PII type name from pattern index."""
        type_mapping = {
            0: "email",
            1: "phone_us",
            2: "phone_us_intl",
            3: "ssn",
            4: "ssn_spaces",
            5: "credit_card",
            6: "credit_card_long",
            7: "address",
            8: "api_key_long",
            9: "bearer_token",
            10: "api_key_explicit",
            11: "url_sensitive",
            12: "pii_explicit",
        }

        return type_mapping.get(pattern_index, f"pattern_{pattern_index}")


class Anonymizer:
    """Handles anonymization of user data."""

    def __init__(self, config: PrivacyConfig):
        self.config = config
        self.pii_detector = PIIDetector(config)

        # Initialize encryption if enabled
        self.cipher = None
        if config.enable_encryption and config.encryption_key:
            try:
                self.cipher = Fernet(config.encryption_key.encode())
            except Exception as e:
                logger.error(f"Failed to initialize encryption: {e}")

    def hash_ip_address(self, ip_address: str) -> str:
        """Hash IP address for privacy."""
        if not self.config.enable_ip_hashing:
            return ip_address

        try:
            # Validate IP address
            ip_obj = ipaddress.ip_address(ip_address)

            # For IPv4, consider masking the last octet before hashing
            if isinstance(ip_obj, ipaddress.IPv4Address):
                # Mask last octet for additional privacy
                ip_parts = str(ip_obj).split(".")
                masked_ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0"
                ip_to_hash = masked_ip
            else:
                # For IPv6, consider masking the last 64 bits
                ip_int = int(ip_obj)
                masked_int = ip_int & 0xFFFFFFFFFFFFFFFF0000000000000000
                ip_to_hash = str(ipaddress.IPv6Address(masked_int))

            # Hash with salt
            salted_ip = f"{ip_to_hash}{self.config.hash_salt}"
            hashed_ip = hashlib.pbkdf2_hmac(
                self.config.hash_algorithm,
                salted_ip.encode(),
                self.config.hash_salt.encode(),
                100000,  # iterations
            )

            return base64.b64encode(hashed_ip).decode()[:32]  # Truncate for storage

        except Exception as e:
            logger.error(f"Error hashing IP address: {e}")
            return "hash_error"

    def hash_user_agent(self, user_agent: str) -> str:
        """Hash user agent for privacy."""
        if not self.config.enable_user_agent_hashing or not user_agent:
            return "unknown"

        try:
            # Extract browser family for basic analytics while preserving privacy
            browser_family = self._extract_browser_family(user_agent)

            # Hash with salt
            salted_ua = f"{browser_family}{self.config.hash_salt}"
            hashed_ua = hashlib.pbkdf2_hmac(
                self.config.hash_algorithm,
                salted_ua.encode(),
                self.config.hash_salt.encode(),
                100000,
            )

            return base64.b64encode(hashed_ua).decode()[:24]

        except Exception as e:
            logger.error(f"Error hashing user agent: {e}")
            return "hash_error"

    def anonymize_query(self, query: str) -> Dict[str, Any]:
        """Anonymize user query."""
        if not self.config.enable_query_anonymization:
            return {
                "original_query": query,
                "anonymized_query": query,
                "pii_detected": False,
                "pii_redacted": False,
            }

        # Detect PII
        pii_result = self.pii_detector.detect_pii(query)

        # Redact PII if found
        if pii_result["has_pii"]:
            anonymized_query = self.pii_detector.redact_pii(query)
            pii_redacted = True
        else:
            anonymized_query = query
            pii_redacted = False

        return {
            "original_query": query,
            "anonymized_query": anonymized_query,
            "pii_detected": pii_result["has_pii"],
            "pii_redacted": pii_redacted,
            "pii_types": pii_result.get("types", []),
            "pii_count": pii_result.get("count", 0),
        }

    def encrypt_sensitive_data(self, data: str) -> Optional[str]:
        """Encrypt sensitive data if encryption is enabled."""
        if not self.cipher or not data:
            return None

        try:
            encrypted_data = self.cipher.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            return None

    def decrypt_sensitive_data(self, encrypted_data: str) -> Optional[str]:
        """Decrypt sensitive data if encryption is enabled."""
        if not self.cipher or not encrypted_data:
            return None

        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            return None

    def _extract_browser_family(self, user_agent: str) -> str:
        """Extract browser family from user agent string."""
        user_agent_lower = user_agent.lower()

        if "chrome" in user_agent_lower and "edg" not in user_agent_lower:
            return "chrome"
        elif "firefox" in user_agent_lower:
            return "firefox"
        elif "safari" in user_agent_lower and "chrome" not in user_agent_lower:
            return "safari"
        elif "edg" in user_agent_lower:
            return "edge"
        elif "opera" in user_agent_lower or "opr" in user_agent_lower:
            return "opera"
        elif "ie" in user_agent_lower or "trident" in user_agent_lower:
            return "ie"
        else:
            return "other"


class PrivacyManager:
    """Main privacy management interface."""

    def __init__(self, config: Optional[PrivacyConfig] = None):
        self.config = config or PrivacyConfig()
        self.anonymizer = Anonymizer(self.config)
        self.pii_detector = PIIDetector(self.config)

    def process_request_data(
        self, ip_address: str, user_agent: str, query: str
    ) -> Dict[str, Any]:
        """Process and anonymize request data."""
        # Hash IP and user agent
        hashed_ip = self.anonymizer.hash_ip_address(ip_address)
        hashed_user_agent = self.anonymizer.hash_user_agent(user_agent)

        # Anonymize query
        query_result = self.anonymizer.anonymize_query(query)

        return {
            "ip_address_hash": hashed_ip,
            "user_agent_hash": hashed_user_agent,
            "original_query": query_result["original_query"],
            "anonymized_query": query_result["anonymized_query"],
            "pii_detected": query_result["pii_detected"],
            "pii_redacted": query_result["pii_redacted"],
            "pii_types": query_result.get("pii_types", []),
            "pii_count": query_result.get("pii_count", 0),
            "processed_at": datetime.utcnow().isoformat(),
        }

    def should_block_request(self, processed_data: Dict[str, Any]) -> bool:
        """Determine if request should be blocked due to PII."""
        # Block if excessive PII detected
        if processed_data.get("pii_count", 0) > 5:
            logger.warning(
                f"Request blocked: excessive PII detected ({processed_data['pii_count']} items)"
            )
            return True

        # Block if certain sensitive PII types detected
        sensitive_types = {"ssn", "credit_card", "api_key_explicit"}
        detected_types = set(processed_data.get("pii_types", []))

        if sensitive_types.intersection(detected_types):
            logger.warning(
                f"Request blocked: sensitive PII types detected: {detected_types}"
            )
            return True

        return False

    def create_privacy_headers(self) -> Dict[str, str]:
        """Create privacy-related response headers."""
        return {
            "X-Privacy-Policy": "https://example.com/privacy",
            "X-Data-Processing": "anonymized",
            "X-Pii-Detection": "enabled"
            if self.config.enable_pii_detection
            else "disabled",
            "X-Data-Retention": f"{self.config.session_retention_hours}h",
        }

    def cleanup_expired_data(self, data_store: Dict[str, Any]) -> int:
        """Clean up expired data based on retention policies."""
        cutoff_time = datetime.utcnow() - timedelta(
            hours=self.config.session_retention_hours
        )

        expired_keys = []
        for key, data in data_store.items():
            if isinstance(data, dict) and "created_at" in data:
                try:
                    created_at = datetime.fromisoformat(data["created_at"])
                    if created_at < cutoff_time:
                        expired_keys.append(key)
                except (ValueError, TypeError):
                    # Invalid timestamp, mark for removal
                    expired_keys.append(key)

        # Remove expired data
        for key in expired_keys:
            del data_store[key]

        logger.info(f"Cleaned up {len(expired_keys)} expired privacy records")
        return len(expired_keys)


# Global privacy manager instance
_privacy_manager = None


def get_privacy_manager() -> PrivacyManager:
    """Get global privacy manager instance."""
    global _privacy_manager
    if _privacy_manager is None:
        _privacy_manager = PrivacyManager()
    return _privacy_manager


# Utility functions
def hash_ip_address(ip_address: str) -> str:
    """Hash IP address using global privacy manager."""
    manager = get_privacy_manager()
    return manager.anonymizer.hash_ip_address(ip_address)


def hash_user_agent(user_agent: str) -> str:
    """Hash user agent using global privacy manager."""
    manager = get_privacy_manager()
    return manager.anonymizer.hash_user_agent(user_agent)


def anonymize_query(query: str) -> Dict[str, Any]:
    """Anonymize query using global privacy manager."""
    manager = get_privacy_manager()
    return manager.anonymizer.anonymize_query(query)


def detect_pii(text: str) -> Dict[str, Any]:
    """Detect PII in text using global privacy manager."""
    manager = get_privacy_manager()
    return manager.pii_detector.detect_pii(text)


def redact_pii(text: str, replacement: str = "[REDACTED]") -> str:
    """Redact PII from text using global privacy manager."""
    manager = get_privacy_manager()
    return manager.pii_detector.redact_pii(text, replacement)


# Health check for privacy
async def privacy_health_check() -> Dict[str, Any]:
    """Perform health check on privacy system."""
    try:
        config = PrivacyConfig()
        manager = PrivacyManager(config)

        # Test anonymization
        test_ip = "192.168.1.100"
        test_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        test_query = "What is robotics? My email is test@example.com"

        processed = manager.process_request_data(test_ip, test_ua, test_query)

        # Verify PII detection
        pii_detected = processed.get("pii_detected", False)
        pii_redacted = processed.get("pii_redacted", False)

        health_status = {
            "status": "healthy",
            "anonymization_working": len(processed.get("ip_address_hash", "")) > 0,
            "pii_detection_working": pii_detected,
            "pii_redaction_working": pii_redacted,
            "test_results": {
                "ip_hashed": bool(processed.get("ip_address_hash")),
                "ua_hashed": bool(processed.get("user_agent_hash")),
                "pii_found": pii_detected,
                "pii_types": processed.get("pii_types", []),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        return health_status

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
