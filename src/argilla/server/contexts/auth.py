from sqlalchemy import select
from argilla.server.database import SessionLocal
from argilla.server.models.user import User
from passlib.context import CryptContext

_CRYPT_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_username(username):
  session = SessionLocal()

  return session.scalar(select(User).where(User.username == username))

def authenticate_user(username, password):
  user = get_user_by_username(username)

  # TODO: Avoid time attacks where user is not present
  if user and _verify_password(password, user.password_hash):
    return user


def _verify_password(password, hashed_password):
  return _CRYPT_CONTEXT.verify(password, hashed_password)
