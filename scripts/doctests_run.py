#!/usr/bin/env python3

import os
import subprocess
import multiprocessing
from pathlib import Path
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
from utils import *

def try_extract_meaningful_output(original_text: str, path: Path) -> str:
    marked_text = ALL_OUTPUT_START + original_text + ALL_OUTPUT_END
    segment_start = marked_text.find(MEANINGFUL_OUTPUT_START)
    segment_end = marked_text.find(MEANINGFUL_OUTPUT_END)
    if segment_end < 0 or segment_start < 0:
        print(f"Cannot find segment start or end in {path}")
        return marked_text
    segment = marked_text[segment_start + len(MEANINGFUL_OUTPUT_START):segment_end].strip()
    return segment

def process_single_doctest(dir_path: Path):
    eo_file_path = dir_path / "app.eo"
    expected_output_path = dir_path / "expected.txt"
    stdin_path = dir_path / "stdin.txt"
    if not eo_file_path.exists():
        raise Exception(f"{eo_file_path} does not exist")
    if not expected_output_path.exists():
        raise Exception(f"{expected_output_path} does not exist")
    stdin_content = "" if not stdin_path.exists() else open(stdin_path).read()

    output_file = dir_path / "actual.txt"
    if output_file.exists():
        os.remove(output_file)
    subprocess.run([
        "npx", "eoc", "clean", "--global"
    ], 
                   check=False,
                   cwd=dir_path)

    link_result = subprocess.run([
        "npx", "eoc", "link"
    ], 
                                 check=False,
                                 cwd=dir_path,
                                 capture_output=True,
                                 text=True)
    dataize_result = subprocess.run([
        "npx", "eoc", "dataize", "--alone", "doctest-entry"
    ], 
                                    check=False,
                                    cwd=dir_path,
                                    capture_output=True,
                                    text=True,
                                    input=stdin_content + "\n")
    print(dataize_result.stdout)
    if dataize_result.stderr is not None:
        print(Fore.RED + dataize_result.stderr + Style.RESET_ALL)
    if link_result.stderr is not None:
        print(Fore.RED + link_result.stderr + Style.RESET_ALL)
    open(output_file, 'w').write(
        try_extract_meaningful_output(
            without_ansi_marks(
                link_result.stdout + 
                    ("" if link_result.stderr is None else f'\n{link_result.stderr}') +
                    '\n' +
                    dataize_result.stdout + 
                    ("" if dataize_result.stderr is None else f'\n{dataize_result.stderr}')),
            output_file))

def main():
    colorama_init()
    for model_dir_path in get_all_model_subdirectories():
        for single_doctest_dir in non_excluded_subdirectories(model_dir_path):
            print(f'Running doctest from {single_doctest_dir}...')
            try:
                p = multiprocessing.Process(target=process_single_doctest, args=[single_doctest_dir])
                p.start()

                # Wait for 3 minutes or until process finishes
                p.join(180)

                # If thread is still active
                if p.is_alive():
                    print("KILLING PROCESS")
                    p.kill()
            except Exception as e:
                print(f"Error processing {single_doctest_dir}: {e}")

if __name__ == "__main__":
    main()
