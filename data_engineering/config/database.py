"""
Database Configuration and Connection Management
"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from loguru import logger

load_dotenv()

class DatabaseConfig:
    """Database configuration and connection management"""
    
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', '127.0.0.1'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'crypto_db'),
            'user': os.getenv('DB_USER', 'crypto_user'),
            'password': os.getenv('DB_PASSWORD', '')
        }
        self.conn = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.config)
            logger.info("✅ Database connection established")
            return self.conn
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def get_cursor(self, dict_cursor=True):
        """Get database cursor"""
        if not self.conn or self.conn.closed:
            self.connect()
        
        if dict_cursor:
            return self.conn.cursor(cursor_factory=RealDictCursor)
        return self.conn.cursor()
    
    def execute_script(self, script_path):
        """Execute SQL script from file"""
        try:
            with open(script_path, 'r') as file:
                sql_script = file.read()
            
            cursor = self.get_cursor(dict_cursor=False)
            cursor.execute(sql_script)
            self.conn.commit()
            logger.info(f"✅ Executed script: {script_path}")
        except Exception as e:
            logger.error(f"❌ Script execution failed: {e}")
            if self.conn:
                self.conn.rollback()
            raise
    
    def execute_query(self, query, params=None, fetch=True):
        """Execute a SQL query"""
        try:
            cursor = self.get_cursor(dict_cursor=True)
            cursor.execute(query, params)
            
            if fetch:
                return cursor.fetchall()
            else:
                self.conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            if self.conn:
                self.conn.rollback()
            raise
    
    def close(self):
        """Close database connection"""
        if self.conn and not self.conn.closed:
            self.conn.close()
            logger.info("🔒 Database connection closed")