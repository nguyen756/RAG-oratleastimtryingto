import re
sample_text = """Hard Hit Lv 1 Skill ... Game Description: "Brutally hit the target with the weapon. Chance to inflict [Flinch] on the target." One-Handed Sword bonus: Flinch chance +50% Two-Handed Sword bonus: Skill Multiplier +0.5 Hard Hit | #blade-skills🗡 1. Astute Lv 1 Skill ... Two-Handed Sword bonus: Critical Rate of buff is doubled Astute | #blade-skills🗡 Trigger Slash Lv 2 Skill ... This skill's Animation Time Modifier buff overrides all other Motion Speed modifiers Trigger Slash | #blade-skills🗡"""

def semantic_chunker(raw_text):
    pattern = r"\|\s*#[^\s]+"
    chunks = re.split(pattern, raw_text)
    return [chunk.strip() for chunk in chunks if chunk.strip()]
results = semantic_chunker(sample_text)
for i, chunk in enumerate(results):
    print(f"\n--- CHUNK {i + 1} ---")
    print(chunk)