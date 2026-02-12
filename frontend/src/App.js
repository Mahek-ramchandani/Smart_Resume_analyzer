import React, { useState, useRef } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef(null);

  const analyzeResume = async () => {
    if (!file) {
      alert("Please upload a resume PDF");
      return;
    }

    const formData = new FormData();
    formData.append("resume", file);

    setLoading(true);
    setResult(null);

    try {
      const res = await axios.post("http://127.0.0.1:5000/analyze", formData);
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert("Backend not running or error occurred. Check the terminal.");
    }

    setLoading(false);
  };

  const onFileChange = (e) => {
    const f = e.target.files && e.target.files[0];
    if (f && f.type !== "application/pdf") {
      alert("Please upload a PDF file.");
      return;
    }
    setFile(f || null);
  };

  return (
    <div className="app-container">
      <div className="card">
        <div className="header">
          <div className="brand-dot">SR</div>
          <div>
            <h1 className="title">Smart Resume Analyzer</h1>
            <p className="subtitle">Upload a resume PDF to get role-matching suggestions</p>
          </div>
        </div>

        <div className="layout">
          <div className="uploader">
            <h3 style={{marginTop:0}}>Upload Resume</h3>
            <div className="file-input">
              <label className="file-label" onClick={() => inputRef.current && inputRef.current.click()}>
                Choose PDF
              </label>
              <div className="file-name">{file ? file.name : "No file chosen"}</div>
              <input
                ref={inputRef}
                type="file"
                accept=".pdf"
                style={{display:'none'}}
                onChange={onFileChange}
              />
            </div>

            <button className="analyze-btn" onClick={analyzeResume} disabled={loading}>
              {loading ? "Analyzing..." : "Analyze Resume"}
            </button>

            <div className="footer">Tip: Use a well-formatted PDF for best results.</div>
          </div>

          <div className="results">
            <h3 style={{marginTop:0}}>Results</h3>
            {!result && <p style={{color:'rgba(0,48,73,0.6)'}}>No results yet. Upload a resume to analyze.</p>}

            {result && (
              <>
                <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',gap:12}}>
                  <div>
                    <div style={{fontSize:'1rem',color:'var(--navy)'}}>Best Role</div>
                    <div style={{marginTop:6,display:'flex',alignItems:'center',gap:10}}>
                      <div className="best-badge">{result.best_role}</div>
                      <div style={{ marginTop: 10, fontSize: "1.1rem", fontWeight: 600 }}>
                      ATS Resume Score: 
                      <span style={{ color: "#2ecc71", marginLeft: 8 }}>
                      {result.ats_score}%
                      </span>
                      </div>
                      <div style={{color:'rgba(0,48,73,0.7)',fontWeight:600}}>{" "}</div>
                    </div>
                  </div>
                  <div style={{textAlign:'right',color:'rgba(0,48,73,0.6)'}}>Confidence</div>
                </div>

                <div style={{marginTop:14}}>
                  {Object.entries(result.scores).map(([role, score]) => (
                    <div key={role} className="role-card">
                      <div style={{flex:1}}>
                        <div className="role-title">{role}</div>
                        <div className="bar-wrap">
                          <div className="bar" style={{width: `${Math.max(2, score)}%`}} />
                        </div>
                      </div>
                      <div style={{width:80,textAlign:'right'}}>
                        <div className="role-score">{score}%</div>
                      </div>
                    </div>
                  ))}
                </div>

                {result.suggestions && (
                  <div style={{ marginTop: 20, padding: 15, backgroundColor: "#f0f4f8", borderRadius: 8, border: "1px solid #d0dce6" }}>
                    <h3 style={{ marginTop: 0, color: "#003049", marginBottom: 12 }}>📋 Resume Improvement Suggestions:</h3>
                    <ul style={{ margin: 0, paddingLeft: 20, color: "#003049" }}>
                      {result.suggestions.map((item, index) => (
                        <li key={index} style={{ marginBottom: 8, lineHeight: 1.5 }}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;