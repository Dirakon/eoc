#!/usr/bin/env bash

curl -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Accept: application/json" \
  -H "Accept-Encoding: gzip,deflate" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Connection: close" \
  -H "Content-Type: application/json" \
  -H "User-Agent: OpenAI/JS 4.86.1" \
  -H "X-Stainless-Arch: x64" \
  -H "X-Stainless-Lang: js" \
  -H "X-Stainless-Os: Linux" \
  -H "X-Stainless-Package-Version: 4.86.1" \
  -H "X-Stainless-Retry-Count: 0" \
  -H "X-Stainless-Runtime: node" \
  -H "X-Stainless-Runtime-Version: v20.18.1" \
  -H "X-Stainless-Timeout: 600000" \
  --data "{  \"model\": \"deepseek/deepseek-r1\",  \"n\": 1,  \"stream\": false, \"messages\": [    {      \"role\": \"user\",      \"content\": \"$PROMPT_\"    }  ]}" \
  --compressed

exit 1


  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Authorization: Bearer test" \

curl -X POST "https://openrouter.ai/api/v1/chat/completions" \
curl -X POST "https://rbaskets.in/q4trm76/chat/completions" \

  --data "{  \"model\": \"deepseek/deepseek-r1\",  \"n\": 1,  \"stream\": false, \"messages\": [    {      \"role\": \"user\",      \"content\": \"$PROMPT_\"    }  ]}" \
  --data "{  \"model\": \"deepseek/deepseek-r1:free\",  \"n\": 1,  \"stream\": true,  \"stream_options\": {    \"include_usage\": true  },  \"messages\": [    {      \"role\": \"user\",      \"content\": \"Say hi\"    }  ]}"
  --data "{  \"model\": \"deepseek/deepseek-r1:free\",  \"n\": 1,  \"stream\": false, \"messages\": [    {      \"role\": \"user\",      \"content\": \"Say hi\"    }  ]}"
