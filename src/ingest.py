"""
Ingest Pipeline: 单篇文章摄入

流程:
1. 读取 raw/ 文章
2. 解析元数据（标题/作者/日期/URL）
3. LLM 提取知识（实体/概念/信号/主张）
4. 生成来源页（knowledge/sources/YYYY-MM-DD-{id}.md）
5. 更新实体页（knowledge/entities/{规范名}.md）
6. 更新概念页（knowledge/concepts/{概念名}.md）
7. 更新索引（knowledge/index.md）
8. git commit
"""

import os
import re
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

import yaml

from extractor import KnowledgeExtractor


TZ = timezone(timedelta(hours=8))


class ArticleParser:
    """解析原始文章文件"""

    @staticmethod
    def parse(filepath: str) -> dict:
        """
        解析 markdown 文章，提取元数据
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取标题（第一行 H1）
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else "Untitled"

        # 提取作者
        author_match = re.search(r'作者：(.+?)(\s+\|)', content)
        author = author_match.group(1).strip() if author_match else "Unknown"

        # 提取发布时间
        date_match = re.search(r'发布时间：发布于(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})', content)
        if date_match:
            pub_date = date_match.group(1).strip()
        else:
            # 尝试其他格式
            date_match2 = re.search(r'(\d{4}-\d{2}-\d{2})', content)
            pub_date = date_match2.group(1) if date_match2 else datetime.now(TZ).strftime('%Y-%m-%d')

        # 提取原文链接
        url_match = re.search(r'原文链接：(https?://\S+)', content)
        url = url_match.group(1) if url_match else ""

        # 提取正文（--- 之后、爬取时间之前）
        body = content
        # 移除元数据行
        body = re.sub(r'> 作者：.+\n', '', body)
        body = re.sub(r'> 点赞：.+\n', '', body)
        body = re.sub(r'> 原文链接：.+\n', '', body)
        body = re.sub(r'---\s*\n', '\n', body)
        body = re.sub(r'\*爬取时间：.+\*', '', body)
        body = re.sub(r'@今日话题\s+@雪球创作者中心\s+@小秘书', '', body)
        body = re.sub(r'#[^#\s]+#', '', body)

        # 清理空行
        body = '\n'.join(line for line in body.split('\n') if line.strip())

        return {
            'id': Path(filepath).stem,
            'title': title,
            'author': author,
            'date': pub_date,
            'url': url,
            'body': body.strip(),
            'source': 'xueqiu',
            'raw_path': filepath,
        }


class SourcePageWriter:
    """生成来源页"""

    def __init__(self, knowledge_dir: str):
        self.sources_dir = Path(knowledge_dir) / "sources"
        self.sources_dir.mkdir(parents=True, exist_ok=True)

    def write(self, article: dict, extraction: dict, quality_score: float) -> str:
        """
        生成来源页 Markdown

        Returns:
            生成的文件路径
        """
        date_str = article['date'][:10] if len(article['date']) >= 10 else article['date']
        filename = f"{date_str}-{article['id']}.md"
        filepath = self.sources_dir / filename

        # 构建 frontmatter
        frontmatter = {
            'title': article['title'],
            'url': article['url'],
            'date': article['date'],
            'author': article['author'],
            'source': article['source'],
            'raw_id': article['id'],
        }

        # 提取的实体
        if extraction.get('entities'):
            frontmatter['entities'] = [e['name'] for e in extraction['entities']]
            frontmatter['tickers'] = list(set(
                e.get('ticker') for e in extraction['entities']
                if e.get('ticker')
            ))

        # 提取的概念
        if extraction.get('concepts'):
            frontmatter['concepts'] = [c['name'] for c in extraction['concepts']]

        # 提取的信号
        if extraction.get('signals'):
            frontmatter['signals'] = extraction['signals']

        # 质量评分
        frontmatter['quality_score'] = quality_score
        frontmatter['extraction_confidence'] = extraction.get('extraction_confidence', 0.0)
        frontmatter['needs_review'] = extraction.get('needs_review', False)
        if extraction.get('review_reasons'):
            frontmatter['review_reasons'] = extraction['review_reasons']

        # 生成 Markdown
        yaml_front = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)

        md_content = f"""---
{yaml_front}---

# {article['title']}

> 作者：{article['author']} | 发布时间：{article['date']}
> 原文链接：{article['url']}

