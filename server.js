
const express = require('express');
const OpenAI = require('openai');
const app = express();

// Initialize OpenAI client
const client = new OpenAI({
    apiKey: "dne",
    baseURL: "http://127.0.0.1:1234/v1", 
});

// Basic greeting route (example)
app.get('/', (req, res) => {
    res.send('Hello! This is your basic OpenAI integration.');
});

app.get('/api/chat', async (req,res) => {
  
  try {
    const response = await client.chat.completions.create({
      messages: [{ role: 'user', content: 'Say this is a test' }],
      model: 'deepseek-r1-distill-qwen-7b',
    });

    res.status(200).json(response.choices[0])
  } catch (error) {
    console.error('OpenAI API Error:', error);
    res.status(500).json({ error: 'Failed to get response from OpenAI' });
  }

})

// Run server on port 3000
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
