"""
Knowledge Extractor: 从投资文章中提取结构化知识

输入: Markdown 文章
输出: JSON（实体/概念/信号/主张）
"""

import json
import os
import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ExtractedEntity:
    name: str          # 规范名（优先使用词典）
    type: str          # company / person / product / index
    role: str          # analyzed / mentioned / example / background
    confidence: str    # high / medium / low
    ticker: Optional[str] = None
    aliases_found: List[str] = field(default_factory=list)


@dataclass
class ExtractedConcept:
    name: str          # 概念名
    definition: str    # 一句话定义
    role: str          # core / related / mentioned
    confidence: str    # high / medium / low
    entities_related: List[str] = field(default_factory=list)


@dataclass
class ExtractedSignal:
    entity: str        # 关联实体（规范名）
    direction: str     # positive / negative / neutral
    confidence: str    # high / medium / low
    time_frame: str    # short_term / medium_term / long_term
    summary: str       # 核心观点摘要
    caveats: List[str] = field(default_factory=list)
    quote: str = ""    # 原文引用
    business_line: Optional[str] = None


@dataclass
class ExtractedClaim:
    statement: str     # 主张内容
    entity: Optional[str] = None
    concept: Optional[str] = None
    quote: str = ""
    confidence: str = "medium"


@dataclass
class ExtractionResult:
    entities: List[ExtractedEntity] = field(default_factory=list)
    concepts: List[ExtractedConcept] = field(default_factory=list)
    signals: List[ExtractedSignal] = field(default_factory=list)
    claims: List[ExtractedClaim] = field(default_factory=list)
    quality_score: float = 0.0
    extraction_confidence: float = 0.0
    needs_review: bool = False
    review_reasons: List[str] = field(default_factory=list)


