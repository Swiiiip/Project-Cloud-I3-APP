import os

import uvicorn
from dotenv import load_dotenv

from src.services.gateway.app import create_app
from src.services.gateway.internal_client import InternalServiceClient
from src.services.gateway.session.signed_cookie_session_resolver import SignedCookieSessionResolver
from src.utils.logger_coonfigurator import LoggerConfigurator
from src.utils.path_handler import PathHandler


def main():
    LoggerConfigurator.config_logger()
    load_dotenv(dotenv_path=PathHandler.dot_env(), override=False)

    internal_client = InternalServiceClient(
        game_service_base_url=os.environ["GAME_SERVICE_BASE_URL"],
        catalog_service_base_url=os.environ["CATALOG_SERVICE_BASE_URL"],
        render_service_base_url=os.environ["RENDER_SERVICE_BASE_URL"],
        timeout_seconds=int(os.environ["INTERNAL_HTTP_TIMEOUT_SECONDS"]),
    )
    session_resolver = SignedCookieSessionResolver(os.environ["SESSION_COOKIE_SECRET"])
    app = create_app(internal_client, session_resolver)
    uvicorn.run(app,
                host=os.environ["API_HOST"],
                port=int(os.environ["API_PORT"]))


if __name__ == '__main__':
    main()
