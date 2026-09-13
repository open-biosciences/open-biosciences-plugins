"""Every server declared in .mcp.json must be acknowledged by the skills.

AGE-723. This is the fourth instance of declaration drift in this plugin
(Tier-1a banner, bundle watermark, publish CLI docs, now frontmatter bindings).
Each earlier one was fixed individually and none of the fixes prevented the next,
because each fix corrected a *value* and nothing asserted the two declarations
still agreed.

This test asserts the agreement itself rather than any particular value, so it
survives the pending design decision about how metadata-only connectors should be
bound. It fails when `.mcp.json` and the skill frontmatter disagree, in either
direction:

  - a server is connected at runtime but no skill acknowledges it  (the AGE-723 bug)
  - a skill binds a server that `.mcp.json` does not declare       (the inverse)

A connector that is deliberately not bound by any skill is declared here, in
INTENTIONALLY_UNBOUND, with the reason. That list is the audit surface: adding to
it is a visible decision, whereas silence is what produced this defect.
"""
import json
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[2]
MCP_JSON = PLUGIN / ".mcp.json"
SKILLS = PLUGIN / "skills"

# Servers in .mcp.json that no skill currently binds, each with its reason.
#
# This list is the audit surface. An entry here is a *visible, dated decision*;
# an unlisted unbound server is the AGE-723 defect. Removing an entry and binding
# the server is what the resolving change looks like.
INTENTIONALLY_UNBOUND: dict[str, str] = {
    "psychology-mcp": (
        "AGE-723, recorded 2026-09-13. Declared in .mcp.json since 2026-08-15 "
        "(AGE-587) and reachable at runtime, but deliberately NOT yet bound in "
        "skill frontmatter: psychology-mcp supplies registration metadata "
        "(DOI, venue_class, classification_basis, retraction_status), not claim "
        "content, and whether a metadata-only route may raise a claim's evidence "
        "tier is an open design question (depth-model vs separate binding keys vs "
        "flat-list-plus-rule). Binding it into bindings.literature alongside a "
        "claim-content connector would pre-decide that question by flattening the "
        "distinction. Remove this entry when the design decision lands."
    ),
}


def declared_servers() -> set[str]:
    data = json.loads(MCP_JSON.read_text(encoding="utf-8"))
    return set((data.get("mcpServers") or {}).keys())


def _frontmatter(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def bound_servers() -> dict[str, set[str]]:
    """skill name -> set of connector names named anywhere in its bindings block."""
    out: dict[str, set[str]] = {}
    for skill in sorted(SKILLS.iterdir()):
        md = skill / "SKILL.md"
        if not md.is_file():
            continue
        fm = _frontmatter(md)
        if "bindings:" not in fm:
            out[skill.name] = set()
            continue
        block = fm.split("bindings:", 1)[1]
        names: set[str] = set()
        for raw in block.splitlines():
            line = raw.split("#", 1)[0]          # strip trailing comments
            if ":" not in line:
                continue
            _, _, value = line.partition(":")
            for tok in value.replace("[", " ").replace("]", " ").replace(",", " ").split():
                if tok.startswith("~~"):          # unbound placeholder, not a server
                    continue
                names.add(tok)
        out[skill.name] = names
    return out


class TestDeclarationConsistency(unittest.TestCase):
    def test_every_declared_server_is_bound_by_some_skill(self):
        declared = declared_servers()
        bound = set().union(*bound_servers().values()) if bound_servers() else set()
        missing = declared - bound - set(INTENTIONALLY_UNBOUND)
        self.assertEqual(
            missing,
            set(),
            "server(s) declared in .mcp.json but named by no skill's frontmatter "
            f"bindings: {sorted(missing)}. Either bind them in the relevant skill, "
            "or add them to INTENTIONALLY_UNBOUND with a reason. Silence is what "
            "produced AGE-723.",
        )

    def test_no_skill_binds_an_undeclared_server(self):
        declared = declared_servers()
        for skill, names in bound_servers().items():
            unknown = names - declared
            self.assertEqual(
                unknown,
                set(),
                f"{skill} binds connector(s) absent from .mcp.json: {sorted(unknown)}. "
                "A binding the runtime cannot satisfy is a false capability claim.",
            )

    def test_intentionally_unbound_entries_carry_a_reason(self):
        for name, reason in INTENTIONALLY_UNBOUND.items():
            self.assertTrue(
                reason and reason.strip(),
                f"{name} is listed as intentionally unbound with no reason given.",
            )

    def test_no_skill_claims_a_declared_connector_is_still_pending(self):
        """Prose must not say a connector is coming when .mcp.json already has it."""
        pending = ("arrives with", "will arrive", "not yet wired", "Tier-2 wires")
        declared = declared_servers()
        offenders = []
        for skill in sorted(SKILLS.iterdir()):
            md = skill / "SKILL.md"
            if not md.is_file():
                continue
            for n, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
                if not any(p.lower() in line.lower() for p in pending):
                    continue
                for server in declared:
                    if server in line:
                        offenders.append(f"{skill.name}/SKILL.md:{n}: {line.strip()}")
        self.assertEqual(
            offenders,
            [],
            "skill prose describes an already-declared connector as pending:\n"
            + "\n".join(offenders),
        )


if __name__ == "__main__":
    unittest.main()
