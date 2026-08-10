import json

log_path = r"C:\Users\HP\.gemini\antigravity-ide\brain\7d7045ae-dbee-4ee4-ae92-92ea9f05ac28\.system_generated\logs\transcript_full.jsonl"

with open(log_path, 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if 'baseProfile' in line:
            print(f"Line {idx} length: {len(line)}")
            # Print a portion around baseProfile
            pos = line.find('baseProfile')
            print("Content snippet:", line[pos-100:pos+1000])
            break
