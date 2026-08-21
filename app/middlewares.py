import re
from typing import NamedTuple

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.database import rate_limiter_redis
from app.core.security import decode_jwt


class RateRule(NamedTuple):
    limit: int
    window: int
    type: str
    error_msg: str
    methods: set[str] | None = None


class GlobalRateLimiterMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        user_uuid = await self._get_user_uuid_from_request(request)
        if user_uuid:
            is_allowed, ttl = await self._check_rate_limit(
                key=f"ratelimit:user:{user_uuid}", limit=100, window_seconds=60
            )
            error_msg = "User account rate limit exceeded"
        else:
            client_ip = self._get_client_ip_from_request(request)
            is_allowed, ttl = await self._check_rate_limit(
                key=f"ratelimit:ip:{client_ip}", limit=60, window_seconds=60
            )
            error_msg = "IP rate limit exceeded"

        if not is_allowed:
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": error_msg},
                headers={"Retry-After": str(ttl)},
            )
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)

    async def _check_rate_limit(
        self, key: str, limit: int, window_seconds: int
    ) -> tuple[bool, int]:
        async with rate_limiter_redis.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            pipe.expire(key, window_seconds, nx=True)
            pipe.ttl(key)
            results = await pipe.execute()

        current_requests = results[0]
        ttl = results[2]

        if current_requests > limit:
            return False, ttl if ttl > 0 else window_seconds

        return True, 0

    async def _get_user_uuid_from_request(self, request: Request) -> str | None:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header[7:]

        try:
            payload = await decode_jwt(token)
            if payload:
                return payload.get("sub")
        except Exception:
            return None

        return None

    def _get_client_ip_from_request(self, request: Request) -> str:
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()

        x_real_ip = request.headers.get("X-Real-IP")
        if x_real_ip:
            return x_real_ip.strip()

        return request.client.host if request.client else "unknown"


class EndpointRateLimiterMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.rules: dict[re.Pattern[str], RateRule] = {
            re.compile(r"^/auth/register$"): RateRule(
                5, 60, "ip", "Registering limit exceeded", methods={"POST"}
            ),
            re.compile(r"^/auth/login$"): RateRule(
                5, 60, "ip", "Login limit exceeded", methods={"POST"}
            ),
            re.compile(r"^/guest/diary$"): RateRule(
                1, 3600, "ip", "Guest diary limit exceeded", methods={"POST"}
            ),
            re.compile(r"^/pdf/diary/.+$"): RateRule(
                1, 3600, "user", "Generate pdf limit exceeded", methods={"POST"}
            ),
        }

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        path = request.url.path
        method = request.method.upper()

        rule_match = None
        matched_pattern_str = None
        for pattern, rule in self.rules.items():
            if pattern.match(path):
                if rule.methods and method not in rule.methods:
                    continue

                rule_match = rule
                matched_pattern_str = pattern.pattern
                break

        if not rule_match:
            await self.app(scope, receive, send)
            return
        client_ip = self._get_client_ip_from_request(request)
        rate_key = f"rate-limit:{client_ip}:{matched_pattern_str}"

        if rule_match.type == "user":
            user_uuid = await self._get_user_uuid(request)
            if not user_uuid:
                await self.app(scope, receive, send)
                return
            rate_key = f"rate-limit:{user_uuid}:{matched_pattern_str}"

        is_allowed, ttl = await self._check_rate_limit(
            key=rate_key, limit=rule_match.limit, window_seconds=rule_match.window
        )

        if not is_allowed:
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": rule_match.error_msg},
                headers={"Retry-After": str(ttl)},
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)

    async def _check_rate_limit(
        self, key: str, limit: int, window_seconds: int
    ) -> tuple[bool, int]:
        async with rate_limiter_redis.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            pipe.expire(key, window_seconds, nx=True)
            pipe.ttl(key)
            results = await pipe.execute()

        current_requests = results[0]
        ttl = results[2]

        if current_requests > limit:
            return False, ttl if ttl > 0 else window_seconds

        return True, 0

    async def _get_user_uuid(self, request: Request) -> str | None:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header[7:]
        try:
            payload = await decode_jwt(token)
            if payload:
                return payload.get("sub")
        except Exception:
            return None
        return None

    def _get_client_ip_from_request(self, request: Request) -> str:
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()

        x_real_ip = request.headers.get("X-Real-IP")
        if x_real_ip:
            return x_real_ip.strip()

        return request.client.host if request.client else "unknown"
