import warnings

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from gqlauth.settings_type import GqlAuthSettings


def get_settings() -> GqlAuthSettings:
    settings: GqlAuthSettings
    if user_settings := getattr(django_settings, "GQL_AUTH", False):
        if isinstance(user_settings, GqlAuthSettings):
            settings = user_settings

        else:
            raise ImproperlyConfigured(
                f"GQL_AUTH settings should be of type "
                f"{GqlAuthSettings}, but you provided {type(user_settings)}"
            )

    else:  # pragma: no cover
        warnings.warn(
            "You have not provided any custom gql auth settings falling back to defaults"
        )
        settings = GqlAuthSettings()

    missing = []
    if settings.SEND_ACTIVATION_EMAIL and not settings.ACTIVATION_PATH_ON_EMAIL:
        missing.append("ACTIVATION_PATH_ON_EMAIL")
    if settings.SEND_PASSWORD_SET_EMAIL and not settings.PASSWORD_SET_PATH_ON_EMAIL:
        missing.append("PASSWORD_SET_PATH_ON_EMAIL")
    if settings.SEND_PASSWORD_RESET_EMAIL and not settings.PASSWORD_RESET_PATH_ON_EMAIL:
        missing.append("PASSWORD_RESET_PATH_ON_EMAIL")

    if missing:
        raise ImproperlyConfigured(
            f"GQL_AUTH missing required settings: {', '.join(missing)}. "
            "These settings are required because the corresponding email features are enabled. "
            "If you don't need these features, you can disable them in GQL_AUTH settings."
        )
    return settings


gqlauth_settings: GqlAuthSettings = get_settings()
