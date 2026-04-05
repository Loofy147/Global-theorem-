import os

files_to_review = [
    "research/fso_holographic_recovery.py",
    "research/fso_monitor_recovery.py"
]

for file in files_to_review:
    print(f"--- FILE: {file} ---")
    with open(file, 'r') as f:
        print(f.read())
    print("\n" + "="*50 + "\n")
