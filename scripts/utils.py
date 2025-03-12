from pathlib import Path
import re

ALL_OUTPUT_START = "<ALL-OUTPUT-START>"
MEANINGFUL_OUTPUT_START = "<MEANINGFUL-OUTPUT-START>"

ALL_OUTPUT_END = "<ALL-OUTPUT-END>"
MEANINGFUL_OUTPUT_END = "<MEANINGFUL-OUTPUT-END>"

COMMENT_PLACEHOLDER = "<STRUCTURE-BELOW-IS-TO-BE-DOCUMENTED>"

ansi_re = re.compile(r'\x1b\[[0-9;]*m')

def without_ansi_marks(text: str) -> str:
    return re.sub(ansi_re, '', text)

def non_excluded_subdirectories(dir_path: Path)-> list[Path]:
    return list([i for i in dir_path.iterdir() if 
        i.is_dir() 
        and ('node_modules' not in i.name)
        and (not i.name.startswith("."))
    ])

def get_all_model_subdirectories() -> list[Path]:
    directories = []
    runs_temp = Path("./runs_temp")
    for dir_path in non_excluded_subdirectories(runs_temp):
        for model_dir_path in non_excluded_subdirectories(dir_path):
            directories.append(model_dir_path)
    return directories


def sanitize(s: str) -> str:
    s = re.sub(r'[^a-zA-Z0-9]', '-', s)
    s = re.sub(r'-+', '-', s)
    s = s.strip('-')
    return s.lower()

def find_nth_substr(original_text: str, substr_to_find: str, n: int) -> int:
    start = original_text.find(substr_to_find)
    while start >= 0 and n > 1:
        start = original_text.find(substr_to_find, start+len(substr_to_find))
        n -= 1
    return start
