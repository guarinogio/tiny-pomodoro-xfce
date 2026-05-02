import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=DeprecationWarning)

from .app import main as run_app


def main():
    run_app(Path(__file__).resolve())
