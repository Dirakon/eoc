1. Research special tokens
  (deepseek `<assistant>` etc - https://www.redditmedia.com/r/LocalLLaMA/comments/1i5s74x/deepseekr1_ggufs_all_distilled_2_to_16bit_ggufs/)
2. [DONE] research openrouter?
3. [DONE] make everything openai api way
4. Add timings
5. [DONE] Add stdin to tests
6. Note tha reasoning models help debug explanation problems
6.1. Note tha some cheapskate models (llama, qwen) invent doctest syntax - [] for arrays, etc
6.2. Note different LLM muscules for writing code and documenting/understanding/explaining it
6.3. Note the overexplaining
6.4. Note the cost/time and shit by the by.
6.5. Note that some LLMs decide to document all functions, which opens more potential for factual errors.
6.6. For future research mention that the documentation scope and the number of errors should also be measured (i.e. 1 error vs errors)
7. [DONE] Parallel requests to openrouter
8. [DONE] Other models
9. [DONE] Also print stderr with RED
10. [DONE] Fix objects not being printed
11. Go though actualized - 
  redundant empty list ought to be punished
12. And go through understandability - some should be punished on relevance instead.
13. Im on like 11-12-13








Prompt templates:
- Normal
- Normal - language explanation
- Normal - doctests
- Normal - doctests - language explanation
- Improved: more language context - more example - give explanataion of used language structures (list, text, chained, etc)
- Improved - doctests



Stats:
1. Doctest state by LLM (x - llms, y - colored bars, count by states)
2. Output quality by doctest state (x - quality to mesaure (+overall), y - mutliple neighboring colored bars, value by states)
3. Similar to above, but value by LLMs
