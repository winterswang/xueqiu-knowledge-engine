"""
知识查询模块
四层检索：实体直达 → 索引层 → 来源页检索 → 综合层
"""

import yaml
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta, timezone

# 统一使用东八区，不依赖系统时区
TZ = timezone(timedelta(hours=8))


@dataclass
class QueryResult:
    """查询结果"""
    query: str
    layer: str  # 命中层级
    entities: List[Dict]
    concepts: List[Dict]
    sources: List[Dict]
    signals: List[Dict]
    summary: str


class KnowledgeQuery:
    """知识库查询引擎"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.knowledge_dir = self.base_dir / "knowledge"
        self.entities_dir = self.knowledge_dir / "entities"
        self.concepts_dir = self.knowledge_dir / "concepts"
        self.sources_dir = self.knowledge_dir / "sources"
        
        # 内存索引（小数据量可全量加载）
        self._entity_index = {}
        self._concept_index = {}
        self._source_index = {}
        self._build_index()
    
    def _build_index(self):
        """构建内存索引"""
        # 实体索引
        for f in self.entities_dir.glob("*.md"):
            self._entity_index[f.stem.replace('实体_', '')] = str(f)
        
        # 概念索引
        for f in self.concepts_dir.glob("*.md"):
            self._concept_index[f.stem.replace('概念_', '')] = str(f)
        
        # 来源索引（按日期）
        for f in self.sources_dir.glob("*.md"):
            # 解析日期前缀
            match = re.match(r'(\d{4}-\d{2}-\d{2})-', f.name)
            if match:
                date_key = match.group(1)
                if date_key not in self._source_index:
                    self._source_index[date_key] = []
                self._source_index[date_key].append(str(f))
    
    def _load_frontmatter(self, filepath: str) -> Dict:
        """加载文件的 frontmatter"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if match:
                fm = yaml.safe_load(match.group(1))
                return fm if fm is not None else {}
            return {}
        except Exception:
            return {}
    
    # ========== Layer 1: 实体直达 ==========
    
    def query_entity(self, entity_name: str) -> Optional[Dict]:
        """精确查询实体
        
        支持：
        - 精确匹配文件名
        - 别名匹配
        - 股票代码匹配
        """
        # 精确匹配
        for stem, path in self._entity_index.items():
            if stem.lower() == entity_name.lower():
                fm = self._load_frontmatter(path)
                fm['_file'] = path
                return fm
        
        # 别名匹配
        for stem, path in self._entity_index.items():
            fm = self._load_frontmatter(path)
            aliases = [a.lower() for a in fm.get('aliases', [])]
            if entity_name.lower() in aliases:
                fm['_file'] = path
                return fm
        
        # 股票代码匹配
        for stem, path in self._entity_index.items():
            fm = self._load_frontmatter(path)
            ticker = fm.get('ticker', '') or ''
            if ticker.upper() == entity_name.upper():
                fm['_file'] = path
                return fm
        
        return None
    
    # ========== Layer 2: 索引层 ==========
    
    def search_entities(self, keyword: str) -> List[Dict]:
        """模糊搜索实体"""
        results = []
        keyword_lower = keyword.lower()
        
        for stem, path in self._entity_index.items():
            fm = self._load_frontmatter(path)
            
            # 检查名称、别名、股票代码
            name = fm.get('name', '')
            aliases = fm.get('aliases', [])
            ticker = fm.get('ticker', '')
            
            if (keyword_lower in name.lower() or 
                any(keyword_lower in (a or '').lower() for a in aliases) or
                keyword_lower in (ticker or '').lower()):
                fm['_file'] = path
                results.append(fm)
        
        return results
    
    def search_concepts(self, keyword: str) -> List[Dict]:
        """模糊搜索概念"""
        results = []
        keyword_lower = keyword.lower()
        
        for stem, path in self._concept_index.items():
            fm = self._load_frontmatter(path)
            
            name = fm.get('name', '')
            definition = fm.get('definition', '')
            
            if keyword_lower in name.lower() or keyword_lower in definition.lower():
                fm['_file'] = path
                results.append(fm)
        
        return results
    
    # ========== Layer 3: 来源页检索 ==========
    
    def search_sources(self, keyword: str, days: int = None) -> List[Dict]:
        """在来源页中搜索关键词
        
        Args:
            keyword: 搜索关键词
            days: 最近 N 天的来源页（None = 全部）
        """
        results = []
        keyword_lower = keyword.lower()
        
        # 日期过滤
        cutoff_date = None
        if days:
            cutoff_date = (datetime.now(TZ) - timedelta(days=days)).strftime('%Y-%m-%d')
        
        for date_key, files in self._source_index.items():
            if cutoff_date and date_key < cutoff_date:
                continue
            
            for filepath in files:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if keyword_lower in content.lower():
                        fm = self._load_frontmatter(filepath)
                        fm['_file'] = filepath
                        fm['_excerpt'] = self._extract_excerpt(content, keyword)
                        results.append(fm)
                except Exception:
                    continue
        
        # 按日期降序
        results.sort(key=lambda x: x.get('date', ''), reverse=True)
        return results
    
    def _extract_excerpt(self, content: str, keyword: str, context: int = 80) -> str:
        """提取关键词上下文"""
        keyword_lower = keyword.lower()
        idx = content.lower().find(keyword_lower)
        if idx == -1:
            return ""
        
        start = max(0, idx - context)
        end = min(len(content), idx + len(keyword) + context)
        excerpt = content[start:end]
        
        # 标记关键词
        # 找到实际位置（考虑大小写）
        actual_idx = excerpt.lower().find(keyword_lower)
        if actual_idx >= 0:
            excerpt = (excerpt[:actual_idx] + "**" + 
                      excerpt[actual_idx:actual_idx+len(keyword)] + "**" +
                      excerpt[actual_idx+len(keyword):])
        
        return excerpt
    
    # ========== Layer 4: 综合查询 ==========
    
    def query(self, q: str) -> QueryResult:
        """综合查询
        
        查询语法：
        - "拼多多" → 实体直达
        - "拼多" → 模糊搜索
        - "AI" → 概念/实体/来源综合搜索
        """
        q = q.strip()
        
        # Layer 1: 实体直达
        entity = self.query_entity(q)
        if entity:
            return self._format_entity_result(q, entity)
        
        # Layer 2: 索引层
        entities = self.search_entities(q)
        concepts = self.search_concepts(q)
        
        if entities or concepts:
            return self._format_index_result(q, entities, concepts)
        
        # Layer 3: 来源页检索
        sources = self.search_sources(q, days=30)
        if sources:
            return self._format_source_result(q, sources)
        
        # Layer 4: 综合层（扩大时间范围）
        all_sources = self.search_sources(q)
        return self._format_comprehensive_result(q, all_sources)
    
    def _format_entity_result(self, q: str, entity: Dict) -> QueryResult:
        """格式化实体查询结果"""
        signals = []
        for entry in entity.get('timeline', []):
            for s in entry.get('signals', []):
                signals.append({
                    'date': entry.get('date'),
                    'direction': s.get('direction'),
                    'confidence': s.get('confidence'),
                    'summary': s.get('summary'),
                    'caveats': s.get('caveats', []),
                })
        
        # 按时间降序
        signals.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        # 统计
        direction_counts = {}
        for s in signals:
            d = s['direction']
            direction_counts[d] = direction_counts.get(d, 0) + 1
        
        summary = f"实体: {entity.get('name')} ({entity.get('ticker', 'N/A')})\n"
        summary += f"类型: {entity.get('type', 'unknown')}\n"
        summary += f"信号数量: {len(signals)}\n"
        summary += f"方向分布: {direction_counts}\n"
        
        latest = signals[0] if signals else None
        if latest:
            summary += f"\n最新信号 ({latest['date']}):\n"
            summary += f"  [{latest['direction']}] {latest['summary']}\n"
        
        return QueryResult(
            query=q,
            layer="entity_direct",
            entities=[entity],
            concepts=[],
            sources=[],
            signals=signals,
            summary=summary,
        )
    
    def _format_index_result(self, q: str, entities: List[Dict], 
                           concepts: List[Dict]) -> QueryResult:
        """格式化索引查询结果"""
        summary = f"找到 {len(entities)} 个实体, {len(concepts)} 个概念\n\n"
        
        if entities:
            summary += "实体:\n"
            for e in entities[:5]:
                summary += f"  • {e.get('name')} ({e.get('ticker', 'N/A')})\n"
        
        if concepts:
            summary += "\n概念:\n"
            for c in concepts[:5]:
                summary += f"  • {c.get('name')}: {c.get('definition', '')[:60]}...\n"
        
        return QueryResult(
            query=q,
            layer="index",
            entities=entities,
            concepts=concepts,
            sources=[],
            signals=[],
            summary=summary,
        )
    
    def _format_source_result(self, q: str, sources: List[Dict]) -> QueryResult:
        """格式化来源查询结果"""
        summary = f"最近30天找到 {len(sources)} 篇相关来源\n\n"
        
        for s in sources[:5]:
            title = s.get('title', 'Untitled')
            date = s.get('date', 'Unknown')
            excerpt = s.get('_excerpt', '')
            summary += f"  [{date}] {title[:50]}\n"
            if excerpt:
                summary += f"      {excerpt[:100]}...\n"
        
        return QueryResult(
            query=q,
            layer="source",
            entities=[],
            concepts=[],
            sources=sources,
            signals=[],
            summary=summary,
        )
    
    def _format_comprehensive_result(self, q: str, 
                                   sources: List[Dict]) -> QueryResult:
        """格式化综合查询结果"""
        if sources:
            summary = f"历史共找到 {len(sources)} 篇相关来源\n\n"
            for s in sources[:5]:
                title = s.get('title', 'Untitled')
                date = s.get('date', 'Unknown')
                summary += f"  [{date}] {title[:50]}\n"
        else:
            summary = f"未找到与 '{q}' 相关的任何内容"
        
        return QueryResult(
            query=q,
            layer="comprehensive",
            entities=[],
            concepts=[],
            sources=sources,
            signals=[],
            summary=summary,
        )
    
    # ========== 日报生成 ==========
    
    def generate_daily_brief(self, date: str = None) -> str:
        """生成日报
        
        Args:
            date: 日期字符串 'YYYY-MM-DD'，None = 今天
        
        Returns:
            Markdown 格式的日报
        """
        if date is None:
            date = datetime.now(TZ).strftime('%Y-%m-%d')
        
        # 获取当天的来源页
        sources = self._source_index.get(date, [])
        
        lines = [
            f"# 知识引擎日报 — {date}",
            "",
            f"今日新增来源: {len(sources)} 篇",
            "",
        ]
        
        # 实体信号汇总
        entity_signals = {}
        for filepath in sources:
            fm = self._load_frontmatter(filepath)
            for signal in fm.get('signals', []):
                entity = signal.get('entity', 'Unknown')
                if entity not in entity_signals:
                    entity_signals[entity] = []
                entity_signals[entity].append(signal)
        
        if entity_signals:
            lines.extend(["## 实体信号", ""])
            for entity, signals in sorted(entity_signals.items()):
                latest = signals[-1]  # 最新的信号
                direction = latest.get('direction', 'neutral')
                emoji = {"positive": "📈", "negative": "📉", "neutral": "➡️"}.get(direction, "➡️")
                lines.append(f"{emoji} **{entity}**: {latest.get('summary', '')}")
                lines.append("")
        
        # 新提及实体
        new_entities = set()
        for filepath in sources:
            fm = self._load_frontmatter(filepath)
            new_entities.update(fm.get('entities', []))
        
        if new_entities:
            lines.extend(["## 新提及实体", ""])
            for e in sorted(new_entities)[:10]:
                lines.append(f"- {e}")
            lines.append("")
        
        # 新提及概念
        new_concepts = set()
        for filepath in sources:
            fm = self._load_frontmatter(filepath)
            new_concepts.update(fm.get('concepts', []))
        
        if new_concepts:
            lines.extend(["## 新提及概念", ""])
            for c in sorted(new_concepts)[:10]:
                lines.append(f"- {c}")
            lines.append("")
        
        return '\n'.join(lines)


# ========== CLI ==========

if __name__ == "__main__":
    import sys
    
    query_engine = KnowledgeQuery(".")
    
    if len(sys.argv) < 2:
        print("Usage: python query.py <query>")
        print("       python query.py --daily [YYYY-MM-DD]")
        sys.exit(1)
    
    if sys.argv[1] == "--daily":
        date = sys.argv[2] if len(sys.argv) > 2 else None
        print(query_engine.generate_daily_brief(date))
    else:
        q = ' '.join(sys.argv[1:])
        result = query_engine.query(q)
        print(f"Query: {result.query}")
        print(f"Layer: {result.layer}")
        print(f"{'='*60}")
        print(result.summary)
        
        if result.signals:
            print(f"\n{'='*60}")
            print("Signals:")
            for s in result.signals[:5]:
                print(f"  [{s['date']}] {s['direction']} ({s['confidence']}): {s['summary'][:60]}")
