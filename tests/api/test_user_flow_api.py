import pytest

from unifi_tests.api_client import UniFiApiClient

pytestmark = pytest.mark.api


def test_admin_creates_local_user_who_can_then_log_in(settings, new_user, user_cleanup):
    admin = UniFiApiClient(settings.base_url)

    login = admin.login(settings.admin_username, settings.admin_password, settings.admin_otp())
    assert login.status_code == 200, f"Admin login failed: {login.status_code} {login.text}"

    created = admin.create_local_user(**new_user, role_id=admin.get_role_id())
    user_cleanup.append(new_user["username"])
    assert created.status_code in (200, 201), f"User creation failed: {created.status_code} {created.text}"

    logout = admin.logout()
    assert logout.status_code in (200, 204), f"Logout failed: {logout.status_code} {logout.text}"
    assert admin.whoami().status_code == 401, "Session still valid after logout"

    local = UniFiApiClient(settings.base_url)
    local_login = local.login(new_user["username"], new_user["password"])
    assert local_login.status_code == 200, f"Local user login failed: {local_login.status_code} {local_login.text}"
    assert local.whoami().json()["username"] == new_user["username"]
