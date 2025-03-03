#!/usr/bin/env bash

# OLLAMA_MODELS=("llama3.2:3b" "deepseek-r1:8b")
OLLAMA_MODELS=("deepseek-r1:8b")

# Find all subdirectories in runs_temp
find ./runs_temp -mindepth 1 -maxdepth 1 -type d | while read -r dir; do
    # Process each model for the current directory
    for model in "${OLLAMA_MODELS[@]}"; do
	# Sanitize model name for filename by replacing ':' with '-'
	safe_model="${model//:/-}"
	
	# Construct paths with proper quoting
	output_file="${dir}/out_${safe_model}.json"
	prompt_template="${dir}/prompt.txt"
	
	# Run the command if prompt template exists
	if [ -f "$prompt_template" ]; then
	    echo "Processing $(basename "$dir") with model $model"
	    node ./src/eoc.js generate_comments \
		--provider ollama \
		--ctx_size 8000 \
		--ollama_model "$model" \
		--source app.eo \
		--output "$output_file" \
		--comment_placeholder "<STRUCTURE-BELOW-IS-TO-BE-DOCUMENTED>"\
		--prompt_template "$prompt_template"
	    # Cleanup
	    ollama stop "$model"
	else
	    echo "Warning: Missing prompt template in ${dir}"
	fi
    done
done
