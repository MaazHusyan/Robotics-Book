"""
Data privacy and GDPR compliance module.
Provides comprehensive data protection, consent management, and privacy controls.
"""

import asyncio
import json
import logging
import hashlib
import secrets
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import re
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class DataType(Enum):
    """Types of personal data."""

    EMAIL = "email"
    NAME = "name"
    IP_ADDRESS = "ip_address"
    USER_AGENT = "user_agent"
    LOCATION = "location"
    QUERY = "query"
    SESSION_DATA = "session_data"
    ANALYTICS = "analytics"
    CONSENT = "consent"
    PREFERENCES = "preferences"


class ConsentType(Enum):
    """Types of consent."""

    ANALYTICS = "analytics"
    MARKETING = "marketing"
    PERSONALIZATION = "personalization"
    FUNCTIONAL = "functional"
    THIRD_PARTY = "third_party"


class DataRetentionPeriod(Enum):
    """Data retention periods."""

    IMMEDIATE = "immediate"  # Delete immediately
    ONE_DAY = "1_day"
    ONE_WEEK = "1_week"
    ONE_MONTH = "1_month"
    THREE_MONTHS = "3_months"
    SIX_MONTHS = "6_months"
    ONE_YEAR = "1_year"
    TWO_YEARS = "2_years"
    SEVEN_YEARS = "7_years"  # Legal requirement in some jurisdictions


@dataclass
class ConsentRecord:
    """Record of user consent."""

    id: str
    user_id: str
    consent_type: ConsentType
    granted: bool
    timestamp: datetime
    ip_address: str
    user_agent: str
    version: str = "1.0"
    expires_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None


@dataclass
class DataSubject:
    """Data subject (user) information."""

    id: str
    identifier: str  # Could be email, user ID, etc.
    identifier_type: str
    created_at: datetime
    last_updated: datetime
    consents: Dict[ConsentType, ConsentRecord] = field(default_factory=dict)
    data_retention_settings: Dict[DataType, DataRetentionPeriod] = field(
        default_factory=dict
    )
    deletion_requests: List[Dict[str, Any]] = field(default_factory=list)
    data_export_requests: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class DataProcessingRecord:
    """Record of data processing activity."""

    id: str
    data_subject_id: str
    data_type: DataType
    operation: str  # create, read, update, delete
    purpose: str
    legal_basis: str
    timestamp: datetime
    processed_by: str
    data_hash: Optional[str] = None
    retention_period: Optional[DataRetentionPeriod] = None


