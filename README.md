# dm-skills

Agent skills for running and prepping D&D adventures.

| Skill | Purpose |
|---|---|
| [adventure-tuning](adventure-tuning/SKILL.md) | Converts published adventures into DM-ready encounter writeups (acoustics, gated observations, DM synopsis, stunts, morale engine). |
| [abovevtt-tokens](abovevtt-tokens/SKILL.md) | Updates tokens in AboveVTT `.abovevtt` exports with stat blocks, HP/AC, vision, art, and border colors. |
| [hollow-reach-builder](hollow-reach-builder/SKILL.md) | Generates high-efficiency, 2-to-4-hour West Marches adventures for Hollow Reach using the 5-Room Dungeon / Three-Act Structure, dynamic adversary rosters, 30/20 combat math, and tactile layered challenges. |

## Install

Symlink each skill into a project's `.agents/skills/` folder:

```bash
mkdir -p /path/to/project/.agents/skills
ln -s "$(pwd)/adventure-tuning" /path/to/project/.agents/skills/adventure-tuning
ln -s "$(pwd)/abovevtt-tokens" /path/to/project/.agents/skills/abovevtt-tokens
ln -s "$(pwd)/hollow-reach-builder" /path/to/project/.agents/skills/hollow-reach-builder
```

Edits made through the symlinks land in this repo.
