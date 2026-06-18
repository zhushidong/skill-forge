import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# CLI treats current working directory as project root
PROJECT_ROOT = Path.cwd()

DATA_DIR = PROJECT_ROOT / "data"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
SAMPLES_DIR = PROJECT_ROOT / "samples"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
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

# Complete directory structure
ALL_DIRS = [
    "data/materials/articles",
    "data/materials/books",
    "data/materials/chatlogs",
    "data/materials/cases",
    "data/materials/comments",
    "data/materials/external_agents",
    "data/materials/external_skills",
    "data/materials/prompts",
    "data/materials/workflows",
    "data/skills/draft",
    "data/skills/trained",
    "data/skills/tested",
    "data/skills/mature",
    "data/skills/retired",
    "data/drills",
    "data/field_logs",
    "data/reviews",
    "data/recommendations",
    "data/proposals",
    "data/imports",
    "data/profiles",
    "templates",
]

MATERIAL_DIR = DATA_DIR / "materials"
SKILLS_DIR = DATA_DIR / "skills"
DRILLS_DIR = DATA_DIR / "drills"
FIELD_LOGS_DIR = DATA_DIR / "field_logs"
REVIEWS_DIR = DATA_DIR / "reviews"
RECOMMENDATIONS_DIR = DATA_DIR / "recommendations"
IMPORTS_DIR = DATA_DIR / "imports"
PROFILES_DIR = DATA_DIR / "profiles"
PROPOSALS_DIR = DATA_DIR / "proposals"