class PrivacyManager:
    """Comprehensive privacy and GDPR compliance manager."""

    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key.encode())

        # Data storage
        self.data_subjects: Dict[str, DataSubject] = {}
        self.consent_records: Dict[str, ConsentRecord] = {}
        self.processing_records: List[DataProcessingRecord] = []
        self.anonymized_data: Dict[str, Any] = {}

        # Privacy settings
        self.default_retention_periods = {
            DataType.EMAIL: DataRetentionPeriod.TWO_YEARS,
            DataType.NAME: DataRetentionPeriod.TWO_YEARS,
            DataType.IP_ADDRESS: DataRetentionPeriod.ONE_MONTH,
            DataType.USER_AGENT: DataRetentionPeriod.ONE_MONTH,
            DataType.LOCATION: DataRetentionPeriod.SIX_MONTHS,
            DataType.QUERY: DataRetentionPeriod.ONE_YEAR,
            DataType.SESSION_DATA: DataRetentionPeriod.ONE_DAY,
            DataType.ANALYTICS: DataRetentionPeriod.TWO_YEARS,
            DataType.CONSENT: DataRetentionPeriod.SEVEN_YEARS,
            DataType.PREFERENCES: DataRetentionPeriod.TWO_YEARS,
        }

        # Sensitive data patterns
        self.sensitive_patterns = {
            "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "phone": re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
            "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            "credit_card": re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
            "ip_address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
        }

        self._cleanup_task = None
        self._running = False

    def _generate_encryption_key(self) -> str:
        """Generate a new encryption key."""
        return Fernet.generate_key().decode()

    async def start(self):
        """Start the privacy manager."""
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Privacy manager started")

    async def stop(self):
        """Stop the privacy manager."""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Privacy manager stopped")

    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise

    def hash_data(self, data: str, salt: Optional[str] = None) -> str:
        """Hash data for pseudonymization."""
        if salt is None:
            salt = secrets.token_hex(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
        )
        hashed_data = kdf.derive(data.encode())
        return base64.b64encode(hashed_data).decode()

    def anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize personal data."""
        anonymized = data.copy()

        # Anonymize common PII fields
        if "email" in anonymized:
            anonymized["email"] = self._anonymize_email(anonymized["email"])

        if "name" in anonymized:
            anonymized["name"] = self._anonymize_name(anonymized["name"])

        if "ip_address" in anonymized:
            anonymized["ip_address"] = self._anonymize_ip(anonymized["ip_address"])

        if "user_agent" in anonymized:
            anonymized["user_agent"] = self._anonymize_user_agent(
                anonymized["user_agent"]
            )

        # Remove sensitive patterns from text fields
        for key, value in anonymized.items():
            if isinstance(value, str):
                anonymized[key] = self._remove_sensitive_patterns(value)

        return anonymized

    def _anonymize_email(self, email: str) -> str:
        """Anonymize email address."""
        if "@" not in email:
            return email

        local, domain = email.split("@", 1)
        if len(local) > 2:
            local = local[0] + "*" * (len(local) - 2) + local[-1]
        else:
            local = "*" * len(local)

        return f"{local}@{domain}"

    def _anonymize_name(self, name: str) -> str:
        """Anonymize name."""
        if len(name) <= 2:
            return "*" * len(name)

        return name[0] + "*" * (len(name) - 2) + name[-1]

    def _anonymize_ip(self, ip: str) -> str:
        """Anonymize IP address (keep first two octets)."""
        try:
            parts = ip.split(".")
            if len(parts) == 4:
                return f"{parts[0]}.{parts[1]}.xxx.xxx"
        except:
            pass
        return "xxx.xxx.xxx.xxx"

    def _anonymize_user_agent(self, user_agent: str) -> str:
        """Anonymize user agent."""
        # Keep browser type but remove version and unique identifiers
        if "Chrome" in user_agent:
            return "Chrome/xxx.xxx.xxx"
        elif "Firefox" in user_agent:
            return "Firefox/xxx.xxx"
        elif "Safari" in user_agent:
            return "Safari/xxx"
        else:
            return "Browser/xxx"

    def _remove_sensitive_patterns(self, text: str) -> str:
        """Remove sensitive patterns from text."""
        cleaned = text

        for pattern_name, pattern in self.sensitive_patterns.items():
            if pattern_name in ["email", "phone", "ssn", "credit_card"]:
                # Replace with placeholder
                cleaned = pattern.sub(f"[{pattern_name.upper()}]", cleaned)

        return cleaned

    def get_or_create_data_subject(
        self, identifier: str, identifier_type: str = "email"
    ) -> DataSubject:
        """Get or create a data subject."""
        subject_id = hashlib.md5(f"{identifier}_{identifier_type}".encode()).hexdigest()

        if subject_id not in self.data_subjects:
            now = datetime.now()
            data_subject = DataSubject(
                id=subject_id,
                identifier=identifier,
                identifier_type=identifier_type,
                created_at=now,
                last_updated=now,
                data_retention_settings=self.default_retention_periods.copy(),
            )
            self.data_subjects[subject_id] = data_subject
            logger.info(f"Created new data subject: {subject_id}")

        return self.data_subjects[subject_id]

    def record_consent(
        self,
        user_id: str,
        consent_type: ConsentType,
        granted: bool,
        ip_address: str,
        user_agent: str,
        expires_at: Optional[datetime] = None,
    ) -> ConsentRecord:
        """Record user consent."""
        consent_id = hashlib.md5(
            f"{user_id}_{consent_type.value}_{datetime.now().isoformat()}".encode()
        ).hexdigest()

        consent_record = ConsentRecord(
            id=consent_id,
            user_id=user_id,
            consent_type=consent_type,
            granted=granted,
            timestamp=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )

        self.consent_records[consent_id] = consent_record

        # Update data subject
        data_subject = self.get_or_create_data_subject(user_id)
        data_subject.consents[consent_type] = consent_record
        data_subject.last_updated = datetime.now()

        logger.info(f"Recorded consent for {user_id}: {consent_type.value} = {granted}")

        return consent_record

    def has_consent(self, user_id: str, consent_type: ConsentType) -> bool:
        """Check if user has given consent."""
        data_subject = self.data_subjects.get(hashlib.md5(user_id.encode()).hexdigest())
        if not data_subject:
            return False

        consent = data_subject.consents.get(consent_type)
        if not consent:
            return False

        # Check if consent is still valid
        if consent.withdrawn_at:
            return False

        if consent.expires_at and consent.expires_at < datetime.now():
            return False

        return consent.granted

    def withdraw_consent(self, user_id: str, consent_type: ConsentType) -> bool:
        """Withdraw user consent."""
        data_subject = self.data_subjects.get(hashlib.md5(user_id.encode()).hexdigest())
        if not data_subject:
            return False

        consent = data_subject.consents.get(consent_type)
        if not consent:
            return False

        consent.withdrawn_at = datetime.now()
        data_subject.last_updated = datetime.now()

        logger.info(f"Withdrew consent for {user_id}: {consent_type.value}")

        return True

    def record_processing_activity(
        self,
        data_subject_id: str,
        data_type: DataType,
        operation: str,
        purpose: str,
        legal_basis: str,
        processed_by: str,
        data_hash: Optional[str] = None,
    ) -> DataProcessingRecord:
        """Record data processing activity."""
        record_id = hashlib.md5(
            f"{data_subject_id}_{data_type.value}_{datetime.now().isoformat()}".encode()
        ).hexdigest()

        processing_record = DataProcessingRecord(
            id=record_id,
            data_subject_id=data_subject_id,
            data_type=data_type,
            operation=operation,
            purpose=purpose,
            legal_basis=legal_basis,
            timestamp=datetime.now(),
            processed_by=processed_by,
            data_hash=data_hash,
            retention_period=self.default_retention_periods.get(data_type),
        )

        self.processing_records.append(processing_record)

        return processing_record

    def request_data_deletion(self, user_id: str, reason: str = "user_request") -> str:
        """Request deletion of user data."""
        request_id = hashlib.md5(
            f"delete_{user_id}_{datetime.now().isoformat()}".encode()
        ).hexdigest()

        deletion_request = {
            "id": request_id,
            "user_id": user_id,
            "reason": reason,
            "timestamp": datetime.now(),
            "status": "pending",
            "completed_at": None,
        }

        data_subject = self.get_or_create_data_subject(user_id)
        data_subject.deletion_requests.append(deletion_request)

        logger.info(f"Data deletion requested for {user_id}: {request_id}")

        return request_id

    async def execute_data_deletion(self, request_id: str) -> bool:
        """Execute data deletion request."""
        # Find the deletion request
        deletion_request = None
        data_subject = None

        for subject in self.data_subjects.values():
            for req in subject.deletion_requests:
                if req["id"] == request_id:
                    deletion_request = req
                    data_subject = subject
                    break
            if deletion_request:
                break

        if not deletion_request or not data_subject:
            logger.error(f"Deletion request not found: {request_id}")
            return False

        try:
            # Delete processing records
            self.processing_records = [
                record
                for record in self.processing_records
                if record.data_subject_id != data_subject.id
            ]

            # Delete consent records
            consent_ids_to_delete = [
                consent_id
                for consent_id, consent in self.consent_records.items()
                if consent.user_id == data_subject.identifier
            ]

            for consent_id in consent_ids_to_delete:
                del self.consent_records[consent_id]

            # Mark data subject as deleted (keep for audit trail)
            data_subject.identifier = "DELETED"
            data_subject.identifier_type = "deleted"

            # Update request status
            deletion_request["status"] = "completed"
            deletion_request["completed_at"] = datetime.now()

            logger.info(f"Data deletion completed for request: {request_id}")
            return True

        except Exception as e:
            logger.error(f"Error executing data deletion: {e}")
            deletion_request["status"] = "failed"
            return False

    def request_data_export(self, user_id: str, format: str = "json") -> str:
        """Request export of user data."""
        request_id = hashlib.md5(
            f"export_{user_id}_{datetime.now().isoformat()}".encode()
        ).hexdigest()

        export_request = {
            "id": request_id,
            "user_id": user_id,
            "format": format,
            "timestamp": datetime.now(),
            "status": "pending",
            "completed_at": None,
            "download_url": None,
        }

        data_subject = self.get_or_create_data_subject(user_id)
        data_subject.data_export_requests.append(export_request)

        logger.info(f"Data export requested for {user_id}: {request_id}")

        return request_id

    async def execute_data_export(self, request_id: str) -> Optional[str]:
        """Execute data export request."""
        # Find the export request
        export_request = None
        data_subject = None

        for subject in self.data_subjects.values():
            for req in subject.data_export_requests:
                if req["id"] == request_id:
                    export_request = req
                    data_subject = subject
                    break
            if export_request:
                break

        if not export_request or not data_subject:
            logger.error(f"Export request not found: {request_id}")
            return None

        try:
            # Collect all user data
            user_data = {
                "data_subject": asdict(data_subject),
                "consent_records": [
                    asdict(consent)
                    for consent in self.consent_records.values()
                    if consent.user_id == data_subject.identifier
                ],
                "processing_records": [
                    asdict(record)
                    for record in self.processing_records
                    if record.data_subject_id == data_subject.id
                ],
                "export_timestamp": datetime.now().isoformat(),
                "export_format": export_request["format"],
            }

            # Generate export file (in real implementation, this would be stored)
            export_data = json.dumps(user_data, indent=2, default=str)
            export_hash = hashlib.sha256(export_data.encode()).hexdigest()

            # Update request status
            export_request["status"] = "completed"
            export_request["completed_at"] = datetime.now()
            export_request["download_url"] = f"/exports/{request_id}?hash={export_hash}"

            logger.info(f"Data export completed for request: {request_id}")

            return export_request["download_url"]

        except Exception as e:
            logger.error(f"Error executing data export: {e}")
            export_request["status"] = "failed"
            return None

    async def _cleanup_loop(self):
        """Periodic cleanup of expired data."""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Clean every hour
                self._cleanup_expired_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    def _cleanup_expired_data(self):
        """Clean up expired data based on retention policies."""
        now = datetime.now()
        cutoff_times = {}

        # Calculate cutoff times for each data type
        for data_type, retention_period in self.default_retention_periods.items():
            if retention_period == DataRetentionPeriod.IMMEDIATE:
                cutoff_times[data_type] = now
            elif retention_period == DataRetentionPeriod.ONE_DAY:
                cutoff_times[data_type] = now - timedelta(days=1)
            elif retention_period == DataRetentionPeriod.ONE_WEEK:
                cutoff_times[data_type] = now - timedelta(weeks=1)
            elif retention_period == DataRetentionPeriod.ONE_MONTH:
                cutoff_times[data_type] = now - timedelta(days=30)
            elif retention_period == DataRetentionPeriod.THREE_MONTHS:
                cutoff_times[data_type] = now - timedelta(days=90)
            elif retention_period == DataRetentionPeriod.SIX_MONTHS:
                cutoff_times[data_type] = now - timedelta(days=180)
            elif retention_period == DataRetentionPeriod.ONE_YEAR:
                cutoff_times[data_type] = now - timedelta(days=365)
            elif retention_period == DataRetentionPeriod.TWO_YEARS:
                cutoff_times[data_type] = now - timedelta(days=730)
            elif retention_period == DataRetentionPeriod.SEVEN_YEARS:
                cutoff_times[data_type] = now - timedelta(days=2555)

        # Clean processing records
        original_count = len(self.processing_records)
        self.processing_records = [
            record
            for record in self.processing_records
            if (
                record.data_type not in cutoff_times
                or record.timestamp > cutoff_times[record.data_type]
            )
        ]

        cleaned_count = original_count - len(self.processing_records)
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} expired processing records")

        # Clean expired consent records
        expired_consents = []
        for consent_id, consent in self.consent_records.items():
            if consent.expires_at and consent.expires_at < now:
                expired_consents.append(consent_id)

        for consent_id in expired_consents:
            del self.consent_records[consent_id]

        if expired_consents:
            logger.info(f"Cleaned up {len(expired_consents)} expired consent records")

    def get_privacy_statistics(self) -> Dict[str, Any]:
        """Get privacy and compliance statistics."""
        now = datetime.now()

        # Count active consents
        active_consents = defaultdict(int)
        total_consents = defaultdict(int)

        for consent in self.consent_records.values():
            total_consents[consent.consent_type] += 1
            if consent.granted and not consent.withdrawn_at:
                if not consent.expires_at or consent.expires_at > now:
                    active_consents[consent.consent_type] += 1

        # Processing records by type
        processing_by_type = defaultdict(int)
        processing_by_operation = defaultdict(int)

        for record in self.processing_records:
            processing_by_type[record.data_type] += 1
            processing_by_operation[record.operation] += 1

        # Data subjects
        active_subjects = len(
            [s for s in self.data_subjects.values() if s.identifier != "DELETED"]
        )
        deleted_subjects = len(
            [s for s in self.data_subjects.values() if s.identifier == "DELETED"]
        )

        # Pending requests
        pending_deletions = sum(
            len([req for req in s.deletion_requests if req["status"] == "pending"])
            for s in self.data_subjects.values()
        )

        pending_exports = sum(
            len([req for req in s.data_export_requests if req["status"] == "pending"])
            for s in self.data_subjects.values()
        )

        return {
            "data_subjects": {
                "active": active_subjects,
                "deleted": deleted_subjects,
                "total": len(self.data_subjects),
            },
            "consents": {
                "active": dict(active_consents),
                "total": dict(total_consents),
            },
            "processing_records": {
                "by_type": dict(processing_by_type),
                "by_operation": dict(processing_by_operation),
                "total": len(self.processing_records),
            },
            "requests": {
                "pending_deletions": pending_deletions,
                "pending_exports": pending_exports,
            },
            "compliance": {
                "encryption_enabled": True,
                "anonymization_enabled": True,
                "retention_policies_active": True,
                "consent_management_active": True,
            },
        }


# Singleton instance
privacy_manager = PrivacyManager()
