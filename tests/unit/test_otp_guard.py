import pytest

from unifi_tests import config


class FakeTotp:
    codes = iter(())

    def __init__(self, secret):
        pass

    def now(self):
        return next(FakeTotp.codes)


@pytest.fixture
def otp_env(monkeypatch, tmp_path):
    monkeypatch.setattr(config.pyotp, "TOTP", FakeTotp)
    monkeypatch.setattr(config.time, "sleep", lambda _: None)
    monkeypatch.setattr(config, "_STATE_FILE", tmp_path / "last_otp", raising=False)
    config._last_otp.clear()
    return config.Settings("https://x", "u", "p", "secret", "pw")


def test_code_used_by_another_process_is_not_reused(otp_env):
    config._STATE_FILE.write_text("111111")  # left behind by an earlier process
    FakeTotp.codes = iter(["111111", "111111", "222222"])
    assert otp_env.admin_otp() == "222222"


def test_code_is_recorded_for_other_processes(otp_env):
    FakeTotp.codes = iter(["333333"])
    otp_env.admin_otp()
    assert config._STATE_FILE.read_text() == "333333"


def test_same_process_still_waits_for_next_window(otp_env):
    FakeTotp.codes = iter(["444444", "444444", "555555"])
    assert otp_env.admin_otp() == "444444"
    assert otp_env.admin_otp() == "555555"