## 正文

{article['body'][:2000]}{'...' if len(article['body']) > 2000 else ''}

## 提取摘要

### 实体
{self._format_entities(extraction.get('entities', []))}

### 概念
{self._format_concepts(extraction.get('concepts', []))}

### 信号
{self._format_signals(extraction.get('signals', []))}

### 关键主张
{self._format_claims(extraction.get('claims', []))}
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

        return str(filepath)

    def _format_entities(self, entities: list) -> str:
        if not entities:
            return "_无明确提及的实体_"
        lines = []
        for e in entities:
            ticker = f" ({e.get('ticker', '')})" if e.get('ticker') else ""
            lines.append(f"- **{e['name']}**{ticker} — {e.get('type', 'unknown')} ({e.get('role', 'mentioned')}, {e.get('confidence', 'medium')})")
        return '\n'.join(lines)

    def _format_concepts(self, concepts: list) -> str:
        if not concepts:
            return "_无提取的概念_"
        lines = []
        for c in concepts:
            lines.append(f"- **{c['name']}** — {c.get('definition', '')[:80]}...")
        return '\n'.join(lines)

    def _format_signals(self, signals: list) -> str:
        if not signals:
            return "_无明确投资信号_"
        lines = []
        for s in signals:
            emoji = {"positive": "📈", "negative": "📉", "neutral": "➡️"}.get(s['direction'], "➡️")
            caveats = f" (注意: {', '.join(s.get('caveats', []))})" if s.get('caveats') else ""
            lines.append(f"- {emoji} **[{s['direction']}]** {s['entity']}: {s['summary']}{caveats}")
        return '\n'.join(lines)

    def _format_claims(self, claims: list) -> str:
        if not claims:
            return "_无提取的关键主张_"
        lines = []
        for i, c in enumerate(claims[:5], 1):
            lines.append(f"{i}. {c['statement'][:100]}...")
            if c.get('quote'):
                lines.append(f"   > 原文: {c['quote'][:80]}...")
        return '\n'.join(lines)


