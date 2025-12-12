"""
Security headers and CORS configuration middleware.
Provides comprehensive security headers and CORS policies for web applications.
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint

logger = logging.getLogger(__name__)


@dataclass
class SecurityConfig:
    """Configuration for security headers and CORS."""

    # Security Headers
    enable_security_headers: bool = True

    # Content Security Policy
    csp_enabled: bool = True
    csp_default_src: List[str] = field(default_factory=lambda: ["'self'"])
    csp_script_src: List[str] = field(
        default_factory=lambda: ["'self'", "'unsafe-inline'", "'unsafe-eval'"]
    )
    csp_style_src: List[str] = field(
        default_factory=lambda: ["'self'", "'unsafe-inline'"]
    )
    csp_img_src: List[str] = field(
        default_factory=lambda: ["'self'", "data:", "https:"]
    )
    csp_connect_src: List[str] = field(default_factory=lambda: ["'self'"])
    csp_font_src: List[str] = field(default_factory=lambda: ["'self'", "data:"])
    csp_object_src: List[str] = field(default_factory=lambda: ["'none'"])
    csp_media_src: List[str] = field(default_factory=lambda: ["'self'"])
    csp_frame_src: List[str] = field(default_factory=lambda: ["'none'"])
    csp_worker_src: List[str] = field(default_factory=lambda: ["'self'"])
    csp_manifest_src: List[str] = field(default_factory=lambda: ["'self'"])
    csp_upgrade_insecure_requests: bool = True

    # Other Security Headers
    x_frame_options: str = "DENY"
    x_content_type_options: str = "nosniff"
    x_xss_protection: str = "1; mode=block"
    referrer_policy: str = "strict-origin-when-cross-origin"
    permissions_policy: Dict[str, List[str]] = field(default_factory=dict)
    strict_transport_security: bool = True
    hsts_max_age: int = 31536000  # 1 year
    hsts_include_subdomains: bool = True
    hsts_preload: bool = False

    # CORS Configuration
    cors_enabled: bool = True
    cors_allow_origins: List[str] = field(
        default_factory=lambda: ["http://localhost:3000", "https://localhost:3000"]
    )
    cors_allow_methods: List[str] = field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    cors_allow_headers: List[str] = field(default_factory=lambda: ["*"])
    cors_allow_credentials: bool = False
    cors_expose_headers: List[str] = field(default_factory=list)
    cors_max_age: int = 600

    # Additional Security
    content_type_nosniff: bool = True
    cross_domain_policies: bool = True

    def __post_init__(self):
        """Initialize default values."""
        if self.csp_default_src is None:
            self.csp_default_src = ["'self'"]
        if self.csp_script_src is None:
            self.csp_script_src = ["'self'", "'unsafe-inline'", "'unsafe-eval'"]
        if self.csp_style_src is None:
            self.csp_style_src = ["'self'", "'unsafe-inline'"]
        if self.csp_img_src is None:
            self.csp_img_src = ["'self'", "data:", "https:"]
        if self.csp_connect_src is None:
            self.csp_connect_src = ["'self'"]
        if self.csp_font_src is None:
            self.csp_font_src = ["'self'", "data:"]
        if self.csp_object_src is None:
            self.csp_object_src = ["'none'"]
        if self.csp_media_src is None:
            self.csp_media_src = ["'self'"]
        if self.csp_frame_src is None:
            self.csp_frame_src = ["'none'"]
        if self.csp_worker_src is None:
            self.csp_worker_src = ["'self'"]
        if self.csp_manifest_src is None:
            self.csp_manifest_src = ["'self'"]

        if self.permissions_policy is None:
            self.permissions_policy = {
                "geolocation": [],
                "microphone": [],
                "camera": [],
                "payment": [],
                "usb": [],
                "magnetometer": [],
                "gyroscope": [],
                "accelerometer": [],
                "ambient-light-sensor": [],
                "autoplay": ["'self'"],
                "encrypted-media": [],
                "fullscreen": ["'self'"],
                "picture-in-picture": ["'self'"],
                "speaker": [],
                "vr": [],
                "clipboard-read": [],
                "clipboard-write": ["'self'"],
                "gamepad": [],
                "hid": [],
                "idle-detection": [],
                "local-fonts": [],
                "screen-wake-lock": [],
                "web-share": [],
                "xr-spatial-tracking": [],
            }

        if self.cors_allow_origins is None:
            self.cors_allow_origins = [
                "http://localhost:3000",
                "https://localhost:3000",
            ]
        if self.cors_allow_methods is None:
            self.cors_allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        if self.cors_allow_headers is None:
            self.cors_allow_headers = ["*"]
        if self.cors_expose_headers is None:
            self.cors_expose_headers = []


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to responses."""

    def __init__(self, app, config: Optional[SecurityConfig] = None):
        super().__init__(app)
        self.config = config or SecurityConfig()

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Add security headers to response."""
        response = await call_next(request)

        if not self.config.enable_security_headers:
            return response

        # Content Security Policy
        if self.config.csp_enabled:
            csp_header = self._build_csp_header()
            response.headers["Content-Security-Policy"] = csp_header

        # Frame protection
        if self.config.x_frame_options:
            response.headers["X-Frame-Options"] = self.config.x_frame_options

        # Content type protection
        if self.config.content_type_nosniff:
            response.headers["X-Content-Type-Options"] = (
                self.config.x_content_type_options
            )

        # XSS protection
        if self.config.x_xss_protection:
            response.headers["X-XSS-Protection"] = self.config.x_xss_protection

        # Referrer policy
        if self.config.referrer_policy:
            response.headers["Referrer-Policy"] = self.config.referrer_policy

        # Permissions policy
        if self.config.permissions_policy:
            permissions_header = self._build_permissions_policy()
            response.headers["Permissions-Policy"] = permissions_header

        # Strict Transport Security (HTTPS only)
        if self.config.strict_transport_security and request.url.scheme == "https":
            hsts_header = f"max-age={self.config.hsts_max_age}"
            if self.config.hsts_include_subdomains:
                hsts_header += "; includeSubDomains"
            if self.config.hsts_preload:
                hsts_header += "; preload"
            response.headers["Strict-Transport-Security"] = hsts_header

        # Cross domain policies
        if self.config.cross_domain_policies:
            response.headers["X-Permitted-Cross-Domain-Policies"] = "master-only"
            response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
            response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
            response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

        # Additional security headers
        response.headers["X-DNS-Prefetch-Control"] = "off"
        response.headers["X-Download-Options"] = "noopen"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["Clear-Site-Data"] = (
            '"cache", "cookies", "storage", "executionContexts"'
        )

        # Remove server information
        if "Server" in response.headers:
            del response.headers["Server"]

        # Remove powered by header
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]

        return response

    def _build_csp_header(self) -> str:
        """Build Content Security Policy header."""
        directives = []

        # Default source
        if self.config.csp_default_src:
            directives.append(f"default-src {' '.join(self.config.csp_default_src)}")

        # Script sources
        if self.config.csp_script_src:
            directives.append(f"script-src {' '.join(self.config.csp_script_src)}")

        # Style sources
        if self.config.csp_style_src:
            directives.append(f"style-src {' '.join(self.config.csp_style_src)}")

        # Image sources
        if self.config.csp_img_src:
            directives.append(f"img-src {' '.join(self.config.csp_img_src)}")

        # Connect sources
        if self.config.csp_connect_src:
            directives.append(f"connect-src {' '.join(self.config.csp_connect_src)}")

        # Font sources
        if self.config.csp_font_src:
            directives.append(f"font-src {' '.join(self.config.csp_font_src)}")

        # Object sources
        if self.config.csp_object_src:
            directives.append(f"object-src {' '.join(self.config.csp_object_src)}")

        # Media sources
        if self.config.csp_media_src:
            directives.append(f"media-src {' '.join(self.config.csp_media_src)}")

        # Frame sources
        if self.config.csp_frame_src:
            directives.append(f"frame-src {' '.join(self.config.csp_frame_src)}")

        # Worker sources
        if self.config.csp_worker_src:
            directives.append(f"worker-src {' '.join(self.config.csp_worker_src)}")

        # Manifest sources
        if self.config.csp_manifest_src:
            directives.append(f"manifest-src {' '.join(self.config.csp_manifest_src)}")

        # Upgrade insecure requests
        if self.config.csp_upgrade_insecure_requests:
            directives.append("upgrade-insecure-requests")

        # Additional security directives
        directives.extend(
            [
                "base-uri 'self'",
                "form-action 'self'",
                "frame-ancestors 'none'",
                "navigate-to 'self'",
            ]
        )

        return "; ".join(directives)

    def _build_permissions_policy(self) -> str:
        """Build Permissions Policy header."""
        policies = []

        for feature, allowed_origins in self.config.permissions_policy.items():
            if allowed_origins:
                policies.append(f"{feature}=({' '.join(allowed_origins)})")
            else:
                policies.append(f"{feature}=()")

        return ", ".join(policies)


class CORSMiddlewareWrapper:
    """Wrapper for FastAPI CORS middleware with enhanced security."""

    def __init__(self, app, config: SecurityConfig = None):
        self.config = config or SecurityConfig()
        self.app = app

        if self.config.cors_enabled:
            # Add FastAPI CORS middleware
            app.add_middleware(
                CORSMiddleware,
                allow_origins=self.config.cors_allow_origins,
                allow_credentials=self.config.cors_allow_credentials,
                allow_methods=self.config.cors_allow_methods,
                allow_headers=self.config.cors_allow_headers,
                expose_headers=self.config.cors_expose_headers,
                max_age=self.config.cors_max_age,
            )

    def get_app(self):
        """Get the app with CORS middleware applied."""
        return self.app


class SecurityManager:
    """Main security manager for headers and CORS."""

    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()
        self.security_headers_middleware = None
        self.cors_middleware = None

    def apply_security_middleware(self, app) -> Any:
        """Apply all security middleware to the FastAPI app."""
        # Apply security headers middleware
        self.security_headers_middleware = SecurityHeadersMiddleware(app, self.config)

        # Apply CORS middleware
        self.cors_middleware = CORSMiddlewareWrapper(app, self.config)

        logger.info("Security middleware applied to application")

        return self.cors_middleware.get_app()

    def update_config(self, **kwargs):
        """Update security configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"Updated security config: {key} = {value}")

    def get_security_headers(self) -> Dict[str, str]:
        """Get current security headers configuration."""
        headers = {}

        if self.config.csp_enabled:
            headers["Content-Security-Policy"] = self._build_csp_header()

        if self.config.x_frame_options:
            headers["X-Frame-Options"] = self.config.x_frame_options

        if self.config.content_type_nosniff:
            headers["X-Content-Type-Options"] = self.config.x_content_type_options

        if self.config.x_xss_protection:
            headers["X-XSS-Protection"] = self.config.x_xss_protection

        if self.config.referrer_policy:
            headers["Referrer-Policy"] = self.config.referrer_policy

        if self.config.permissions_policy:
            headers["Permissions-Policy"] = self._build_permissions_policy()

        return headers

    def _build_csp_header(self) -> str:
        """Build Content Security Policy header."""
        directives = []

        if self.config.csp_default_src:
            directives.append(f"default-src {' '.join(self.config.csp_default_src)}")

        if self.config.csp_script_src:
            directives.append(f"script-src {' '.join(self.config.csp_script_src)}")

        if self.config.csp_style_src:
            directives.append(f"style-src {' '.join(self.config.csp_style_src)}")

        if self.config.csp_img_src:
            directives.append(f"img-src {' '.join(self.config.csp_img_src)}")

        if self.config.csp_connect_src:
            directives.append(f"connect-src {' '.join(self.config.csp_connect_src)}")

        if self.config.csp_font_src:
            directives.append(f"font-src {' '.join(self.config.csp_font_src)}")

        if self.config.csp_object_src:
            directives.append(f"object-src {' '.join(self.config.csp_object_src)}")

        if self.config.csp_media_src:
            directives.append(f"media-src {' '.join(self.config.csp_media_src)}")

        if self.config.csp_frame_src:
            directives.append(f"frame-src {' '.join(self.config.csp_frame_src)}")

        if self.config.csp_worker_src:
            directives.append(f"worker-src {' '.join(self.config.csp_worker_src)}")

        if self.config.csp_manifest_src:
            directives.append(f"manifest-src {' '.join(self.config.csp_manifest_src)}")

        if self.config.csp_upgrade_insecure_requests:
            directives.append("upgrade-insecure-requests")

        directives.extend(
            [
                "base-uri 'self'",
                "form-action 'self'",
                "frame-ancestors 'none'",
                "navigate-to 'self'",
            ]
        )

        return "; ".join(directives)

    def _build_permissions_policy(self) -> str:
        """Build Permissions Policy header."""
        policies = []

        for feature, allowed_origins in self.config.permissions_policy.items():
            if allowed_origins:
                policies.append(f"{feature}=({' '.join(allowed_origins)})")
            else:
                policies.append(f"{feature}=()")

        return ", ".join(policies)

    def validate_cors_origin(self, origin: str) -> bool:
        """Validate if origin is allowed for CORS."""
        if not self.config.cors_enabled:
            return False

        if "*" in self.config.cors_allow_origins:
            return True

        if origin in self.config.cors_allow_origins:
            return True

        # Check for wildcard subdomains
        for allowed_origin in self.config.cors_allow_origins:
            if allowed_origin.startswith("*."):
                domain = allowed_origin[2:]
                if origin.endswith(domain):
                    return True

        return False

    def get_security_report(self) -> Dict[str, Any]:
        """Get security configuration report."""
        return {
            "security_headers": {
                "enabled": self.config.enable_security_headers,
                "csp_enabled": self.config.csp_enabled,
                "x_frame_options": self.config.x_frame_options,
                "x_content_type_options": self.config.x_content_type_options,
                "x_xss_protection": self.config.x_xss_protection,
                "referrer_policy": self.config.referrer_policy,
                "strict_transport_security": self.config.strict_transport_security,
                "hsts_max_age": self.config.hsts_max_age,
                "hsts_include_subdomains": self.config.hsts_include_subdomains,
                "hsts_preload": self.config.hsts_preload,
            },
            "cors": {
                "enabled": self.config.cors_enabled,
                "allowed_origins": self.config.cors_allow_origins,
                "allowed_methods": self.config.cors_allow_methods,
                "allowed_headers": self.config.cors_allow_headers,
                "allow_credentials": self.config.cors_allow_credentials,
                "expose_headers": self.config.cors_expose_headers,
                "max_age": self.config.cors_max_age,
            },
            "content_security_policy": {
                "default_src": self.config.csp_default_src,
                "script_src": self.config.csp_script_src,
                "style_src": self.config.csp_style_src,
                "img_src": self.config.csp_img_src,
                "connect_src": self.config.csp_connect_src,
                "font_src": self.config.csp_font_src,
                "object_src": self.config.csp_object_src,
                "media_src": self.config.csp_media_src,
                "frame_src": self.config.csp_frame_src,
                "worker_src": self.config.csp_worker_src,
                "manifest_src": self.config.csp_manifest_src,
                "upgrade_insecure_requests": self.config.csp_upgrade_insecure_requests,
            },
            "permissions_policy": self.config.permissions_policy,
            "security_score": self._calculate_security_score(),
        }

    def _calculate_security_score(self) -> float:
        """Calculate security configuration score."""
        score = 0.0
        max_score = 100.0

        # Security headers (40 points)
        if self.config.enable_security_headers:
            score += 10
        if self.config.csp_enabled:
            score += 10
        if self.config.x_frame_options:
            score += 5
        if self.config.content_type_nosniff:
            score += 5
        if self.config.x_xss_protection:
            score += 5
        if self.config.referrer_policy:
            score += 5

        # HSTS (10 points)
        if self.config.strict_transport_security:
            score += 10

        # CORS (20 points)
        if self.config.cors_enabled:
            score += 10
            if self.config.cors_allow_origins != ["*"]:
                score += 5
            if not self.config.cors_allow_credentials:
                score += 5

        # CSP strictness (20 points)
        if self.config.csp_enabled:
            if "'none'" in self.config.csp_object_src:
                score += 5
            if "'none'" in self.config.csp_frame_src:
                score += 5
            if "'unsafe-inline'" not in self.config.csp_script_src:
                score += 5
            if "'unsafe-eval'" not in self.config.csp_script_src:
                score += 5

        # Permissions policy (10 points)
        if self.config.permissions_policy:
            score += 10

        return min(score, max_score)


