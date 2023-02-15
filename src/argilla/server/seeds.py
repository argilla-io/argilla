from argilla.server.database import SessionLocal
from argilla.server.models import User


def development_seeds():
    session = SessionLocal()

    session.add_all([
        User(
            first_name="John",
            last_name="Doe",
            username="argilla",
            email="john@argilla.io",
            password_hash="$2y$05$eaw.j2Kaw8s8vpscVIZMfuqSIX3OLmxA21WjtWicDdn0losQ91Hw.",
            api_key="1234"
        ),
        User(
            first_name="Tanya",
            last_name="Franklin",
            username="tanya",
            email="tanya@argilla.io",
            password_hash="$2y$05$eaw.j2Kaw8s8vpscVIZMfuqSIX3OLmxA21WjtWicDdn0losQ91Hw.",
            api_key="123456"
        )
    ])

    session.commit()
