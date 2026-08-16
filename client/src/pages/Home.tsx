/* Evidence Ledger direction: warm dossier canvas, ink typography, copper keel line, evidence before decoration. */
import { useMemo, useState } from "react";
import { ArrowUpRight, Check, ChevronRight, CircleAlert, FileText, GitPullRequest, ShieldCheck, Terminal } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const checks = [
  { id: "structure", title: "Repository structure", group: "Maintainer", status: "verified", score: 100, source: ".gitignore · README.md · .github/", detail: "Core repository entry points are present." },
  { id: "documentation", title: "Documentation", group: "Docs", status: "verified", score: 100, source: "README.md", detail: "README provides 8 sections and a setup path." },
  { id: "tests", title: "Test surface", group: "Quality", status: "verified", score: 100, source: "tests/", detail: "Found 1 test directory and 4 test files." },
  { id: "ci", title: "Continuous integration", group: "Automation", status: "verified", score: 100, source: ".github/workflows/ci.yml", detail: "Found 1 workflow file with lint, types, tests, and build." },
  { id: "license", title: "Open-source license", group: "Legal", status: "verified", score: 100, source: "LICENSE", detail: "MIT license is present and inspectable." },
  { id: "packaging", title: "Build/package metadata", group: "Build", status: "attention", score: 72, source: "pyproject.toml", detail: "Build metadata is present; release metadata needs review." },
  { id: "secret-hygiene", title: "Secret hygiene", group: "Security", status: "verified", score: 100, source: ".", detail: "No high-confidence hard-coded secret pattern detected." },
];

const statusStyles: Record<string, string> = { verified: "status-verified", attention: "status-attention", blocked: "status-blocked" };

export default function Home() {
  const [filter, setFilter] = useState("All checks");
  const [selected, setSelected] = useState(checks[1]);
  const groups = ["All checks", ...Array.from(new Set(checks.map((check) => check.group)))];
  const filtered = useMemo(() => filter === "All checks" ? checks : checks.filter((check) => check.group === filter), [filter]);
  const verified = checks.filter((check) => check.status === "verified").length;
  const score = Math.round(checks.reduce((sum, check) => sum + check.score, 0) / checks.length);

  return (
    <div className="shipwright-shell">
      <aside className="shipwright-rail">
        <div className="brand-lockup"><div className="brand-mark">S</div><div><div className="brand-name">SHIPWRIGHT</div><div className="brand-sub">RELEASE EVIDENCE</div></div></div>
        <div className="rail-rule" />
        <p className="rail-label">Repository</p>
        <div className="repo-switcher"><span className="repo-dot" /> <span>shipwright</span><ChevronRight size={15} /></div>
        <nav className="rail-nav" aria-label="Primary navigation">
          <a className="rail-link active" href="#overview"><FileText size={16} /> Overview</a>
          <a className="rail-link" href="#checks"><ShieldCheck size={16} /> Checks <span>07</span></a>
          <a className="rail-link" href="#pull-request"><GitPullRequest size={16} /> Pull request <span>02</span></a>
        </nav>
        <div className="rail-footer"><div className="rail-label">Local mode</div><div className="local-status"><span /> No source leaves this machine</div><div className="mono-caption">v0.1.0 · policy/public-release</div></div>
      </aside>

      <main className="shipwright-main" id="overview">
        <header className="topbar"><div><div className="eyebrow">REPOSITORY / RELEASE READINESS</div><h1>Shipwright report</h1></div><div className="top-actions"><Button variant="outline" className="outline-copper"><Terminal size={15} /> Run locally</Button><Button className="copper-button">Export report <ArrowUpRight size={15} /></Button></div></header>
        <section className="verdict-panel">
          <div className="verdict-copy"><div className="eyebrow copper-text">VERDICT · 16 AUG 2026 / 17:22 UTC</div><h2>Ready, with one<br /><em>open question.</em></h2><p>Most release signals are verified. Review the packaging evidence before cutting the next tag.</p><div className="verdict-meta"><span><Check size={14} /> {verified} verified</span><span><CircleAlert size={14} /> 1 attention</span><span className="mono-caption">shipwright.toml</span></div></div>
          <div className="score-block"><div className="score-label">READINESS</div><div className="score-number">{score}<small>/100</small></div><div className="score-bar"><span style={{ width: `${score}%` }} /></div><div className="score-foot"><span>policy threshold</span><b>80</b></div></div>
          <img className="stamp-image" src="/manus-storage/shipwright-release-stamp_1f32e65a.png" alt="Copper release stamp" />
        </section>

        <section className="ledger-section" id="checks">
          <div className="section-heading"><div><div className="eyebrow">THE EVIDENCE LEDGER</div><h3>Seven signals. One decision.</h3></div><div className="filter-tabs">{groups.map((group) => <button key={group} className={filter === group ? "filter active" : "filter"} onClick={() => setFilter(group)}>{group}</button>)}</div></div>
          <div className="ledger-layout"><div className="ledger-list">{filtered.map((check, index) => <button key={check.id} className={`ledger-row ${selected.id === check.id ? "selected" : ""}`} onClick={() => setSelected(check)}><span className="keel-node" /><span className="row-index">0{index + 1}</span><span className="row-main"><strong>{check.title}</strong><small>{check.source}</small></span><span className={`row-status ${statusStyles[check.status]}`}>{check.status}</span><span className="row-score">{check.score}</span><ChevronRight size={16} className="row-arrow" /></button>)}</div>
            <aside className="evidence-drawer"><div className="drawer-top"><span className="eyebrow">SELECTED EVIDENCE</span><span className={`drawer-dot ${statusStyles[selected.status]}`} /></div><h4>{selected.title}</h4><p>{selected.detail}</p><div className="evidence-stamp"><span className="stamp-label">SOURCE PATH</span><code>{selected.source}</code></div><div className="evidence-stamp"><span className="stamp-label">CHECK ID</span><code>{selected.id}</code></div><div className="drawer-action"><span>Next action</span><strong>{selected.status === "attention" ? "Review release metadata" : "No action required"}</strong></div><Button variant="outline" className="drawer-button">Open evidence <ArrowUpRight size={14} /></Button></aside>
          </div>
        </section>
        <footer className="page-footer"><span>SHIPWRIGHT / LOCAL-FIRST RELEASE EVIDENCE</span><span className="mono-caption">Generated from deterministic checks · no network required</span></footer>
      </main>
    </div>
  );
}