# Utility functions
def create_production_security_config() -> SecurityConfig:
    """Create security config for production environment."""
    return SecurityConfig(
        enable_security_headers=True,
        csp_enabled=True,
        csp_default_src=["'self'"],
        csp_script_src=["'self'"],  # Remove unsafe inline/eval for production
        csp_style_src=["'self'"],  # Remove unsafe inline for production
        csp_img_src=["'self'", "data:", "https:"],
        csp_connect_src=["'self'"],
        csp_font_src=["'self'", "data:"],
        csp_object_src=["'none'"],
        csp_media_src=["'self'"],
        csp_frame_src=["'none'"],
        csp_worker_src=["'self'"],
        csp_manifest_src=["'self'"],
        csp_upgrade_insecure_requests=True,
        x_frame_options="DENY",
        x_content_type_options="nosniff",
        x_xss_protection="1; mode=block",
        referrer_policy="strict-origin-when-cross-origin",
        strict_transport_security=True,
        hsts_max_age=31536000,
        hsts_include_subdomains=True,
        hsts_preload=True,
        cors_enabled=True,
        cors_allow_origins=["https://yourdomain.com"],  # Specific domains only
        cors_allow_methods=["GET", "POST", "PUT", "DELETE"],
        cors_allow_headers=["Content-Type", "Authorization"],
        cors_allow_credentials=False,
        cors_expose_headers=[],
        cors_max_age=600,
    )


