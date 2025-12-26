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
            raise Exception(
                f"GQL_AUTH settings should be of type "
                f"{GqlAuthSettings}, but you provided {type(user_settings)}"
            )

    else:  # pragma: no cover
        warnings.warn(
            "You have not provided any custom gql auth settings falling back to defaults"
        )
        settings = GqlAuthSettings()

    required = [
        "ACTIVATION_PATH_ON_EMAIL",
        "PASSWORD_SET_PATH_ON_EMAIL",
        "PASSWORD_RESET_PATH_ON_EMAIL",
    ]

    missing = [k for k in required if not getattr(settings, k, None)]
    if missing:
        raise ImproperlyConfigured(
            f"GQL_AUTH missing required settings: {', '.join(missing)}"
        )
    return settings


gqlauth_settings: GqlAuthSettings = get_settings()