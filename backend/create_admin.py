import getpass
import sys

from app.db.session import SessionLocal
from app.schemas.user import UserCreate, UserRole
from app.services.user import (
    UsernameAlreadyExistsError,
    UserService,
)


def main() -> None:
    username = input("Nom administrateur : ").strip()
    password = getpass.getpass("Mot de passe : ")
    confirmation = getpass.getpass(
        "Confirmation : "
    )

    if password != confirmation:
        print("Les mots de passe ne correspondent pas.")
        raise SystemExit(1)

    db = SessionLocal()

    try:
        user = UserService().create_user(
            db,
            UserCreate(
                username=username,
                password=password,
                role=UserRole.admin,
            ),
        )

        print(
            f"Administrateur créé : "
            f"{user.username} ({user.id})"
        )

    except UsernameAlreadyExistsError:
        print("Ce nom d'utilisateur existe déjà.")
        raise SystemExit(1)

    finally:
        db.close()


if __name__ == "__main__":
    main()
