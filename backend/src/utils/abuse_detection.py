"""
Enhanced abuse detection and prevention system.
Provides advanced pattern detection, behavioral analysis, and automated response.
"""

import asyncio
import time
import logging
import json
import re
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque, Counter
import hashlib
import ipaddress
from enum import Enum

logger = logging.getLogger(__name__)


class AbuseType(Enum):
    """Types of abuse patterns."""

    BRUTE_FORCE = "brute_force"
    DDOS = "ddos"
    SCRAPING = "scraping"
    INJECTION_ATTACK = "injection_attack"
    XSS_ATTACK = "xss_attack"
    PATH_TRAVERSAL = "path_traversal"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    RESOURCE_ABUSE = "resource_abuse"
    SPAM = "spam"


class ThreatLevel(Enum):
    """Threat severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AbusePattern:
    """Pattern definition for abuse detection."""

    id: str
    name: str
    abuse_type: AbuseType
    pattern: str
    threat_level: ThreatLevel
    description: str
    action: str  # block, flag, throttle, monitor
    window_seconds: int = 300
    threshold: int = 5
    enabled: bool = True


@dataclass
class AbuseEvent:
    """Record of detected abuse."""

    id: str
    client_ip: str
    abuse_type: AbuseType
    threat_level: ThreatLevel
    pattern_id: str
    timestamp: datetime
    evidence: str
    action_taken: str
    blocked_until: Optional[datetime] = None


@dataclass
class ClientProfile:
    """Behavioral profile for a client."""

    ip_address: str
    user_agent_hash: str
    first_seen: datetime
    last_seen: datetime
    request_count: int = 0
    suspicious_requests: int = 0
    blocked_count: int = 0
    threat_score: float = 0.0
    reputation_score: float = 100.0
    request_patterns: Dict[str, int] = field(default_factory=dict)
    endpoint_access: Dict[str, int] = field(default_factory=dict)
    time_distribution: List[int] = field(default_factory=list)  # requests per hour
    geo_location: Optional[str] = None
    asn: Optional[str] = None

    def update_reputation(self, event: AbuseEvent):
        """Update reputation based on abuse event."""
        threat_weights = {
            ThreatLevel.LOW: -1.0,
            ThreatLevel.MEDIUM: -5.0,
            ThreatLevel.HIGH: -15.0,
            ThreatLevel.CRITICAL: -30.0,
        }

        penalty = threat_weights.get(event.threat_level, -1.0)
        self.reputation_score = max(0, self.reputation_score + penalty)
        self.threat_score = min(100, self.threat_score + abs(penalty))
        self.suspicious_requests += 1

        if event.action_taken == "block":
            self.blocked_count += 1


class AbuseDetector:
    """Advanced abuse detection and prevention system."""

    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.client_profiles: Dict[str, ClientProfile] = {}
        self.abuse_events: deque = deque(maxlen=10000)  # Keep last 10k events
        self.blocked_ips: Dict[str, datetime] = {}
        self.throttled_ips: Dict[
            str, Tuple[datetime, int]
        ] = {}  # IP -> (until, requests_per_minute)
        self.whitelisted_ips: Set[str] = set()
        self.blacklisted_ips: Set[str] = set()
        self._running = False
        self._cleanup_task = None

        # Statistics
        self.stats = {
            "total_requests": 0,
            "abuse_detected": 0,
            "ips_blocked": 0,
            "ips_throttled": 0,
            "patterns_matched": defaultdict(int),
            "threat_levels": defaultdict(int),
            "start_time": datetime.now(),
        }

    def _initialize_patterns(self) -> List[AbusePattern]:
        """Initialize abuse detection patterns."""
        return [
            # SQL Injection patterns
            AbusePattern(
                id="sql_injection_1",
                name="SQL Injection - Union Select",
                abuse_type=AbuseType.INJECTION_ATTACK,
                pattern=r"(?i)(union\s+select|select\s+.*\s+from)",
                threat_level=ThreatLevel.HIGH,
                description="SQL injection attempt with UNION SELECT",
                action="block",
                window_seconds=300,
                threshold=1,
            ),
            AbusePattern(
                id="sql_injection_2",
                name="SQL Injection - Comment Based",
                abuse_type=AbuseType.INJECTION_ATTACK,
                pattern=r"(?i)(--|#|/\*|\*/)",
                threat_level=ThreatLevel.MEDIUM,
                description="SQL comment characters detected",
                action="flag",
                window_seconds=300,
                threshold=3,
            ),
            # XSS patterns
            AbusePattern(
                id="xss_script",
                name="XSS - Script Tag",
                abuse_type=AbuseType.XSS_ATTACK,
                pattern=r"(?i)<script[^>]*>.*?</script>",
                threat_level=ThreatLevel.HIGH,
                description="Cross-site scripting attempt with script tags",
                action="block",
                window_seconds=300,
                threshold=1,
            ),
            AbusePattern(
                id="xss_javascript",
                name="XSS - JavaScript Protocol",
                abuse_type=AbuseType.XSS_ATTACK,
                pattern=r"(?i)javascript\s*:",
                threat_level=ThreatLevel.HIGH,
                description="JavaScript protocol in URL",
                action="block",
                window_seconds=300,
                threshold=1,
            ),
            # Path traversal
            AbusePattern(
                id="path_traversal",
                name="Path Traversal",
                abuse_type=AbuseType.PATH_TRAVERSAL,
                pattern=r"(?i)(\.\./|\.\.\\|%2e%2e%2f|%2e%2e%5c)",
                threat_level=ThreatLevel.HIGH,
                description="Path traversal attempt",
                action="block",
                window_seconds=300,
                threshold=1,
            ),
            # Command injection
            AbusePattern(
                id="command_injection",
                name="Command Injection",
                abuse_type=AbuseType.INJECTION_ATTACK,
                pattern=r"(?i)(;\s*(ls|cat|whoami|id|pwd|uname)|\|\s*(ls|cat|whoami|id|pwd|uname))",
                threat_level=ThreatLevel.CRITICAL,
                description="Command injection attempt",
                action="block",
                window_seconds=300,
                threshold=1,
            ),
            # Brute force patterns
            AbusePattern(
                id="brute_force_auth",
                name="Brute Force Authentication",
                abuse_type=AbuseType.BRUTE_FORCE,
                pattern=r"(?i)(login|auth|signin).*?(password|pass|pwd)",
                threat_level=ThreatLevel.MEDIUM,
                description="Potential brute force authentication attack",
                action="throttle",
                window_seconds=600,
                threshold=10,
            ),
            # Scraping patterns
            AbusePattern(
                id="web_scraping",
                name="Web Scraping",
                abuse_type=AbuseType.SCRAPING,
                pattern=r"(?i)(bot|crawler|scraper|spider)",
                threat_level=ThreatLevel.LOW,
                description="Web scraping bot detected",
                action="monitor",
                window_seconds=3600,
                threshold=50,
            ),
            # Suspicious user agents
            AbusePattern(
                id="suspicious_ua",
                name="Suspicious User Agent",
                abuse_type=AbuseType.SUSPICIOUS_PATTERN,
                pattern=r"(?i)(curl|wget|python|perl|java|go-http)",
                threat_level=ThreatLevel.LOW,
                description="Non-browser user agent",
                action="flag",
                window_seconds=3600,
                threshold=20,
            ),
            # Resource abuse
            AbusePattern(
                id="resource_abuse",
                name="Resource Abuse",
                abuse_type=AbuseType.RESOURCE_ABUSE,
                pattern=r"(?i)(large|bulk|mass).*?(download|export|query)",
                threat_level=ThreatLevel.MEDIUM,
                description="Potential resource abuse",
                action="throttle",
                window_seconds=1800,
                threshold=5,
            ),
        ]

    async def start(self):
        """Start the abuse detection system."""
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Abuse detection system started")

    async def stop(self):
        """Stop the abuse detection system."""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Abuse detection system stopped")

    async def analyze_request(
        self, request_data: Dict[str, Any]
    ) -> Optional[AbuseEvent]:
        """Analyze a request for abuse patterns."""
        client_ip = request_data.get("client_ip", "unknown")
        user_agent = request_data.get("user_agent", "")
        path = request_data.get("path", "")
        method = request_data.get("method", "")
        headers = request_data.get("headers", {})
        body = request_data.get("body", "")
        query_params = request_data.get("query_params", {})

        # Update statistics
        self.stats["total_requests"] += 1

        # Get or create client profile
        profile = self._get_or_create_profile(client_ip, user_agent)
        profile.last_seen = datetime.now()
        profile.request_count += 1

        # Update request patterns
        profile.request_patterns[method] = profile.request_patterns.get(method, 0) + 1
        profile.endpoint_access[path] = profile.endpoint_access.get(path, 0) + 1

        # Check if IP is blacklisted
        if client_ip in self.blacklisted_ips:
            return self._create_abuse_event(
                client_ip=client_ip,
                abuse_type=AbuseType.SUSPICIOUS_PATTERN,
                threat_level=ThreatLevel.CRITICAL,
                pattern_id="blacklisted_ip",
                evidence="IP is blacklisted",
                action="block",
            )

        # Check if IP is currently blocked
        if client_ip in self.blocked_ips:
            if self.blocked_ips[client_ip] > datetime.now():
                return None  # Already blocked
            else:
                del self.blocked_ips[client_ip]  # Block expired

        # Check for pattern matches
        combined_text = f"{path} {method} {body} {str(query_params)} {str(headers)}"

        for pattern in self.patterns:
            if not pattern.enabled:
                continue

            if re.search(pattern.pattern, combined_text, re.IGNORECASE):
                # Check threshold
                recent_matches = self._count_recent_matches(
                    client_ip, pattern, pattern.window_seconds
                )

                if recent_matches >= pattern.threshold:
                    abuse_event = self._create_abuse_event(
                        client_ip=client_ip,
                        abuse_type=pattern.abuse_type,
                        threat_level=pattern.threat_level,
                        pattern_id=pattern.id,
                        evidence=f"Pattern matched: {pattern.name}",
                        action=pattern.action,
                    )

                    # Take action based on pattern
                    await self._take_action(abuse_event)

                    # Update profile
                    profile.update_reputation(abuse_event)

                    # Update statistics
                    self.stats["abuse_detected"] += 1
                    self.stats["patterns_matched"][pattern.id] += 1
                    self.stats["threat_levels"][pattern.threat_level.value] += 1

                    return abuse_event

        # Behavioral analysis
        behavioral_abuse = await self._analyze_behavior(profile)
        if behavioral_abuse:
            await self._take_action(behavioral_abuse)
            profile.update_reputation(behavioral_abuse)
            return behavioral_abuse

        return None

    def _get_or_create_profile(self, client_ip: str, user_agent: str) -> ClientProfile:
        """Get or create client profile."""
        if client_ip not in self.client_profiles:
            user_agent_hash = hashlib.md5(user_agent.encode()).hexdigest()[:16]

            profile = ClientProfile(
                ip_address=client_ip,
                user_agent_hash=user_agent_hash,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
            )

            self.client_profiles[client_ip] = profile

        return self.client_profiles[client_ip]

    def _count_recent_matches(
        self, client_ip: str, pattern: AbusePattern, window_seconds: int
    ) -> int:
        """Count recent pattern matches for a client."""
        cutoff_time = datetime.now() - timedelta(seconds=window_seconds)

        count = 0
        for event in self.abuse_events:
            if (
                event.client_ip == client_ip
                and event.pattern_id == pattern.id
                and event.timestamp > cutoff_time
            ):
                count += 1

        return count

    async def _analyze_behavior(self, profile: ClientProfile) -> Optional[AbuseEvent]:
        """Analyze client behavior for anomalies."""
        # High request rate
        if (
            profile.request_count > 1000
            and profile.request_count
            / max(1, (datetime.now() - profile.first_seen).total_seconds() / 3600)
            > 100
        ):
            return self._create_abuse_event(
                client_ip=profile.ip_address,
                abuse_type=AbuseType.DDOS,
                threat_level=ThreatLevel.HIGH,
                pattern_id="high_request_rate",
                evidence=f"High request rate: {profile.request_count} requests",
                action="throttle",
            )

        # Low reputation score
        if profile.reputation_score < 20:
            return self._create_abuse_event(
                client_ip=profile.ip_address,
                abuse_type=AbuseType.SUSPICIOUS_PATTERN,
                threat_level=ThreatLevel.MEDIUM,
                pattern_id="low_reputation",
                evidence=f"Low reputation score: {profile.reputation_score}",
                action="throttle",
            )

        # Multiple blocked attempts
        if profile.blocked_count > 5:
            return self._create_abuse_event(
                client_ip=profile.ip_address,
                abuse_type=AbuseType.SUSPICIOUS_PATTERN,
                threat_level=ThreatLevel.HIGH,
                pattern_id="repeated_blocks",
                evidence=f"Repeated blocking: {profile.blocked_count} times",
                action="block",
            )

        return None

    def _create_abuse_event(
        self,
        client_ip: str,
        abuse_type: AbuseType,
        threat_level: ThreatLevel,
        pattern_id: str,
        evidence: str,
        action: str,
    ) -> AbuseEvent:
        """Create an abuse event record."""
        event_id = hashlib.md5(
            f"{client_ip}_{pattern_id}_{time.time()}".encode()
        ).hexdigest()

        return AbuseEvent(
            id=event_id,
            client_ip=client_ip,
            abuse_type=abuse_type,
            threat_level=threat_level,
            pattern_id=pattern_id,
            timestamp=datetime.now(),
            evidence=evidence,
            action_taken=action,
        )

    async def _take_action(self, event: AbuseEvent):
        """Take action based on abuse event."""
        if event.action_taken == "block":
            block_duration = self._get_block_duration(event.threat_level)
            self.blocked_ips[event.client_ip] = datetime.now() + timedelta(
                seconds=block_duration
            )
            event.blocked_until = self.blocked_ips[event.client_ip]
            self.stats["ips_blocked"] += 1

        elif event.action_taken == "throttle":
            throttle_duration = self._get_throttle_duration(event.threat_level)
            requests_per_minute = self._get_throttle_limit(event.threat_level)
            self.throttled_ips[event.client_ip] = (
                datetime.now() + timedelta(seconds=throttle_duration),
                requests_per_minute,
            )
            self.stats["ips_throttled"] += 1

        # Store event
        self.abuse_events.append(event)

        logger.warning(
            f"Abuse detected: {event.abuse_type.value} from {event.client_ip} - {event.evidence}"
        )

    def _get_block_duration(self, threat_level: ThreatLevel) -> int:
        """Get block duration based on threat level."""
        durations = {
            ThreatLevel.LOW: 300,  # 5 minutes
            ThreatLevel.MEDIUM: 1800,  # 30 minutes
            ThreatLevel.HIGH: 3600,  # 1 hour
            ThreatLevel.CRITICAL: 86400,  # 24 hours
        }
        return durations.get(threat_level, 1800)

    def _get_throttle_duration(self, threat_level: ThreatLevel) -> int:
        """Get throttle duration based on threat level."""
        durations = {
            ThreatLevel.LOW: 600,  # 10 minutes
            ThreatLevel.MEDIUM: 1800,  # 30 minutes
            ThreatLevel.HIGH: 3600,  # 1 hour
            ThreatLevel.CRITICAL: 7200,  # 2 hours
        }
        return durations.get(threat_level, 1800)

    def _get_throttle_limit(self, threat_level: ThreatLevel) -> int:
        """Get throttle limit based on threat level."""
        limits = {
            ThreatLevel.LOW: 60,  # 60 requests per minute
            ThreatLevel.MEDIUM: 30,  # 30 requests per minute
            ThreatLevel.HIGH: 10,  # 10 requests per minute
            ThreatLevel.CRITICAL: 5,  # 5 requests per minute
        }
        return limits.get(threat_level, 30)

    def is_ip_blocked(self, client_ip: str) -> bool:
        """Check if IP is currently blocked."""
        if client_ip in self.blocked_ips:
            if self.blocked_ips[client_ip] > datetime.now():
                return True
            else:
                del self.blocked_ips[client_ip]  # Block expired
        return False

    def is_ip_throttled(self, client_ip: str) -> Tuple[bool, Optional[int]]:
        """Check if IP is throttled and return rate limit."""
        if client_ip in self.throttled_ips:
            until, limit = self.throttled_ips[client_ip]
            if until > datetime.now():
                return True, limit
            else:
                del self.throttled_ips[client_ip]  # Throttle expired
        return False, None

    def add_whitelist(self, ip: str):
        """Add IP to whitelist."""
        self.whitelisted_ips.add(ip)
        logger.info(f"Added IP to whitelist: {ip}")

    def remove_whitelist(self, ip: str):
        """Remove IP from whitelist."""
        self.whitelisted_ips.discard(ip)
        logger.info(f"Removed IP from whitelist: {ip}")

    def add_blacklist(self, ip: str):
        """Add IP to blacklist."""
        self.blacklisted_ips.add(ip)
        logger.info(f"Added IP to blacklist: {ip}")

    def remove_blacklist(self, ip: str):
        """Remove IP from blacklist."""
        self.blacklisted_ips.discard(ip)
        logger.info(f"Removed IP from blacklist: {ip}")

    async def _cleanup_loop(self):
        """Periodic cleanup of old data."""
        while self._running:
            try:
                await asyncio.sleep(300)  # Clean every 5 minutes
                self._cleanup_old_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    def _cleanup_old_data(self):
        """Clean up old data to prevent memory leaks."""
        cutoff_time = datetime.now() - timedelta(hours=24)

        # Clean old client profiles
        profiles_to_remove = []
        for ip, profile in self.client_profiles.items():
            if (
                profile.last_seen < cutoff_time
                and ip not in self.blocked_ips
                and ip not in self.throttled_ips
                and ip not in self.blacklisted_ips
            ):
                profiles_to_remove.append(ip)

        for ip in profiles_to_remove:
            del self.client_profiles[ip]

        # Clean expired blocks and throttles
        expired_blocks = []
        for ip, until in self.blocked_ips.items():
            if until <= datetime.now():
                expired_blocks.append(ip)

        for ip in expired_blocks:
            del self.blocked_ips[ip]

        expired_throttles = []
        for ip, (until, _) in self.throttled_ips.items():
            if until <= datetime.now():
                expired_throttles.append(ip)

        for ip in expired_throttles:
            del self.throttled_ips[ip]

        if profiles_to_remove or expired_blocks or expired_throttles:
            logger.debug(
                f"Cleaned up {len(profiles_to_remove)} profiles, {len(expired_blocks)} blocks, {len(expired_throttles)} throttles"
            )

    def get_statistics(self) -> Dict[str, Any]:
        """Get abuse detection statistics."""
        uptime = datetime.now() - self.stats["start_time"]

        return {
            **self.stats,
            "uptime_seconds": uptime.total_seconds(),
            "active_profiles": len(self.client_profiles),
            "currently_blocked": len(self.blocked_ips),
            "currently_throttled": len(self.throttled_ips),
            "whitelisted_ips": len(self.whitelisted_ips),
            "blacklisted_ips": len(self.blacklisted_ips),
            "abuse_rate": self.stats["abuse_detected"]
            / max(1, self.stats["total_requests"])
            * 100,
            "top_threats": dict(Counter(self.stats["threat_levels"]).most_common(5)),
            "top_patterns": dict(
                Counter(self.stats["patterns_matched"]).most_common(10)
            ),
        }

    def get_client_profile(self, client_ip: str) -> Optional[ClientProfile]:
        """Get client profile by IP."""
        return self.client_profiles.get(client_ip)

    def get_recent_abuse_events(self, limit: int = 100) -> List[AbuseEvent]:
        """Get recent abuse events."""
        return list(self.abuse_events)[-limit:]

    def export_abuse_data(self, hours: int = 24) -> Dict[str, Any]:
        """Export abuse data for analysis."""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        recent_events = [
            event for event in self.abuse_events if event.timestamp > cutoff_time
        ]

        return {
            "export_time": datetime.now().isoformat(),
            "timeframe_hours": hours,
            "total_events": len(recent_events),
            "events_by_type": Counter(
                event.abuse_type.value for event in recent_events
            ),
            "events_by_threat": Counter(
                event.threat_level.value for event in recent_events
            ),
            "top_offenders": Counter(
                event.client_ip for event in recent_events
            ).most_common(10),
            "events": [
                {
                    "id": event.id,
                    "client_ip": event.client_ip,
                    "abuse_type": event.abuse_type.value,
                    "threat_level": event.threat_level.value,
                    "pattern_id": event.pattern_id,
                    "timestamp": event.timestamp.isoformat(),
                    "evidence": event.evidence,
                    "action_taken": event.action_taken,
                    "blocked_until": event.blocked_until.isoformat()
                    if event.blocked_until
                    else None,
                }
                for event in recent_events
            ],
        }


# Singleton instance
abuse_detector = AbuseDetector()
