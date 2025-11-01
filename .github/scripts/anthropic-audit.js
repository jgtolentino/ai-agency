// Minimal runner that sends repo_tree + files and asks Claude to use the Skill.
const fs = require("fs");
const path = require("path");
const fetch = require("node-fetch");

(async () => {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  const model = process.env.MODEL || "claude-3-5-sonnet-20241022";
  const skill = process.env.SKILL || "repo-auditor";

  const repo_tree = fs.readFileSync("repo_tree.txt", "utf8");
  const files = fs.readFileSync(".audit/in/files.txt", "utf8");

  const system = `You are equipped with the "${skill}" Skill from .claude/skills.
Use it to audit this repository. Output two artifacts:
1) Markdown report
2) Strict JSON exactly matching templates/findings.json.schema.
Keep findings <= 40. Provide concrete fixes.`;

  const user = [
    { type: "text", text: "REPO TREE:\n" + repo_tree },
    { type: "text", text: "FILES:\n" + files }
  ];

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
      "anthropic-beta": "messages-2024-10-22,skills-2024-10-22",
      "content-type": "application/json"
    },
    body: JSON.stringify({
      model,
      system,
      max_tokens: 8000,
      messages: [{ role: "user", content: user }]
    })
  });

  if (!res.ok) {
    console.error(await res.text());
    process.exit(1);
  }
  const data = await res.json();
  const text = data?.content?.map(c => c.text || "").join("\n") || "";

  // crude split based on markers the SKILL template uses
  fs.mkdirSync(".audit/out", { recursive: true });
  const mdMatch = text.match(/```markdown([\s\S]*?)```/i) || text.match(/<REPORT>([\s\S]*?)<\/REPORT>/i);
  const jsonMatch = text.match(/```json([\s\S]*?)```/i);

  fs.writeFileSync(".audit/out/raw.txt", text);
  fs.writeFileSync(".audit/out/report.md", mdMatch ? mdMatch[1].trim() : text);
  if (jsonMatch) fs.writeFileSync(".audit/out/findings.json", jsonMatch[1].trim());
  console.log("Audit complete: wrote .audit/out/report.md and findings.json (if present).");
})();
