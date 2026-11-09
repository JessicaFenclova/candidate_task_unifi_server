import re

from playwright.sync_api import Page, expect


class LoginPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.username = page.locator("input[name=username]")
        self.password = page.locator("input[name=password]")
        self.sign_in = page.get_by_role("button", name="Sign In")
        self.mfa_heading = page.get_by_text("App Authentication")
        self.mfa_first_digit = page.locator("input").first

    def open(self):
        self.page.goto(self.base_url)
        expect(self.username).to_be_visible()

    def login(self, username: str, password: str, otp: str = ""):
        self.username.fill(username)
        self.password.fill(password)
        self.sign_in.click()
        if otp:
            expect(self.mfa_heading).to_be_visible()
            self.mfa_first_digit.click()
            # The code is six separate inputs that auto-advance, so type it key by key.
            self.page.keyboard.type(otp, delay=80)

    def expect_logged_in(self):
        expect(self.page).to_have_url(re.compile(r"/network/default/"))

    def expect_logged_out(self):
        expect(self.page).to_have_url(re.compile(r"/login"))
        expect(self.username).to_be_visible()


class Navigation:
    """Controls shared by every page after login."""

    def __init__(self, page: Page):
        self.page = page
        self.account_menu = page.get_by_role("banner").get_by_role("button").last
        self.sign_out = page.get_by_text("Sign Out", exact=True)

    def logout(self):
        self.account_menu.click()
        self.sign_out.click()


class AdminsPage:
    """Network app > Admins & Users."""

    PATH = "/network/default/admins/users"

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.create_new = page.get_by_text("Create New", exact=True).first
        self.create_new_user = page.get_by_text("Create New User", exact=True)
        self.first_name = page.get_by_label("First Name")
        self.last_name = page.get_by_label("Last Name")
        self.email = page.get_by_label("Email", exact=True)
        self.admin_checkbox = page.locator("#use-admin")
        self.local_only = page.get_by_text("Restrict to Local Access Only", exact=True)
        # Username and password labels are plain text, not tied to their inputs.
        self.username = page.locator("xpath=//div[normalize-space(text())='Username']/following::input[1]")
        self.password = page.locator("xpath=//div[normalize-space(text())='Password']/following::input[1]")
        self.create_button = page.get_by_role("button", name="Create", exact=True)

    def open(self):
        self.page.goto(f"{self.base_url}{self.PATH}")
        expect(self.create_new).to_be_visible()

    def create_local_user(self, first_name: str, last_name: str, email: str, username: str, password: str):
        self.create_new.click()
        self.create_new_user.click()
        self.first_name.fill(first_name)
        self.last_name.fill(last_name)
        self.email.fill(email)
        self.admin_checkbox.check(force=True)
        self.local_only.click()
        self.username.fill(username)
        self.password.fill(password)
        expect(self.create_button).to_be_enabled()
        self.create_button.click()

    def expect_user_listed(self, email: str):
        expect(self.page.get_by_text(email)).to_be_visible()
