#
# import sqlite3
# from datetime import datetime, date
# import bcrypt
# import os
#
# # Fix for SQLite date adapter deprecation in Python 3.12+
# def adapt_date_iso(val):
#     """Adapt datetime.date to ISO 8601 date."""
#     return val.isoformat()
#
# def adapt_datetime_iso(val):
#     """Adapt datetime.datetime to ISO 8601 date."""
#     return val.isoformat()
#
# def convert_date(val):
#     """Convert ISO 8601 date to datetime.date object."""
#     return datetime.strptime(val.decode(), '%Y-%m-%d').date()
#
# def convert_datetime(val):
#     """Convert ISO 8601 datetime to datetime.datetime object."""
#     try:
#         return datetime.strptime(val.decode(), '%Y-%m-%d %H:%M:%S')
#     except ValueError:
#         return datetime.strptime(val.decode(), '%Y-%m-%d %H:%M:%S.%f')
#
# def convert_timestamp(val):
#     """Convert timestamp to datetime object."""
#     return datetime.fromisoformat(val.decode())
#
# # Register the adapters and converters
# sqlite3.register_adapter(datetime, adapt_datetime_iso)
# sqlite3.register_adapter(date, adapt_date_iso)
# sqlite3.register_converter("date", convert_date)
# sqlite3.register_converter("datetime", convert_datetime)
# sqlite3.register_converter("timestamp", convert_timestamp)
# sqlite3.register_converter("TIMESTAMP", convert_timestamp)
#
# def get_db_connection():
#     """Get database connection with proper configuration"""
#     conn = sqlite3.connect('water_tracker.db', detect_types=sqlite3.PARSE_DECLTYPES)
#     conn.row_factory = sqlite3.Row
#     # Enable foreign keys
#     conn.execute("PRAGMA foreign_keys = ON")
#     return conn
#
# def hash_password(password):
#     return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
#
# def check_password(password, hashed):
#     return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
#
# def init_db():
#     """Initialize database with all required tables"""
#     conn = get_db_connection()
#     c = conn.cursor()
#
#     # Create users table
#     c.execute('''CREATE TABLE IF NOT EXISTS users
#                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
#                   username TEXT UNIQUE NOT NULL,
#                   email TEXT UNIQUE NOT NULL,
#                   password TEXT NOT NULL,
#                   daily_goal INTEGER DEFAULT 2000,
#                   weight_kg REAL,
#                   activity_level TEXT DEFAULT 'moderate',
#                   theme TEXT DEFAULT 'light',
#                   email_notifications BOOLEAN DEFAULT 1,
#                   reminder_frequency TEXT DEFAULT 'daily',
#                   role TEXT DEFAULT 'user',
#                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
#
#     # Create water intake table with better indexing
#     c.execute('''CREATE TABLE IF NOT EXISTS water_intake
#                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
#                   user_id INTEGER NOT NULL,
#                   amount INTEGER NOT NULL,
#                   timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                   FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE)''')
#
#     # Create achievements table
#     c.execute('''CREATE TABLE IF NOT EXISTS achievements
#                  (id INTEGER PRIMARY KEY,
#                   name TEXT NOT NULL,
#                   description TEXT NOT NULL,
#                   icon TEXT NOT NULL,
#                   condition TEXT NOT NULL)''')
#
#     # Create user_achievements table with CASCADE delete
#     c.execute('''CREATE TABLE IF NOT EXISTS user_achievements
#                  (user_id INTEGER,
#                   achievement_id INTEGER,
#                   unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                   PRIMARY KEY (user_id, achievement_id),
#                   FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
#                   FOREIGN KEY (achievement_id) REFERENCES achievements (id) ON DELETE CASCADE)''')
#
#     # Create email logs table with CASCADE delete
#     c.execute('''CREATE TABLE IF NOT EXISTS email_logs
#                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
#                   user_id INTEGER NOT NULL,
#                   email_type TEXT NOT NULL,
#                   sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                   status TEXT DEFAULT 'sent',
#                   FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE)''')
#
#     # Insert default achievements
#     achievements = [
#         (1, 'First Step', 'Log your first water intake', '🚰', 'first_log'),
#         (2, 'Hydration Novice', 'Reach daily goal 3 days in a row', '⭐', 'streak_3'),
#         (3, 'Water Master', 'Reach daily goal 7 days in a row', '🏆', 'streak_7'),
#         (4, 'Overachiever', 'Drink 3000ml in one day', '💪', 'overachieve'),
#         (5, 'Consistent', 'Log water for 5 consecutive days', '📅', 'consistent_5'),
#         (6, 'Early Bird', 'Log water before 8 AM', '🌅', 'early_bird'),
#         (7, 'Week Warrior', 'Complete weekly goal', '🔋', 'week_warrior'),
#     ]
#     c.executemany('INSERT OR IGNORE INTO achievements VALUES (?, ?, ?, ?, ?)', achievements)
#
#     # Create indexes for better performance
#     c.execute('CREATE INDEX IF NOT EXISTS idx_water_intake_user_date ON water_intake(user_id, DATE(timestamp))')
#     c.execute('CREATE INDEX IF NOT EXISTS idx_water_intake_timestamp ON water_intake(timestamp)')
#     c.execute('CREATE INDEX IF NOT EXISTS idx_email_logs_user_date ON email_logs(user_id, DATE(sent_at))')
#     c.execute('CREATE INDEX IF NOT EXISTS idx_user_achievements_user ON user_achievements(user_id)')
#
#     # MIGRATION: Add role column if it doesn't exist
#     try:
#         c.execute("SELECT role FROM users LIMIT 1")
#     except sqlite3.OperationalError:
#         c.execute('ALTER TABLE users ADD COLUMN role TEXT DEFAULT "user"')
#         print("Added role column to users table")
#
#     # MIGRATION: Add other columns if they don't exist
#     try:
#         c.execute("SELECT email_notifications FROM users LIMIT 1")
#     except sqlite3.OperationalError:
#         c.execute('ALTER TABLE users ADD COLUMN email_notifications BOOLEAN DEFAULT 1')
#         c.execute('ALTER TABLE users ADD COLUMN reminder_frequency TEXT DEFAULT "daily"')
#         print("Added email notification columns to users table")
#
#     # Create default admin user if it doesn't exist
#     c.execute('SELECT id FROM users WHERE username = "admin"')
#     if not c.fetchone():
#         c.execute(
#             'INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
#             ('admin', 'admin@hydrotrack.com', hash_password('admin123'), 'admin')
#         )
#         print("Default admin user created: username='admin', password='admin123'")
#
#     conn.commit()
#     conn.close()
#     print("Database initialized successfully!")

