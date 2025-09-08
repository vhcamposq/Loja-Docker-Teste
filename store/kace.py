import os
from typing import Optional

import pymysql
from dotenv import load_dotenv


class KaceClient:
    def __init__(self):
        # Load .env once when the module/class is used (safe and idempotent)
        load_dotenv()
        self.host = os.getenv("KACE_DB_HOST")
        self.port = int(os.getenv("KACE_DB_PORT", "3306"))
        self.db = os.getenv("KACE_DB_NAME")
        self.user = os.getenv("KACE_DB_USER")
        self.password = os.getenv("KACE_DB_PASSWORD")
        self.ssl_ca = os.getenv("KACE_DB_SSL_CA")  # optional

    def get_connection(self):
        kwargs = {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "database": self.db,
            "cursorclass": pymysql.cursors.DictCursor,
            "connect_timeout": 5,
            "read_timeout": 5,
            "write_timeout": 5,
            "charset": "utf8mb4",
            "autocommit": True,
        }
        if self.ssl_ca:
            kwargs["ssl"] = {"ca": self.ssl_ca}
        return pymysql.connect(**kwargs)

    def get_latest_hostname_for_user(self, username: str) -> Optional[str]:
        """
        Returns the most recent MACHINE.NAME for the given username matched against MACHINE.USER_LOGGED
        using a LIKE pattern. The most recent is determined by LAST_INVENTORY DESC.
        """
        if not username:
            return None
        # Normalize expected username (strip domain if given)
        if "@" in username:
            username = username.split("@")[0]

        sql = (
            "SELECT NAME AS HOSTNAME FROM MACHINE "
            "WHERE USER_LOGGED LIKE %s "
            "ORDER BY LAST_INVENTORY DESC "
            "LIMIT 1"
        )
        like_param = f"%{username}%"
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (like_param,))
                    row = cur.fetchone()
                    if row and row.get("HOSTNAME"):
                        return row["HOSTNAME"]
        except Exception:
            # Intentionally swallow errors here; caller will handle fallback.
            return None
        return None


def get_latest_hostname_for_user(username: str) -> Optional[str]:
    """Functional wrapper for convenience."""
    client = KaceClient()
    return client.get_latest_hostname_for_user(username)
