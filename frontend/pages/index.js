import React, { useState } from "react";
import axios from "axios";

export default function PhishShield() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);

  const predict = async () => {
    try {
      const res = await axios.post(
        "https://capturethephish-a1x4.onrender.com/predict",
        { subject: "User input", body: text }
      );
      setResult(res.data);
    } catch (err) {
      console.error("Prediction error:", err);
      alert("⚠️ Unable to connect to the detection server. Please try again later.");
    }
  };

  const getSafetyTips = (isPhishing) => {
    if (isPhishing) {
      return (
        <ul className="list-disc pl-6 text-left text-red-100 mt-2">
          <li>Never click suspicious links or attachments.</li>
          <li>Check the sender’s email address and domain carefully.</li>
          <li>Do not share personal or banking details over email.</li>
          <li>Hover over links to preview the real URL before clicking.</li>
          <li>Report suspicious mail to your security team or mark as spam.</li>
        </ul>
      );
    } else {
      return (
        <ul className="list-disc pl-6 text-left text-green-100 mt-2">
          <li>Keep browser and antivirus updated.</li>
          <li>Double-check URLs before logging in.</li>
          <li>Stay alert for grammar or branding inconsistencies.</li>
          <li>Keep practicing safe email habits.</li>
          <li>When in doubt, verify via official channels (not email links).</li>
        </ul>
      );
    }
  };

  return (
    // Background container: image + dark overlay for contrast
    <div className="min-h-screen relative flex items-center justify-center">
      {/* Background image */}
      <div
        className="absolute inset-0 bg-center bg-cover"
        style={{ backgroundImage: "url('/attack-verified-gmail.png')" }}
        aria-hidden="true"
      />
      {/* Dark translucent overlay with slight blur for readability */}
      <div
        className="absolute inset-0 bg-black/55 backdrop-blur-sm"
        aria-hidden="true"
      />

      {/* Main content card */}
      <div className="relative z-10 w-full max-w-3xl p-8">
        <div className="bg-white/8 backdrop-blur-md border border-white/20 rounded-2xl p-6 shadow-xl">
          <header className="text-center mb-4">
            <h1 className="text-4xl font-extrabold text-white tracking-wide">PhishShield 🛡️</h1>
            <p className="text-sm text-white/90 mt-2 max-w-2xl mx-auto">
              Paste email text or a suspicious URL below. PhishShield detects phishing
              indicators and gives actionable safety tips.
            </p>
          </header>

          <textarea
            className="w-full rounded-lg p-4 mt-4 text-gray-900 placeholder:text-gray-500"
            rows={6}
            placeholder="📧 Paste your email content here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />

          <div className="flex items-center justify-between mt-4">
            <button
              onClick={predict}
              className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg shadow-md transition"
            >
              🔍 Check for Phishing
            </button>
            <div className="text-sm text-white/90">Model: live</div>
          </div>

          {result && (
            <div className="mt-6 p-5 rounded-xl shadow-inner" style={{ background: "linear-gradient(90deg, rgba(0,0,0,0.45), rgba(0,0,0,0.35))" }}>
              {result.phish_prob > 0.5 ? (
                <>
                  <p className="text-2xl font-bold text-red-300 mb-2">
                    🚨 Phishing Detected! ({(result.phish_prob * 100).toFixed(1)}%)
                  </p>
                  <p className="text-sm text-white/90 mb-3">
                    This message shows phishing indicators. Follow these steps to protect yourself:
                  </p>
