<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Mini Data Platform</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap" rel="stylesheet" />
<style>
  :root {
    --bg: #0a0d14;
    --surface: #111520;
    --surface2: #161c2d;
    --border: #1e2a42;
    --accent: #00d4ff;
    --accent2: #0066ff;
    --accent3: #7c3aed;
    --green: #00e5a0;
    --yellow: #ffd23f;
    --text: #c8d6f0;
    --text-dim: #5a6a8a;
    --text-bright: #e8f0ff;
    --mono: 'IBM Plex Mono', monospace;
    --sans: 'IBM Plex Sans', sans-serif;
  }

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    font-size: 15px;
    line-height: 1.75;
    min-height: 100vh;
  }

  /* Grid background */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(var(--border) 1px, transparent 1px),
      linear-gradient(90deg, var(--border) 1px, transparent 1px);
    background-size: 48px 48px;
    opacity: 0.3;
    pointer-events: none;
    z-index: 0;
  }

  .wrap {
    max-width: 920px;
    margin: 0 auto;
    padding: 0 32px 80px;
    position: relative;
    z-index: 1;
  }

  /* ── HERO ── */
  .hero {
    padding: 72px 0 56px;
    border-bottom: 1px solid var(--border);
    position: relative;
    overflow: hidden;
  }

  .hero::after {
    content: '';
    position: absolute;
    top: -60px;
    right: -80px;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(0,102,255,0.12) 0%, transparent 70%);
    pointer-events: none;
  }

  .badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 500;
    color: var(--accent);
    background: rgba(0,212,255,0.08);
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 4px;
    padding: 4px 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 24px;
  }

  .badge::before {
    content: '';
    width: 6px;
    height: 6px;
    background: var(--accent);
    border-radius: 50%;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }

  h1 {
    font-family: var(--mono);
    font-size: clamp(32px, 5vw, 52px);
    font-weight: 600;
    color: var(--text-bright);
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-bottom: 16px;
  }

  h1 span {
    color: var(--accent);
  }

  .hero-sub {
    font-size: 17px;
    font-weight: 300;
    color: var(--text-dim);
    max-width: 560px;
    line-height: 1.6;
    margin-bottom: 32px;
  }

  .pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .pill {
    font-family: var(--mono);
    font-size: 12px;
    padding: 5px 12px;
    border-radius: 4px;
    border: 1px solid var(--border);
    color: var(--text-dim);
    background: var(--surface);
    letter-spacing: 0.04em;
  }

  .pill.green { color: var(--green); border-color: rgba(0,229,160,0.25); background: rgba(0,229,160,0.06); }
  .pill.blue { color: var(--accent); border-color: rgba(0,212,255,0.25); background: rgba(0,212,255,0.06); }
  .pill.purple { color: #a78bfa; border-color: rgba(124,58,237,0.3); background: rgba(124,58,237,0.08); }

  /* ── SECTION HEADERS ── */
  h2 {
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 500;
    color: var(--accent);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin: 56px 0 24px;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  h2::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, var(--border), transparent);
  }

  h3 {
    font-family: var(--mono);
    font-size: 14px;
    font-weight: 500;
    color: var(--text-bright);
    margin: 28px 0 12px;
    letter-spacing: 0.02em;
  }

  h4 {
    font-family: var(--sans);
    font-size: 13px;
    font-weight: 600;
    color: var(--accent);
    margin: 20px 0 8px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }

  p {
    color: var(--text);
    margin-bottom: 12px;
    font-weight: 300;
  }

  /* ── CARDS ── */
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 24px 28px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
  }

  .card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px;
    height: 100%;
    background: linear-gradient(to bottom, var(--accent), var(--accent2));
    opacity: 0;
    transition: opacity 0.2s;
  }

  .card:hover { border-color: rgba(0,212,255,0.3); }
  .card:hover::before { opacity: 1; }

  .card-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }

  @media (max-width: 600px) { .card-grid { grid-template-columns: 1fr; } }

  .card-label {
    font-family: var(--mono);
    font-size: 10px;
    color: var(--text-dim);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 6px;
  }

  .card-title {
    font-family: var(--mono);
    font-size: 15px;
    font-weight: 600;
    color: var(--text-bright);
    margin-bottom: 8px;
  }

  .card-body {
    font-size: 13px;
    font-weight: 300;
    color: var(--text-dim);
    line-height: 1.6;
  }

  /* ── TABLES ── */
  .tbl-wrap { overflow-x: auto; margin: 20px 0; }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    font-family: var(--mono);
  }

  thead tr {
    background: var(--surface2);
    border-bottom: 1px solid var(--border);
  }

  thead th {
    padding: 10px 16px;
    text-align: left;
    font-size: 10px;
    font-weight: 500;
    color: var(--text-dim);
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }

  tbody tr {
    border-bottom: 1px solid rgba(30,42,66,0.5);
    transition: background 0.15s;
  }

  tbody tr:hover { background: rgba(0,212,255,0.03); }

  tbody td {
    padding: 10px 16px;
    color: var(--text);
    font-weight: 400;
  }

  tbody td:first-child {
    color: var(--accent);
    font-weight: 500;
  }

  /* ── CODE ── */
  pre {
    background: #080b12;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 18px 20px;
    overflow-x: auto;
    margin: 16px 0;
    position: relative;
  }

  pre::before {
    content: attr(data-lang);
    position: absolute;
    top: 10px; right: 14px;
    font-family: var(--mono);
    font-size: 10px;
    color: var(--text-dim);
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }

  code {
    font-family: var(--mono);
    font-size: 13px;
    color: var(--green);
    line-height: 1.7;
  }

  p code, li code {
    background: rgba(0,229,160,0.08);
    border: 1px solid rgba(0,229,160,0.15);
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 12px;
    color: var(--green);
  }

  /* ── PIPELINE STEPS ── */
  .pipeline {
    display: flex;
    flex-direction: column;
    gap: 0;
    margin: 24px 0;
  }

  .step {
    display: flex;
    align-items: flex-start;
    gap: 20px;
    padding: 16px 0;
    position: relative;
  }

  .step + .step { border-top: 1px solid var(--border); }

  .step-num {
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 600;
    color: var(--accent2);
    background: rgba(0,102,255,0.12);
    border: 1px solid rgba(0,102,255,0.25);
    border-radius: 4px;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
  }

  .step-content strong {
    font-family: var(--mono);
    font-size: 13px;
    font-weight: 500;
    color: var(--text-bright);
    display: block;
    margin-bottom: 2px;
  }

  .step-content span {
    font-size: 13px;
    color: var(--text-dim);
    font-weight: 300;
  }

  /* ── SERVICES ── */
  .services {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
    margin: 20px 0;
  }

  .service {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 16px 18px;
  }

  .service-name {
    font-family: var(--mono);
    font-size: 12px;
    font-weight: 600;
    color: var(--text-bright);
    margin-bottom: 4px;
  }

  .service-port {
    font-family: var(--mono);
    font-size: 20px;
    font-weight: 600;
    color: var(--accent);
    margin-bottom: 4px;
  }

  .service-desc {
    font-size: 12px;
    color: var(--text-dim);
  }

  /* ── LISTS ── */
  ul, ol {
    padding-left: 0;
    list-style: none;
    margin: 12px 0 20px;
  }

  ul li, ol li {
    padding: 5px 0 5px 22px;
    color: var(--text);
    font-size: 14px;
    font-weight: 300;
    position: relative;
  }

  ul li::before {
    content: '—';
    position: absolute;
    left: 0;
    color: var(--text-dim);
    font-family: var(--mono);
    font-size: 12px;
  }

  ol { counter-reset: item; }
  ol li { counter-increment: item; }
  ol li::before {
    content: counter(item, decimal-leading-zero);
    position: absolute;
    left: 0;
    color: var(--accent2);
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 600;
    top: 6px;
  }

  /* ── FLOW DIAGRAM ── */
  .flow-diagram {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 28px;
    margin: 20px 0;
    overflow-x: auto;
  }

  .flow-row {
    display: flex;
    align-items: center;
    gap: 0;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
  }

  .flow-node {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 10px 18px;
    font-family: var(--mono);
    font-size: 12px;
    font-weight: 500;
    color: var(--text-bright);
    white-space: nowrap;
  }

  .flow-node.accent { border-color: rgba(0,212,255,0.4); color: var(--accent); }
  .flow-node.green { border-color: rgba(0,229,160,0.4); color: var(--green); }

  .flow-arrow {
    color: var(--text-dim);
    font-family: var(--mono);
    font-size: 16px;
    padding: 0 4px;
  }

  /* ── SECTION DIVIDER ── */
  .divider {
    height: 1px;
    background: linear-gradient(to right, transparent, var(--border), transparent);
    margin: 48px 0;
  }

  /* ── HIGHLIGHT BOX ── */
  .info-box {
    background: rgba(0,102,255,0.06);
    border: 1px solid rgba(0,102,255,0.2);
    border-left: 3px solid var(--accent2);
    border-radius: 4px;
    padding: 16px 20px;
    margin: 20px 0;
    font-size: 14px;
    font-weight: 300;
    color: var(--text);
  }

  .info-box strong {
    color: var(--accent);
    font-family: var(--mono);
    font-size: 12px;
    font-weight: 500;
    display: block;
    margin-bottom: 6px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  /* ── STRUCTURE TREE ── */
  .tree {
    background: #080b12;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 20px 24px;
    font-family: var(--mono);
    font-size: 13px;
    line-height: 1.9;
    overflow-x: auto;
  }

  .tree .dir { color: var(--accent); }
  .tree .file { color: var(--text-dim); }
  .tree .comment { color: rgba(90,106,138,0.6); }

  /* ── FOOTER ── */
  footer {
    margin-top: 80px;
    padding-top: 32px;
    border-top: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: gap;
    gap: 12px;
  }

  footer span {
    font-family: var(--mono);
    font-size: 12px;
    color: var(--text-dim);
    letter-spacing: 0.04em;
  }

  .license-badge {
    font-family: var(--mono);
    font-size: 11px;
    padding: 4px 10px;
    border: 1px solid var(--border);
    border-radius: 4px;
    color: var(--text-dim);
  }

  /* ── ANIMATE IN ── */
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .hero { animation: fadeUp 0.5s ease both; }
  section { animation: fadeUp 0.5s ease both; animation-delay: 0.1s; }
</style>
</head>
<body>
<div class="wrap">

  <!-- HERO -->
  <div class="hero">
    <div class="badge">data engineering project</div>
    <h1>Mini Data <span>Platform</span></h1>
    <p class="hero-sub">A containerized end-to-end data platform for ingesting, processing, storing, and visualizing e-commerce data using modern data engineering tools.</p>
    <div class="pill-row">
      <span class="pill blue">Docker</span>
      <span class="pill blue">Apache Airflow</span>
      <span class="pill green">PostgreSQL</span>
      <span class="pill green">MinIO</span>
      <span class="pill purple">Metabase</span>
      <span class="pill purple">Python</span>
      <span class="pill">GitHub Actions</span>
    </div>
  </div>

  <!-- OVERVIEW -->
  <section>
    <h2>Project Overview</h2>

    <h3>What</h3>
    <p>Mini Data Platform is a containerized data platform built with Docker Compose that demonstrates how modern data systems work together.</p>
    <p>The platform automatically:</p>
    <ul>
      <li>Generates sample e-commerce data</li>
      <li>Uploads it to object storage</li>
      <li>Detects and processes new data</li>
      <li>Loads cleaned data into a database</li>
      <li>Visualizes insights through dashboards</li>
    </ul>

    <p>The system integrates several widely used data engineering tools:</p>
    <div class="tbl-wrap">
      <table>
        <thead><tr><th>Tool</th><th>Purpose</th></tr></thead>
        <tbody>
          <tr><td>PostgreSQL</td><td>Analytical data storage</td></tr>
          <tr><td>Apache Airflow</td><td>Workflow orchestration</td></tr>
          <tr><td>MinIO</td><td>Object storage (S3 compatible)</td></tr>
          <tr><td>Metabase</td><td>Data visualization and dashboards</td></tr>
        </tbody>
      </table>
    </div>

    <h3>Why</h3>
    <p>Modern data platforms consist of multiple components working together:</p>
    <div class="tbl-wrap">
      <table>
        <thead><tr><th>Layer</th><th>Example Tool</th></tr></thead>
        <tbody>
          <tr><td>Data Ingestion</td><td>Object Storage</td></tr>
          <tr><td>Workflow Orchestration</td><td>Airflow</td></tr>
          <tr><td>Data Processing</td><td>Python ETL</td></tr>
          <tr><td>Data Warehouse</td><td>PostgreSQL</td></tr>
          <tr><td>Business Intelligence</td><td>Metabase</td></tr>
        </tbody>
      </table>
    </div>
    <p>This project demonstrates how these systems integrate together in a simplified architecture.</p>
    <p>It is ideal for learning:</p>
    <ul>
      <li>Data engineering fundamentals</li>
      <li>ETL pipeline development</li>
      <li>Workflow orchestration</li>
      <li>Docker based infrastructure</li>
      <li>Data visualization pipelines</li>
      <li>CI/CD for data platforms</li>
    </ul>

    <h3>How</h3>
    <p>The system works through an automated pipeline:</p>
    <div class="pipeline">
      <div class="step"><div class="step-num">01</div><div class="step-content"><strong>Data generators create synthetic e-commerce CSV files</strong></div></div>
      <div class="step"><div class="step-num">02</div><div class="step-content"><strong>Files are uploaded to MinIO object storage</strong></div></div>
      <div class="step"><div class="step-num">03</div><div class="step-content"><strong>Airflow scans MinIO for new files</strong></div></div>
      <div class="step"><div class="step-num">04</div><div class="step-content"><strong>ETL pipelines clean and transform the data</strong></div></div>
      <div class="step"><div class="step-num">05</div><div class="step-content"><strong>Processed data is stored in PostgreSQL</strong></div></div>
      <div class="step"><div class="step-num">06</div><div class="step-content"><strong>Metabase dashboards visualize insights</strong></div></div>
    </div>
  </section>

  <!-- ARCHITECTURE -->
  <section>
    <h2>Architecture Overview</h2>

    <div class="flow-diagram">
      <div class="flow-row">
        <div class="flow-node">User</div>
        <div class="flow-arrow">→</div>
        <div class="flow-node accent">Metabase</div>
        <div class="flow-arrow">←</div>
        <div class="flow-node green">PostgreSQL</div>
        <div class="flow-arrow">←</div>
        <div class="flow-node">Python ETL</div>
        <div class="flow-arrow">←</div>
        <div class="flow-node">Apache Airflow</div>
        <div class="flow-arrow">←</div>
        <div class="flow-node">MinIO</div>
        <div class="flow-arrow">←</div>
        <div class="flow-node">Data Generator</div>
      </div>
    </div>
    <p>The entire platform runs inside Docker containers. Components interact through an internal Docker network.</p>

    <h3>Data Flow</h3>
    <div class="pipeline">
      <div class="step"><div class="step-num">01</div><div class="step-content"><strong>Generator → MinIO</strong><span>Upload CSV files</span></div></div>
      <div class="step"><div class="step-num">02</div><div class="step-content"><strong>Airflow → MinIO</strong><span>Scan for new files, return file list</span></div></div>
      <div class="step"><div class="step-num">03</div><div class="step-content"><strong>Airflow → ETL</strong><span>Trigger entity pipelines</span></div></div>
      <div class="step"><div class="step-num">04</div><div class="step-content"><strong>ETL → PostgreSQL</strong><span>Load cleaned data</span></div></div>
      <div class="step"><div class="step-num">05</div><div class="step-content"><strong>PostgreSQL → Metabase</strong><span>Query datasets</span></div></div>
      <div class="step"><div class="step-num">06</div><div class="step-content"><strong>Metabase → User</strong><span>Display dashboards</span></div></div>
    </div>
  </section>

  <!-- TECH STACK -->
  <section>
    <h2>Tech Stack</h2>
    <div class="tbl-wrap">
      <table>
        <thead><tr><th>Technology</th><th>Purpose</th></tr></thead>
        <tbody>
          <tr><td>Docker</td><td>Containerization</td></tr>
          <tr><td>Docker Compose</td><td>Multi-service orchestration</td></tr>
          <tr><td>PostgreSQL</td><td>Data warehouse</td></tr>
          <tr><td>Apache Airflow</td><td>Workflow orchestration</td></tr>
          <tr><td>MinIO</td><td>Object storage</td></tr>
          <tr><td>Metabase</td><td>Data visualization</td></tr>
          <tr><td>Python</td><td>ETL pipelines</td></tr>
          <tr><td>GitHub Actions</td><td>CI/CD automation</td></tr>
        </tbody>
      </table>
    </div>

    <h3>Service Ports</h3>
    <div class="services">
      <div class="service">
        <div class="service-name">PostgreSQL</div>
        <div class="service-port">5432</div>
        <div class="service-desc">Data warehouse</div>
      </div>
      <div class="service">
        <div class="service-name">Airflow Webserver</div>
        <div class="service-port">8080</div>
        <div class="service-desc">Workflow UI</div>
      </div>
      <div class="service">
        <div class="service-name">MinIO API</div>
        <div class="service-port">9000</div>
        <div class="service-desc">Object storage API</div>
      </div>
      <div class="service">
        <div class="service-name">MinIO Console</div>
        <div class="service-port">9001</div>
        <div class="service-desc">Object storage UI</div>
      </div>
      <div class="service">
        <div class="service-name">Metabase</div>
        <div class="service-port">3000</div>
        <div class="service-desc">BI dashboards</div>
      </div>
    </div>

    <h3>Docker Image</h3>
    <p>The project builds and deploys the Docker image:</p>
    <pre data-lang="docker"><code>percyayimbila/mini-data-platform:latest</code></pre>
  </section>

  <!-- PROJECT STRUCTURE -->
  <section>
    <h2>Project Structure</h2>
    <div class="tree">
<span class="dir">Mini_Data_Platform/</span>
├── <span class="dir">.github/workflows/</span>
│   └── <span class="file">main.yml</span>
│
├── <span class="dir">airflow/dags/</span>
│   ├── <span class="file">etl_minio_pipeline_dag.py</span>
│   └── <span class="file">pipeline.py</span>
│
├── <span class="dir">data/tmp/</span>
│   ├── <span class="dir">users/</span>
│   ├── <span class="dir">products/</span>
│   ├── <span class="dir">orders/</span>
│   └── <span class="dir">order_items/</span>
│
├── <span class="dir">scripts/</span>
│
├── <span class="dir">src/</span>
│   ├── <span class="dir">data_generators/</span>
│   ├── <span class="dir">detection/</span>
│   ├── <span class="dir">etl/</span>
│   │   ├── <span class="file">base_etl.py</span>
│   │   ├── <span class="file">users_etl.py</span>
│   │   ├── <span class="file">products_etl.py</span>
│   │   ├── <span class="file">orders_etl.py</span>
│   │   └── <span class="file">order_items_etl.py</span>
│   ├── <span class="dir">data_quality/</span>
│   ├── <span class="dir">scripts/</span>
│   │   └── <span class="file">db_init.sql</span>
│   └── <span class="dir">utils/</span>
│
├── <span class="dir">tests/</span>
│
├── <span class="file">docker-compose.yml</span>
├── <span class="file">docker-compose.prod.yml</span>
├── <span class="file">Dockerfile</span>
├── <span class="file">requirements.txt</span>
└── <span class="file">README.md</span>
    </div>
  </section>

  <!-- PREREQUISITES -->
  <section>
    <h2>Prerequisites</h2>
    <p>Install the following before running the project.</p>
    <ul>
      <li>Docker</li>
      <li>Docker Compose</li>
      <li>Python 3.11+</li>
      <li>Git</li>
    </ul>
  </section>

  <!-- INSTALLATION -->
  <section>
    <h2>Installation and Setup</h2>

    <h3>Clone the repository</h3>
    <pre data-lang="bash"><code>git clone https://github.com/&lt;your-username&gt;/Mini_Data_Platform.git
cd Mini_Data_Platform</code></pre>

    <h3>Create the environment file</h3>
    <pre data-lang=".env"><code>POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=ecommerce
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin</code></pre>

    <h3>Running the Platform</h3>
    <p>Start all services using Docker Compose.</p>
    <pre data-lang="bash"><code>docker compose up -d</code></pre>
    <p>Verify running containers.</p>
    <pre data-lang="bash"><code>docker ps</code></pre>

    <h3>Accessing Services</h3>
    <div class="tbl-wrap">
      <table>
        <thead><tr><th>Service</th><th>URL</th></tr></thead>
        <tbody>
          <tr><td>Airflow</td><td>http://localhost:8080</td></tr>
          <tr><td>MinIO Console</td><td>http://localhost:9001</td></tr>
          <tr><td>Metabase</td><td>http://localhost:3000</td></tr>
          <tr><td>PostgreSQL</td><td>localhost:5432</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <!-- DATA PIPELINE -->
  <section>
    <h2>Data Pipeline Explanation</h2>
    <p>The platform contains two main Airflow pipelines.</p>

    <div class="card-grid">
      <div class="card">
        <div class="card-label">Pipeline 01</div>
        <div class="card-title">Data Generation Pipeline</div>
        <div class="card-body">
          DAG: <code>pipeline.py</code><br /><br />
          Generates synthetic e-commerce datasets and uploads CSV files to MinIO.<br /><br />
          Entities: Users, Products, Orders, Order Items
        </div>
      </div>
      <div class="card">
        <div class="card-label">Pipeline 02</div>
        <div class="card-title">ETL Processing Pipeline</div>
        <div class="card-body">
          DAG: <code>etl_minio_pipeline_dag.py</code><br /><br />
          Runs every 5 minutes. Scans MinIO, registers new files, fetches pending files, runs ETL by entity type.
        </div>
      </div>
    </div>

    <h3>Entity ETL Pipelines</h3>
    <p>Each dataset has its own ETL module under <code>src/etl/</code>.</p>
    <div class="tbl-wrap">
      <table>
        <thead><tr><th>ETL Module</th><th>Purpose</th></tr></thead>
        <tbody>
          <tr><td>users_etl.py</td><td>Process user data</td></tr>
          <tr><td>products_etl.py</td><td>Process product data</td></tr>
          <tr><td>orders_etl.py</td><td>Process order data</td></tr>
          <tr><td>order_items_etl.py</td><td>Process order item data</td></tr>
        </tbody>
      </table>
    </div>

    <p>All ETL pipelines extend <code>base_etl.py</code>, which provides shared functionality:</p>
    <ul>
      <li>File loading</li>
      <li>Data cleaning</li>
      <li>Data transformation</li>
      <li>PostgreSQL loading</li>
      <li>Logging</li>
    </ul>

    <h3>MinIO Storage</h3>
    <p>Bucket name: <code>ecommerce-data</code></p>
    <p>Example stored files:</p>
    <pre data-lang="storage"><code>users_2026_03_01.csv
products_2026_03_01.csv
orders_2026_03_01.csv
order_items_2026_03_01.csv</code></pre>

    <h3>Complete Data Flow</h3>
    <div class="pipeline">
      <div class="step"><div class="step-num">01</div><div class="step-content"><strong>Data generator creates CSV files</strong></div></div>
      <div class="step"><div class="step-num">02</div><div class="step-content"><strong>Files are uploaded to MinIO bucket</strong><span>ecommerce-data</span></div></div>
      <div class="step"><div class="step-num">03</div><div class="step-content"><strong>Airflow scans MinIO every 5 minutes</strong></div></div>
      <div class="step"><div class="step-num">04</div><div class="step-content"><strong>New files are registered and processed</strong></div></div>
      <div class="step"><div class="step-num">05</div><div class="step-content"><strong>ETL cleans and transforms the data</strong></div></div>
      <div class="step"><div class="step-num">06</div><div class="step-content"><strong>Data is loaded into PostgreSQL</strong></div></div>
      <div class="step"><div class="step-num">07</div><div class="step-content"><strong>Metabase queries PostgreSQL</strong></div></div>
      <div class="step"><div class="step-num">08</div><div class="step-content"><strong>Dashboards visualize insights</strong></div></div>
    </div>
  </section>

  <!-- USE CASE -->
  <section>
    <h2>Example Use Case</h2>
    <p>Imagine an e-commerce platform collecting transaction data. This platform can answer questions like:</p>
    <ul>
      <li>Top selling products</li>
      <li>Revenue trends</li>
      <li>Customer growth</li>
      <li>Order frequency</li>
    </ul>
    <p>Metabase dashboards can display:</p>
    <ul>
      <li>Sales over time</li>
      <li>Product popularity</li>
      <li>Customer distribution</li>
      <li>Order volume</li>
    </ul>

    <h3>Dashboard Examples</h3>
    <div class="card-grid">
      <div class="card">
        <div class="card-label">Screenshot placeholder</div>
        <div class="card-title">Metabase Dashboards</div>
        <div class="card-body">docs/dashboard_sales.png<br />docs/dashboard_orders.png</div>
      </div>
      <div class="card">
        <div class="card-label">Screenshot placeholder</div>
        <div class="card-title">Airflow DAGs</div>
        <div class="card-body">docs/airflow_dag_etl.png<br />docs/airflow_dag_generation.png</div>
      </div>
      <div class="card">
        <div class="card-label">Screenshot placeholder</div>
        <div class="card-title">MinIO Storage</div>
        <div class="card-body">docs/minio_bucket.png</div>
      </div>
      <div class="card">
        <div class="card-label">Screenshot placeholder</div>
        <div class="card-title">CI/CD Pipeline</div>
        <div class="card-body">docs/github_actions_pipeline.png</div>
      </div>
    </div>
  </section>

  <!-- CI/CD -->
  <section>
    <h2>CI/CD Pipeline</h2>
    <p>The project uses GitHub Actions.</p>

    <h3>Continuous Integration</h3>
    <p>On every push:</p>
    <ul>
      <li>Install dependencies</li>
      <li>Run tests</li>
      <li>Build Docker image</li>
      <li>Push image to Docker Hub</li>
    </ul>

    <h3>Continuous Deployment</h3>
    <p>When merging to main:</p>
    <ul>
      <li>Pull latest Docker image</li>
      <li>Start production stack</li>
      <li>Deploy containers</li>
    </ul>

    <h3>Data Flow Validation</h3>
    <p>The pipeline ensures the following flow works correctly:</p>
    <div class="info-box">
      <strong>Validated flow</strong>
      MinIO → Airflow → ETL → PostgreSQL → Metabase
    </div>
    <p>This guarantees that files are detected, ETL processes run successfully, data reaches PostgreSQL, and dashboards update automatically.</p>
  </section>

  <!-- TROUBLESHOOTING -->
  <section>
    <h2>Troubleshooting</h2>

    <h3>Containers not starting</h3>
    <p>Check logs:</p>
    <pre data-lang="bash"><code>docker compose logs</code></pre>

    <h3>Airflow not loading DAGs</h3>
    <p>Restart Airflow services.</p>
    <pre data-lang="bash"><code>docker compose restart airflow</code></pre>

    <h3>PostgreSQL connection errors</h3>
    <p>Verify environment variables in <code>.env</code>.</p>

    <h3>MinIO bucket missing</h3>
    <p>Create the bucket: <code>ecommerce-data</code></p>
  </section>

  <!-- FUTURE -->
  <section>
    <h2>Future Improvements</h2>
    <p>Potential improvements for the platform:</p>
    <ul>
      <li>Add Kafka for streaming ingestion</li>
      <li>Implement dbt transformations</li>
      <li>Use DuckDB or ClickHouse for analytics</li>
      <li>Add data quality monitoring</li>
      <li>Add data lineage tracking</li>
      <li>Deploy using Kubernetes</li>
      <li>Implement data lake architecture</li>
    </ul>
  </section>

  <!-- CONTRIBUTION -->
  <section>
    <h2>Contribution Guide</h2>
    <p>Contributions are welcome.</p>
    <ol>
      <li>Fork the repository</li>
      <li>Create a new branch: <code>feature/your-feature</code></li>
      <li>Commit your changes</li>
      <li>Submit a Pull Request</li>
    </ol>
  </section>

  <footer>
    <span>Mini Data Platform</span>
    <span class="license-badge">MIT License</span>
  </footer>

</div>
</body>
</html>