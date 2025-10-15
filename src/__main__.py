"""Top-level entrypoint for the package."""
from .etl import config


def main():
    print("EPL DW package. Run specific ETL modules, e.g., python -m src.etl.main")


if __name__ == "__main__":
    main()
