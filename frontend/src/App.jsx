import { useRef, useState } from "react";

const API = `${import.meta.env.VITE_API_BASE_URL}/api/v1`;

/* =========================================================
   ICONS
========================================================= */

function ShieldIcon({ size = 24 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 3L20 6V11C20 16.5 16.5 20 12 21C7.5 20 4 16.5 4 11V6L12 3Z" />
      <path d="M8.5 12L11 14.5L16 9.5" />
    </svg>
  );
}

function UploadIcon() {
  return (
    <svg
      width="30"
      height="30"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 16V4" />
      <path d="M7 9L12 4L17 9" />
      <path d="M5 20H19" />
    </svg>
  );
}

function LinkIcon() {
  return (
    <svg
      width="19"
      height="19"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M10 13a5 5 0 0 0 7.07.07l2-2a5 5 0 0 0-7.07-7.07l-1.15 1.15" />
      <path d="M14 11a5 5 0 0 0-7.07-.07l-2 2A5 5 0 0 0 7 20l1.15-1.15" />
    </svg>
  );
}

function FileIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M14 2H6a2 2 0 0 0-2 2V20a2 2 0 0 0 2 2H18a2 2 0 0 0 2-2V8Z" />
      <path d="M14 2V8H20" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg
      width="17"
      height="17"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M5 12L10 17L19 7" />
    </svg>
  );
}

/* =========================================================
   APP
========================================================= */