import mysql.connector
from mysql.connector import Error
import bcrypt
import os
from datetime import datetime, date


class Database:
    def __init__(self):
        self.host = os.getenv('MYSQL_HOST', 'localhost')
        self.database = os.getenv('MYSQL_DATABASE', 'hydrotracker')
        self.user = os.getenv('MYSQL_USER', 'root')
        self.password = os.getenv('MYSQL_PASSWORD', '')
        self.connection = None

    def get_connection(self):
        """Get database connection"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connection = mysql.connector.connect(
                    host=self.host,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                    autocommit=True
                )
            return self.connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None

    def execute_query(self, query, params=None, fetch=False):
        """Execute a query and return results if fetch=True"""
        conn = self.get_connection()
        if not conn:
            return None

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                conn.commit()
                return cursor.lastrowid
        except Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            cursor.close()

    def execute_one(self, query, params=None):
        """Execute a query and return single result"""
        conn = self.get_connection()
        if not conn:
            return None

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            cursor.close()


# Global database instance
db = Database()


def get_db_connection():
    """Get database connection for compatibility with existing code"""
    return db


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def init_db():
    """Initialize database - for MySQL, we assume the schema is already created"""
    try:
        # Test connection and print success message
        conn = db.get_connection()
        if conn and conn.is_connected():
            print("✅ MySQL database connected successfully!")

            # Verify tables exist
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"📊 Found {len(tables)} tables in database")
            cursor.close()

            return True
        else:
            print("❌ Failed to connect to MySQL database")
            return False
    except Error as e:
        print(f"❌ Error initializing database: {e}")
        return False