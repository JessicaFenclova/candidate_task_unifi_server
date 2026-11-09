import os
import time
from dataclasses import dataclass, field

import pyotp
from dotenv import load_dotenv

load_dotenv()

_last_otp: dict[str, str] = {}


@dataclass(frozen=True)
class Settings:
    base_url: str
    admin_username: str = field(repr=False)
    admin_password: str = field(repr=False)
    admin_totp_secret: str = field(repr=False)
    local_user_password: str = field(repr=False)

    def admin_otp(self) -> str:
        """Fresh MFA code (empty if MFA is not configured). The server rejects a reused code,
        so wait for the next 30s window when this one was already handed out."""
        if not self.admin_totp_secret:
            return ""
        totp = pyotp.TOTP(self.admin_totp_secret)
        code = totp.now()
        while code == _last_otp.get("code"):
            time.sleep(1)
            code = totp.now()
        _last_otp["code"] = code
        return code


def load_settings() -> Settings:
    missing = [k for k in ("UNIFI_ADMIN_USERNAME", "UNIFI_ADMIN_PASSWORD") if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)}. Copy .env.example to .env.")
    return Settings(
        base_url=os.getenv("UNIFI_BASE_URL", "https://localhost:11443").rstrip("/"),
        admin_username=os.environ["UNIFI_ADMIN_USERNAME"],
        admin_password=os.environ["UNIFI_ADMIN_PASSWORD"],
        admin_totp_secret=os.getenv("UNIFI_ADMIN_TOTP_SECRET", ""),
        local_user_password=os.getenv("UNIFI_LOCAL_USER_PASSWORD", "ChangeMe-Test-12345"),
    )
