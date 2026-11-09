import pytest

from unifi_tests.pages import AdminsPage, LoginPage, Navigation

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "ignore_https_errors": True, "viewport": {"width": 1400, "height": 1000}}


def test_admin_creates_local_user_who_can_then_log_in(page, settings, new_user, user_cleanup):
    login = LoginPage(page, settings.base_url)
    admins = AdminsPage(page, settings.base_url)
    nav = Navigation(page)

    login.open()
    login.login(settings.admin_username, settings.admin_password, settings.admin_otp())
    login.expect_logged_in()

    admins.open()
    admins.create_local_user("Auto", "Test", new_user["email"], new_user["username"], new_user["password"])
    user_cleanup.append(new_user["username"])
    admins.expect_user_listed(new_user["email"])

    nav.logout()
    login.expect_logged_out()

    login.login(new_user["username"], new_user["password"])
    login.expect_logged_in()
