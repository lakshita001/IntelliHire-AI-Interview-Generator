from database.db import get_db

class Interview:
    @staticmethod
    def create(user_id, company, domain, subdomain, level, num_questions):
        conn = get_db()
        cur = conn.execute(
            "INSERT INTO interviews (user_id, company_name, domain, subdomain, level, num_questions) VALUES (?,?,?,?,?,?)",
            (user_id, company, domain, subdomain, level, num_questions)
        )
        conn.commit()
        iid = cur.lastrowid
        conn.close()
        return iid

    @staticmethod
    def get_by_user(user_id):
        conn = get_db()
        rows = conn.execute(
            "SELECT * FROM interviews WHERE user_id = ? ORDER BY date DESC", (user_id,)
        ).fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_by_id(interview_id):
        conn = get_db()
        row = conn.execute("SELECT * FROM interviews WHERE id = ?", (interview_id,)).fetchone()
        conn.close()
        return row
