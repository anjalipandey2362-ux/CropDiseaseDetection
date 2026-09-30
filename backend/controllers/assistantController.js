import { processAssistantQuery } from '../services/assistantService.js';

/**
 * Controller to process AI Agriculture Assistant queries
 */
export async function chatWithAI(req, res) {
  try {
    const { question, diseaseContext, cropContext } = req.body;
    
    if (!question || typeof question !== 'string') {
      return res.status(400).json({ error: "Missing or invalid question parameter" });
    }

    const reply = await processAssistantQuery(question, diseaseContext, cropContext);

    return res.status(200).json({ reply });
  } catch (err) {
    console.error("[AssistantController] Error:", err);
    return res.status(500).json({ 
      reply: "Sorry, the AI Agriculture Assistant is temporarily unavailable. Please consult your local agriculture officer." 
    });
  }
}
