"""
知识引擎日报生成模块
与现有 analyzer.py 日报对比
"""

import sys
sys.path.insert(0, 'src')

from query import KnowledgeQuery
from datetime import datetime


def generate_knowledge_daily_report(base_dir: str = '.', date: str = None) -> str:
    """生成知识引擎日报"""
    q = KnowledgeQuery(base_dir)
    
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # 获取当天来源页
    sources = q._source_index.get(date, [])
    
    lines = [
        f"# 📊 价值投资日报（知识引擎版）",
        "",
        f"**日期**：{date}",
        "",
        "---",
        "",
        "## 一、概览",
        "",
        f"- **今日新增来源**：{len(sources)} 篇",
        "",
        "---",
        "",
    ]
    
    # 信号汇总
    entity_signals = {}
    all_concepts = set()
    all_entities = set()
    
    for filepath in sources:
        fm = q._load_frontmatter(filepath)
        
        # 收集信号
        for signal in fm.get('signals', []):
            entity = signal.get('entity', 'Unknown')
            if entity not in entity_signals:
                entity_signals[entity] = []
            entity_signals[entity].append(signal)
        
        # 收集实体和概念
        all_entities.update(fm.get('entities', []))
        all_concepts.update(fm.get('concepts', []))
    
    # 二、实体信号
    if entity_signals:
        lines.extend([
            "## 二、实体投资信号",
            "",
        ])
        
        for entity, signals in sorted(entity_signals.items()):
            # 取最新信号
            latest = max(signals, key=lambda x: x.get('date', ''))
            direction = latest.get('direction', 'neutral')
            emoji = {"positive": "📈", "negative": "📉", "neutral": "➡️"}.get(direction, "➡️")
            
            lines.append(f"### {emoji} {entity}")
            lines.append("")
            
            for s in sorted(signals, key=lambda x: x.get('date', ''), reverse=True):
                d_emoji = {"positive": "📈", "negative": "📉", "neutral": "➡️"}.get(s.get('direction'), "➡️")
                lines.append(f"- [{s.get('date', '?')}] {d_emoji} [{s.get('confidence', 'medium')}] {s.get('summary', '')}")
                if s.get('caveats'):
                    for c in s['caveats'][:2]:
                        lines.append(f"  ⚠️ {c}")
            lines.append("")
    
    # 三、新提及实体
    if all_entities:
        lines.extend([
            "## 三、新提及实体",
            "",
        ])
        
        # 区分有信号和无信号的实体
        signaled = set(entity_signals.keys())
        mentioned_only = all_entities - signaled
        
        if signaled:
            lines.append("**有投资信号的实体：**")
            for e in sorted(signaled):
                lines.append(f"- {e}")
            lines.append("")
        
        if mentioned_only:
            lines.append("**被提及的实体：**")
            for e in sorted(mentioned_only)[:15]:
                lines.append(f"- {e}")
            lines.append("")
    
    # 四、新提及概念
    if all_concepts:
        lines.extend([
            "## 四、新提及概念",
            "",
        ])
        
        for c in sorted(all_concepts)[:15]:
            lines.append(f"- {c}")
        lines.append("")
    
    # 五、来源详情
    if sources:
        lines.extend([
            "---",
            "",
            "## 五、来源详情",
            "",
        ])
        
        for i, filepath in enumerate(sorted(sources), 1):
            fm = q._load_frontmatter(filepath)
            title = fm.get('title', 'Untitled')[:50]
            url = fm.get('url', '')
            author = fm.get('author', 'Unknown')
            
            lines.append(f"### {i}. {title}")
            lines.append(f"- 作者：{author}")
            if url:
                lines.append(f"- 链接：{url}")
            
            # 信号
            sigs = fm.get('signals', [])
            if sigs:
                lines.append(f"- 信号：{len(sigs)} 条")
                for s in sigs[:2]:
                    d_emoji = {"positive": "📈", "negative": "📉", "neutral": "➡️"}.get(s.get('direction'), "➡️")
                    lines.append(f"  - {d_emoji} {s.get('entity')}: {s.get('summary', '')[:60]}")
            
            lines.append("")
    
    # 总结
    lines.extend([
        "---",
        "",
        "## 六、今日总结",
        "",
        f"- **信号实体数**：{len(entity_signals)}",
        f"- **提及实体数**：{len(all_entities)}",
        f"- **提及概念数**：{len(all_concepts)}",
        "",
        "---",
        "",
        f"*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "*数据源：雪球知识引擎*",
        "",
    ])
    
    return '\n'.join(lines)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="日期 YYYY-MM-DD")
    parser.add_argument("--output", help="输出文件路径")
    args = parser.parse_args()
    
    report = generate_knowledge_daily_report(date=args.date)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    else:
        print(report)
