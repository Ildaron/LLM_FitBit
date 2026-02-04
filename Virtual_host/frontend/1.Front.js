import { useState } from "react";

function App() {
  const [avgHr, setAvgHr] = useState(150);
  const [duration, setDuration] = useState(45);
  const [sleep, setSleep] = useState(6);
  const [result, setResult] = useState("");

  const getAdvice = async () => {
    const res = await fetch("http://localhost:8000/coach", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        avg_hr: avgHr,
        duration,
        sleep
      })
    });

    const data = await res.json();
    setResult(data.message);
  };

  return (
    <div style={{ padding: 30, maxWidth: 500 }}>
      <h1>🏋️ AI Coach</h1>

      <label>Avg Heart Rate</label>
      <input value={avgHr} onChange={e => setAvgHr(e.target.value)} />

      <label>Workout Duration (min)</label>
      <input value={duration} onChange={e => setDuration(e.target.value)} />

      <label>Sleep Hours</label>
      <input value={sleep} onChange={e => setSleep(e.target.value)} />

      <button onClick={getAdvice} style={{ marginTop: 15 }}>
        Get AI Advice
      </button>

      {result && (
        <div style={{ marginTop: 20, background: "#f0f0f0", padding: 10 }}>
          <strong>Recommendation:</strong>
          <p>{result}</p>
        </div>
      )}
    </div>
  );
}

export default App;
