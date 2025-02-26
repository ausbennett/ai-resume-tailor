
import express from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import multer from 'multer';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs/promises'

import chatRoutes from './routes/chat.routes.js';

dotenv.config();


const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);


const app = express();
const upload = multer({ dest: 'uploads/' });

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
// Upload endpoint
app.post('/upload', upload.single('resume'), async (req, res) => {
  try {
    const { file } = req;
    const { jobDescription } = req.body;

    if (!file || !jobDescription) {
      return res.status(400).json({ error: 'Missing required fields' });
    }


    // Add your processing logic here
    const fileContent = await fs.readFile(file.path, 'utf-8');
    
    // Log the contents
    console.log('=== RESUME CONTENT ===');
    console.log(fileContent);
    console.log('=== JOB DESCRIPTION ===');
    console.log(jobDescription);
    
   // Clean up the temporary file
    await fs.unlink(file.path);

    const analysisResult = {
      status: 'success',
      fileName: file.originalname,
      jobDescriptionLength: jobDescription.length,
      analysis: "Sample analysis result"
    };

    res.status(200).json(analysisResult);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Routes
app.use('/api', chatRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});

// Run server on port 3000
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
