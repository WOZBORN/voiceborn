from src.models import Base, engine, SessionLocal
from src.models.user import User
from datetime import datetime, timedelta


LIMIT_DAYS = 30


def init_db():
    Base.metadata.create_all(bind=engine)


def ensure_user_exists(user_id: int):
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if not user:
            user = User(telegram_id=user_id)
            session.add(user)
            session.commit()


def increment_limit_usage(user_id: int, length: int):
    with SessionLocal() as session:
        user = session.get(User, user_id)
        user.limit_usage += length
        session.commit()


def check_and_reset_limit_if_expired(user: User) -> tuple[bool, int]:
    now = datetime.utcnow()
    with SessionLocal() as session:
        if user.limit_renew_date:
            delta = now - user.limit_renew_date
            if delta > timedelta(days=LIMIT_DAYS):
                user.limit_usage = 0
                user.limit_renew_date = now
                session.commit()
                return True, LIMIT_DAYS
            else:
                days_left = LIMIT_DAYS - delta.days
                return False, max(days_left, 0)
        else:
            # Если почему-то дата отсутствует — инициализируем
            user.limit_renew_date = now
            session.commit()
            return False, LIMIT_DAYS


def has_enough_limit(user_id: int, text: str = "") -> tuple[bool, int, int]:
    with SessionLocal() as session:
        user = session.get(User, user_id)

        was_reset, _ = check_and_reset_limit_if_expired(user)

        usage = user.limit_usage
        limit = user.limit
        if usage + len(text) >= limit:
            return False, usage, limit
        return True, usage, limit


if __name__ == "__main__":
    init_db()