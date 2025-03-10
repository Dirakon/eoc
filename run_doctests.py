#!/usr/bin/env python3

import os
import re
import subprocess
import multiprocessing
import time
from pathlib import Path
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

colorama_init()
def try_extract_meaningful_output(original_text: str, path: Path) -> str:
    segment_start = original_text.find("<START>")
    segment_end = original_text.find("<END>")
    if segment_end < 0 or segment_start < 0:
        print(f"Cannot find segment start or end in {path}")
        return original_text
    segment = original_text[segment_start + len("<START>"):segment_end].strip()
    return segment

def process_single_doctest(dir_path: Path):
    eo_file_path = dir_path / "app.eo"
    expected_output_path = dir_path / "expected.txt"
    if not eo_file_path.exists():
        raise Exception(f"{eo_file_path} does not exist")
    if not expected_output_path.exists():
        raise Exception(f"{expected_output_path} does not exist")

    # expected_output = open(expected_output_path).read()
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
                                    text=True)
    print(dataize_result.stdout)
    if dataize_result.stderr is not None:
        print(Fore.RED + dataize_result.stderr + Style.RESET_ALL)
    if link_result.stderr is not None:
        print(Fore.RED + link_result.stderr + Style.RESET_ALL)
    open(output_file, 'w').write(
        try_extract_meaningful_output(
            link_result.stdout + 
                ("" if link_result.stderr is None else f'\n{link_result.stderr}') +
                '\n' +
                dataize_result.stdout + 
                ("" if dataize_result.stderr is None else f'\n{dataize_result.stderr}'),
            output_file))

def non_excluded_subdirectories(dir_path: Path)-> list[Path]:
    return [i for i in dir_path.iterdir() if 
        i.is_dir() 
        and ('node_modules' not in i.name)
        and (not i.name.startswith("."))
    ]

def main():
    runs_temp = Path("./runs_temp")
    for test_run_dir_path in non_excluded_subdirectories(runs_temp):
        for model_specific_out_dir_path in non_excluded_subdirectories(test_run_dir_path):
            for single_doctest_dir in non_excluded_subdirectories(model_specific_out_dir_path):
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
