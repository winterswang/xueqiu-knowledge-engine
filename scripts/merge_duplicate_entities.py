#!/usr/bin/env python3
"""
实体去重：按ticker合并重复实体，把aliases/timeline合并，保留信息最多的实体，删除重复
"""
import re
import yaml
from pathlib import Path
from collections import defaultdict

PROJECT_DIR = Path(__file__).resolve().parent.parent
ENTITIES_DIR = PROJECT_DIR / "knowledge" / "entities"

def parse_md(path):
    content = path.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return {}, content
    try:
        return yaml.safe_load(m.group(1)) or {}, content
    except:
        return {}, content

def main():
    import argparse
    parser = argparse.ArgumentParser(description="实体去重合并")
    parser.add_argument("--dry-run", action="store_true", help="只显示会合并什么，不实际删除")
    parser.add_argument("--backup-dir", type=str, default=None, help="删除前备份到此目录")
    args = parser.parse_args()

    dry_run = args.dry_run
    backup_dir = Path(args.backup_dir) if args.backup_dir else None
    if backup_dir and not dry_run:
        backup_dir.mkdir(parents=True, exist_ok=True)

    # 按ticker分组
    ticker_groups = defaultdict(list)
    for f in ENTITIES_DIR.glob("*.md"):
        fm, content = parse_md(f)
        ticker = fm.get("ticker", "").strip()
        if ticker:
            # 标准化ticker格式
            ticker = ticker.replace(".US","").replace(".HK","").replace(".SH","").replace(".SZ","").upper()
            ticker_groups[ticker].append((f, fm, content))
    
    print(f"共有 {sum(len(v) for v in ticker_groups.values())} 个带ticker实体")
    print(f"唯一ticker数: {len(ticker_groups)}")
    print(f"重复ticker数: {len([t for t,v in ticker_groups.items() if len(v) > 1])}")
    print()
    
    merged_count = 0
    deleted_files = []
    
    for ticker, entries in ticker_groups.items():
        if len(entries) == 1:
            # 补全market字段（如果空的话，从ticker判断）
            f, fm, content = entries[0]
            if not fm.get("market"):
                # 简单判断：纯数字是A股，4位数字是港股，字母是美股
                if ticker.isdigit():
                    if len(ticker) <= 4:
                        fm["market"] = "HK"
                    else:
                        fm["market"] = "CN"
                else:
                    fm["market"] = "US"
                # 重新写文件
                new_content = "---\n" + yaml.dump(fm, allow_unicode=True, sort_keys=False) + "---\n" + content.split("---", 2)[-1].lstrip("\n")
                f.write_text(new_content, encoding="utf-8")
            continue
        
        # 有重复：选信息最多的（timeline最长+aliases最多）作为主文件
        entries.sort(key=lambda x: (len(x[1].get("timeline", [])), len(x[1].get("aliases", []))), reverse=True)
        main_f, main_fm, main_content = entries[0]
        
        # 合并其他实体的aliases和timeline到主实体
        all_aliases = set(main_fm.get("aliases", []))
        all_timeline = {}
        for t in main_fm.get("timeline", []):
            if t.get("date"):
                all_timeline[t["date"]] = t
        
        for other_f, other_fm, other_content in entries[1:]:
            # 合并别名
            for a in other_fm.get("aliases", []):
                if a and a not in all_aliases:
                    all_aliases.add(a)
            # 合并timeline（按date去重）
            for t in other_fm.get("timeline", []):
                if t.get("date") and t["date"] not in all_timeline:
                    all_timeline[t["date"]] = t
            # 删除其他文件
            if dry_run:
                print(f"  [DRY-RUN] would merge & delete: {other_f.name}")
            else:
                if backup_dir:
                    backup_path = backup_dir / other_f.name
                    backup_path.write_bytes(other_f.read_bytes())
                other_f.unlink()
                deleted_files.append(other_f.name)
                merged_count += 1
        
        # 更新主实体
        main_fm["aliases"] = sorted(list(all_aliases))
        main_fm["timeline"] = sorted(all_timeline.values(), key=lambda x: x.get("date",""), reverse=True)
        # 补全market
        if not main_fm.get("market"):
            if ticker.isdigit():
                if len(ticker) <= 4:
                    main_fm["market"] = "HK"
                else:
                    main_fm["market"] = "CN"
            else:
                main_fm["market"] = "US"
        
        # 重写主文件
        new_content = "---\n" + yaml.dump(main_fm, allow_unicode=True, sort_keys=False) + "---\n" + main_content.split("---", 2)[-1].lstrip("\n")
        main_f.write_text(new_content, encoding="utf-8")
    
    print(f"合并完成：删除重复实体 {merged_count} 个")
    print(f"剩余实体数: {len(list(ENTITIES_DIR.glob('*.md')))}")
    print(f"按市场统计：")
    market_count = defaultdict(int)
    for f in ENTITIES_DIR.glob("*.md"):
        fm, _ = parse_md(f)
        market_count[fm.get("market","UNKNOWN")] += 1
    for m,c in market_count.items():
        print(f"  {m}: {c}")

if __name__ == "__main__":
    main()
