"""
Validator: 数据验证层

规则:
1. 格式验证（严格）: 必填字段缺失 → 拒绝写入
2. 业务规则（警告）: 别名重复、概念去重 → 标记警告，不阻断
3. 质量评分: 计算综合质量分
"""

import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional

import yaml

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    field: str
    message: str
    severity: str  # error / warning


@dataclass
class ValidationResult:
    valid: bool  # 是否通过格式验证
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    quality_score: float = 0.0


class SourceValidator:
    """来源页验证器"""

    REQUIRED_FIELDS = ["title", "url", "date", "author"]

    def validate(self, frontmatter: dict, body: str = "") -> ValidationResult:
        result = ValidationResult(valid=True)

        # 1. 必填字段检查
        for field in self.REQUIRED_FIELDS:
            if field not in frontmatter or not frontmatter[field]:
                result.errors.append(ValidationError(
                    field=field,
                    message=f"必填字段缺失: {field}",
                    severity="error",
                ))

        # 2. 信号完整性检查
        if "signals" in frontmatter:
            if not isinstance(frontmatter["signals"], list):
                result.errors.append(ValidationError(
                    field="signals",
                    message="signals 必须是列表",
                    severity="error",
                ))
            else:
                for i, s in enumerate(frontmatter["signals"]):
                    if "direction" not in s:
                        result.errors.append(ValidationError(
                            field=f"signals[{i}].direction",
                            message="信号缺少 direction 字段",
                            severity="error",
                        ))
                    elif s["direction"] not in ["positive", "negative", "neutral"]:
                        result.warnings.append(ValidationError(
                            field=f"signals[{i}].direction",
                            message=f"未知方向: {s['direction']}",
                            severity="warning",
                        ))

        # 3. 质量评分合理性
        quality = frontmatter.get("quality_score", 0)
        if quality < 0 or quality > 1:
            result.errors.append(ValidationError(
                field="quality_score",
                message=f"quality_score 超出范围 [0,1]: {quality}",
                severity="error",
            ))

        if result.errors:
            result.valid = False

        result.quality_score = self._calculate_quality(frontmatter, result)
        return result

    def _calculate_quality(self, frontmatter: dict, result: ValidationResult) -> float:
        base_score = frontmatter.get("quality_score", 0)
        penalty = len(result.errors) * 0.3 + len(result.warnings) * 0.1
        signals = frontmatter.get("signals", [])
        if signals:
            complete = sum(1 for s in signals if s.get("quote") and s.get("summary") and s.get("direction"))
            bonus = (complete / len(signals)) * 0.1
        else:
            bonus = 0
        return round(max(0, min(1, base_score - penalty + bonus)), 2)


class EntityValidator:
    """实体页验证器"""

    def validate(self, frontmatter: dict, all_entities: dict = None) -> ValidationResult:
        result = ValidationResult(valid=True)

        if "name" not in frontmatter or not frontmatter["name"]:
            result.errors.append(ValidationError(
                field="name", message="实体名缺失", severity="error",
            ))

        valid_types = ["company", "person", "product", "index", "fund", "investor"]
        entity_type = frontmatter.get("type", "company")
        if entity_type not in valid_types:
            result.warnings.append(ValidationError(
                field="type", message=f"未知实体类型: {entity_type}", severity="warning",
            ))

        aliases = frontmatter.get("aliases", [])
        if len(aliases) != len(set(aliases)):
            result.warnings.append(ValidationError(
                field="aliases", message="别名列表有重复", severity="warning",
            ))

        if all_entities:
            entity_name = frontmatter.get("name", "")
            for other_name, other_data in all_entities.items():
                if other_name == entity_name:
                    continue
                common = set(aliases) & set(other_data.get("aliases", []))
                if common:
                    result.warnings.append(ValidationError(
                        field="aliases",
                        message=f"与实体 '{other_name}' 别名冲突: {common}",
                        severity="warning",
                    ))

        if result.errors:
            result.valid = False
        return result


