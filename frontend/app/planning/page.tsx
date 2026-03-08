import fs from "fs";
import path from "path";

function loadPlanningDoc() {
  const candidates = [
    path.join(process.cwd(), "docs", "planning.md"),
    path.join(process.cwd(), "..", "docs", "planning.md"),
  ];
  for (const p of candidates) {
    if (fs.existsSync(p)) return fs.readFileSync(p, "utf-8");
  }
  return "planning.md not found";
}

export default function PlanningPage() {
  const md = loadPlanningDoc();
  return (
    <section>
      <h2>Planning / Spec</h2>
      <pre style={{ whiteSpace: "pre-wrap", lineHeight: 1.6, background: "#fafafa", padding: 16 }}>{md}</pre>
    </section>
  );
}
