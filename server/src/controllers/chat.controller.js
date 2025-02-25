
import client from '../services/openai.service.js'

export const sendChat = async (req,res) => {

  const { message } = req.body

  try {
    const response = await client.chat.completions.create({
      messages: [{ role: 'user', content: message }],
      model: 'deepseek-r1-distill-qwen-7b',
    });

    res.status(200).json(response.choices[0])
  } catch (error) {
    console.error('OpenAI API Error:', error);
    res.status(500).json({ error: 'Failed to get response from OpenAI' });
  }
}

