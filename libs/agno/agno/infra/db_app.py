from __future__ import annotations

from agno.infra.app import ContainerContext, InfraApp, InfraResource  # noqa: F401


class DbApp(InfraApp):
    db_user: str | None = None
    db_password: str | None = None
    db_database: str | None = None
    db_driver: str | None = None

    def get_db_user(self) -> str | None:
        return self.db_user or self.get_secret_from_file("DB_USER")

    def get_db_password(self) -> str | None:
        return self.db_password or self.get_secret_from_file("DB_PASSWORD")

    def get_db_database(self) -> str | None:
        return self.db_database or self.get_secret_from_file("DB_DATABASE")

    def get_db_driver(self) -> str | None:
        return self.db_driver or self.get_secret_from_file("DB_DRIVER")

    def get_db_host(self) -> str | None:
        raise NotImplementedError

    def get_db_port(self) -> int | None:
        raise NotImplementedError

    def get_db_connection(self) -> str | None:
        user = self.get_db_user()
        password = self.get_db_password()
        database = self.get_db_database()
        driver = self.get_db_driver()
        host = self.get_db_host()
        port = self.get_db_port()
        return f"{driver}://{user}:{password}@{host}:{port}/{database}"

    def get_db_host_local(self) -> str | None:
        return "localhost"

    def get_db_port_local(self) -> int | None:
        return self.host_port

    def get_db_connection_local(self) -> str | None:
        user = self.get_db_user()
        password = self.get_db_password()
        database = self.get_db_database()
        driver = self.get_db_driver()
        host = self.get_db_host_local()
        port = self.get_db_port_local()
        return f"{driver}://{user}:{password}@{host}:{port}/{database}"
