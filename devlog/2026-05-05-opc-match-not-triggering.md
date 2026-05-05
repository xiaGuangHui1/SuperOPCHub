# Bug 复盘：AI 对话一直追问不推荐 OPC

**日期：** 2026-05-05
**严重程度：** P0 — 核心功能不可用
**影响范围：** `/api/chat` 对话接口，OPC 匹配推荐完全失效
**相关 commits：** `8483f3c`, `dd2deab`, `6bfa4c5`

---

## 现象

用户在 Super OPC Hub 的 AI 对话框中发送需求后，AI 不仅不推荐接单的 OPC（一人公司），反而不断追问细节。无论对话多少轮，都无法触发 OPC 匹配和推荐。

## 根因链分析

匹配不触发的链路中有 **5 个独立 bug** 叠加：

### Bug 1: `is_complete` 完全依赖 LLM 判断（最致命）

**文件：** `api/models/schemas.py:44` + `api/main.py:95`

```python
class DemandProfileOut(BaseModel):
    is_complete: bool = False  # 默认 False
```

`is_complete` 的默认值是 `False`。虽然 `EXTRACTION_SYSTEM` 提示词要求 LLM 在 `project_type` 非空时设为 `True`，但 LLM（尤其是 DeepSeek 等小模型）经常**漏掉**这个字段赋值。结果：

```
LLM 成功提取 project_type="AI客服" → 但忘记设置 is_complete=True
→ is_complete 保持默认 False → 匹配逻辑被跳过
→ AI 收到"暂无匹配结果" → 部分模型倾向追问
```

**修复：** 在 `api/main.py:93` 添加代码兜底：

```python
demand_profile.is_complete = bool(demand_profile.project_type)
```

### Bug 2: 提取 prompt 缺少"财务系统"类别

**文件：** `api/services/prompting.py:13`

旧 prompt 列举的 `project_type` 示例缺少"财务系统"：

```
旧: （如"网站建设""AI客服""小程序开发""品牌设计""数据看板""跨境电商""短视频"）
```

但前端建议按钮包含"想让财务对账自动完成"，种子数据也有 10 个财务类 OPC 画像。用户点击该按钮后，LLM 没有"财务系统"这个类别引导，可能映射到不相关的类别。

**修复：** 改为显式枚举全部 7 个支持类别：

```
新: 必须从下列类别中选一个最匹配的：AI客服、跨境电商、数据看板、品牌设计、财务系统、小程序开发、短视频
```

### Bug 3: 匹配搜索文本缺少 `skills_required`

**文件：** `api/services/matching.py:25-32`

LLM 提取了精确的技能关键词（如 `["AI客服系统", "自然语言处理"]`），但匹配引擎构建搜索文本时只用了 `project_type + description + industry`，**丢弃了技能需求**。这是 LLM 提供的最精准匹配信号。

**修复：** 搜索文本中加入 `skills_required`：

```python
if demand.skills_required:
    search_parts.append(" ".join(demand.skills_required))
```

### Bug 4: 中文关键词匹配因空格失效

**文件：** `api/services/matching.py:80-110`

匹配算法对中文关键词做精确子串匹配。但 OPC 画像中的角色包含空格（如 `"AI 客服系统架构师"`），而 LLM 提取的类别不含空格（`"AI客服"`），导致：

```
"AI客服" in "AI 客服系统架构师" → False  （中间有空格）
```

**修复：** 增加去空格匹配策略：

```python
# 去空格后再匹配
opc_no_space = opc_text.replace(" ", "")
if word_no_space in opc_no_space:  # "AI客服" in "AI客服系统架构师" → True
    hits += 0.8
```

同时增加 3 字子串匹配，提高中文词组精度。

### Bug 5: OPC 画像字段 null 导致 TypeError

**文件：** `api/services/matching.py:40-46`

数据库中部分 OPC 画像的 `description` 或 `skills` 为 `null`（而非空字符串），`str.join()` 直接抛 `TypeError`：

```python
opc_text = " ".join([
    p.get("role", ""),
    p.get("description", ""),  # 若为 None, .get 返回 None, join 崩溃
    p.get("skills", ""),       # 同上
])
```

**修复：** 统一使用 `or ""` 兜底：

```python
opc_text = " ".join([
    p.get("role") or "",
    p.get("description") or "",
    p.get("skills") or "",
])
```

---

## 修复后测试结果

使用 `deepseek-chat` 模型端到端测试：

| 输入 | project_type | 匹配分数 | AI 回复 |
|------|-------------|---------|---------|
| 想用AI接住所有客户咨询 | AI客服 | 55-60% | 直接推荐 OPC |
| 想把产品卖到海外去 | 跨境电商 | 55-65% | 直接推荐 OPC |
| 想让财务对账自动完成 | 财务系统 | 73-93% | 直接推荐 OPC |
| 想做一个官网展示我的产品 | 网站建设 | 45% | 直接推荐 OPC |
| 想在微信里把生意做起来 | 小程序开发 | 70-85% | 直接推荐 OPC |

**所有场景均在第一轮对话直接推荐 OPC，不再追问。**

---

## 附带修复

- **数据库去重：** 旧版种子脚本（7 个画像）与新版（70 个画像）同时存在，导致 5 组重复 OPC，已软删除清理。
- **日志补全：** `api/main.py` 添加了每次请求的完整跟踪日志（用户输入 → 提取结果 → 匹配分数 → AI 回复），线下可直接查看 `/tmp/opc-api.log`。
- **demand_profiles 表补列：** 新建 `api/migrations/004_demand_profiles_add_columns.sql`，补全 `project_scope`、`industry`、`collaboration_mode` 等缺失列。

---

## 教训

1. **LLM 返回的 boolean 标志不可信。** 凡是能通过现有数据推导的字段，绝不让 LLM 来设。`is_complete` 应该完全由 `bool(project_type)` 决定。
2. **提示词中的类别枚举必须与实际数据对齐。** 前端按钮、种子数据、提取 prompt、匹配关键词四者必须严格一致，缺一不可。
3. **数据库 nullable 字段必须在代码层兜底。** 任何 `str.join()` 或字符串操作前，都应 `or ""` 处理 null 值。
4. **中文文本匹配必须考虑空格。** OPC 画像中的角色/描述常含空格（"AI 客服系统架构师"），但用户输入和 LLM 提取结果不含空格（"AI客服"），匹配算法必须先去空格再比较。
