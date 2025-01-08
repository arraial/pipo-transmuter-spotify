"""Common configuration.

Load importable settings from configuration files.
"""

import os

from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    root_path=os.path.dirname(os.path.realpath(__file__)),
    core_loaders=["YAML"],
    envvar_prefix="PIPO",
    default_env="default",
    env="default",
    environments=True,
    validate_on_update=True,
    load_dotenv=True,
    dotenv_override=True,
    ignore_unknown_envvars=True,
    settings_files=["settings.yaml", ".secrets.yaml", ".secrets.json"],
)

# lazy evaluation, check on usage only
settings.validators.register(
    validators=[
        Validator(
            "app",
            "queue_broker_url",
            must_exist=True,
            neq="",
        ),
        Validator(
            "spotify.secret",
            neq="",
            must_exist=True,
            when=Validator("spotify.client", neq="", must_exist=True),
        ),
    ],
)
