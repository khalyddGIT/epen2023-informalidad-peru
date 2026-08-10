import json

log_path = r"C:\Users\HP\.gemini\antigravity-ide\brain\7d7045ae-dbee-4ee4-ae92-92ea9f05ac28\.system_generated\logs\transcript_full.jsonl"

with open(log_path, 'r', encoding='utf-8') as f:
    for line_idx, line in enumerate(f):
        if '<svg' in line:
            print(f"Line {line_idx} has <svg, length={len(line)}")
            idx = line.find('<svg')
            snippet = line[idx:idx+500]
            print("Snippet:", snippet)
            break
