#!/usr/bin/env python3
"""vendor-ask-guard (prototype): scan agent skill files for vendor-growth
instructions — directives that serve the vendor, not the user.

Design: the target is DATA, never instructions. Static regex scan only;
nothing is executed. Every finding cites file:line. A finding is a flag
for human review, not proof of malice.

Usage: python3 vendor_ask_guard.py <skill-dir> [--json]
Exit codes: 0 = no findings above low, 1 = medium+ findings, 2 = error.
"""
import json
import os
import re
import sys

RULES = [
    # (id, severity, family, pattern, message)
    ("STAR_ASK", "medium", "growth-directive",
     r"\bstars?(ring)? (the|this|our|my) (GitHub )?repo(sitory)?\b",
     "Instruction to solicit a GitHub star"),
    ("STAR_ASK_ALT", "medium", "growth-directive",
     r"\bstarred (us|it|the repo)\b|support .*with a star\b",
     "Instruction to solicit a GitHub star (alt phrasing)"),
    ("STAR_ASK_API", "medium", "growth-directive",
     r"user/starred/",
     "GitHub star API endpoint referenced (starring as the user)"),
    ("STAR_ASK_SUPPORT", "medium", "growth-directive",
     r"support the project by starring",
     "Instruction to ask the user to star the project"),
    ("GIVE_STAR", "medium", "growth-directive",
     r"give us a star",
     "Instruction to solicit a GitHub star"),
    ("FOLLOW_ASK", "low", "growth-directive",
     r"follow (us|me) on",
     "Instruction to solicit a social follow"),
    ("SUBSCRIBE_ASK", "low", "growth-directive",
     r"subscribe to (our|my) (newsletter|youtube|channel|blog)",
     "Instruction to solicit a subscription"),
    ("SHARE_ASK", "medium", "growth-directive",
     r"share this (with|on)|share this (skill|repo|project|tool|post) with|spread the word|tell (your|a) friend|forward this to",
     "Instruction to solicit sharing / word-of-mouth"),
    ("SELF_PROMO", "medium", "growth-directive",
     r"tell the user about our|let the user know about|recommend our|suggest our product|mention our (product|tool|service|app)|check out our (product|tool|service|app|platform|hosted|pro|paid|premium|cloud|managed)|try our (product|tool|service|app)",
     "Instruction to promote the vendor's own offering"),
    ("RATING_ASK", "low", "growth-directive",
     r"\bleave (us |a )?reviews?\b|\brate (us|this skill|the skill)\b",
     "Instruction to solicit a rating/review"),
    ("NEWSLETTER_ASK", "low", "growth-directive",
     r"sign up for (our|my) newsletter",
     "Instruction to solicit a newsletter signup"),
    ("TELEMETRY_PING", "info", "telemetry",
     r"(curl|wget|Invoke-WebRequest)[^\n]*(analytics|telemetry|/track|metrics\.|collect\?)",
     "Possible telemetry/usage ping in a command"),
    ("INSTALL_PING", "info", "telemetry",
     r"installs? (are |is )?(counted|tracked)",
     "Documentation admits install counting/tracking"),
    ("SOCIAL_POST_ASK", "medium", "growth-directive",
     r"(tweet|post) about (this|it|us)|announce (this|it) on (x|twitter|linkedin)",
     "Instruction to post about the project on social media"),
    ("COMMENT_ASK", "low", "growth-directive",
     r"leave a comment on (our|this)|comment on our (release|launch|post)",
     "Instruction to solicit engagement on vendor content"),
    ("COMMUNITY_ASK", "low", "growth-directive",
     r"join our (discord|community|slack|forum)",
     "Instruction to funnel users into vendor community"),
    ("SPONSOR_ASK", "low", "growth-directive",
     r"sponsor (us|me|this project)|buy me a coffee|support us on (patreon|github sponsors|open collective)",
     "Instruction to solicit money/sponsorship"),
    ("BACKLINK_ASK", "medium", "growth-directive",
     r"link back to (us|our)|add (a |our )badge to your readme|powered-by badge",
     "Instruction to solicit backlinks/badges (SEO juice)"),
    ("TESTIMONIAL_ASK", "low", "growth-directive",
     r"share your results with us|tell us how you used|send us your (story|use case)",
     "Instruction to harvest user testimonials"),
    ("AFFILIATE_LINK", "info", "telemetry",
     r"https?://[^\s)]*[?&](ref=|affiliate=|via=|utm_source=)",
     "Tracked/attributed outbound link in skill text"),
]

SEV_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3}

TEXT_EXTS = {".md", ".txt", ".rst", ".json", ".yaml", ".yml", ".sh"}


def scan_file(path):
    findings = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError as e:
        return [("ERROR", "error", "io", 0, str(e))]
    for i, line in enumerate(lines, 1):
        for rid, sev, fam, pat, msg in RULES:
            if re.search(pat, line, re.IGNORECASE):
                findings.append((rid, sev, fam, i, line.strip()[:160]))
    return findings


def scan_dir(root):
    results = []
    for dirpath, _, filenames in os.walk(root):
        for fn in sorted(filenames):
            if os.path.splitext(fn)[1].lower() not in TEXT_EXTS:
                continue
            p = os.path.join(dirpath, fn)
            for f in scan_file(p):
                results.append((os.path.relpath(p, root),) + f)
    return results


def main():
    if len(sys.argv) < 2:
        print("usage: vendor_ask_guard.py <skill-dir> [--json]", file=sys.stderr)
        return 2
    root = sys.argv[1]
    as_json = "--json" in sys.argv
    if not os.path.isdir(root):
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2
    results = scan_dir(root)
    counts = {}
    for r in results:
        counts[r[2]] = counts.get(r[2], 0) + 1
    worst = max([SEV_ORDER[r[2]] for r in results], default=0)
    if as_json:
        print(json.dumps({
            "target": root,
            "findings": [
                {"file": r[0], "rule": r[1], "severity": r[2],
                 "family": r[3], "line": r[4], "match": r[5]}
                for r in results
            ],
            "counts": counts,
        }, indent=2))
    else:
        if not results:
            print("No vendor-ask findings.")
        for r in results:
            print(f"[{r[2].upper()}] {r[1]} {r[0]}:{r[4]}")
            print(f"    {r[3]}: {r[5]}")
        print(f"\nFindings: " + ("none" if not counts else
              " | ".join(f"{k} {v}" for k, v in sorted(counts.items()))))
    return 1 if worst >= SEV_ORDER["medium"] else 0


if __name__ == "__main__":
    sys.exit(main())
