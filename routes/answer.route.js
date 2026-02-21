const router = express.Router();
import express from 'express';
router.get('/' , async (req, res) => {
  res.render('index');
});
router.post('/', async (req, res) => {
    const userPrompt = req.body.prompt; 

    try {
        const pythonResponse = await fetch('http://localhost:8080/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: userPrompt }) 
        });
        const data = await pythonResponse.json();
        res.render('index', { 
            answer: data.answer 
        });

    } catch (error) {
        console.error("Python backend error:", error);
        res.render('index', { 
            answer: "Error: Make sure the Docker container is running on port 8080." 
        });
    }
});

export default router;