def create_development_security_config() -> SecurityConfig:
    """Create security config for development environment."""
    return SecurityConfig(
        enable_security_headers=True,
        csp_enabled=True,
        csp_default_src=["'self'"],
        csp_script_src=[
            "'self'",
            "'unsafe-inline'",
            "'unsafe-eval'",
        ],  # Allow for development
        csp_style_src=["'self'", "'unsafe-inline'"],  # Allow for development
        csp_img_src=["'self'", "data:", "https:"],
        csp_connect_src=["'self'", "ws:", "wss:"],  # Allow WebSocket for development
        csp_font_src=["'self'", "data:"],
        csp_object_src=["'none'"],
        csp_media_src=["'self'"],
        csp_frame_src=["'none'"],
        csp_worker_src=["'self'"],
        csp_manifest_src=["'self'"],
        csp_upgrade_insecure_requests=False,  # Disable for HTTP development
        x_frame_options="DENY",
        x_content_type_options="nosniff",
        x_xss_protection="1; mode=block",
        referrer_policy="strict-origin-when-cross-origin",
        strict_transport_security=False,  # Disable for HTTP development
        cors_enabled=True,
        cors_allow_origins=["http://localhost:3000", "https://localhost:3000", "*"],
        cors_allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        cors_allow_headers=["*"],
        cors_allow_credentials=True,
        cors_expose_headers=["*"],
        cors_max_age=600,
    )


# Singleton instance
security_manager = SecurityManager()
