import { useState } from 'react';

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [status, setStatus] = useState('idle');
  const [modelVersion, setModelVersion] = useState('unknown');

  const handleRun = async () => {
    setStatus('running');
    try {
      const res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      const data = await res.json();
      setResponse(data.response || JSON.stringify(data));
    } catch (err) {
      setResponse('Error: ' + err.message);
    } finally {
      setStatus('idle');
    }
  };

  const handleTrain = async () => {
    setStatus('training');
    try {
      const res = await fetch('/api/train', { method: 'POST' });
      const data = await res.json();
      setResponse(data.status || JSON.stringify(data));
      // In a real app, you would poll for model version updates
      setModelVersion('latest');
    } catch (err) {
      setResponse('Error: ' + err.message);
    } finally {
      setStatus('idle');
    }
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>EVEZ Self-Updating System</h1>
      <div>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter your prompt..."
          rows={4}
          style={{ width: '100%', marginBottom: '1rem' }}
        />
      </div>
      <div>
        <button onClick={handleRun} disabled={status === 'running'}>
          {status === 'running' ? 'Running...' : 'Run EVEZ'}
        </button>
        <button onClick={handleTrain} disabled={status === 'training'} style={{ marginLeft: '1rem' }}>
          {status === 'training' ? 'Training...' : 'Train System'}
        </button>
      </div>
      <div style={{ marginTop: '2rem' }}>
        <h2>Response:</h2>
        <pre>{response}</pre>
      </div>
      <div style={{ marginTop: '2rem' }}>
        <h2>System Status:</h2>
        <p>Status: {status}</p>
        <p>Model Version: {modelVersion}</p>
      </div>
    </div>
  );
}