class ConceptValidator:
    """概念页验证器"""

    def validate(self, frontmatter: dict, all_concepts: dict = None) -> ValidationResult:
        result = ValidationResult(valid=True)

        if "name" not in frontmatter or not frontmatter["name"]:
            result.errors.append(ValidationError(
                field="name", message="概念名缺失", severity="error",
            ))

        definition = frontmatter.get("definition", "")
        if not definition or len(definition) < 10:
            result.warnings.append(ValidationError(
                field="definition", message="概念定义过短或缺失", severity="warning",
            ))

        # 宏观概念允许无实体关联
        entities = frontmatter.get("entities", [])
        if not entities:
            macro_keywords = ["通胀", "供给", "产业链", "行业", "周期", "宏观", "政策"]
            concept_name = frontmatter.get("name", "")
            is_macro = any(kw in concept_name for kw in macro_keywords)
            if not is_macro:
                result.warnings.append(ValidationError(
                    field="entities", message="概念未关联任何实体", severity="warning",
                ))

        if all_concepts:
            concept_name = frontmatter.get("name", "")
            for other_name in all_concepts.keys():
                if other_name == concept_name:
                    continue
                similarity = self._name_similarity(concept_name, other_name)
                if similarity > 0.85:
                    result.warnings.append(ValidationError(
                        field="name",
                        message=f"与概念 '{other_name}' 名字相似度 {similarity:.2f}",
                        severity="warning",
                    ))

        if result.errors:
            result.valid = False
        return result

    def _name_similarity(self, name1: str, name2: str) -> float:
        if name1 in name2 or name2 in name1:
            return 0.9
        len1, len2 = len(name1), len(name2)
        if len1 == 0 or len2 == 0:
            return 0.0
        common = len(set(name1) & set(name2))
        return common / max(len1, len2)


class KnowledgeValidator:
    """知识库全局验证器"""

    def __init__(self, knowledge_dir: str):
        self.knowledge_dir = knowledge_dir
        self.source_validator = SourceValidator()
        self.entity_validator = EntityValidator()
        self.concept_validator = ConceptValidator()

    def validate_all(self) -> dict:
        from pathlib import Path
        results = {
            "sources": [], "entities": [], "concepts": [],
            "summary": {"total_errors": 0, "total_warnings": 0, "valid_sources": 0, "invalid_sources": 0}
        }

        all_entities, all_concepts = {}, {}

        entities_dir = Path(self.knowledge_dir) / "entities"
        for f in entities_dir.glob("*.md"):
            fm = self._parse_frontmatter(f)
            if fm:
                all_entities[fm.get("name", f.stem)] = fm

        concepts_dir = Path(self.knowledge_dir) / "concepts"
        for f in concepts_dir.glob("*.md"):
            fm = self._parse_frontmatter(f)
            if fm:
                all_concepts[fm.get("name", f.stem)] = fm

        sources_dir = Path(self.knowledge_dir) / "sources"
        for f in sources_dir.glob("*.md"):
            fm = self._parse_frontmatter(f)
            if fm:
                r = self.source_validator.validate(fm)
                results["sources"].append({
                    "file": f.name, "valid": r.valid,
                    "errors": [e.__dict__ for e in r.errors],
                    "warnings": [w.__dict__ for w in r.warnings],
                    "quality_score": r.quality_score,
                })
                results["summary"]["total_errors"] += len(r.errors)
                results["summary"]["total_warnings"] += len(r.warnings)
                if r.valid:
                    results["summary"]["valid_sources"] += 1
                else:
                    results["summary"]["invalid_sources"] += 1

        for name, fm in all_entities.items():
            r = self.entity_validator.validate(fm, all_entities)
            results["entities"].append({
                "name": name, "valid": r.valid,
                "errors": [e.__dict__ for e in r.errors],
                "warnings": [w.__dict__ for w in r.warnings],
            })
            results["summary"]["total_errors"] += len(r.errors)
            results["summary"]["total_warnings"] += len(r.warnings)

        for name, fm in all_concepts.items():
            r = self.concept_validator.validate(fm, all_concepts)
            results["concepts"].append({
                "name": name, "valid": r.valid,
                "errors": [e.__dict__ for e in r.errors],
                "warnings": [w.__dict__ for w in r.warnings],
            })
            results["summary"]["total_errors"] += len(r.errors)
            results["summary"]["total_warnings"] += len(r.warnings)

        return results

    def _parse_frontmatter(self, filepath) -> Optional[dict]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if match:
                return yaml.safe_load(match.group(1)) or {}
        except Exception as e:
            logger.warning("Failed to parse frontmatter in %s: %s", filepath, e)
        return None


if __name__ == "__main__":
    import json, os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    knowledge_dir = os.path.join(base_dir, "knowledge")

    print(f"Validating knowledge base: {knowledge_dir}")
    validator = KnowledgeValidator(knowledge_dir)
    results = validator.validate_all()

    print(f"\n{'='*60}")
    print("VALIDATION SUMMARY")
    print(f"{'='*60}")
    print(f"Sources: {len(results['sources'])} ({results['summary']['valid_sources']} valid)")
    print(f"Entities: {len(results['entities'])}")
    print(f"Concepts: {len(results['concepts'])}")
    print(f"Total Errors: {results['summary']['total_errors']}")
    print(f"Total Warnings: {results['summary']['total_warnings']}")

    for source in results["sources"]:
        if source["errors"] or source["warnings"]:
            print(f"\n📄 {source['file']}")
            for e in source["errors"]: print(f"  ❌ [{e['severity']}] {e['field']}: {e['message']}")
            for w in source["warnings"]: print(f"  ⚠️  [{w['severity']}] {w['field']}: {w['message']}")
