#!/usr/bin/env bash

# https://stackoverflow.com/questions/44810685/how-to-sanitize-a-string-in-bash/44811468#44811468
sanitize() {
    local s="${1?need a string}" # receive input in first argument
    s="${s//[^[:alnum:]]/-}"     # replace all non-alnum characters to -
    s="${s//+(-)/-}"             # convert multiple - to single -
    s="${s/#-}"                  # remove - from start
    s="${s/%-}"                  # remove - from end
    echo "${s,,}"                # convert to lowercase
}

MODELS=("deepseek/deepseek-r1:free")

# Find all subdirectories in runs_temp
find ./runs_temp -mindepth 1 -maxdepth 1 -type d | while read -r dir; do
    # Process each model for the current directory
    for model in "${MODELS[@]}"; do
	# Sanitize model name for filename by replacing ':' with '-'
	safe_model=$(sanitize model)
	
	# Construct paths with proper quoting
	output_file="${dir}/out_${safe_model}.json"
	prompt_template="${dir}/prompt.txt"
	
	# Run the command if prompt template exists
	if [ -f "$prompt_template" ]; then
	    echo "Processing $(basename "$dir") with model $model"
	    node ./src/eoc.js generate_comments \
		--provider openai \
		--openai_model "$model" \
		--openai_token "$OPENROUTER_API_KEY"\
		--openai_url "https://openrouter.ai/api/v1"\
		--source app.eo \
		--output "$output_file" \
		--comment_placeholder "<STRUCTURE-BELOW-IS-TO-BE-DOCUMENTED>"\
		--prompt_template "$prompt_template"
	else
	    echo "Warning: Missing prompt template in ${dir}"
	fi
    done
done
