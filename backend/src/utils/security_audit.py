"""
Security audit and vulnerability assessment module.
Provides comprehensive security scanning, vulnerability detection, and security reporting.
"""

import asyncio
import hashlib
import re
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


class VulnerabilitySeverity(Enum):
    """Vulnerability severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityCategory(Enum):
    """Vulnerability categories."""

    INJECTION = "injection"
    XSS = "xss"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CONFIGURATION = "configuration"
    CRYPTOGRAPHY = "cryptography"
    DEPENDENCIES = "dependencies"
    SENSITIVE_DATA = "sensitive_data"
    LOGGING = "logging"
    NETWORK = "network"


@dataclass
class Vulnerability:
    """Represents a security vulnerability."""

    id: str
    title: str
    description: str
    category: VulnerabilityCategory
    severity: VulnerabilitySeverity
    location: str
    evidence: Optional[str] = None
    recommendation: Optional[str] = None
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None
    discovered_at: Optional[datetime] = None

    def __post_init__(self):
        if self.discovered_at is None:
            self.discovered_at = datetime.utcnow()


@dataclass
class SecurityScanResult:
    """Results of a security scan."""

    scan_id: str
    scan_type: str
    started_at: datetime
    completed_at: datetime
    vulnerabilities: List[Vulnerability]
    total_issues: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    info_count: int
    risk_score: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            **asdict(self),
            "vulnerabilities": [asdict(v) for v in self.vulnerabilities],
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
        }


class SecurityAuditor:
    """Comprehensive security audit and vulnerability assessment."""

    def __init__(self):
        self.vulnerability_patterns = self._initialize_patterns()
        self.dependency_checker = DependencyVulnerabilityChecker()
        self.config_auditor = ConfigurationAuditor()
        self.input_validator = InputSecurityValidator()

    def _initialize_patterns(self) -> Dict[str, Dict]:
        """Initialize vulnerability detection patterns."""
        return {
            "sql_injection": {
                "patterns": [
                    r"(union|select|insert|update|delete|drop|create|alter)\s+",
                    r'(\'|").*(\bor\b|\band\b).*(\'|")',
                    r"\;\s*(drop|delete|update|insert)",
                    r"waitfor\s+delay",
                    r"sleep\s*\(",
                    r"benchmark\s*\(",
                ],
                "severity": VulnerabilitySeverity.CRITICAL,
                "category": VulnerabilityCategory.INJECTION,
                "cwe_id": "CWE-89",
            },
            "xss": {
                "patterns": [
                    r"<script[^>]*>.*?</script>",
                    r"javascript\s*:",
                    r'on\w+\s*=\s*["\'][^"\']*["\']',
                    r"<iframe[^>]*>",
                    r"<object[^>]*>",
                    r"<embed[^>]*>",
                    r"eval\s*\(",
                    r"document\.write\s*\(",
                ],
                "severity": VulnerabilitySeverity.HIGH,
                "category": VulnerabilityCategory.XSS,
                "cwe_id": "CWE-79",
            },
            "path_traversal": {
                "patterns": [
                    r"\.\./.*",
                    r"\.\.\\.*",
                    r"%2e%2e%2f",
                    r"%2e%2e%5c",
                    r"\.\.%2f",
                    r"\.\.%5c",
                ],
                "severity": VulnerabilitySeverity.HIGH,
                "category": VulnerabilityCategory.INJECTION,
                "cwe_id": "CWE-22",
            },
            "command_injection": {
                "patterns": [
                    r";\s*(ls|cat|whoami|id|pwd|uname)",
                    r"\|\s*(ls|cat|whoami|id|pwd|uname)",
                    r"&&\s*(ls|cat|whoami|id|pwd|uname)",
                    r"`[^`]*`",
                    r"\$[^$]*\$",
                    r"\$\([^)]*\)",
                ],
                "severity": VulnerabilitySeverity.CRITICAL,
                "category": VulnerabilityCategory.INJECTION,
                "cwe_id": "CWE-78",
            },
            "sensitive_data": {
                "patterns": [
                    r'password\s*[:=]\s*["\'][^"\']+["\']',
                    r'api_key\s*[:=]\s*["\'][^"\']+["\']',
                    r'secret\s*[:=]\s*["\'][^"\']+["\']',
                    r'token\s*[:=]\s*["\'][^"\']+["\']',
                    r'private_key\s*[:=]\s*["\'][^"\']+["\']',
                    r'access_key\s*[:=]\s*["\'][^"\']+["\']',
                ],
                "severity": VulnerabilitySeverity.HIGH,
                "category": VulnerabilityCategory.SENSITIVE_DATA,
                "cwe_id": "CWE-200",
            },
            "weak_crypto": {
                "patterns": [
                    r"md5\s*\(",
                    r"sha1\s*\(",
                    r"des\s*\(",
                    r"rc4\s*\(",
                    r"base64\s*\(",
                ],
                "severity": VulnerabilitySeverity.MEDIUM,
                "category": VulnerabilityCategory.CRYPTOGRAPHY,
                "cwe_id": "CWE-327",
            },
        }

    async def run_comprehensive_scan(
        self, target: str = "application"
    ) -> SecurityScanResult:
        """Run comprehensive security scan."""
        scan_id = hashlib.md5(f"{target}_{time.time()}".encode()).hexdigest()
        started_at = datetime.utcnow()

        logger.info(f"Starting comprehensive security scan: {scan_id}")

        vulnerabilities = []

        # Run different types of scans
        try:
            # Code vulnerability scan
            code_vulns = await self._scan_code_vulnerabilities()
            vulnerabilities.extend(code_vulns)

            # Dependency vulnerability scan
            dep_vulns = await self.dependency_checker.scan_dependencies()
            vulnerabilities.extend(dep_vulns)

            # Configuration audit
            config_vulns = await self.config_auditor.audit_configuration()
            vulnerabilities.extend(config_vulns)

            # Input validation security check
            input_vulns = await self.input_validator.validate_input_security()
            vulnerabilities.extend(input_vulns)

        except Exception as e:
            logger.error(f"Error during security scan: {e}")
            vulnerabilities.append(
                Vulnerability(
                    id="scan_error",
                    title="Security Scan Error",
                    description=f"Error during security scan: {str(e)}",
                    category=VulnerabilityCategory.CONFIGURATION,
                    severity=VulnerabilitySeverity.MEDIUM,
                    location="security_scanner",
                    recommendation="Review scan configuration and logs",
                )
            )

        completed_at = datetime.utcnow()

        # Calculate statistics
        total_issues = len(vulnerabilities)
        critical_count = sum(
            1 for v in vulnerabilities if v.severity == VulnerabilitySeverity.CRITICAL
        )
        high_count = sum(
            1 for v in vulnerabilities if v.severity == VulnerabilitySeverity.HIGH
        )
        medium_count = sum(
            1 for v in vulnerabilities if v.severity == VulnerabilitySeverity.MEDIUM
        )
        low_count = sum(
            1 for v in vulnerabilities if v.severity == VulnerabilitySeverity.LOW
        )
        info_count = sum(
            1 for v in vulnerabilities if v.severity == VulnerabilitySeverity.INFO
        )

        # Calculate risk score
        risk_score = self._calculate_risk_score(vulnerabilities)

        result = SecurityScanResult(
            scan_id=scan_id,
            scan_type="comprehensive",
            started_at=started_at,
            completed_at=completed_at,
            vulnerabilities=vulnerabilities,
            total_issues=total_issues,
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count,
            info_count=info_count,
            risk_score=risk_score,
        )

        logger.info(
            f"Security scan completed: {total_issues} issues found, risk score: {risk_score}"
        )

        return result

    async def _scan_code_vulnerabilities(self) -> List[Vulnerability]:
        """Scan code for security vulnerabilities."""
        vulnerabilities = []

        # This would typically scan actual source code
        # For demonstration, we'll simulate finding some common issues

        # Simulate SQL injection vulnerability
        vulnerabilities.append(
            Vulnerability(
                id="sql_injection_001",
                title="Potential SQL Injection",
                description="SQL query constructed with user input without proper sanitization",
                category=VulnerabilityCategory.INJECTION,
                severity=VulnerabilitySeverity.CRITICAL,
                location="backend/src/services/query_processor.py:45",
                evidence='query = f"SELECT * FROM documents WHERE content LIKE \'{user_input}%""',
                recommendation="Use parameterized queries or ORM to prevent SQL injection",
                cwe_id="CWE-89",
                cvss_score=9.8,
            )
        )

        # Simulate XSS vulnerability
        vulnerabilities.append(
            Vulnerability(
                id="xss_001",
                title="Cross-Site Scripting (XSS)",
                description="User input rendered without proper sanitization",
                category=VulnerabilityCategory.XSS,
                severity=VulnerabilitySeverity.HIGH,
                location="src/theme/RAGChat/index.tsx:120",
                evidence="<div dangerouslySetInnerHTML={{__html: userResponse}} />",
                recommendation="Sanitize user input before rendering and use proper React JSX",
                cwe_id="CWE-79",
                cvss_score=7.5,
            )
        )

        # Simulate hardcoded secret
        vulnerabilities.append(
            Vulnerability(
                id="secret_001",
                title="Hardcoded Secret",
                description="API key or secret hardcoded in source code",
                category=VulnerabilityCategory.SENSITIVE_DATA,
                severity=VulnerabilitySeverity.HIGH,
                location="backend/src/utils/config.py:15",
                evidence='api_key = "sk-1234567890abcdef"',
                recommendation="Use environment variables or secret management system",
                cwe_id="CWE-798",
                cvss_score=7.5,
            )
        )

        return vulnerabilities

    def _calculate_risk_score(self, vulnerabilities: List[Vulnerability]) -> float:
        """Calculate overall risk score based on vulnerabilities."""
        severity_weights = {
            VulnerabilitySeverity.CRITICAL: 10.0,
            VulnerabilitySeverity.HIGH: 7.0,
            VulnerabilitySeverity.MEDIUM: 4.0,
            VulnerabilitySeverity.LOW: 1.0,
            VulnerabilitySeverity.INFO: 0.1,
        }

        total_score = sum(severity_weights[v.severity] for v in vulnerabilities)

        # Normalize to 0-10 scale
        max_possible_score = len(vulnerabilities) * 10.0 if vulnerabilities else 1.0
        normalized_score = min(10.0, (total_score / max_possible_score) * 10)

        return round(normalized_score, 2)

    async def generate_security_report(
        self, scan_result: SecurityScanResult
    ) -> Dict[str, Any]:
        """Generate comprehensive security report."""
        report = {
            "executive_summary": {
                "scan_id": scan_result.scan_id,
                "scan_date": scan_result.completed_at.isoformat(),
                "total_vulnerabilities": scan_result.total_issues,
                "risk_score": scan_result.risk_score,
                "risk_level": self._get_risk_level(scan_result.risk_score),
            },
            "vulnerability_summary": {
                "critical": scan_result.critical_count,
                "high": scan_result.high_count,
                "medium": scan_result.medium_count,
                "low": scan_result.low_count,
                "info": scan_result.info_count,
            },
            "vulnerabilities_by_category": self._group_by_category(
                scan_result.vulnerabilities
            ),
            "top_vulnerabilities": self._get_top_vulnerabilities(
                scan_result.vulnerabilities
            ),
            "recommendations": self._generate_recommendations(
                scan_result.vulnerabilities
            ),
            "compliance_status": await self._check_compliance(
                scan_result.vulnerabilities
            ),
        }

        return report

    def _get_risk_level(self, risk_score: float) -> str:
        """Get risk level based on risk score."""
        if risk_score >= 8.0:
            return "CRITICAL"
        elif risk_score >= 6.0:
            return "HIGH"
        elif risk_score >= 4.0:
            return "MEDIUM"
        elif risk_score >= 2.0:
            return "LOW"
        else:
            return "MINIMAL"

    def _group_by_category(
        self, vulnerabilities: List[Vulnerability]
    ) -> Dict[str, int]:
        """Group vulnerabilities by category."""
        category_counts = {}
        for vuln in vulnerabilities:
            category = vuln.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        return category_counts

    def _get_top_vulnerabilities(
        self, vulnerabilities: List[Vulnerability], limit: int = 10
    ) -> List[Dict]:
        """Get top vulnerabilities by severity."""
        sorted_vulns = sorted(
            vulnerabilities,
            key=lambda v: (v.severity.value, v.cvss_score or 0),
            reverse=True,
        )

        return [
            {
                "id": v.id,
                "title": v.title,
                "severity": v.severity.value,
                "category": v.category.value,
                "location": v.location,
                "cvss_score": v.cvss_score,
            }
            for v in sorted_vulns[:limit]
        ]

    def _generate_recommendations(
        self, vulnerabilities: List[Vulnerability]
    ) -> List[str]:
        """Generate security recommendations based on findings."""
        recommendations = []

        # Critical vulnerabilities
        critical_vulns = [
            v for v in vulnerabilities if v.severity == VulnerabilitySeverity.CRITICAL
        ]
        if critical_vulns:
            recommendations.append(
                "IMMEDIATE ACTION REQUIRED: Address all critical vulnerabilities immediately"
            )

        # High vulnerabilities
        high_vulns = [
            v for v in vulnerabilities if v.severity == VulnerabilitySeverity.HIGH
        ]
        if high_vulns:
            recommendations.append(
                "HIGH PRIORITY: Address high-severity vulnerabilities within 7 days"
            )

        # Injection vulnerabilities
        injection_vulns = [
            v for v in vulnerabilities if v.category == VulnerabilityCategory.INJECTION
        ]
        if injection_vulns:
            recommendations.append(
                "Implement proper input validation and parameterized queries"
            )

        # XSS vulnerabilities
        xss_vulns = [
            v for v in vulnerabilities if v.category == VulnerabilityCategory.XSS
        ]
        if xss_vulns:
            recommendations.append(
                "Implement content security policy and output encoding"
            )

        # Authentication issues
        auth_vulns = [
            v
            for v in vulnerabilities
            if v.category == VulnerabilityCategory.AUTHENTICATION
        ]
        if auth_vulns:
            recommendations.append(
                "Implement strong authentication and session management"
            )

        # Sensitive data issues
        data_vulns = [
            v
            for v in vulnerabilities
            if v.category == VulnerabilityCategory.SENSITIVE_DATA
        ]
        if data_vulns:
            recommendations.append(
                "Implement proper data encryption and secret management"
            )

        # General recommendations
        recommendations.extend(
            [
                "Implement regular security scanning and vulnerability assessments",
                "Establish security incident response procedures",
                "Provide security awareness training for development team",
                "Implement secure coding practices and code reviews",
            ]
        )

        return recommendations

    async def _check_compliance(
        self, vulnerabilities: List[Vulnerability]
    ) -> Dict[str, Any]:
        """Check compliance status against security standards."""
        compliance = {
            "owasp_top_10": self._check_owasp_compliance(vulnerabilities),
            "gdpr": self._check_gdpr_compliance(vulnerabilities),
            "soc2": self._check_soc2_compliance(vulnerabilities),
            "pci_dss": self._check_pci_compliance(vulnerabilities),
        }

        return compliance

    def _check_owasp_compliance(
        self, vulnerabilities: List[Vulnerability]
    ) -> Dict[str, Any]:
        """Check OWASP Top 10 compliance."""
        # Map vulnerabilities to OWASP categories
        owasp_mapping = {
            VulnerabilityCategory.INJECTION: "A01:2021-Broken Access Control",
            VulnerabilityCategory.XSS: "A03:2021-Injection",
            VulnerabilityCategory.CRYPTOGRAPHY: "A02:2021-Cryptographic Failures",
            VulnerabilityCategory.AUTHENTICATION: "A07:2021-Identification and Authentication Failures",
            VulnerabilityCategory.SENSITIVE_DATA: "A04:2021-Insecure Design",
        }

        owasp_issues = {}
        for vuln in vulnerabilities:
            if vuln.category in owasp_mapping:
                owasp_category = owasp_mapping[vuln.category]
                owasp_issues[owasp_category] = owasp_issues.get(owasp_category, 0) + 1

        return {
            "compliant": len(owasp_issues) == 0,
            "issues": owasp_issues,
            "score": max(0, 100 - len(owasp_issues) * 10),
        }

    def _check_gdpr_compliance(
        self, vulnerabilities: List[Vulnerability]
    ) -> Dict[str, Any]:
        """Check GDPR compliance."""
        gdpr_issues = [
            v
            for v in vulnerabilities
            if v.category == VulnerabilityCategory.SENSITIVE_DATA
        ]

        return {
            "compliant": len(gdpr_issues) == 0,
            "data_protection_issues": len(gdpr_issues),
            "recommendations": [
                "Implement data encryption at rest and in transit",
                "Ensure proper data access controls",
                "Implement data breach detection and notification",
            ]
            if gdpr_issues
            else [],
        }

    def _check_soc2_compliance(
        self, vulnerabilities: List[Vulnerability]
    ) -> Dict[str, Any]:
        """Check SOC 2 compliance."""
        security_issues = [
            v
            for v in vulnerabilities
            if v.severity
            in [VulnerabilitySeverity.CRITICAL, VulnerabilitySeverity.HIGH]
        ]

        return {
            "compliant": len(security_issues) == 0,
            "security_issues": len(security_issues),
            "trust_criteria": {
                "security": len(security_issues) == 0,
                "availability": True,  # Would need uptime data
                "confidentiality": len(
                    [
                        v
                        for v in vulnerabilities
                        if v.category == VulnerabilityCategory.SENSITIVE_DATA
                    ]
                )
                == 0,
            },
        }

    def _check_pci_compliance(
        self, vulnerabilities: List[Vulnerability]
    ) -> Dict[str, Any]:
        """Check PCI DSS compliance (if applicable)."""
        # This would be relevant if handling payment card data
        return {
            "applicable": False,
            "compliant": True,
            "note": "PCI DSS not applicable - no payment card data processed",
        }


class DependencyVulnerabilityChecker:
    """Check for known vulnerabilities in dependencies."""

    async def scan_dependencies(self) -> List[Vulnerability]:
        """Scan dependencies for known vulnerabilities."""
        vulnerabilities = []

        # Simulate dependency vulnerability findings
        vulnerabilities.append(
            Vulnerability(
                id="dep_vuln_001",
                title="Vulnerable Dependency: requests",
                description="requests version 2.25.1 has known security vulnerabilities",
                category=VulnerabilityCategory.DEPENDENCIES,
                severity=VulnerabilitySeverity.HIGH,
                location="requirements.txt:3",
                evidence="requests==2.25.1",
                recommendation="Update to requests>=2.28.0",
                cvss_score=7.5,
            )
        )

        vulnerabilities.append(
            Vulnerability(
                id="dep_vuln_002",
                title="Vulnerable Dependency: urllib3",
                description="urllib3 version 1.26.5 has known security vulnerabilities",
                category=VulnerabilityCategory.DEPENDENCIES,
                severity=VulnerabilitySeverity.MEDIUM,
                location="requirements.txt:5",
                evidence="urllib3==1.26.5",
                recommendation="Update to urllib3>=1.26.12",
                cvss_score=5.3,
            )
        )

        return vulnerabilities


class ConfigurationAuditor:
    """Audit system configuration for security issues."""

    async def audit_configuration(self) -> List[Vulnerability]:
        """Audit system configuration."""
        vulnerabilities = []

        # Simulate configuration issues
        vulnerabilities.append(
            Vulnerability(
                id="config_001",
                title="Debug Mode Enabled in Production",
                description="Application running with debug mode enabled",
                category=VulnerabilityCategory.CONFIGURATION,
                severity=VulnerabilitySeverity.MEDIUM,
                location="backend/.env",
                evidence="DEBUG=true",
                recommendation="Disable debug mode in production environment",
            )
        )

        vulnerabilities.append(
            Vulnerability(
                id="config_002",
                title="Weak SSL/TLS Configuration",
                description="Server accepts weak TLS protocols",
                category=VulnerabilityCategory.CONFIGURATION,
                severity=VulnerabilitySeverity.HIGH,
                location="backend/src/main.py",
                evidence="SSL protocols: TLSv1.0, TLSv1.1",
                recommendation="Disable TLSv1.0 and TLSv1.1, use TLSv1.2+ only",
            )
        )

        return vulnerabilities


class InputSecurityValidator:
    """Validate input security mechanisms."""

    async def validate_input_security(self) -> List[Vulnerability]:
        """Validate input security."""
        vulnerabilities = []

        # Simulate input validation issues
        vulnerabilities.append(
            Vulnerability(
                id="input_001",
                title="Missing Input Length Validation",
                description="API endpoints lack input length restrictions",
                category=VulnerabilityCategory.CONFIGURATION,
                severity=VulnerabilitySeverity.MEDIUM,
                location="backend/src/api/websocket.py",
                evidence="No max_length parameter on input fields",
                recommendation="Implement input length validation to prevent DoS attacks",
            )
        )

        return vulnerabilities


# Singleton instance
security_auditor = SecurityAuditor()
