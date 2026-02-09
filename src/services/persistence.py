import mysql.connector
import json
from src.config import Config
from typing import Dict, Any

class PersistenceLayer:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            port=Config.MYSQL_PORT
        )
        self.cursor = self.conn.cursor(dictionary=True)
        self._init_db()

    def _init_db(self):
        """
        Create database and table if not exists.
        """
        # Create DB if strictly needed, but usually we connect to a server.
        # Assuming database exists or we create it.
        # Ideally, we connect to server first, ensure DB exists, then use it.
        # For blueprint simplicity, we assume DB 'kpi_agent_db' might need creation.
        
        # Note: To create DB, we need a connection without database specified or handle it.
        # Here we just ensure the table exists in the current DB context.
        try:
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DATABASE}")
            self.conn.database = Config.MYSQL_DATABASE
        except mysql.connector.Error as err:
            print(f"Database error: {err}")

        # Create generic table for analysis sessions
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                session_id VARCHAR(255) PRIMARY KEY,
                data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def save_session(self, session_id: str, data: Dict[str, Any]):
        """
        Save the entire analysis result (KPIs, Cards, Data) to MySQL as JSON.
        """
        sql = """
            INSERT INTO analysis_results (session_id, data)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE data = %s
        """
        json_data = json.dumps(data)
        self.cursor.execute(sql, (session_id, json_data, json_data))
        self.conn.commit()
        print(f"Saved session {session_id} to MySQL")

    def get_session(self, session_id: str) -> Dict[str, Any]:
        sql = "SELECT data FROM analysis_results WHERE session_id = %s"
        self.cursor.execute(sql, (session_id,))
        result = self.cursor.fetchone()
        if result and result['data']:
            # mysql-connector might return dict or string depending on version
            if isinstance(result['data'], str):
                return json.loads(result['data'])
            return result['data']
        return None
