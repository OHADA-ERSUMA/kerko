"""
A sample Flask application using the Kerko blueprint.


import os
import kerko
from flask import Flask, render_template
from flask_mail import Mail
from flask_babel import get_locale
from kerko.config_helpers import config_update, parse_config

from . import logging
from .config_helpers import KerkoAppModel, load_config_files
from .extensions import babel, bootstrap

mail = Mail()

def create_app() -> Flask:
    
   # Application factory.

    #Explained here: http://flask.pocoo.org/docs/patterns/appfactories/
    
    try:
        app = Flask(__name__, instance_path=os.environ.get("KERKOAPP_INSTANCE_PATH"))

    except ValueError as e:
        msg = f"Unable to initialize the application. {e}"
        raise RuntimeError(msg) from e

 # Config SMTP
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'roukayathfadeyi5@gmail.com'
    app.config['MAIL_PASSWORD'] = 'yhypkrykgbzdjjvl'
    app.config['MAIL_DEFAULT_SENDER'] = ('Nom Affiché', 'roukayathfadeyi5@gmail.com')

    mail.init_app(app)

    # Initialize app configuration with Kerko's defaults.
    config_update(app.config, kerko.DEFAULTS)

    # Update app configuration from TOML configuration file(s).
    load_config_files(app, os.environ.get("KERKOAPP_CONFIG_FILES"))

    # Update app configuration from environment variables.
    app.config.from_prefixed_env(prefix="KERKOAPP")

    # Validate configuration and save its parsed version.
    parse_config(app.config)

    # Validate extra configuration model and save its parsed version.
    if app.config.get("kerkoapp"):
        parse_config(app.config, "kerkoapp", KerkoAppModel)

    # Initialize the Composer object.
    app.config["kerko_composer"] = kerko.composer.Composer(app.config)

    # ----
    # If you are deriving your own custom application from KerkoApp, here is a
    # good place to alter the Composer object, perhaps adding facets.
    # ----

    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)

    return app


def register_extensions(app: Flask) -> None:
    # Initialize Babel to use translations from both Kerko and the app. Config
    # parameters BABEL_DOMAIN and BABEL_TRANSLATION_DIRECTORIES may override
    # these defaults. When multiple translation directories are used, a domain
    # MUST be specified for each directory. Thus, both lists must have the same
    # number of items (separated by semi-colons).
    domain = f"{kerko.TRANSLATION_DOMAIN};messages"
    directories = f"{kerko.TRANSLATION_DIRECTORY};translations"
    babel.init_app(
        app,
        default_domain=domain,
        default_translation_directories=directories,
    )

    logging.init_app(app)
    bootstrap.init_app(app)


def register_blueprints(app: Flask) -> None:
    # Setting `url_prefix` is required to distinguish the blueprint's static
    # folder route URL from the app's.
    app.register_blueprint(kerko.make_blueprint(), url_prefix="/biblio")


def register_errorhandlers(app: Flask) -> None:
    def render_error(error):
        # If a HTTPException, pull the `code` attribute; default to 500.
        error_code = getattr(error, "code", 500)
        context = {
            "locale": get_locale(),
        }
        return render_template(f"kerkoapp/{error_code}.html.jinja2", **context), error_code

    for errcode in [400, 403, 404, 500, 503]:
        app.errorhandler(errcode)(render_error)

Kerko: A Flask blueprint that provides faceted search for bibliographies based on Zotero.

import errno
import pathlib
import sys

from kerko.blueprint import Blueprint
from kerko.config_helpers import load_toml

# Kerko won't load translations on its own. To load them, an application may add
# the following domain and translation directory to its Babel configuration.
TRANSLATION_DOMAIN = "kerko"
TRANSLATION_DIRECTORY = str(pathlib.Path(__file__).parent / "translations")
TRANSLATION_DIRECTORIES = [  # DEPRECATED: Remove in Kerko 2.x.
    str(pathlib.Path(__file__).parent / "translations")
]

try:
    DEFAULTS = load_toml(pathlib.Path(__file__).parent /  "default_config.toml")
except RuntimeError as e:
    print(e, file=sys.stderr)  # noqa: T201
    sys.exit(errno.EINTR)  # This should make the WSGI server exit as well.


def make_blueprint():
    return Blueprint(
        "biblio",
        __name__,
        static_folder="static",
        template_folder="templates",
    )
"""


"""
A sample Flask application using the Kerko blueprint.
"""

import os
from flask import Flask, render_template
from flask_mail import Mail
from flask_babel import get_locale
import kerko
from kerko.config_helpers import config_update, parse_config
from . import logging
from .config_helpers import KerkoAppModel, load_config_files
from .extensions import babel, bootstrap

# Initialisation de l'extension mail
mail = Mail()

def create_app() -> Flask:
    """
    Application factory.
    Voir : http://flask.pocoo.org/docs/patterns/appfactories/
    """
    try:
        app = Flask(__name__, instance_path=os.environ.get("KERKOAPP_INSTANCE_PATH"))
    except ValueError as e:
        raise RuntimeError(f"Unable to initialize the application. {e}") from e

    # Configuration de l'envoi des mails (⚠️ Ces infos devraient être dans un fichier .env pour la sécurité)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'roukayathfadeyi5@gmail.com'
    app.config['MAIL_PASSWORD'] = 'yhypkrykgbzdjjvl'
    app.config['MAIL_DEFAULT_SENDER'] = ('Nom Affiché', 'roukayathfadeyi5@gmail.com')

    # Initialisation du service de mail
    mail.init_app(app)

    # Configuration par défaut de Kerko
    config_update(app.config, kerko.DEFAULTS)

    # Surcharge depuis fichiers .toml
    load_config_files(app, os.environ.get("KERKOAPP_CONFIG_FILES"))

    # Surcharge depuis les variables d'environnement KERKOAPP_
    app.config.from_prefixed_env(prefix="KERKOAPP")

    # Analyse de configuration
    parse_config(app.config)

    # Validation de configuration spécifique à l'application
    if app.config.get("kerkoapp"):
        parse_config(app.config, "kerkoapp", KerkoAppModel)

    # Initialisation du compositeur Kerko
    app.config["kerko_composer"] = kerko.composer.Composer(app.config)

    # Enregistrement des modules Flask
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)

    return app


def register_extensions(app: Flask) -> None:
    # Initialisation de Babel avec les traductions de Kerko et de l'app
    domain = f"{kerko.TRANSLATION_DOMAIN};messages"
    directories = f"{kerko.TRANSLATION_DIRECTORY};translations"

    babel.init_app(
        app,
        default_domain=domain,
        default_translation_directories=directories,
    )

    logging.init_app(app)
    bootstrap.init_app(app)


def register_blueprints(app: Flask) -> None:
    # Enregistrement du blueprint Kerko avec préfixe d'URL
    app.register_blueprint(kerko.make_blueprint(), url_prefix="/biblio")


def register_errorhandlers(app: Flask) -> None:
    def render_error(error):
        # Gestion personnalisée des pages d'erreurs
        error_code = getattr(error, "code", 500)
        context = {
            "locale": get_locale(),
        }
        return render_template(f"kerkoapp/{error_code}.html.jinja2", **context), error_code

    for errcode in [400, 403, 404, 500, 503]:
        app.errorhandler(errcode)(render_error)

