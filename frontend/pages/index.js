import { useState } from 'react'
import axios from 'axios'

export default function Home() {
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)

  const predict = async () => {
    const res = await axios.post('https://<render-backend-url>/predict', { text })
    setResult(res.data)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 to-purple-200 flex flex-col items-center justify-center">
      <h1 className="text-3xl font-bold mb-6">PhishShield 🛡️</h1>
      <textarea
        className="p-3 border rounded w-96"
        rows="5"
        placeholder="Paste your email text here..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button onClick={predict} className="mt-4 px-6 py-2 bg-indigo-600 text-white rounded">Check</button>
      {result && (
        <div className="mt-4 text-xl">
          {result.phishing_probability > 0.5
            ? <p className="text-red-600">🚨 Phishing ({(result.phishing_probability*100).toFixed(1)}%)</p>
            : <p className="text-green-600">✅ Safe ({(100 - result.phishing_probability*100).toFixed(1)}%)</p>}
        </div>
      )}
    </div>
  )
}
