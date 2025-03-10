#!/usr/bin/env python3

import os
import re
import subprocess
from pathlib import Path

def sanitize(s: str) -> str:
    s = re.sub(r'[^a-zA-Z0-9]', '-', s)
    s = re.sub(r'-+', '-', s)
    s = s.strip('-')
    return s.lower()

class ModelSetup:
    def __init__(self, openai_url:str, openai_token:str, model_name:str, provider_abr:str):
        self.openai_url = openai_url
        self.openai_token = openai_token
        self.model_name = model_name
        self.provider_abr = provider_abr

class OpenRouterModelSetup(ModelSetup):
    def __init__(self, model_name:str):
        super().__init__(
            "https://openrouter.ai/api/v1",
            os.environ["OPENROUTER_API_KEY"],
            model_name,
            "OR")


MODELS:list[ModelSetup] = [
    OpenRouterModelSetup("deepseek/deepseek-r1:free")
]

def main():
    runs_temp = Path("./runs_temp")
    for dir_path in runs_temp.iterdir():
        if not dir_path.is_dir():
            continue

        for model in MODELS:
            safe_model = sanitize(f'{model.model_name}_{model.provider_abr}')
            prompt_template = dir_path / "prompt.txt"
            output_dir = dir_path / f"out_{safe_model}"
            output_file = output_dir / "mapping.json"

            output_dir.mkdir(parents=True, exist_ok=True)

            if not prompt_template.exists():
                print(f"Warning: Missing prompt template in {dir_path}")
                continue

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
                    "--comment_placeholder", "<STRUCTURE-BELOW-IS-TO-BE-DOCUMENTED>",
                    "--prompt_template", str(prompt_template)
                ], check=True)

                subprocess.run([
                    "./generate_doctest.py",
                    "app.eo",
                    str(output_file),
                    "# <STRUCTURE-BELOW-IS-TO-BE-DOCUMENTED>"
                ], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error processing {dir_path.name}: {e}")

if __name__ == "__main__":
    main()
