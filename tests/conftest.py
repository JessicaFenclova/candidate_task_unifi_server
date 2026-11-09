import uuid

import pytest
from playwright.sync_api import expect

from unifi_tests.api_client import UniFiApiClient
from unifi_tests.config import Settings, load_settings

# The console is a slow single-page app, so Playwright's 5s default is too tight.
expect.set_options(timeout=20_000)


@pytest.fixture(scope="session")
def settings() -> Settings:
    return load_settings()


@pytest.fixture
def new_user(settings):
    """Unique credentials for a throwaway local user."""
    suffix = uuid.uuid4().hex[:8]
    return {
        "username": f"autotest_{suffix}",
        "email": f"autotest_{suffix}@example.com",
        "password": settings.local_user_password,
    }


@pytest.fixture
def user_cleanup(settings):
    """Deletes users registered by name after the test, even if it failed."""
    usernames: list[str] = []
    yield usernames
    if not usernames:
        return
    admin = UniFiApiClient(settings.base_url)
    admin.login(settings.admin_username, settings.admin_password, settings.admin_otp())
    for user in admin.list_users():
        if user.get("username") in usernames:
            admin.delete_user(user["unique_id"])
