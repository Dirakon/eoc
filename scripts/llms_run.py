#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple
from utils import *

MAX_CONCURRENT_TASKS = 6  # Configurable concurrency limit

class ModelSetup:
    def __init__(self, openai_url: str, openai_token: str, model_name: str, provider_abr: str):
        self.openai_url = openai_url
        self.openai_token = openai_token
        self.model_name = model_name
        self.provider_abr = provider_abr

class OpenRouterModelSetup(ModelSetup):
    def __init__(self, model_name: str):
        super().__init__(
            "https://openrouter.ai/api/v1",
            os.environ["OPENROUTER_API_KEY"],
            model_name,
            "OR")

MODELS: list[ModelSetup] = [
    # OpenRouterModelSetup("deepseek/deepseek-r1"),
    # OpenRouterModelSetup("anthropic/claude-3.7-sonnet"),
    OpenRouterModelSetup("meta-llama/llama-3.3-70b-instruct"),
    OpenRouterModelSetup("qwen/qwq-32b"),
    OpenRouterModelSetup("google/gemini-2.0-flash-lite-001"),
    OpenRouterModelSetup("google/gemini-2.0-flash-001"),


    # Free:
    # OpenRouterModelSetup("deepseek/deepseek-r1:free"), # Output gets cut off cuz too long
    # OpenRouterModelSetup("google/gemini-2.0-flash-thinking-exp:free"),
    # OpenRouterModelSetup("google/gemini-2.0-pro-exp-02-05:free"),
]

def process_dir_model(dir_path: Path, model: ModelSetup) -> None:
    safe_model = sanitize(f'{model.model_name}_{model.provider_abr}')
    prompt_template = dir_path / "prompt.txt"
    output_dir = dir_path / f"out_{safe_model}"
    output_file = output_dir / "mapping.json"

    output_dir.mkdir(parents=True, exist_ok=True)

    if not prompt_template.exists():
        print(f"Warning: Missing prompt template in {dir_path}")
        return

    print(f"Processing {dir_path.name} with model {model.model_name}")
    try:
        subprocess.run([
            "node", "./src/eoc.js", "generate_comments",
            "--provider", "openai",
            "--openai_model", model.model_name,
            "--openai_token", model.openai_token,
            "--openai_url", model.openai_url,
            "--source", "app.eo",
            "--output", str(output_file),
            "--comment_placeholder", COMMENT_PLACEHOLDER,
            "--prompt_template", str(prompt_template)
        ], check=True)

        subprocess.run([
            "./generate_doctest.py",
            "app.eo",
            str(output_file),
            f"# {COMMENT_PLACEHOLDER}"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error processing {dir_path.name}: {e}")

def unpack_and_process_dir_model(input: Tuple[Path, ModelSetup]):
    dir_path, model = input
    process_dir_model(dir_path, model)

def main():
    runs_temp = Path("./runs_temp")
    inputs = []
    for dir_path in non_excluded_subdirectories(runs_temp):
        for model in MODELS:
            inputs.append((dir_path, model))
    
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_TASKS) as executor:
        executor.map(unpack_and_process_dir_model, inputs)

if __name__ == "__main__":
    main()
