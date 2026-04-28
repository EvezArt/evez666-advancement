export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const { prompt } = req.body;

  if (!prompt) {
    res.status(400).json({ error: 'Prompt is required' });
    return;
  }

  const HF_TOKEN = process.env.HF_TOKEN;
  if (!HF_TOKEN) {
    res.status(500).json({ error: 'HF_TOKEN not configured' });
    return;
  }

  // Replace with your actual Hugging Face model ID
  const MODEL_ID = "your-username/evez-model"; // <-- CHANGE THIS

  try {
    const hfResponse = await fetch(
      `https://api-inference.huggingface.co/models/${MODEL_ID}`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${HF_TOKEN}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ inputs: prompt, parameters: { wait_for_model: true } }),
      }
    );

    if (!hfResponse.ok) {
      throw new Error(`Hugging Face API error: ${hfResponse.status}`);
    }

    const result = await hfResponse.json();

    // The inference API returns different formats; we'll try to extract the generated text.
    let outputText = "";
    if (Array.isArray(result) && result[0] && result[0].generated_text) {
      outputText = result[0].generated_text;
    } else if (result.generated_text) {
      outputText = result.generated_text;
    } else {
      outputText = JSON.stringify(result);
    }

    res.status(200).json({ response: outputText });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: error.message || 'Unknown error' });
  }
}