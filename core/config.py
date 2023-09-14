import os

from dotenv import load_dotenv
from pydantic import BaseConfig

load_dotenv()


class GlobalConfig(BaseConfig):
    title: str = os.environ.get("TITLE")
    version: str = "1.0.0"
    description: str = os.environ.get("DESCRIPTION")
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    api_prefix: str = "/api/blocklist"
    valid_api_keys: dict = {
        "view": [i for i in os.environ.get("VIEW_API_KEYS").split(" ")],
        "edit": [i for i in os.environ.get("EDIT_API_KEYS").split(" ")],
    }
    fastapi_port: os.environ.get("FASTAPI_PORT")
    debug: bool = os.environ.get("DEBUG")
    postgres_user: str = os.environ.get("POSTGRES_USER")
    postgres_password: str = os.environ.get("POSTGRES_PASSWORD")
    postgres_server: str = os.environ.get("POSTGRES_SERVER")
    postgres_port: int = int(os.environ.get("POSTGRES_PORT"))
    postgres_db: str = os.environ.get("POSTGRES_DB")
    db_echo_log: bool = True if os.environ.get("DEBUG") == "True" else False
    alchemy_api_key: str = os.environ.get("ALCHEMY_API_KEY")
    google_api_key: str = os.environ.get("GOOGLE_API_KEY")
    mnemonichq_api_key: str = os.environ.get("MNEMONICHQ_API_KEY")
    camo_key: str = os.environ.get("CAMO_KEY")
    domain: str = os.environ.get("DOMAIN")
    tags_metadata: dict = [
        {
            "name": "Wallet Addresses",
            "description": "Information about an NFT address. ETH / Polygon only.",
        },
        {
            "name": "NFT Contracts",
            "description": "Information about NFT contracts marked as spam or malicious.",
        },
        {
            "name": "Domains",
            "description": "Information about domains marked as malicious. Input should exclude `http://` and `https://`",
        },
        {
            "name": "Encode / Decode Urls",
            "description": "Encode Urls to hex string, and use the hex string for accessing for image/audio/video/json content through a reverse proxy",
        },
    ]

    @property
    def sync_database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"

    @property
    def async_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"

    @property
    def sync_database_url_local(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@localhost:{self.postgres_port}/{self.postgres_db}"

    @property
    def async_database_url_local(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@localhost:{self.postgres_port}/{self.postgres_db}"


settings = GlobalConfig()
