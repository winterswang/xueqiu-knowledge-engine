#!/usr/bin/env python3
"""
知识库清理脚本：
1. 删除非公司实体（人物/产品/其他非投资标的）
2. 删除空实体（无timeline/无信号/无关联文章）
3. 删除过细概念（只有1篇文章提到、无明确信号）
4. 输出清理统计
"""
import os
import re
import yaml
from pathlib import Path
from collections import defaultdict

KB_DIR = Path("/root/code/xueqiu-knowledge-engine/knowledge")
ENTITIES_DIR = KB_DIR / "entities"
CONCEPTS_DIR = KB_DIR / "concepts"
SOURCES_DIR = KB_DIR / "sources"

def parse_md_frontmatter(path):
    """解析markdown frontmatter"""
    content = path.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return {}, content
    try:
        fm = yaml.safe_load(m.group(1))
        return fm or {}, content
    except Exception:
        return {}, content

def main():
    stats = defaultdict(int)
    
    # ========== 清理实体 ==========
    print("=== 清理实体 ===")
    entities_to_delete = []
    entity_files = list(ENTITIES_DIR.glob("*.md"))
    
    for f in entity_files:
        fm, content = parse_md_frontmatter(f)
        if not fm:
            entities_to_delete.append(f)
            stats["entity_parse_failed"] += 1
            continue
        
        # 规则1：type不是company的，是人物/产品/其他，删掉
        ent_type = fm.get("type", "")
        if ent_type != "company":
            entities_to_delete.append(f)
            stats[f"entity_non_company_{ent_type}"] += 1
            continue
        
        # 规则2：没有ticker，不是上市公司，删掉
        ticker = fm.get("ticker", "")
        if not ticker:
            entities_to_delete.append(f)
            stats["entity_no_ticker"] += 1
            continue
        
        # 规则3：timeline为空或长度为0，空实体删掉
        timeline = fm.get("timeline", [])
        if not timeline or len(timeline) == 0:
            entities_to_delete.append(f)
            stats["entity_empty_timeline"] += 1
            continue
    
    # 删除实体
    for f in entities_to_delete:
        f.unlink()
    
    print(f"实体总数原: {len(entity_files)} → 删除: {len(entities_to_delete)} → 剩余: {len(entity_files) - len(entities_to_delete)}")
    print(f"删除原因统计: {dict(stats)}")
    print()
    
    # ========== 清理概念 ==========
    print("=== 清理概念 ===")
    concepts_to_delete = []
    concept_files = list(CONCEPTS_DIR.glob("*.md"))
    
    for f in concept_files:
        fm, content = parse_md_frontmatter(f)
        if not fm:
            concepts_to_delete.append(f)
            stats["concept_parse_failed"] += 1
            continue
        
        # 规则1：entities为空，且sources为空 → 孤立概念删掉
        related = fm.get("entities", [])
        sources = fm.get("sources", [])
        
        # 没有关联实体 + 没有来源 → 完全孤立删掉
        if not related and not sources:
            concepts_to_delete.append(f)
            stats["concept_isolated"] += 1
            continue
        
        # 规则2：只在1篇文章中提到 + 内容里没有明确看多/看空信号 → 过细概念删掉
        content_lower = content.lower()
        has_signal = any(kw in content for kw in ["看多", "看空", "bull", "bear", "利好", "利空", "买入", "卖出", "推荐"])
        if len(sources) <= 1 and not has_signal:
            concepts_to_delete.append(f)
            stats["concept_trivial"] += 1
            continue
    
    # 删除概念
    for f in concepts_to_delete:
        f.unlink()
    
    print(f"概念总数原: {len(concept_files)} → 删除: {len(concepts_to_delete)} → 剩余: {len(concept_files) - len(concepts_to_delete)}")
    print(f"删除原因统计: { {k:v for k,v in stats.items() if 'concept' in k} }")
    print()
    
    # ========== 更新索引页 ==========
    print("=== 更新索引 ===")
    # 重新生成索引统计
    remaining_entities = len(list(ENTITIES_DIR.glob("*.md")))
    remaining_concepts = len(list(CONCEPTS_DIR.glob("*.md")))
    remaining_sources = len(list(SOURCES_DIR.glob("*.md")))
    print(f"清理完成：\n  来源文章: {remaining_sources}\n  公司实体: {remaining_entities}\n  投资概念: {remaining_concepts}")
    
    # 写清理日志
    log_path = KB_DIR / "cleanup_log.txt"
    with open(log_path, "a", encoding="utf-8") as f:
        from datetime import datetime
        f.write(f"\n=== 清理 {datetime.now().isoformat()} ===\n")
        f.write(f"删除实体: {len(entities_to_delete)}\n")
        f.write(f"删除概念: {len(concepts_to_delete)}\n")
        f.write(f"剩余: {remaining_entities}实体 / {remaining_concepts}概念 / {remaining_sources}来源\n")

if __name__ == "__main__":
    main()
