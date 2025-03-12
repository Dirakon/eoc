#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
from utils import *

START_NOT_FOUND = -1
END_NOT_FOUND = -2

GRADE_NO_DOCTEST = 0
GRADE_COMPILATION_ERROR = 1
GRADE_RUNTIME_ERROR = 2
GRADE_WRONG_OUTPUT = 3
GRADE_CORRECT_OUTPUT = 4

def try_extract_meaningful_output(original_text: str) -> str | int:
    if not ALL_OUTPUT_START in original_text:
        # Assuming no error - already truncated
        return original_text
    segment_start = original_text.find(MEANINGFUL_OUTPUT_START)
    segment_end = original_text.find(MEANINGFUL_OUTPUT_END)
    if segment_start < 0:
        return START_NOT_FOUND
    if segment_end < 0:
        return END_NOT_FOUND
    raise Exception(f"Both marks are found, which should be impossible:\n{original_text}") 

def write_doctest_grade(path: Path, grade: int):
    if path.exists():
        os.remove(path)
    open(path, "w").write(str(grade))


def grade_single_doctest(dir_path: Path):
    eo_file_path = dir_path / "app.eo"
    expected_output_path = dir_path / "expected.txt"
    actual_output_path = dir_path / "actual.txt"
    grade_path = dir_path / "grade" / "doctest.txt"
    os.makedirs(grade_path.parent, exist_ok=True)
    if not eo_file_path.exists() or \
        not expected_output_path.exists() or \
        not actual_output_path.exists():
        write_doctest_grade(grade_path, GRADE_NO_DOCTEST)
        return

    expected_content = open(expected_output_path).read()
    actual_content = try_extract_meaningful_output(open(actual_output_path).read())

    if type(actual_content) is int:
        write_doctest_grade(
                grade_path, 
                GRADE_COMPILATION_ERROR \
                    if actual_content == START_NOT_FOUND \
                    else GRADE_RUNTIME_ERROR)
    elif type(actual_content) is str:
        write_doctest_grade(
            grade_path, 
            GRADE_CORRECT_OUTPUT \
                if actual_content.strip() == expected_content.strip() \
                else GRADE_WRONG_OUTPUT)


def main():
    colorama_init()
    for model_dir_path in get_all_model_subdirectories():
        for single_doctest_dir in non_excluded_subdirectories(model_dir_path):
            grade_single_doctest(single_doctest_dir)

if __name__ == "__main__":
    main()
