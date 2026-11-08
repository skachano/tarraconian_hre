import re

with open("sinosphere_titles_and_characters_1154.md") as f:
    lines = f.readlines()

errors = []
in_table = False
table_header_cols = 0
table_name = ""

for idx, line in enumerate(lines, 1):
    l = line.strip()
    if l.startswith("|") and not in_table:
        # Start of a table
        in_table = True
        parts = [p.strip() for p in l.split("|")]
        table_header_cols = len(parts)
        table_name = l[:50]
        continue
    elif l.startswith("|") and in_table:
        parts = [p.strip() for p in l.split("|")]
        if len(parts) != table_header_cols:
            errors.append((idx, f"Column count mismatch: expected {table_header_cols}, got {len(parts)}", l[:60]))
    elif not l.startswith("|") and in_table:
        in_table = False

print(f"Total table column errors: {len(errors)}")
for e in errors[:10]:
    print(f"Line {e[0]}: {e[1]} in '{e[2]}'")
