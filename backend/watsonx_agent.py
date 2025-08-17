import base64, json, requests
from typing import Dict, Any, Optional
import config

def _mock_response(skill_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
    item = inputs.get("item_name") or "clothing item"
    condition = inputs.get("condition") or "good"
    if skill_name == "style":
        return {"style_tips": [
            f"Pair the {item} with slim dark jeans and white sneakers for casual look.",
            f"Layer with a blazer for smart-casual, add minimal jewelry.",
            "Try monochrome tones for a modern aesthetic."
        ]}
    if skill_name == "recycle":
        return {"recycle_tips": [
            "Check local textile recycling bins or municipal programs.",
            "If the item is natural fiber (cotton), you can compost small scraps.",
            "Repurpose worn areas into cleaning rags or craft projects."
        ]}
    if skill_name == "sell":
        return {"estimated_price": {"min": 12, "max": 20, "currency":"USD"}, "platforms": ["eBay", "Depop", "Poshmark"], "listing_text": f"{condition} {item} - great condition, clear photos"}
    if skill_name == "donate":
        return {"donation_centers": [
            {"name":"Community Thrift", "address":"123 Donation St", "distance_m": 800},
            {"name":"Green Wardrobe", "address":"45 Recycle Ave", "distance_m": 2200}
        ]}
    return {"message":"ok"}

def call_orchestrate_skill(skill_id: str, inputs: Dict[str, Any], image_bytes: Optional[bytes]=None) -> Dict[str, Any]:
    if config.WATSONX_MOCK:
        mapping = {
            config.STYLE_SKILL_ID: "style",
            config.RECYCLE_SKILL_ID: "recycle",
            config.SELL_SKILL_ID: "sell",
            config.DONATE_SKILL_ID: "donate"
        }
        skill_name = mapping.get(skill_id, "style")
        return _mock_response(skill_name, inputs)

    payload = {"skill_id": skill_id, "inputs": inputs}
    if image_bytes:
        payload["image_base64"] = base64.b64encode(image_bytes).decode("utf-8")
    headers = {"Authorization": f"Bearer {config.WATSONX_API_KEY}", "Content-Type":"application/json"}
    resp = requests.post(config.WATSONX_ORCH_URL, headers=headers, json=payload, timeout=60)
    try:
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e), "status": getattr(resp, 'status_code', None), "body": getattr(resp, 'text', str(resp))}
