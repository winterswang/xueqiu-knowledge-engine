"""小批量测试：50篇文章"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ingest import IngestPipeline
import yaml

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 加载词典
dict_path = os.path.join(base_dir, "config", "entity_dictionary.yaml")
entity_dict = {}
if os.path.exists(dict_path):
    with open(dict_path) as f:
        entity_dict = yaml.safe_load(f) or {}
    print(f"Loaded dictionary: {len(entity_dict.get('verified', {}))} verified entities")

pipeline = IngestPipeline(base_dir)

# 读取测试文件列表
test_list = os.path.join(base_dir, "batch_test_files.txt")
with open(test_list) as f:
    files = [line.strip() for line in f if line.strip()]

print(f"\n{'='*60}")
print(f"Batch Test: {len(files)} articles")
print(f"{'='*60}")

success = skip = fail = 0
for i, fname in enumerate(files, 1):
    fpath = os.path.join(base_dir, fname)
    if not os.path.exists(fpath):
        print(f"\n[{i}/{len(files)}] {fname} - FILE NOT FOUND")
        fail += 1
        continue
    
    print(f"\n[{i}/{len(files)}] {fname} ({os.path.getsize(fpath)} bytes)", flush=True)
    
    try:
        result = pipeline.ingest(fpath, entity_dict)
        
        if result.get('skipped'):
            print(f"  ⏭️  Skipped: {result['reason']}", flush=True)
            skip += 1
        elif result['success']:
            entities = len(result.get('entities_updated', []))
            concepts = len(result.get('concepts_updated', []))
            print(f"  ✅ OK: {entities} entities, {concepts} concepts", flush=True)
            success += 1
        else:
            print(f"  ❌ Failed: {result['error']}", flush=True)
            fail += 1
    except Exception as e:
        print(f"  ❌ Exception: {e}", flush=True)
        fail += 1

# Git commit
print(f"\n{'='*60}")
print("Git commit...")
if pipeline.git_commit(f"batch test: {success} success, {skip} skip, {fail} fail"):
    print("✅ Committed")
else:
    print("⚠️ Commit skipped")

# Summary
print(f"\n{'='*60}")
print("BATCH TEST SUMMARY")
print(f"{'='*60}")
print(f"Success: {success}")
print(f"Skipped: {skip}")
print(f"Failed:  {fail}")
print(f"Total:   {success + skip + fail}")

# Knowledge base stats
sources = len(list(Path(base_dir, "knowledge/sources").glob("*.md")))
entities = len(list(Path(base_dir, "knowledge/entities").glob("*.md")))
concepts = len(list(Path(base_dir, "knowledge/concepts").glob("*.md")))
print(f"\nKnowledge base:")
print(f"  Sources: {sources}")
print(f"  Entities: {entities}")
print(f"  Concepts: {concepts}")
