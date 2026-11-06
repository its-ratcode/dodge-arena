"""Entry point: ``python -m app``."""

from app.meta import APP_NAME, VERSION


def main() -> None:
    print(f"{APP_NAME} {VERSION}")


if __name__ == "__main__":
    main()
