#!/usr/bin/env python3

import os
import subprocess
import multiprocessing
from pathlib import Path
import sys
import time
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
import json
from utils import *

def main():
    dirs_to_skip = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    total_model_dirs = len(get_all_model_subdirectories())
    for model_dir_no, model_dir_path in list(enumerate(get_all_model_subdirectories()))[dirs_to_skip:]:
        print(f"Grading model dir #{model_dir_no}/{total_model_dirs}")
        time.sleep(0.5)
        eo_file = "app.eo"
        generated_mapping_file = model_dir_path / "mapping.json"
        generated_mapping_content:list[str] = json.loads(open(generated_mapping_file).read())
        eo_file_content = open(eo_file).read()

        for i, _ in enumerate(generated_mapping_content):
            correct_mark_start = find_nth_substr(eo_file_content, f'# {COMMENT_PLACEHOLDER}', i + 1)
            correct_mark_line = eo_file_content[:correct_mark_start].count('\n')
            
            app_file = model_dir_path / str(i) / "app.eo"
            manual_grade_file = model_dir_path / str(i) / "grade" / "manual.txt"

            if not manual_grade_file.exists():
                default_manual_grade_file = \
                    "Accuracy: x\n" + \
                    "Completeness: x\n" + \
                    "Relevance: x\n" + \
                    "Understandability: x\n" + \
                    "Formatting: x\n"
                os.makedirs(manual_grade_file.parent, exist_ok=True)
                open(manual_grade_file, 'w').write(default_manual_grade_file)

            subprocess.call(
                    f"dev +{correct_mark_line} {app_file} {manual_grade_file}",
                    shell=True)

if __name__ == "__main__":
    main()
