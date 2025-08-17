import os

WATSONX_API_KEY = os.getenv("WATSONX_API_KEY", "")
WATSONX_ORCH_URL = os.getenv("WATSONX_ORCH_URL", "https://api.ibm.com/watsonx/orchestrate/v1/agents")
STYLE_SKILL_ID = os.getenv("STYLE_SKILL_ID", "style-skill-id")
DONATE_SKILL_ID = os.getenv("DONATE_SKILL_ID", "donate-skill-id")
RECYCLE_SKILL_ID = os.getenv("RECYCLE_SKILL_ID", "recycle-skill-id")
SELL_SKILL_ID = os.getenv("SELL_SKILL_ID", "sell-skill-id")

WATSONX_MOCK = os.getenv("WATSONX_MOCK", "true").lower() in ("1","true","yes")
KEEP_UPLOADS = os.getenv("KEEP_UPLOADS", "false").lower() in ("1","true","yes")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
