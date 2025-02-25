import { Router } from 'express';
const router = Router()

import { sendChat } from '../controllers/chat.controller.js';

router.post('/chat', sendChat);

export default router

