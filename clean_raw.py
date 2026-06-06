#!/usr/bin/env python3
"""Clean raw/ directories for editions that already have EPUBs in sent/."""
import os, shutil

raw_dir = '/home/devuser/myapps/newshit/raw'
sent_dir = '/home/devuser/myapps/newshit/sent'

sent_files = os.listdir(sent_dir)

to_delete = []
for entry in sorted(os.listdir(raw_dir)):
    entry_path = os.path.join(raw_dir, entry)
    if not os.path.isdir(entry_path):
        continue
    num = entry.replace('edicao-', '').replace('edica-', '')
    found = any(num in sf for sf in sent_files)
    if found:
        to_delete.append(entry_path)

print(f'Pastas raw/ pra limpar: {len(to_delete)}')
for p in to_delete:
    shutil.rmtree(p)
    print(f'  Deletado: {p}')

remaining = [e for e in os.listdir(raw_dir) if os.path.isdir(os.path.join(raw_dir, e))]
print(f'Restantes em raw/: {remaining if remaining else "nenhuma"}')