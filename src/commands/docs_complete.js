/*
 * The MIT License (MIT)
 *
 * Copyright (c) 2022-2024 Objectionary.com
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

const { ChatOllama } = require('@langchain/ollama');
const { PromptTemplate } = require("@langchain/core/prompts");
const { RunnableSequence } = require("@langchain/core/runnables");
const { StringOutputParser, OutputParserException } = require("@langchain/core/output_parsers");
const { FewShotPromptTemplate } = require("@langchain/core/prompts");
const { readFile, readFileSync, writeFileSync } = require('fs');

function makeModel(opts) {
    switch (opts.provider) {
        case null:
        case undefined:
            throw new Error(`Provider not specified. You have to pass \`--provider\` argument.`);
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
            throw new Error(`\`${opts.provider}\` provider is not supported. Supported providers are: \`ollama\``);
    }
}

/**
 * Command to auto-complete EO documentation from .EO sources.
 * @param {Hash} opts - All options
 */
module.exports = async function(opts) {
    const prompt = new PromptTemplate({
        template: readFileSync(opts.prompt_template, 'utf-8'),
        inputVariables: ["code"],
    });

    //console.log(await prompt.format(
    //    {code:
    //readFileSync(opts.target, 'utf-8')}));
    //return;

    const model = makeModel(opts);

    const chain = RunnableSequence.from([
        prompt,
        model,
        new StringOutputParser(),
    ]);

    const inputCode = readFileSync(opts.target, 'utf-8')
    const comment_placeholder = opts.comment_placeholder;
    const results = [];
    const allLocationsOfPlaceholderInInputCode = Array.from(inputCode.matchAll(comment_placeholder));

    let index = 0;
    for (const location of allLocationsOfPlaceholderInInputCode) {
       const codeBefore = inputCode.slice(0, location.index);
       const codeAfter = inputCode.slice(location.index + location[0].length);
       
       const replacedCodeBefore = codeBefore.replace(comment_placeholder, "");
       const replacedCodeAfter = codeAfter.replace(comment_placeholder, "");

       const focusedInputCode = replacedCodeBefore + comment_placeholder + replacedCodeAfter

       console.log(`Generating documentation... ${index}/${allLocationsOfPlaceholderInInputCode.length}`);
       index++;

       let result = await chain.invoke({ code: focusedInputCode });
       if (result.indexOf("</think>") != -1)
        {
            // deepseek (reasoning-model) specific. TODO: figure out how to make this more general
            const thinkEnd = result.indexOf("</think>") 
            result = result.slice(thinkEnd + "</think>".length + 1).trim()
        }
       console.log(result);
       results.push(result)
    }

    console.log(results);

    writeFileSync(opts.output, JSON.stringify(results))
};
