"""
Batch Ingest: 批量导入历史文章

设计：
- 断点续跑：state.json 记录已处理文件
- 每 N 篇 git commit 一次（默认 50）
- 失败文章记录到 errors.log，不阻断后续
- 单线程（避免 LLM 并发限制）
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import yaml

# 处理 import path
sys.path.insert(0, str(Path(__file__).parent))
from ingest import IngestPipeline


TZ = timezone(timedelta(hours=8))
STATE_FILE = "batch_state.json"
ERROR_LOG = "batch_errors.log"


class BatchIngest:
    def __init__(self, base_dir: str, batch_size: int = 50):
        self.base_dir = Path(base_dir)
        self.raw_dir = self.base_dir / "raw"
        self.batch_size = batch_size
        self.state_file = self.base_dir / STATE_FILE
        self.error_log = self.base_dir / ERROR_LOG
        
        # 加载配置
        self.config = self._load_config()
        self.pipeline = IngestPipeline(base_dir)
        
        # 加载状态
        self.state = self._load_state()
        
        # 加载词典
        self.entity_dict = self._load_dict()
    
    def _load_config(self) -> dict:
        config_path = self.base_dir / "config" / "engine.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def _load_state(self) -> dict:
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {"processed": [], "failed": [], "last_commit": 0}
    
    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _load_dict(self) -> dict:
        dict_path = self.base_dir / "config" / "entity_dictionary.yaml"
        if dict_path.exists():
            with open(dict_path, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def _log_error(self, filepath: str, error: str):
        timestamp = datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')
        with open(self.error_log, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {Path(filepath).name}: {error}\n")
    
    def run(self):
        """执行批量导入"""
        # 获取所有待处理文件（排除已处理）
        all_files = sorted(self.raw_dir.glob("*.md"))
        processed_set = set(self.state.get("processed", []))
        
        pending = [f for f in all_files if f.name not in processed_set]
        total = len(all_files)
        remaining = len(pending)
        
        print(f"=" * 60)
        print(f"Batch Ingest: {total} total, {remaining} pending, {len(processed_set)} done")
        print(f"=" * 60)
        
        if not pending:
            print("✅ All articles processed!")
            return
        
        success_count = 0
        skip_count = 0
        fail_count = 0
        batch_counter = 0
        
        for i, fpath in enumerate(pending, 1):
            print(f"\n[{i}/{remaining}] {fpath.name} ({fpath.stat().st_size} bytes)")
            
            try:
                result = self.pipeline.ingest(str(fpath), self.entity_dict)
                
                if result.get('skipped'):
                    print(f"  ⏭️  Skipped: {result['reason']}")
                    skip_count += 1
                elif result['success']:
                    print(f"  ✅ OK: {len(result.get('entities_updated', []))} entities, {len(result.get('concepts_updated', []))} concepts")
                    success_count += 1
                else:
                    print(f"  ❌ Failed: {result['error']}")
                    fail_count += 1
                    self._log_error(str(fpath), result['error'])
                
                # 标记为已处理（无论成功失败，不再重试同文件）
                self.state["processed"].append(fpath.name)
                batch_counter += 1
                
                # 每 batch_size 篇后 commit
                if batch_counter >= self.batch_size:
                    self._commit_batch()
                    batch_counter = 0
                
                # 定期保存状态（每10篇）
                if i % 10 == 0:
                    self._save_state()
                    
            except Exception as e:
                print(f"  ❌ Exception: {e}")
                fail_count += 1
                self._log_error(str(fpath), str(e))
                self.state["processed"].append(fpath.name)
        
        # 最后一批 commit
        if batch_counter > 0:
            self._commit_batch()
        
        # 最终保存状态
        self._save_state()
        
        # 汇总
        print(f"\n{'=' * 60}")
        print("BATCH COMPLETE")
        print(f"{'=' * 60}")
        print(f"Success: {success_count}")
        print(f"Skipped: {skip_count}")
        print(f"Failed: {fail_count}")
        print(f"Total processed: {success_count + skip_count + fail_count}")
        print(f"State file: {self.state_file}")
        if fail_count > 0:
            print(f"Error log: {self.error_log}")
    
    def _commit_batch(self):
        """提交当前批次"""
        msg = f"batch: ingest {len(self.state['processed']) - self.state.get('last_commit', 0)} articles"
        if self.pipeline.git_commit(msg):
            print(f"  💾 Committed: {msg}")
            self.state["last_commit"] = len(self.state["processed"])
        else:
            print(f"  ⚠️ Commit skipped")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 支持命令行参数：batch_size
    batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    
    batch = BatchIngest(base_dir, batch_size=batch_size)
    batch.run()
