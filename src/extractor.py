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
    verified: bool = False  # 是否在词典中（默认 False，防止未验证实体被误标）
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


def normalize_entity_name(name: str, entity_dict: Optional[dict]) -> tuple:
    """将实体别名归一到规范名，返回 (规范名, ticker, verified)。
    如果不在词典中，返回 (原name, None, False)。
    自动处理港股-W后缀别名匹配："阿里"→"阿里巴巴-W"，"腾讯"→"腾讯控股"
    """
    if not entity_dict or "verified" not in entity_dict:
        return name, None, False
    
    verified = entity_dict["verified"]
    
    # 1. 精确匹配规范名
    if name in verified:
        return name, verified[name].get("ticker"), True
    
    # 2. 精确匹配别名
    for canonical_name, info in verified.items():
        aliases = info.get("aliases", [])
        if name in aliases:
            return canonical_name, info.get("ticker"), True
    
    # 3. 模糊匹配港股后缀：去掉-W/-S后比较
    name_clean = name.replace("-W", "").replace("-S", "")
    for canonical_name, info in verified.items():
        canonical_clean = canonical_name.replace("-W", "").replace("-S", "")
        if name_clean == canonical_clean:
            return canonical_name, info.get("ticker"), True
        # 检查别名去掉-W后匹配
        for alias in info.get("aliases", []):
            if name_clean == alias.replace("-W", "").replace("-S", ""):
                return canonical_name, info.get("ticker"), True
    
    return name, None, False


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
            result = self._parse_output(raw_output, entity_dict)
            # 如果JSON解析失败，重试一次
            if result.needs_review and any("JSON parse failed" in r for r in result.review_reasons):
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": raw_output},
                        {"role": "user", "content": "上次输出JSON格式有误，请严格输出纯JSON，不要添加markdown解释。请重新输出正确的JSON结果："}
                    ],
                    max_tokens=8192,
                    temperature=0.0,
                )
                raw_output = resp.choices[0].message.content
                result = self._parse_output(raw_output, entity_dict)
            return result
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

### 1. 实体提取（可投资标的）
- **核心原则**：只提取可投资的标的（上市公司、拟上市公司、指数）
- ✅ **提取**（以下情况满足其一）：
  - 有股票代码的公司（如 $拼多多(PDD)$、$快手-W(01024)$）
  - 明确可投资的上市公司（文中提到其股票、IPO、财报）
  - 投资指数（如沪深300、纳斯达克100）
  - 知名投资机构（如 GIC、腾讯投资、高瓴）—— 作为 background 角色
- ❌ **不提取**（以下情况全部不提取）：
  - 纯产品/游戏/App 名称（如"心动小镇"、"可灵"、"豆包"、"微信"）
  - 非上市且不可投资的子公司/业务部门（如"多多买菜"、"Temu"——除非文章明确讨论其独立上市前景）
  - 泛化指代（如"某同行"、"互联网巨头"、"龙头企业"）
  - 仅作为案例提及的无代码公司
- **类型**：
  - company: 上市公司/拟上市公司
  - person: 投资人/分析师/企业家
  - product: 产品/服务（仅记录为信息，不建独立实体页）
  - index: 指数/板块
- **角色**：
  - analyzed: 文章重点分析的对象
  - mentioned: 被明确提及但非重点
  - example: 作为案例引用
  - background: 仅作为背景信息
- **规范名优先**：如果实体在词典中，使用词典中的规范名
- **开放识别**：即使实体不在词典中，只要是有股票代码或明确可投资的上市公司，也应识别（标记 verified=false）

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
- **粒度**：能独立回答一个投资问题
  - ✅ 合适粒度："AI基础设施"、"PC端广告变现"、"跨境电商"、"本地生活服务竞争格局"
  - ❌ 太粗："AI"、"互联网"、"投资"
  - ❌ 太细："2026年Q1快手直播收入"（归入实体页属性）
- **业绩分析文章也必须提取概念**：即使是业绩分析文章，也要提取背后的行业概念（如拼多多业绩分析应提取"跨境电商"、"下沉市场竞争"等）
- **概念层级**：提取时标注粒度级别
  - L1 宏观：跨行业通用（如"消费升级"、"AI革命"）
  - L2 中观：行业内通用（如"PC端广告变现"、"新能源汽车电池技术路线"）
  - L3 微观：公司特定（不建概念页，归入实体页）

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
      "verified": true,
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
      "level": "L1|L2|L3",
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

        # 实体去重：按 归一化后的规范名 + type 去重，保留第一个
        seen_entities = set()
        for e in data.get("entities", []):
            raw_name = e.get("name", "")
            entity_type = e.get("type", "company")
            
            # 别名归一化：将别名映射到词典规范名
            canonical_name, ticker, verified = normalize_entity_name(raw_name, entity_dict)
            # 如果LLM返回了ticker优先用LLM的，否则用词典里的
            entity_ticker = e.get("ticker") or ticker
            
            key = (canonical_name, entity_type)
            if key in seen_entities:
                continue
            seen_entities.add(key)

            # 过滤规则：
            # 1. product 类型且未验证：跳过，不建实体页
            # 2. company 类型但未验证且没有ticker（非上市公司）：跳过，产品/一般公司不建实体页
            # 3. person/index 类型：保留
            if not verified:
                if entity_type == "product":
                    continue
                if entity_type == "company" and not entity_ticker:
                    # 未验证且无ticker的公司，大概率是产品/普通公司，不建独立实体页
                    result.review_reasons.append(f"跳过未验证无ticker实体: {canonical_name}")
                    continue

            result.entities.append(ExtractedEntity(
                name=canonical_name,
                type=entity_type,
                role=e.get("role", "mentioned"),
                confidence=e.get("confidence", "medium"),
                verified=verified,
                ticker=entity_ticker,
                aliases_found=e.get("aliases_found", []) + ([raw_name] if raw_name != canonical_name else [])
            ))

        for c in data.get("concepts", []):
            # 概念关联实体也做别名归一化
            related_raw = c.get("entities_related", [])
            related_normalized = []
            seen_related = set()
            for e_name in related_raw:
                canonical, _, _ = normalize_entity_name(e_name, entity_dict)
                if canonical not in seen_related:
                    related_normalized.append(canonical)
                    seen_related.add(canonical)
            
            result.concepts.append(ExtractedConcept(
                name=c.get("name", ""),
                definition=c.get("definition", ""),
                role=c.get("role", "related"),
                confidence=c.get("confidence", "medium"),
                entities_related=related_normalized
            ))

        for s in data.get("signals", []):
            # 信号关联实体也做归一化
            raw_entity = s.get("entity", "")
            canonical_entity, _, _ = normalize_entity_name(raw_entity, entity_dict)
            
            result.signals.append(ExtractedSignal(
                entity=canonical_entity,
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
            verified_mark = "✓" if e.verified else "?"
            print(f"  [{verified_mark}] {e.name} ({e.type}, {e.role}, {e.confidence})")

        print(f"\nConcepts ({len(result.concepts)}):")
        for c in result.concepts:
            print(f"  - {c.name}: {c.definition[:50]}...")

        print(f"\nSignals ({len(result.signals)}):")
        for s in result.signals:
            print(f"  - [{s.direction}] {s.entity}: {s.summary}")

        print(f"\nClaims ({len(result.claims)}):")
        for c in result.claims[:3]:
            print(f"  - {c.statement[:60]}...")
