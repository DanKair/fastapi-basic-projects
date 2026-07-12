from __future__ import annotations

import argparse
import sys
from pathlib import Path

from fastapi import HTTPException

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.database import SessionLocal  # noqa: E402
from models.users import UserRole  # noqa: E402
from services.users import create_user as create_user_record  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a manager/admin user in the database")
    parser.add_argument("--username", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument(
        "--role",
        required=True,
        choices=[UserRole.MANAGER.value, UserRole.ADMIN.value],
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    db = SessionLocal()
    try:
        user = create_user_record(
            db,
            username=args.username,
            email=args.email,
            password=args.password,
            role=UserRole(args.role),
        )
    except HTTPException as exc:
        print(f"Error: {exc.detail}")
        return 1
    finally:
        db.close()

    print(f"Created user id={user.id} username={user.username} role={user.role}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
