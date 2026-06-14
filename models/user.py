from database.db import get_db

class User:
    def __init__(self, id, name, email, is_admin=0):
        self.id = id
        self.name = name
        self.email = email
        self.is_admin = is_admin
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return str(self.id)

    @staticmethod
    def get_by_id(user_id):
        conn = get_db()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        if not row:
            return None
        return User(row["id"], row["name"], row["email"], row["is_admin"])

    @staticmethod
    def get_by_email(email):
        conn = get_db()
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        return row

    @staticmethod
    def get_all_users():
        conn = get_db()
        rows = conn.execute("""
            SELECT u.id, u.name, u.email, u.created_at,
                   COUNT(i.id) as interview_count,
                   MAX(i.date) as last_interview
            FROM users u
            LEFT JOIN interviews i ON u.id = i.user_id
            GROUP BY u.id
            ORDER BY u.created_at DESC
        """).fetchall()
        conn.close()
        return rows

    @staticmethod
    def search_users(query):
        conn = get_db()
        rows = conn.execute("""
            SELECT u.id, u.name, u.email, u.created_at,
                   COUNT(i.id) as interview_count,
                   MAX(i.date) as last_interview
            FROM users u
            LEFT JOIN interviews i ON u.id = i.user_id
            WHERE u.name LIKE ? OR u.email LIKE ?
            GROUP BY u.id
            ORDER BY u.created_at DESC
        """, (f"%{query}%", f"%{query}%")).fetchall()
        conn.close()
        return rows

    @staticmethod
    def make_admin(email):
        conn = get_db()
        conn.execute("UPDATE users SET is_admin = 1 WHERE email = ?", (email,))
        conn.commit()
        conn.close()