import pytest
from django.core.exceptions import ImproperlyConfigured
from gqlauth.settings import get_settings
from gqlauth.settings_type import GqlAuthSettings
from gqlauth.core.constants import Messages


def test_settings_validation_missing_paths():
    # If email is enabled, paths must be provided
    settings = GqlAuthSettings(
        SEND_ACTIVATION_EMAIL=True, ACTIVATION_PATH_ON_EMAIL=None
    )
    # Since it's a frozen dataclass, we usually get it from django settings
    # But here we are testing the logic in get_settings function
    # get_settings uses django.conf.settings.GQL_AUTH
    pass


def test_settings_validation_logic(settings):
    # Test our manual logic in get_settings
    # We can mock django_settings.GQL_AUTH
    from django.conf import settings as django_settings

    # Enable all emails but provide no paths
    bad_settings = GqlAuthSettings(
        SEND_ACTIVATION_EMAIL=True,
        SEND_PASSWORD_RESET_EMAIL=True,
        SEND_PASSWORD_SET_EMAIL=True,
        ACTIVATION_PATH_ON_EMAIL=None,
        PASSWORD_RESET_PATH_ON_EMAIL=None,
        PASSWORD_SET_PATH_ON_EMAIL=None,
    )

    django_settings.GQL_AUTH = bad_settings
    with pytest.raises(ImproperlyConfigured) as excinfo:
        get_settings()
    assert "ACTIVATION_PATH_ON_EMAIL" in str(excinfo.value)
    assert "PASSWORD_RESET_PATH_ON_EMAIL" in str(excinfo.value)
    assert "PASSWORD_SET_PATH_ON_EMAIL" in str(excinfo.value)

    # Disable all emails, no paths needed
    good_settings = GqlAuthSettings(
        SEND_ACTIVATION_EMAIL=False,
        SEND_PASSWORD_RESET_EMAIL=False,
        SEND_PASSWORD_SET_EMAIL=False,
        ACTIVATION_PATH_ON_EMAIL=None,
        PASSWORD_RESET_PATH_ON_EMAIL=None,
        PASSWORD_SET_PATH_ON_EMAIL=None,
    )
    django_settings.GQL_AUTH = good_settings
    loaded = get_settings()
    assert loaded.SEND_ACTIVATION_EMAIL is False


def test_resolver_returns_email_disabled(
    db_verified_user_status, anonymous_schema, app_settings, override_gqlauth
):
    user = db_verified_user_status.user
    email = getattr(user, "email", "test@example.com")
    query = """
    mutation {
        sendPasswordResetEmail(email: "%s")
        { success, errors }
    }
    """ % (email)

    with override_gqlauth(name="SEND_PASSWORD_RESET_EMAIL", replace=False):
        executed = anonymous_schema.execute(query=query)
        assert not executed.errors
        executed = executed.data["sendPasswordResetEmail"]
        assert not executed["success"]
        assert executed["errors"]["email"] == Messages.EMAIL_DISABLED


def test_resend_activation_email_disabled(
    db_unverified_user_status, anonymous_schema, app_settings, override_gqlauth
):
    user = db_unverified_user_status.user
    email = getattr(user, "email", "test@example.com")
    query = """
    mutation {
        resendActivationEmail(email: "%s")
        { success, errors }
    }
    """ % (email)

    with override_gqlauth(name="SEND_ACTIVATION_EMAIL", replace=False):
        executed = anonymous_schema.execute(query=query)
        assert not executed.errors
        executed = executed.data["resendActivationEmail"]
        assert not executed["success"]
        assert executed["errors"]["email"] == Messages.EMAIL_DISABLED