class EntityPageWriter:
    """更新实体页"""

    def __init__(self, knowledge_dir: str):
        self.entities_dir = Path(knowledge_dir) / "entities"
        self.entities_dir.mkdir(parents=True, exist_ok=True)

    def update(self, entity_name: str, entity_data: dict, article: dict, signals: list) -> str:
        """
        更新实体页（追加信号和时间线）

        Returns:
            实体页文件路径
        """
        # 文件名：使用规范名（清理特殊字符）
        safe_name = re.sub(r'[^\w\u4e00-\u9fff\-]', '_', entity_name)
        filepath = self.entities_dir / f"{safe_name}.md"

        # 如果实体页已存在，读取现有内容
        existing_frontmatter = {}
        existing_body = ""
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            # 解析现有 frontmatter
            fm_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if fm_match:
                try:
                    existing_frontmatter = yaml.safe_load(fm_match.group(1)) or {}
                    existing_body = content[fm_match.end():]
                except yaml.YAMLError:
                    pass

        # 构建/更新 frontmatter
        frontmatter = existing_frontmatter.copy()
        frontmatter['name'] = entity_name
        frontmatter['type'] = entity_data.get('type', 'company')
        frontmatter['ticker'] = entity_data.get('ticker', '')
        frontmatter['market'] = entity_data.get('market', '')

        # 更新别名
        aliases = set(frontmatter.get('aliases', []))
        aliases.add(entity_name)
        if entity_data.get('aliases'):
            aliases.update(entity_data['aliases'])
        frontmatter['aliases'] = sorted(aliases)

        # 更新关联概念
        # (在概念页更新时反向更新)

        # 构建信号时间线
        signal_entry = {
            'date': article['date'][:10],
            'source': f"sources/{article['date'][:10]}-{article['id']}.md",
            'signals': signals,
        }

        # 读取现有时间线
        timeline = frontmatter.get('timeline', [])
        timeline.append(signal_entry)
        # 去重：同一天同一来源不重复
        seen = set()
        unique_timeline = []
        for t in timeline:
            key = (t['date'], t['source'])
            if key not in seen:
                seen.add(key)
                unique_timeline.append(t)
        frontmatter['timeline'] = unique_timeline

        # 更新最后更新时间
        frontmatter['last_updated'] = datetime.now(TZ).isoformat()

        # 生成 Markdown
        yaml_front = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)

        md_content = f"""---
{yaml_front}---

# {entity_name}

> 类型: {entity_data.get('type', 'company')}
> 股票代码: {entity_data.get('ticker', 'N/A')}

## 信号时间线

{self._format_timeline(unique_timeline)}

{existing_body if existing_body else ""}
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

        return str(filepath)

    def _format_timeline(self, timeline: list) -> str:
        if not timeline:
            return "_暂无信号记录_"
        lines = []
        for t in sorted(timeline, key=lambda x: x['date'], reverse=True):
            lines.append(f"\n### {t['date']}")
            lines.append(f"> 来源: [{t['source']}]({t['source']})")
            for s in t.get('signals', []):
                emoji = {"positive": "📈", "negative": "📉", "neutral": "➡️"}.get(s['direction'], "➡️")
                lines.append(f"- {emoji} [{s['direction']}] {s.get('summary', '')}")
        return '\n'.join(lines)


class ConceptPageWriter:
    """更新概念页"""

    def __init__(self, knowledge_dir: str):
        self.concepts_dir = Path(knowledge_dir) / "concepts"
        self.concepts_dir.mkdir(parents=True, exist_ok=True)

    def update(self, concept_name: str, concept_data: dict, article: dict, related_entities: list) -> str:
        """
        更新概念页
        """
        safe_name = re.sub(r'[^\w\u4e00-\u9fff\-]', '_', concept_name)
        filepath = self.concepts_dir / f"{safe_name}.md"

        # 读取现有内容
        existing_frontmatter = {}
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            fm_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if fm_match:
                try:
                    existing_frontmatter = yaml.safe_load(fm_match.group(1)) or {}
                except yaml.YAMLError:
                    pass

        # 构建 frontmatter
        frontmatter = existing_frontmatter.copy()
        frontmatter['name'] = concept_name
        frontmatter['definition'] = concept_data.get('definition', '')

        # 更新关联实体
        entities = set(frontmatter.get('entities', []))
        entities.update(related_entities)
        frontmatter['entities'] = sorted(entities)

        # 更新来源
        sources = frontmatter.get('sources', [])
        new_source = f"sources/{article['date'][:10]}-{article['id']}.md"
        if new_source not in sources:
            sources.append(new_source)
        frontmatter['sources'] = sources

        # 更新最后时间
        frontmatter['last_updated'] = datetime.now(TZ).isoformat()

        # 首次创建时添加定义
        body = ""
        if not filepath.exists():
            body = f"""
## 定义

{concept_data.get('definition', '')}

## 关联实体

{chr(10).join(f'- [[entities/{re.sub(r"[^\\w\\u4e00-\\u9fff\\-]", "_", e)}|{e}]]' for e in sorted(entities))}

## 来源文章

{chr(10).join(f'- [{s}]({s})' for s in sources[-10:])}
"""
        else:
            # 已存在，只更新 frontmatter，保留 body
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            fm_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if fm_match:
                body = content[fm_match.end():]

        yaml_front = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)

        md_content = f"""---
{yaml_front}---

# {concept_name}

{body}
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

        return str(filepath)


