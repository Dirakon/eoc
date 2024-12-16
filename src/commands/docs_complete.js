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
const { StringOutputParser } = require("@langchain/core/output_parsers");
const { FewShotPromptTemplate } = require("@langchain/core/prompts");

function makeModel(opts) {
    switch (opts.provider) {
        case null:
        case undefined:
            throw new Error(`Provider not specified. You have to pass \`--provider\` argument.`);
        case 'ollama':
            if (opts.ollama_model == null || opts.ollama_model == undefined) {
                throw new Error(`Ollama model not specified. You have to pass \`--ollama_model\` argument.`);
            }

            return new ChatOllama(
                {
                    model: opts.ollama_model,
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
    const examplePrompt = PromptTemplate.fromTemplate(
        "Input:\n\`\`\`eo\n{code}\n\`\`\`\nOutput: {comment}"
    );
    const examples = [
        {
            code: "# <COMMENT TO BE ADDED>\n[a b] > app\n  add. > @\n    a\n    b",
            comment: "Object that adds two numbers together."
        },
        {
            code: "# <COMMENT TO BE ADDED>\n[as-bytes] > string\n  as-bytes > @\n\n  # Get the length of it.\n  [] > length /number\n\n  # Takes a piece of a string as another string.\n  [start len] > slice /string",
            comment: "An abstraction of a text string, which internally is a chain of bytes."
        }
    ];
    const prompt = new FewShotPromptTemplate({
        examples,
        examplePrompt,
        suffix: "The actual user input to be documented:\n\`\`\`eo\n{code}\n\`\`\`",
        prefix: `Write a comment explaining what the object does. Only write the minimal, succinct explanation that could be inserted as a code comment above the object in place of <COMMENT TO BE ADDED> mark. Do not add any additional text besides the actual comment to be added. You will be provided a few interaction examples and an actual user input afterwards.`,
        inputVariables: ["code"],
    });

    const model = makeModel(opts);

    const chain = RunnableSequence.from([
        prompt,
        model,
        new StringOutputParser(),
    ]);

    const inputCode = `# <COMMENT TO BE ADDED>\n[args] > hello\n  QQ.io.stdout > @\n    "Hello, world!`
    //console.log(await prompt.format({ code:  inputCode}));
    const result = await chain.invoke({ code: inputCode });

    console.log(result);
};
