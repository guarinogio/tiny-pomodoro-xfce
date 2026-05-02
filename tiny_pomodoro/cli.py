import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=DeprecationWarning)

from .app import main


def main_cli():
    main(Path(__file__).resolve())


def main():
    main_cli()
