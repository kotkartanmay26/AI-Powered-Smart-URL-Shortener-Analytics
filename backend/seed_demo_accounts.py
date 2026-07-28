from app.core.database import SessionLocal, create_tables
from app.core.security import get_password_hash
from sqlalchemy import or_

from app.models.user import User


DEMO_ACCOUNTS = [
    {
        "email": "demo.admin@example.com",
        "username": "demo_admin",
        "full_name": "Demo Admin",
        "password": "Admin@12345",
        "is_admin": True,
    },
    {
        "email": "demo.user@example.com",
        "username": "demo_user",
        "full_name": "Demo User",
        "password": "User@12345",
        "is_admin": False,
    },
]


def upsert_demo_accounts() -> None:
    create_tables()
    db = SessionLocal()
    try:
        for account in DEMO_ACCOUNTS:
            user = (
                db.query(User)
                .filter(or_(User.email == account["email"], User.username == account["username"]))
                .first()
            )
            if not user:
                user = User(email=account["email"], username=account["username"])
                db.add(user)
            user.email = account["email"]
            user.username = account["username"]
            user.full_name = account["full_name"]
            user.hashed_password = get_password_hash(account["password"])
            user.is_active = True
            user.is_admin = account["is_admin"]
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    upsert_demo_accounts()
    for account in DEMO_ACCOUNTS:
        role = "Admin" if account["is_admin"] else "User"
        print(f"{role}: {account['email']} / {account['username']} / {account['password']}")