function App() {
  const [activeInput, setActiveInput] = useState("message");
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [file, setFile] = useState(null);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const fileInputRef = useRef(null);

  /* =======================================================
     ANALYZE
  ======================================================= */

  async function analyze() {
    if (!text.trim() && !url.trim() && !file) {
      setError("Please provide a job message, URL, or file.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const createResponse = await fetch(`${API}/analyses`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text,
          source_url: url || null,
        }),
      });

      const created = await createResponse.json();

      if (!createResponse.ok) {
        throw new Error(
          created.detail || "Unable to create analysis."
        );
      }

      const analysisId = created.analysis_id;

      /* Upload selected file */

      if (file) {
        const formData = new FormData();
        formData.append("file", file);

        const uploadResponse = await fetch(
          `${API}/analyses/${analysisId}/files`,
          {
            method: "POST",
            body: formData,
          }
        );

        const uploadData = await uploadResponse.json();

        if (!uploadResponse.ok) {
          throw new Error(
            uploadData.detail || "File upload failed."
          );
        }
      }

      /* Run analysis */

      const runResponse = await fetch(
        `${API}/analyses/${analysisId}/run`,
        {
          method: "POST",
        }
      );

      const runData = await runResponse.json();

      if (!runResponse.ok) {
        throw new Error(
          runData.detail || "Analysis failed."
        );
      }

      /* Get report */

      const reportResponse = await fetch(
        `${API}/analyses/${analysisId}/report`
      );

      const reportData = await reportResponse.json();

      if (!reportResponse.ok) {
        throw new Error(
          reportData.detail || "Could not load report."
        );
      }

      setResult(reportData);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  /* =======================================================
     FILE HANDLING
  ======================================================= */

  function handleFile(event) {
    const selected = event.target.files?.[0];

    if (!selected) return;

    setFile(selected);
    setError("");
  }

  function removeFile() {
    setFile(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  /* =======================================================
     RESET
  ======================================================= */

  function resetAnalysis() {
    setResult(null);
    setText("");
    setUrl("");
    setFile(null);
    setError("");
  }

  /* =======================================================
     RESULT DATA
  ======================================================= */

  const riskLevel =
    result?.assessment?.risk_level || "UNABLE_TO_VERIFY";

  const riskScore =
    result?.assessment?.risk_score ?? 0;

  return (
    <div className="app">

      {/* =====================================================
          NAVBAR
      ====================================================== */}

      <nav className="navbar">
        <div className="nav-inner">

          <div className="brand">

            <div className="brand-icon">
              <ShieldIcon size={22} />
            </div>

            <div>

              <div className="brand-name">
                JobShield<span>AI</span>
              </div>

              <div className="brand-status">
                <span className="status-dot" />
                Verification engine online
              </div>

            </div>

          </div>

          <div className="nav-links">
            <a href="#how">How it works</a>
            <a href="#features">Features</a>
            <a href="#about">About</a>
          </div>

          <button className="nav-button">
            <span>GitHub</span>
            <span>↗</span>
          </button>

        </div>
      </nav>

      {/* =====================================================
          HERO
      ====================================================== */}

      {!result && (
        <section className="hero">

          <div className="hero-glow glow-one" />
          <div className="hero-glow glow-two" />

          <div className="hero-content">

            <div className="trust-pill">
              <span className="pulse-dot" />
              AI-powered recruitment verification
            </div>

            <h1>
              Don't let a fake job
              <br />
              <span>steal your future.</span>
            </h1>

            <p className="hero-text">
              Verify job offers, internships and recruiters using
              evidence-based analysis — before you send money or
              sensitive information.
            </p>

            <div className="hero-stats">

              <div>
                <strong>5+</strong>
                <span>Risk signals</span>
              </div>

              <div className="stat-line" />

              <div>
                <strong>AI</strong>
                <span>Evidence analysis</span>
              </div>

              <div className="stat-line" />

              <div>
                <strong>100%</strong>
                <span>Transparent reports</span>
              </div>

            </div>

          </div>

        </section>
      )}

      {/* =====================================================
          ANALYZER
      ====================================================== */}

      {!result && (
        <section className="analyzer-wrapper">

          <div className="analyzer-card">

            <div className="analyzer-header">

              <div>

                <div className="section-label">
                  JOB ANALYZER
                </div>

                <h2>
                  Is this opportunity safe?
                </h2>

                <p>
                  Upload, paste or enter the opportunity you received.
                </p>

              </div>

              <div className="secure-badge">
                <ShieldIcon size={17} />
                Evidence based
              </div>

            </div>

            {/* INPUT TABS */}

            <div className="input-tabs">

              <button
                className={
                  activeInput === "message"
                    ? "input-tab active"
                    : "input-tab"
                }
                onClick={() => setActiveInput("message")}
              >
                <span>✦</span>
                Paste message
              </button>

              <button
                className={
                  activeInput === "file"
                    ? "input-tab active"
                    : "input-tab"
                }
                onClick={() => setActiveInput("file")}
              >
                <FileIcon />
                Upload file
              </button>

              <button
                className={
                  activeInput === "url"
                    ? "input-tab active"
                    : "input-tab"
                }
                onClick={() => setActiveInput("url")}
              >
                <LinkIcon />
                Job URL
              </button>

            </div>

            {/* MESSAGE */}

            {activeInput === "message" && (
              <div className="input-area">

                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder={`Paste your job or internship message here...

Example:

"Congratulations! You have been selected for our AI internship. Pay ₹2,999 registration fee to confirm your seat..."`}
                />

                <div className="textarea-footer">

                  <span>
                    {text.length} / 30,000 characters
                  </span>

                  <span className="privacy-note">
                    🔒 Your input is analyzed securely
                  </span>

                </div>

              </div>
            )}

            {/* FILE */}

            {activeInput === "file" && (
              <div className="input-area">

                {!file ? (

                  <div
                    className="drop-zone"
                    onClick={() =>
                      fileInputRef.current?.click()
                    }
                  >

                    <div className="upload-circle">
                      <UploadIcon />
                    </div>

                    <h3>
                      Drop your job offer here
                    </h3>

                    <p>
                      Upload a screenshot, PDF or text file
                    </p>

                    <button
                      className="browse-button"
                      onClick={(e) => {
                        e.stopPropagation();
                        fileInputRef.current?.click();
                      }}
                    >
                      Browse files
                    </button>

                    <small>
                      PDF, PNG, JPG, JPEG or TXT · Max 10 MB
                    </small>

                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".pdf,.png,.jpg,.jpeg,.txt"
                      hidden
                      onChange={handleFile}
                    />

                  </div>

                ) : (

                  <div className="selected-file">

                    <div className="file-icon">
                      <FileIcon />
                    </div>

                    <div className="file-details">

                      <strong>{file.name}</strong>

                      <span>
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </span>

                    </div>

                    <button
                      className="remove-file"
                      onClick={removeFile}
                    >
                      Remove
                    </button>

                  </div>

                )}

              </div>
            )}

            {/* URL */}

            {activeInput === "url" && (
              <div className="input-area url-area">

                <div className="url-input-wrapper">

                  <LinkIcon />

                  <input
                    value={url}
                    onChange={(e) =>
                      setUrl(e.target.value)
                    }
                    placeholder="https://company.com/careers/job..."
                  />

                </div>

                <p className="url-help">
                  We'll analyze the domain and available job
                  information. Never enter passwords or private
                  credentials.
                </p>

              </div>
            )}

            {/* EXTRA URL */}

            {activeInput === "message" && (
              <div className="optional-url">

                <LinkIcon />

                <input
                  value={url}
                  onChange={(e) =>
                    setUrl(e.target.value)
                  }
                  placeholder="Add job URL (optional)"
                />

              </div>
            )}

            {/* ERROR */}

            {error && (
              <div className="error-box">
                <span>!</span>
                {error}
              </div>
            )}

            {/* ANALYZE */}

            <button
              className="analyze-button"
              onClick={analyze}
              disabled={
                loading ||
                (!text.trim() &&
                  !url.trim() &&
                  !file)
              }
            >

              {loading ? (
                <>
                  <span className="spinner" />
                  Analyzing opportunity...
                </>
              ) : (
                <>
                  Analyze with JobShield
                  <span className="arrow">→</span>
                </>
              )}

            </button>

            <div className="analysis-note">
              <span>✓</span>
              We never automatically label a company as fraudulent.
              JobShield explains the evidence behind each warning.
            </div>

          </div>

        </section>
      )}

      {/* =====================================================
          RESULT — PROFESSIONAL VERIFICATION REPORT
      ====================================================== */}

      {result && (
        <section className="professional-report">

          <div className="report-toolbar">

            <button
              className="report-back"
              onClick={resetAnalysis}
            >
              ← Analyze another opportunity
            </button>

            <button
              className="report-print"
              onClick={() => window.print()}
            >
              Print / Save PDF ↗
            </button>

          </div>

          <header className="professional-report-header">

            <div className="report-heading">

              <div className="report-eyebrow">
                JOBSHIELD AI · VERIFICATION REPORT
              </div>

              <h1>
                Job Opportunity Analysis
              </h1>

              <p>
                Evidence-based analysis of the submitted job opportunity,
                including extracted information, verification status and risk signals.
              </p>

              <div className="report-meta">

                <span>
                  Analysis ID:{" "}
                  {result.analysis_id ||
                    "JS-" + String(Date.now()).slice(-6)}
                </span>

                <span>
                  Source: Submitted opportunity
                </span>

              </div>

            </div>

            <div
              className={`professional-risk ${riskLevel.toLowerCase()}`}
            >

              <div className="professional-score">

                <strong>{riskScore}</strong>

                <span>/100</span>

              </div>

              <div>

                <small>RISK LEVEL</small>

                <strong>
                  {riskLevel.replaceAll("_", " ")}
                </strong>

                <span>
                  Evidence-based assessment
                </span>

              </div>

            </div>

          </header>

          {/* EXECUTIVE FINDING */}

          <section className="professional-card">

            <div className="professional-section-heading">

              <span>01</span>

              <div>

                <h2>Executive Finding</h2>

                <p>
                  Overall assessment from the available evidence
                </p>

              </div>

            </div>

            <div
              className={`finding-box ${riskLevel.toLowerCase()}`}
            >

              <div className="finding-icon">

                {riskLevel === "LOW"
                  ? "✓"
                  : riskLevel === "UNABLE_TO_VERIFY"
                    ? "?"
                    : "!"}

              </div>

              <div>

                <h3>

                  {riskLevel === "HIGH"
                    ? "Multiple warning signals require attention"
                    : riskLevel === "MEDIUM"
                      ? "Some warning signals require further verification"
                      : riskLevel === "LOW"
                        ? "No major warning signal was detected"
                        : "There is not enough evidence to verify this opportunity"}

                </h3>

                <p>
                  {result.assessment?.summary ||
                    "Review the evidence and verification checks below before proceeding."}
                </p>

              </div>

            </div>

          </section>

          {/* JOB + VERIFICATION */}

          <div className="professional-two-column">

            {/* JOB INFORMATION */}

            <section className="professional-card">

              <div className="professional-section-heading">

                <span>02</span>

                <div>

                  <h2>Job Information</h2>

                  <p>
                    Information extracted from the submission
                  </p>

                </div>

              </div>

              <div className="professional-job-title">

                <div className="professional-job-icon">
                  💼
                </div>

                <div>

                  <h3>
                    {result.job?.job_title ||
                      "Job opportunity"}
                  </h3>

                  <p>
                    {result.job?.company_name ||
                      "Company not provided"}
                  </p>

                </div>

              </div>

              <div className="professional-info-grid">

                <Detail
                  label="Location"
                  value={result.job?.location}
                  icon="📍"
                />

                <Detail
                  label="Salary"
                  value={
                    result.job?.salary ||
                    result.job?.salary_range
                  }
                  icon="₹"
                />

                <Detail
                  label="Stipend"
                  value={result.job?.stipend}
                  icon="₹"
                />

                <Detail
                  label="Recruiter"
                  value={result.job?.recruiter_name}
                  icon="👤"
                />

                <Detail
                  label="Email"
                  value={result.job?.recruiter_email}
                  icon="✉"
                />

                <Detail
                  label="Phone"
                  value={
                    result.job?.phone ||
                    result.job?.recruiter_phone
                  }
                  icon="☎"
                />

                <Detail
                  label="Website"
                  value={
                    result.job?.website ||
                    result.job?.source_url
                  }
                  icon="🔗"
                />

                <Detail
                  label="Payment requested"
                  value={
                    result.job?.payment_request ||
                    result.job?.payment_amount ||
                    "Not detected"
                  }
                  icon="💳"
                />

              </div>

            </section>

            {/* VERIFICATION STATUS */}

            <section className="professional-card">

              <div className="professional-section-heading">

                <span>03</span>

                <div>

                  <h2>Verification Status</h2>

                  <p>
                    Current evidence status
                  </p>

                </div>

              </div>

              <div className="professional-verification-list">

                <VerificationItem
                  label="Company information"
                  verified={result.verified_facts?.some(
                    (x) =>
                      x.toLowerCase().includes("company")
                  )}
                />

                <VerificationItem
                  label="Job opportunity"
                  verified={result.verified_facts?.some(
                    (x) =>
                      x.toLowerCase().includes("job")
                  )}
                />

                <VerificationItem
                  label="Recruiter identity"
                  verified={false}
                />

                <VerificationItem
                  label="Website / domain"
                  verified={false}
                />

              </div>

              <div className="verification-note">

                <span>i</span>

                <p>
                  Not independently verified means there is currently not
                  enough evidence to confirm the claim.
                </p>

              </div>

            </section>

          </div>

          {/* RISK SIGNALS */}

          <section className="professional-card">

            <div className="professional-section-heading heading-with-count">

              <span>04</span>

              <div>

                <h2>Risk Signals</h2>

                <p>
                  Specific indicators detected in the submitted content
                </p>

              </div>

              <span className="professional-count">
                {result.assessment?.signals?.length || 0} signals
              </span>

            </div>

            {!result.assessment?.signals?.length ? (

              <div className="professional-empty">

                <div>✓</div>

                <section>

                  <strong>
                    No major warning signal detected
                  </strong>

                  <p>
                    This does not prove that the opportunity is legitimate.
                    Continue with independent verification.
                  </p>

                </section>

              </div>

            ) : (

              <div className="professional-signal-list">

                {result.assessment.signals.map(
                  (signal, index) => (

                    <div
                      className={`professional-signal ${String(
                        signal.severity || "MEDIUM"
                      ).toLowerCase()}`}
                      key={index}
                    >

                      <div className="professional-signal-icon">
                        !
                      </div>

                      <div className="professional-signal-body">

                        <div className="professional-signal-top">

                          <h3>
                            {String(
                              signal.signal_type ||
                                "Risk signal"
                            ).replaceAll("_", " ")}
                          </h3>

                          <span>
                            {signal.severity || "MEDIUM"}
                          </span>

                        </div>

                        <p>
                          {signal.description}
                        </p>

                        {signal.evidence && (
                          <div className="professional-evidence-line">

                            <strong>Evidence</strong>

                            <span>
                              {signal.evidence}
                            </span>

                          </div>
                        )}

                      </div>

                    </div>

                  )
                )}

              </div>

            )}

          </section>

          {/* EVIDENCE */}

          <section className="professional-card">

            <div className="professional-section-heading">

              <span>05</span>

              <div>

                <h2>Evidence</h2>

                <p>
                  Relevant facts supporting the assessment
                </p>

              </div>

            </div>

            <div className="professional-evidence-panel">

              <div className="professional-evidence-header">

                <span>
                  SUBMITTED OPPORTUNITY
                </span>

                <span>
                  EVIDENCE RECORD
                </span>

              </div>

              {(result.assessment?.signals || [])
                .filter((signal) => signal.evidence)
                .map((signal, index) => (

                  <div
                    className="professional-evidence-row"
                    key={index}
                  >

                    <div>

                      <strong>
                        {String(
                          signal.signal_type ||
                            "Evidence"
                        ).replaceAll("_", " ")}
                      </strong>

                      <span>
                        {signal.severity || "INFO"}
                      </span>

                    </div>

                    <p>
                      {signal.evidence}
                    </p>

                  </div>

                ))}

              {!result.assessment?.signals?.some(
                (signal) => signal.evidence
              ) && (

                <div className="professional-no-evidence">

                  No individual evidence items were returned
                  by the analysis.

                </div>

              )}

            </div>

          </section>

          {/* RECOMMENDED ACTIONS */}

          <section className="professional-card">

            <div className="professional-section-heading">

              <span>06</span>

              <div>

                <h2>Recommended Actions</h2>

                <p>
                  Practical steps before proceeding
                </p>

              </div>

            </div>

            <div className="professional-actions">

              <div className="professional-action">

                <div className="action-index">
                  01
                </div>

                <div>

                  <h3>
                    Verify the company independently
                  </h3>

                  <p>
                    Find the official company website yourself
                    and check whether the role exists on its
                    official careers page.
                  </p>

                </div>

              </div>

              <div className="professional-action">

                <div className="action-index">
                  02
                </div>

                <div>

                  <h3>
                    Verify the recruiter
                  </h3>

                  <p>
                    Use contact information obtained independently
                    from the company rather than relying only on
                    the submitted message.
                  </p>

                </div>

              </div>

              <div className="professional-action">

                <div className="action-index">
                  03
                </div>

                <div>

                  <h3>
                    Do not pay before verification
                  </h3>

                  <p>
                    Be careful with registration, interview,
                    training, security or document-verification fees.
                  </p>

                </div>

              </div>

              <div className="professional-action">

                <div className="action-index">
                  04
                </div>

                <div>

                  <h3>
                    Protect sensitive information
                  </h3>

                  <p>
                    Do not share OTPs, passwords, banking credentials
                    or unnecessary identity documents with an
                    unverified contact.
                  </p>

                </div>

              </div>

            </div>

          </section>

          {/* DISCLAIMER */}

          <section className="professional-disclaimer">

            <div className="professional-disclaimer-icon">
              i
            </div>

            <div>

              <strong>
                Important limitation
              </strong>

              <p>
                JobShield AI identifies risk indicators and summarizes
                the evidence available to it. A HIGH risk result does
                not by itself prove that an opportunity is fraudulent.
                A LOW risk result does not guarantee legitimacy.
                Independently verify important claims before sending
                money or sensitive information.
              </p>

            </div>

          </section>

        </section>
      )}

      {/* =====================================================
          FEATURES
      ====================================================== */}

      {!result && (
        <section
          className="features-section"
          id="features"
        >

          <div className="section-center">

            <div className="section-label">
              BUILT FOR REAL-WORLD JOB SEARCH
            </div>

            <h2>
              More than an AI chatbot.
            </h2>

            <p>
              JobShield combines structured extraction,
              verification signals and transparent risk analysis.
            </p>

          </div>

          <div className="feature-grid">

            <Feature
              icon="🔎"
              title="Evidence-first"
              text="Every warning is connected to an extracted claim or verification signal."
            />

            <Feature
              icon="🛡"
              title="Risk assessment"
              text="Get Low, Medium, High or Unable to Verify instead of an unexplained AI verdict."
            />

            <Feature
              icon="🔗"
              title="URL analysis"
              text="Analyze domains and suspicious URL patterns before you open unknown links."
            />

            <Feature
              icon="📄"
              title="Document analysis"
              text="Analyze screenshots, PDFs and recruiter messages from one interface."
            />

          </div>

        </section>
      )}

      {/* =====================================================
          FOOTER
      ====================================================== */}

      <footer id="about">

        <div className="footer-brand">

          <div className="brand-icon">
            <ShieldIcon size={19} />
          </div>

          <strong>
            JobShield<span>AI</span>
          </strong>

        </div>

        <p>
          Verify before you trust.
        </p>

        <span>
          Built with Python · FastAPI · React · AI
        </span>

      </footer>

    </div>
  );
}

/* =========================================================
   DETAIL COMPONENT
========================================================= */

function Detail({ label, value, icon }) {
  return (
    <div className="detail">

      <div className="detail-icon">
        {icon}
      </div>

      <div>

        <small>
          {label}
        </small>

        <strong>
          {value || "Not provided"}
        </strong>

      </div>

    </div>
  );
}

/* =========================================================
   VERIFICATION ITEM
========================================================= */

function VerificationItem({ label, verified }) {
  return (
    <div className="verification-item">

      <div
        className={
          verified
            ? "verification-icon verified"
            : "verification-icon pending"
        }
      >
        {verified ? "✓" : "?"}
      </div>

      <div>

        <strong>
          {label}
        </strong>

        <span>
          {verified
            ? "Verified"
            : "Not independently verified"}
        </span>

      </div>

    </div>
  );
}

/* =========================================================
   FEATURE
========================================================= */

function Feature({ icon, title, text }) {
  return (
    <div className="feature-card">

      <div className="feature-icon">
        {icon}
      </div>

      <h3>
        {title}
      </h3>

      <p>
        {text}
      </p>

    </div>
  );
}

export default App;