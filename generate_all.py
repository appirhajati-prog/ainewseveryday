import os

files = [
    "config.py",
    "utils/helpers.py",
    "services/logger.py",
    "services/deduplicate.py",
    "services/ranking.py",
    "services/translator.py",
    "services/formatter.py",
    "services/telegram.py",
    "collectors/github.py",
    "collectors/huggingface.py",
    "collectors/hackernews.py",
    "collectors/reddit.py",
    "collectors/producthunt.py",
    "app.py"
]

with open("all_project_codes.txt", "w", encoding="utf-8") as outfile:
    for fpath in files:
        outfile.write(f"\n\n{'='*50}\n")
        outfile.write(f"FILE: {fpath}\n")
        outfile.write(f"{'='*50}\n\n")
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as infile:
                outfile.write(infile.read())
        else:
            outfile.write("[File not found]\n")

print("All codes successfully combined into 'all_project_codes.txt'!")