class IngestPipeline:
    """完整的摄入管线"""

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.knowledge_dir = self.base_dir / "knowledge"
        self.extractor = KnowledgeExtractor()
        self.source_writer = SourcePageWriter(self.knowledge_dir)
        self.entity_writer = EntityPageWriter(self.knowledge_dir)
        self.concept_writer = ConceptPageWriter(self.knowledge_dir)

    def ingest(self, raw_filepath: str, entity_dict: Optional[dict] = None) -> dict:
        """
        摄入单篇文章

        Returns:
            {'success': bool, 'source_page': str, 'entities_updated': list, 'concepts_updated': list, 'error': str}
        """
        try:
            # 1. 解析文章
            article = ArticleParser.parse(raw_filepath)

            # 2. LLM 提取
            result = self.extractor.extract(article['body'], entity_dict)

            # 3. 质量检查
            if result.needs_review:
                print(f"  ⚠️ 需要 review: {', '.join(result.review_reasons)}")

            # 4. 序列化提取结果
            extraction = {
                'entities': [],
                'concepts': [],
                'signals': [],
                'claims': [],
                'extraction_confidence': result.extraction_confidence,
                'needs_review': result.needs_review,
                'review_reasons': result.review_reasons,
            }

            for e in result.entities:
                extraction['entities'].append({
                    'name': e.name, 'type': e.type, 'role': e.role,
                    'confidence': e.confidence, 'ticker': e.ticker,
                    'aliases_found': e.aliases_found,
                })

            for c in result.concepts:
                extraction['concepts'].append({
                    'name': c.name, 'definition': c.definition,
                    'role': c.role, 'confidence': c.confidence,
                    'entities_related': c.entities_related,
                })

            for s in result.signals:
                extraction['signals'].append({
                    'entity': s.entity, 'direction': s.direction,
                    'confidence': s.confidence, 'time_frame': s.time_frame,
                    'summary': s.summary, 'caveats': s.caveats,
                    'quote': s.quote, 'business_line': s.business_line,
                })

            for c in result.claims:
                extraction['claims'].append({
                    'statement': c.statement, 'entity': c.entity,
                    'concept': c.concept, 'quote': c.quote,
                    'confidence': c.confidence,
                })

            # 5. 生成来源页
            source_page = self.source_writer.write(article, extraction, result.quality_score)

            # 6. 更新实体页
            entities_updated = []
            for e in result.entities:
                entity_data = {
                    'type': e.type,
                    'ticker': e.ticker,
                    'aliases': e.aliases_found,
                }
                # 从词典补充信息
                if entity_dict:
                    for status in ['verified', 'unverified']:
                        if e.name in entity_dict.get(status, {}):
                            dict_entry = entity_dict[status][e.name]
                            entity_data['ticker'] = entity_data['ticker'] or dict_entry.get('ticker')
                            entity_data['market'] = dict_entry.get('market', '')
                            break

                entity_signals = [s for s in extraction['signals'] if s['entity'] == e.name]
                ep = self.entity_writer.update(e.name, entity_data, article, entity_signals)
                entities_updated.append(ep)

            # 7. 更新概念页
            concepts_updated = []
            for c in result.concepts:
                cp = self.concept_writer.update(
                    c.name,
                    {'definition': c.definition},
                    article,
                    c.entities_related,
                )
                concepts_updated.append(cp)

            return {
                'success': True,
                'source_page': source_page,
                'entities_updated': entities_updated,
                'concepts_updated': concepts_updated,
                'quality_score': result.quality_score,
                'extraction_confidence': result.extraction_confidence,
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }

    def git_commit(self, message: str):
        """执行 git commit"""
        try:
            subprocess.run(
                ['git', 'add', '-A'],
                cwd=self.base_dir,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.base_dir,
                check=True,
                capture_output=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Git commit failed: {e.stderr.decode()}")
            return False


if __name__ == "__main__":
    import sys

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 加载词典
    dict_path = os.path.join(base_dir, "config", "entity_dictionary.yaml")
    entity_dict = {}
    if os.path.exists(dict_path):
        with open(dict_path) as f:
            entity_dict = yaml.safe_load(f) or {}
        print(f"Loaded dictionary: {len(entity_dict.get('verified', {}))} verified entities")

    # 初始化管线
    pipeline = IngestPipeline(base_dir)

    # 处理 raw/ 目录下的文章
    raw_dir = os.path.join(base_dir, "raw")
    files = sorted(os.listdir(raw_dir))

    print(f"\nFound {len(files)} articles in raw/")

    for fname in files:
        if not fname.endswith('.md'):
            continue

        fpath = os.path.join(raw_dir, fname)
        print(f"\n{'='*60}")
        print(f"Processing: {fname}")
        print(f"{'='*60}")

        result = pipeline.ingest(fpath, entity_dict)

        if result['success']:
            print(f"✅ Source page: {result['source_page']}")
            print(f"   Entities: {len(result['entities_updated'])}")
            print(f"   Concepts: {len(result['concepts_updated'])}")
            print(f"   Quality: {result['quality_score']:.2f} | Confidence: {result['extraction_confidence']:.2f}")
        else:
            print(f"❌ Failed: {result['error']}")

    # Git commit
    print(f"\n{'='*60}")
    print("Git commit...")
    if pipeline.git_commit(f"ingest: {len(files)} articles processed"):
        print("✅ Committed successfully")
    else:
        print("⚠️ Git commit skipped (no changes or error)")