class KnowledgeExtractor:
    """知识提取器"""

    def __init__(self, provider: str = "minimax", model: str = "minimax-m3"):
        self.provider = provider
        self.model = model
        self.client = None
        self._init_client()

    def _init_client(self):
        """初始化 LLM 客户端"""
        try:
            from openai import OpenAI as OpenAIClient
        except ImportError:
            print("请安装 openai: pip install openai")
            return

        if self.provider == "minimax":
            # 字节 coding plan（OpenAI 兼容接口）
            api_key = os.environ.get("ARK_API_KEY") or os.environ.get("MINIMAX_API_KEY")
            base_url = os.environ.get("ARK_CODING_BASE_URL", "https://ark.cn-beijing.volces.com/api/coding/v3")
            if not api_key:
                raise ValueError("ARK_API_KEY or MINIMAX_API_KEY required")
            self.client = OpenAIClient(api_key=api_key, base_url=base_url)

    def extract(self, article_text: str, entity_dict: Optional[dict] = None) -> ExtractionResult:
        """
        从文章中提取知识

        Args:
            article_text: 文章正文（Markdown）
            entity_dict: 预定义实体词典 {规范名: {ticker, aliases}}
        """
        if not self.client:
            raise RuntimeError("LLM client not initialized")

        prompt = self._build_prompt(article_text, entity_dict)

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=8192,
                temperature=0.1,
            )
            raw_output = resp.choices[0].message.content
            return self._parse_output(raw_output, entity_dict)
        except Exception as e:
            return ExtractionResult(
                needs_review=True,
                review_reasons=[f"LLM call failed: {e}"]
            )

    def _build_prompt(self, article_text: str, entity_dict: Optional[dict]) -> str:
        """构建提取 prompt"""

        # 词典提示
        dict_hint = ""
        if entity_dict:
            verified = list(entity_dict.get("verified", {}).keys())[:30]
            dict_hint = f"""
## 已知实体词典（优先使用规范名）
以下是从 watchlist 同步的已知实体，文章中如果提到这些公司/产品，请优先使用词典中的规范名：
{', '.join(verified)}
...
（共 {len(entity_dict.get('verified', {}))} 个已知实体）
"""

        return f"""你是一位价值投资知识提取专家。请严格按以下规则从投资文章中提取结构化知识。

## 提取规则

### 1. 实体提取（公司/人/产品/指数）
- **只提取有明确股票代码或明确业务指向的公司**
- **忽略**：泛化指代（如"某同行"、"互联网巨头"、"龙头企业"）
- **类型**：company / person / product / index
- **角色**：
  - analyzed: 文章重点分析的对象
  - mentioned: 被明确提及但非重点
  - example: 作为案例引用
  - background: 仅作为背景信息
- **规范名优先**：如果实体在词典中，使用词典中的规范名

### 2. 概念提取（抽象主题/投资逻辑）
- **判断标准**：这个主题是否跨实体通用？是否包含行业层面分析？
- **建概念页的情况**（需同时满足）：
  1. 跨实体通用（如"国际化"适用于迈瑞、美团等多家公司）
  2. 信息量大（有行业层面分析，不止一句话提及）
  3. 有投资含义（能指导决策）
- **不建概念页的情况**：
  - 仅某实体特有（如"迈瑞医疗的国际化进展"→ 归入实体页属性）
  - 仅一句话提及
  - 纯财务数据（如"ROIC=15%"）
- **粒度**：能独立回答一个投资问题（如"AI基础设施"✅，"AI"❌太粗）

### 3. 信号提取（投资观点）
- **只提取有明确观点的文章**，纯数据描述不提取信号
- **方向判定**（取主基调）：
  - positive: 明确看好
  - negative: 明确看空
  - neutral: 明确中性/无倾向
- **置信度**：
  - high: 有数据/逻辑强支撑
  - medium: 有支撑但存在不确定性（如"谨慎看好"）
  - low: 支撑较弱或作者语气犹豫
- **时间框架**：short_term / medium_term / long_term
- **nuances 处理**：
  - "谨慎看好" → direction: positive, confidence: medium, caveats: ["整体谨慎"]
  - "短期承压但长期看好" → 拆分为两个信号（short_term negative + long_term positive）
- **约束**：同一实体同一文章最多 2 个信号

### 4. 主张提取（关键论断）
- 提取文章中的核心论断
- 必须附原文引用（quote）
- 标注关联的实体和概念

### 5. 质量评分
- 文章质量（信息密度、逻辑清晰度）: 0-1
- 提取置信度（提取难度、歧义程度）: 0-1
- 需要 review 的情况：
  - 实体识别不确定
  - 信号方向难以判断
  - 概念粒度难以确定

## 输出格式

请输出 **纯 JSON**，不要有任何其他文字：

```json
{{
  "entities": [
    {{
      "name": "规范名",
      "type": "company|person|product|index",
      "role": "analyzed|mentioned|example|background",
      "confidence": "high|medium|low",
      "ticker": "可选",
      "aliases_found": ["文中出现的别名"]
    }}
  ],
  "concepts": [
    {{
      "name": "概念名",
      "definition": "一句话定义",
      "role": "core|related|mentioned",
      "confidence": "high|medium|low",
      "entities_related": ["相关实体规范名"]
    }}
  ],
  "signals": [
    {{
      "entity": "关联实体规范名",
      "direction": "positive|negative|neutral",
      "confidence": "high|medium|low",
      "time_frame": "short_term|medium_term|long_term",
      "summary": "核心观点摘要（20字以内）",
      "caveats": ["风险提示/不确定性"],
      "quote": "原文引用",
      "business_line": "可选：业务线"
    }}
  ],
  "claims": [
    {{
      "statement": "主张内容",
      "entity": "关联实体",
      "concept": "关联概念",
      "quote": "原文引用",
      "confidence": "high|medium|low"
    }}
  ],
  "quality_score": 0.8,
  "extraction_confidence": 0.75,
  "needs_review": false,
  "review_reasons": []
}}
```

{dict_hint}

---

## 待分析文章

{article_text}

---

请输出 JSON："""

    def _parse_output(self, raw_output: str, entity_dict: Optional[dict]) -> ExtractionResult:
        """解析 LLM 输出"""

        # 提取 JSON
        json_match = re.search(r'```json\s*(.*?)\s*```', raw_output, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 尝试直接解析
            json_str = raw_output.strip()

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            return ExtractionResult(
                needs_review=True,
                review_reasons=[f"JSON parse failed: {e}"]
            )

        # 映射到数据结构
        result = ExtractionResult(
            quality_score=data.get("quality_score", 0.0),
            extraction_confidence=data.get("extraction_confidence", 0.0),
            needs_review=data.get("needs_review", False),
            review_reasons=data.get("review_reasons", [])
        )

        for e in data.get("entities", []):
            result.entities.append(ExtractedEntity(
                name=e.get("name", ""),
                type=e.get("type", "company"),
                role=e.get("role", "mentioned"),
                confidence=e.get("confidence", "medium"),
                ticker=e.get("ticker"),
                aliases_found=e.get("aliases_found", [])
            ))

        for c in data.get("concepts", []):
            result.concepts.append(ExtractedConcept(
                name=c.get("name", ""),
                definition=c.get("definition", ""),
                role=c.get("role", "related"),
                confidence=c.get("confidence", "medium"),
                entities_related=c.get("entities_related", [])
            ))

        for s in data.get("signals", []):
            result.signals.append(ExtractedSignal(
                entity=s.get("entity", ""),
                direction=s.get("direction", "neutral"),
                confidence=s.get("confidence", "medium"),
                time_frame=s.get("time_frame", "medium_term"),
                summary=s.get("summary", ""),
                caveats=s.get("caveats", []),
                quote=s.get("quote", ""),
                business_line=s.get("business_line")
            ))

        for c in data.get("claims", []):
            result.claims.append(ExtractedClaim(
                statement=c.get("statement", ""),
                entity=c.get("entity"),
                concept=c.get("concept"),
                quote=c.get("quote", ""),
                confidence=c.get("confidence", "medium")
            ))

        return result


if __name__ == "__main__":
    import yaml

    # 测试
    extractor = KnowledgeExtractor()

    # 加载词典
    dict_path = os.path.join(os.path.dirname(__file__), "..", "config", "entity_dictionary.yaml")
    entity_dict = {}
    if os.path.exists(dict_path):
        with open(dict_path) as f:
            entity_dict = yaml.safe_load(f) or {}

    # 加载测试文章
    raw_dir = os.path.join(os.path.dirname(__file__), "..", "raw")
    for fname in sorted(os.listdir(raw_dir))[:1]:
        fpath = os.path.join(raw_dir, fname)
        with open(fpath) as f:
            article = f.read()

        print(f"\n{'='*60}")
        print(f"Extracting: {fname}")
        print(f"{'='*60}")

        result = extractor.extract(article, entity_dict)

        print(f"\nQuality Score: {result.quality_score}")
        print(f"Extraction Confidence: {result.extraction_confidence}")
        print(f"Needs Review: {result.needs_review}")
        if result.review_reasons:
            print(f"Review Reasons: {result.review_reasons}")

        print(f"\nEntities ({len(result.entities)}):")
        for e in result.entities:
            print(f"  - {e.name} ({e.type}, {e.role}, {e.confidence})")

        print(f"\nConcepts ({len(result.concepts)}):")
        for c in result.concepts:
            print(f"  - {c.name}: {c.definition[:50]}...")

        print(f"\nSignals ({len(result.signals)}):")
        for s in result.signals:
            print(f"  - [{s.direction}] {s.entity}: {s.summary}")

        print(f"\nClaims ({len(result.claims)}):")
        for c in result.claims[:3]:
            print(f"  - {c.statement[:60]}...")
