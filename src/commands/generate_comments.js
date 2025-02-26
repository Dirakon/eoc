/*
 * The MIT License (MIT)
 *
 * Copyright (c) 2022-2025 Objectionary.com
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included
 * in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

const { FakeListChatModel } = require("@langchain/core/utils/testing");
const { PromptTemplate } = require("@langchain/core/prompts");
const { RunnableSequence } = require("@langchain/core/runnables");
const { StringOutputParser } = require("@langchain/core/output_parsers");
const { ChatOllama } = require('@langchain/ollama');
const { HuggingFaceInference } = require("@langchain/community/llms/hf");
const { readFileSync, writeFileSync } = require('fs');

function makeModel(opts) {
    switch (opts.provider) {
        case null:
        case undefined:
            throw new Error(`Provider not specified. You have to pass \`--provider\` argument.`);
        case 'huggingface':
            return new HuggingFaceInference({
                model: opts.huggingface_model,
                apiKey: opts.huggingface_token
              });
        case 'placeholder':
            return new FakeListChatModel({
              responses: ["<PLACEHOLDER_RESPONSE>"],
            });
        case 'ollama':
            if (opts.ollama_model == null || opts.ollama_model == undefined) {
                throw new Error(`Ollama model not specified. You have to pass \`--ollama_model\` argument.`);
            }

            let ctx_size = opts.ctx_size;
            if (ctx_size == null || ctx_size == undefined)
            {
                throw new OutputParserException("sd")
                //? 2048
            }
            else
            {
                ctx_size = parseInt(ctx_size)
            }
            return new ChatOllama(
                {
                    model: opts.ollama_model,
                    numCtx: ctx_size
                });
        default:
            throw new Error(`\`${opts.provider}\` provider is not supported. Currently supported providers are: \`placeholder\`, \'ollama\'`);
    }
}

/**
 * Command to auto-complete EO documentation from .EO sources.
 * @param {Hash} opts - All options
 */
module.exports = async function(opts) {
    const model = makeModel(opts);

    const prompt = new PromptTemplate({
        template: readFileSync(opts.prompt_template, 'utf-8'),
        inputVariables: ["code"],
    });

    const chain = RunnableSequence.from([
        prompt,
        model,
        new StringOutputParser(),
    ]);

    const inputCode = readFileSync(opts.source, 'utf-8')
    const commentPlaceholder = opts.comment_placeholder;
    const results = [];
    const allLocationsOfPlaceholderInInputCode = Array.from(inputCode.matchAll(commentPlaceholder));

    let index = 0;

    for (const location of allLocationsOfPlaceholderInInputCode) {
        const codeBefore = inputCode.slice(0, location.index);
        const replacedCodeBefore = codeBefore.replace(commentPlaceholder, "");

        const codeAfter = inputCode.slice(location.index + commentPlaceholder.length);
        const replacedCodeAfter = codeAfter.replace(commentPlaceholder, "");

        const focusedInputCode = replacedCodeBefore + commentPlaceholder + replacedCodeAfter

        console.debug(`Generating documentation... ${index}/${allLocationsOfPlaceholderInInputCode.length}`);

        let result = await chain.invoke({ code: focusedInputCode });
        console.log(result)

        if (result.indexOf("</think>") != -1)
        {
            // deepseek (reasoning-model) specific. TODO: figure out how to make this more general
            const thinkEnd = result.indexOf("</think>") 
            result = result.slice(thinkEnd + "</think>".length + 1).trim()
        }
        results.push(result)

        index++;
    }

    writeFileSync(opts.output, JSON.stringify(results))
};
