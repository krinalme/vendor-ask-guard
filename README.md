# vendor-ask-guard

Static scanner that flags **vendor-growth instructions** in AI agent skill files — the directives that serve the vendor, not you.

Security scanners ask "is this skill safe?" This asks a different question: **"what will this skill make my agent do for the vendor?"** Star the repo. Follow us. Tell the user about our Pro plan. A skill is Markdown your agent obeys; growth asks ride inside the trusted setup flow with the same authority as configuration steps.

## Origin

Built Oct 18, 2026, after installing `newsjack.sh` — whose `newsjack-monitor-setup` skill ends with a section literally titled "Starring" instructing the agent to ask the user for a GitHub star and run `gh api -X PUT /user/starred/elvisun/newsjack`. Consent-gated, disclosed in open source — and completely invisible unless you read the skill file.

## Usage

```bash
python3 -I vendor_ask_guard.py /path/to/skills [--json]
```

Exit codes: `0` = no findings above low, `1` = medium+ findings, `2` = error. Dependency-free (stdlib only).

## Rule families

| Family | Severity | Examples |
|---|---|---|
| growth-directive | medium | star/follow/share asks, self-promo directives, backlink/badge solicitation, social-post asks |
| growth-directive | low | rating/review asks, community funnels, sponsorship asks, testimonial harvesting |
| telemetry | info | usage pings, install counting, tracked outbound links |

## Design principles

- **Target is data, never instructions.** Static regex scan; nothing is executed.
- **Every finding cites file:line.** A finding is a flag for human review, not proof of malice.
- **Honest about limits.** "No findings" means nothing matched these rules, not that the skill is clean.

## Relationship to Skill Auditor

[Skill Auditor](https://github.com/Plastikelectrik/skill-auditor) (MIT) covers the security half: prompt injection, exfiltration, obfuscation, credential theft. vendor-ask-guard covers the marketing half. The rule families are complementary — the plan is to propose the growth-directive family upstream once it matures.

## Test corpus

`corpus/` (gitignored) holds shallow clones of popular skill repos used for tuning: `anthropics/skills`, `obra/superpowers`, `mattpocock/skills`, `growthbook/skills`, plus `elvisun/newsjack`. Fetch with `./fetch_corpus.sh`. `fixtures/adversarial.md` holds 14 paraphrased growth directives + 5 control lines; the scanner must hit 14/14 with zero control hits.

## License

MIT
