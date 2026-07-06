#!/usr/bin/env python3
"""
Sync raw xueqiu articles to IMA knowledge base.
- Resumable: tracks uploaded files in .ima_sync/uploaded_files.txt
- Deduplicates against existing list
- Processes files in deterministic order
- Copies .md → .txt before upload (IMA media_type=13 for plain text)
"""

import os
import sys
import shutil
import tempfile
import argparse
from pathlib import Path

# Add xueqiu-analyzer-skill to path for ima_kb_uploader
sys.path.insert(0, '/root/code/xueqiu-analyzer-skill/src')

from xueqiu_analyzer.ima_kb_uploader import list_knowledge_bases, upload_file

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "raw"
SYNC_DIR = PROJECT_DIR / ".ima_sync"
UPLOADED_FILE = SYNC_DIR / "uploaded_files.txt"
KB_NAME = "雪球内容数据"


def load_uploaded() -> set[str]:
    """Load set of already-uploaded filenames."""
    if not UPLOADED_FILE.exists():
        return set()
    with open(UPLOADED_FILE, 'r', encoding='utf-8') as f:
        return {line.strip() for line in f if line.strip()}


def save_uploaded(fname: str):
    """Append a filename to the uploaded list."""
    SYNC_DIR.mkdir(parents=True, exist_ok=True)
    with open(UPLOADED_FILE, 'a', encoding='utf-8') as f:
        f.write(fname + '\n')


def find_kb_id(kb_name: str) -> str:
    """Find knowledge base ID by name."""
    kbs = list_knowledge_bases()
    for kb in kbs:
        if kb_name in kb.get('name', ''):
            return kb['id']
    available = '\n  '.join(kb.get('name', '?') for kb in kbs)
    raise RuntimeError(f"知识库 '{kb_name}' 未找到。可用知识库:\n  {available}")


def get_pending_files(uploaded: set[str]) -> list[str]:
    """Get sorted list of .md files in raw/ that haven't been uploaded yet."""
    all_files = sorted(f.name for f in RAW_DIR.glob("*.md"))
    return [f for f in all_files if f not in uploaded]


def main():
    parser = argparse.ArgumentParser(description="Sync raw xueqiu articles to IMA KB")
    parser.add_argument('--count', '-n', type=int, default=60, help='Number of files to upload (default: 60)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be uploaded without actually uploading')
    args = parser.parse_args()

    # Find KB
    kb_id = find_kb_id(KB_NAME)
    print(f"目标知识库: {KB_NAME} (ID: {kb_id[:30]}...)")

    # Load already uploaded
    uploaded = load_uploaded()
    print(f"已上传记录: {len(uploaded)} 篇")

    # Get pending files
    pending = get_pending_files(uploaded)
    print(f"待上传: {len(pending)} 篇")

    if not pending:
        print("✅ 没有待上传文件，全部完成！")
        return

    # Take first N
    batch = pending[:args.count]
    print(f"本次上传: {len(batch)} 篇\n" + "=" * 60)

    if args.dry_run:
        for f in batch:
            print(f"  [DRY] {f}")
        print(f"\n[DRY RUN] 共 {len(batch)} 篇将被上传")
        return

    success = 0
    fail = 0

    for i, fname in enumerate(batch, 1):
        src = RAW_DIR / fname
        if not src.exists():
            print(f"[{i}/{len(batch)}] {fname}... ❌ MISSING")
            fail += 1
            continue

        # Copy to temp as .txt
        tmp_name = fname.replace('.md', '.txt')
        tmp_path = Path(tempfile.gettempdir()) / tmp_name
        shutil.copy2(src, tmp_path)

        try:
            print(f"[{i}/{len(batch)}] {fname}...", end=" ", flush=True)
            media_id = upload_file(str(tmp_path), kb_id)
            print(f"✅ OK ({media_id[:24]}...)")
            save_uploaded(fname)
            success += 1
        except Exception as e:
            err_msg = str(e)[:120]
            print(f"❌ FAIL: {err_msg}")
            fail += 1
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    print("=" * 60)
    print(f"完成！成功: {success}, 失败: {fail}")
    print(f"累计已上传: {len(uploaded) + success} 篇")
    print(f"剩余待上传: {len(pending) - len(batch) + fail} 篇")


if __name__ == "__main__":
    main()
