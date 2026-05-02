#!/usr/bin/env python3
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=DeprecationWarning)

from tiny_pomodoro.app import main


if __name__ == "__main__":
    main(Path(__file__).resolve())
