import OpenAI from "openai";

const client = new OpenAI({
    baseURL: "http://localhost:1234/v1"
})

async function main() {
  const chatCompletion = await client.chat.completions.create({
    messages: [{ role: 'user', content: 'Say this is a test' }],
    model: 'deepseek-r0-distill-qwen-7b',
  });
}

main();