import os
from dataclasses import dataclass
from dotenv import load_dotenv, set_key, find_dotenv

# Run once when the module is imported
DOTENV_PATH = find_dotenv(raise_error_if_not_found=True)
if DOTENV_PATH:
    load_dotenv(DOTENV_PATH, override=True)

@dataclass(frozen = True)
class ProgramSettings:


    @staticmethod
    def get_setting(key: str) -> str | None:
        return os.environ.get(key)


    @staticmethod
    def set_setting(key: str, value: str) -> None:
        os.environ[key] = value
        set_key(DOTENV_PATH, key, value)
