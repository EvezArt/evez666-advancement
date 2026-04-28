export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
  const GITHUB_REPOSITORY = process.env.GITHUB_REPOSITORY; // This is set by Vercel if the repo is connected to GitHub, but we can also use a secret.

  // Alternatively, we can store the repo owner and name in environment variables.
  const REPO_OWNER = process.env.REPO_OWNER; // e.g., "your-username"
  const REPO_NAME = process.env.REPO_NAME; // e.g., "evez-self-update"

  if (!GITHUB_TOKEN || !REPO_OWNER || !REPO_NAME) {
    res.status(500).json({ error: 'GitHub credentials not configured' });
    return;
  }

  try {
    // Trigger a workflow dispatch for the train.yml workflow
    const response = await fetch(
      `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/actions/workflows/train.yml/dispatches`,
      {
        method: 'POST',
        headers: {
          Authorization: `token ${GITHUB_TOKEN}`,
          'Accept': 'application/vnd.github+json',
        },
        body: JSON.stringify({
          ref: 'main', // or whatever branch you want to trigger on
        }),
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`GitHub API error: ${response.status} - ${errorText}`);
    }

    res.status(202).json({ status: 'training triggered' });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: error.message || 'Unknown error' });
  }
}