import os
from pathlib import Path

# Use __file__ to derive absolute project root
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

DATA_DIR = PROJECT_ROOT / "data"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
SAMPLES_DIR = PROJECT_ROOT / "samples"

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

MATERIAL_TYPES = {
    "article": "articles",
    "book": "books",
    "chatlog": "chatlogs",
    "case": "cases",
    "comment": "comments",
    "prompt": "prompts",
    "workflow": "workflows",
    "external_agent": "external_agents",
    "external_skill": "external_skills",
}

SKILL_STATUSES = ["draft", "trained", "tested", "mature", "retired"]

# Mapping from status to directory name
SKILL_STATUS_DIR = {
    "draft": "draft",
    "trained": "trained",
    "tested": "tested",
    "mature": "mature",
    "retired": "retired",
}

MATERIAL_DIR = DATA_DIR / "materials"
SKILLS_DIR = DATA_DIR / "skills"
DRILLS_DIR = DATA_DIR / "drills"
FIELD_LOGS_DIR = DATA_DIR / "field_logs"
REVIEWS_DIR = DATA_DIR / "reviews"
RECOMMENDATIONS_DIR = DATA_DIR / "recommendations"
IMPORTS_DIR = DATA_DIR / "imports"
PROFILES_DIR = DATA_DIR / "profiles"
PROPOSALS_DIR = DATA_DIR / "proposals"
