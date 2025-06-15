import re

def classify_prompt(prompt: str) -> dict:
    prompt_lower = prompt.lower().strip()

    # 1. Compare two players
    compare_match = re.search(r"compare\s+([\w\s\-']+)\s+(and|vs|with)\s+([\w\s\-']+)", prompt_lower)
    if compare_match:
        return {
            "type": "comparison",
            "players": [compare_match.group(1).strip().title(), compare_match.group(3).strip().title()]
        }

    # 2. Trending players
    if "trending" in prompt_lower or "top players" in prompt_lower or "hot players" in prompt_lower:
        return {"type": "trending"}

    # 3. Contract or market-related
    if any(word in prompt_lower for word in ["market value", "contract", "renewal", "transfer fee"]):
        name_match = re.search(r"(?:of|for)\s+([\w\s\-']+)", prompt_lower)
        if name_match:
            return {"type": "contract", "player_name": name_match.group(1).strip().title()}

    # 4. Insight/performance questions
    if any(word in prompt_lower for word in ["performance", "play", "contribution", "insight", "how did"]):
        return {"type": "insight"}

    return {"type": "unknown"}
