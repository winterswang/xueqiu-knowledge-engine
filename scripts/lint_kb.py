#!/usr/bin/env python3
"""知识库lint体检脚本：
1. 孤立实体：没有timeline/没有关联文章
2. 孤立概念：没有关联实体/来源
3. 引用断裂：wikilink指向不存在的页面
4. 标签缺失：缺少必要标签
5. 空定义：概念没有definition
"""
import re
import yaml
from pathlib import Path
from collections import defaultdict

KB_DIR = Path(__file__).parent.parent / "knowledge"
ENTITIES_DIR = KB_DIR / "entities"
CONCEPTS_DIR = KB_DIR / "concepts"
SOURCES_DIR = KB_DIR / "sources"

def parse_frontmatter(path):
    content = path.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return {}, content
    try:
        return yaml.safe_load(m.group(1)) or {}, content
    except:
        return {}, content

def main():
    issues = defaultdict(list)
    
    # 收集所有存在的实体/概念名称
    all_entities = set()
    all_concepts = set()
    entity_sources = defaultdict(set)
    concept_sources = defaultdict(set)
    
    for f in ENTITIES_DIR.glob("*.md"):
        fm, content = parse_frontmatter(f)
        name = fm.get("name", f.stem.replace("实体_", ""))
        all_entities.add(name)
        # 检查标签
        tags = fm.get("tags", [])
        if "_entity_page" not in tags:
            issues["missing_tag"].append(f"实体 {name} 缺少 _entity_page 标签")
        # 检查是否有timeline
        if not fm.get("timeline"):
            issues["empty_entity"].append(f"实体 {name} 没有timeline数据")
    
    for f in CONCEPTS_DIR.glob("*.md"):
        fm, content = parse_frontmatter(f)
        name = fm.get("name", f.stem.replace("概念_", ""))
        all_concepts.add(name)
        tags = fm.get("tags", [])
        if "_concept_page" not in tags:
            issues["missing_tag"].append(f"概念 {name} 缺少 _concept_page 标签")
        if not fm.get("definition"):
            issues["empty_definition"].append(f"概念 {name} 没有definition")
        # 关联实体
        for ent in fm.get("entities", []):
            entity_sources[ent].add(name)
        # 来源
        for src in fm.get("sources", []):
            concept_sources[name].add(src)
    
    # 收集来源中引用的实体/概念
    source_entities = set()
    source_concepts = set()
    for f in SOURCES_DIR.glob("*.md"):
        fm, content = parse_frontmatter(f)
        source_entities.update(fm.get("entities", []))
        source_concepts.update(fm.get("concepts", []))
    
    # 检查孤立实体：从来没在任何来源文章中出现过
    for ent in all_entities:
        if ent not in source_entities and not entity_sources.get(ent):
            issues["orphan_entity"].append(f"实体 {ent} 没有在任何来源/概念中被引用过")
    
    # 检查孤立概念
    for con in all_concepts:
        if len(concept_sources.get(con, set())) == 0 and len(entity_sources) == 0:
            issues["orphan_concept"].append(f"概念 {con} 没有关联来源或实体")
    
    # 检查wikilink断裂
    wikilink_pattern = re.compile(r"\[\[(实体|概念)/([^\]]+)\]\]")
    for d in [ENTITIES_DIR, CONCEPTS_DIR, SOURCES_DIR, KB_DIR]:
        for f in d.glob("*.md"):
            content = f.read_text(encoding="utf-8", errors="replace")
            for match in wikilink_pattern.finditer(content):
                typ, name = match.groups()
                if typ == "实体" and name not in all_entities:
                    issues["broken_link"].append(f"{f.name} 链接到不存在的实体: {name}")
                if typ == "概念" and name not in all_concepts:
                    issues["broken_link"].append(f"{f.name} 链接到不存在的概念: {name}")
    
    # 输出结果
    print("=== 知识库lint体检结果 ===")
    total = 0
    for issue_type, items in issues.items():
        if items:
            print(f"\n❌ {issue_type}: {len(items)} 个问题")
            for it in items[:10]:
                print(f"  - {it}")
            if len(items) > 10:
                print(f"  ... 还有{len(items)-10}个")
            total += len(items)
    
    if total == 0:
        print("✅ 所有检查通过，无问题")
    else:
        print(f"\n总计 {total} 个问题")
    
    return total

if __name__ == "__main__":
    exit(main())
