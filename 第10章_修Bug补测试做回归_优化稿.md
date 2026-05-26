# 第 10 章 场景二：修 Bug、补测试、做回归

修 Bug 是最日常也最考验功力的开发工作。它不只是“让错误消失”，还要理解根因、约束修改范围、用测试锁定正确行为，并确认没有引入新的问题。Codex 在这个场景里的价值，不是替你随手改几行代码，而是把“复现 -> 定位 -> 修复 -> 验证”这条链路变得更清楚、更可控。

上一章讲的是如何接手陌生代码库，重点在于建立地图和边界。到了这一章，我们进入更具体的修改场景：问题已经出现，日志或反馈已经摆在面前，接下来要做的是把它变成一个可复现、可修复、可回归验证的工程闭环。

本章会围绕四件事展开：先把错误上下文整理成结构化 Bug 报告，再约束修改范围防止“顺手重构”，然后讨论 AI 生成测试如何从表面达标走向真正可靠，最后把复现测试、回归测试和 CI 串成一个稳定闭环。

## 10.1 复现问题：从错误日志到结构化 Bug 报告

Bug 修复的第一步是理解问题，而理解的前提是获得足够的错误上下文。一个完整的错误上下文通常包含六类信息：错误信息、触发条件、环境信息、期望行为、实际行为、频率和影响范围。工程师处理 Bug 时，最大的时间消耗往往不是“定位代码”，而是“收集上下文”。把 Codex 当作一个需要上下文的同事：你给它的信息越结构化，它定位根因越快。

### 10.1.1 不要只贴日志，要整理成报告

假设你收到下面这个生产错误。代码清单 10-1 展示了原始日志的典型形态：信息很关键，但如果直接丢给 Codex，它仍然需要先从文本里抽取问题要素。

**代码清单 10-1：缺少 `intensity` 字段导致的 KeyError 日志**

```text
[2026-03-15 14:32:07.891] ERROR [uvicorn.access] Exception in ASGI application
  File "backend/services/chat_service.py", line 142, in _chat_with_memory
    emotion_intensity = emotion_result["intensity"]
KeyError: 'intensity'
```

更高效的做法，是把日志整理成结构化 Bug 报告。表 10-1 给出一个最小模板。它的作用是把“错误发生了”转成“可以开始定位”的任务输入。

**表 10-1：结构化 Bug 报告的六个要素**

| 要素 | 示例 |
| --- | --- |
| 错误信息 | `KeyError: 'intensity'` |
| 触发位置 | `backend/services/chat_service.py:142` |
| 触发条件 | 首次创建会话或情绪分析返回不完整 |
| 期望行为 | 即使缺少字段，也能返回默认情绪强度 |
| 实际行为 | 直接访问字典键，导致请求失败 |
| 影响范围 | 影响聊天主流程，需确认是否必现 |

有了这份报告，你就可以让 Codex 沿着四个问题追查：第 142 行做了什么，`emotion_result` 从哪里来，为什么会缺少 `intensity`，从 Router 到 KeyError 的完整数据流是什么。

### 10.1.2 让 Codex 沿调用栈追数据流

Codex 擅长沿着调用栈追溯数据流。对于上面的 Bug，它应该建立出一条类似图 10-1 的路径：路由接收请求，服务层处理聊天，情绪分析服务返回字典，调用方直接读取字段，最终在缺少键时抛出异常。

**图 10-1：从聊天请求到 KeyError 的数据流**

[drawio 源文件：图10-1_聊天请求到KeyError的数据流.drawio](figures/图10-1_聊天请求到KeyError的数据流.drawio)

这个分析的重点不是让 Codex 给出一个听起来合理的解释，而是把解释绑定到真实文件、真实函数和真实调用链上。如果日志信息不足，比如堆栈被截断、异步错误只指向 `await` 链、第三方库内部错误遮住了业务代码，就让 Codex 主动补充上下文：查找 `emotion_service.analyze()` 的完整实现、LLM 返回格式定义、其他调用方如何处理返回值。

### 10.1.3 复现测试是后续修复的锚点

定位根因之后，不要立刻改代码。更稳的做法是先生成一个会失败的复现测试，作为后续修复的验证基准。代码清单 10-2 展示了一个简化测试：用 monkeypatch 模拟情绪分析服务返回缺少 `intensity` 的结果。

**代码清单 10-2：用复现测试锁定缺失字段问题**

```python
@pytest.mark.asyncio
async def test_chat_uses_default_intensity_when_emotion_result_is_partial(chat_service, chat_request):
    async def fake_analyze(*args, **kwargs):
        return {"emotion": "sad"}

    chat_service.emotion_service.analyze = fake_analyze

    response = await chat_service.chat(chat_request)

    assert response.emotion == "sad"
    assert response.emotion_intensity == 0.5
```

图 10-2 展示了 Bug 修复验证闭环。这个闭环后面还会反复出现：先让问题可复现，再修复，再用同一个测试证明问题消失，最后跑相关回归测试确认没有引入新问题。

**图 10-2：Bug 修复验证闭环**

```mermaid
flowchart LR
    A["结构化 Bug 报告"] --> B["复现测试失败"]
    B --> C["约束范围后修复"]
    C --> D["复现测试通过"]
    D --> E["相关回归测试通过"]
    E --> F["提交说明和风险摘要"]
```

## 10.2 约束修改范围：防止“顺手”重构

一个常见的 Bug 修复陷阱，是“顺便”做了很多改动：给所有方法添加类型注解、重构算法、添加日志、升级依赖。单独看都合理，放在一起就是大爆炸式提交，审查难度高，回滚风险大。

约束 Codex 的修改范围，核心是把“必须修改”和“禁止修改”说清楚。对于上面的 KeyError，可以指定：必须修改 `emotion_service.py` 和 `chat_service.py`，前者确保返回格式完整，后者安全访问字典键；禁止修改其他文件；新增代码风格必须与现有代码一致。

### 10.2.1 最小修复应该是原子的

每个 Bug 修复都应该是原子的：独立完成一个完整修复逻辑，不依赖其他未提交修改。代码清单 10-3 展示了一个最小 diff。它同时在源头补齐返回格式，并在调用方做防御性兜底。

**代码清单 10-3：缺失字段问题的最小修复 diff**

```diff
diff --git a/backend/services/emotion_service.py b/backend/services/emotion_service.py
  result = self._call_llm(messages)
+ result.setdefault("emotion", "neutral")
+ result.setdefault("intensity", 0.5)
  return result

diff --git a/backend/services/chat_service.py b/backend/services/chat_service.py
- emotion_intensity = emotion_result["intensity"]
+ emotion_intensity = emotion_result.get("intensity", 0.5)
```

这类修复的好处，是 reviewer 很容易判断意图：源头保证契约，调用方兜底异常。它没有顺手重构情绪分析模块，也没有把无关日志、类型注解和依赖升级混进同一个 PR。

### 10.2.2 给 Codex 的修复指令要同时包含边界和验证

表 10-2 给出一个修复前指令模板。它不是 prompt 技巧，而是降低越界风险的工程约束。

**表 10-2：Bug 修复前的范围约束模板**

| 指令要素 | 示例 |
| --- | --- |
| 必须修改 | `emotion_service.py`、`chat_service.py` |
| 禁止修改 | 不改路由、不改数据库、不改前端 |
| 复现测试 | 先新增会失败的测试，再修复 |
| 验证命令 | `pytest tests/test_chat_service.py -q` |
| 输出要求 | 展示 diff，说明风险和未改动范围 |

几个实用技巧值得固定下来：先写会失败的复现测试，再写修复；限定文件列表，杜绝 Codex 修改其他文件；让 Codex 先展示 diff 预检，你审核后再落地。这样做不是为了拖慢修复，而是为了让修复从一开始就保持可审查。

## 10.3 AI 生成测试：从表面达标到真正可靠

Codex 能快速生成测试代码，但自动生成测试有一个常见问题：看起来能过，维护性却很差。测试间相互依赖，数据硬编码，只覆盖 happy path，Mock 过度变成“测 Mock”，描述模糊无法充当行为文档。第 10.3 节要处理的，不是“能不能生成测试”，而是“生成的测试是否真的能保护行为”。

判断 AI 生成测试是否可靠，可以从四个角度入手：它是否清楚描述了行为，是否用合适的 Fake 替代过度 Mock，是否有足够强的质量度量，以及是否能根据影响范围选择该跑哪些回归测试。

### 10.3.1 好测试要能说明行为

一个典型的自动生成测试可能长得像代码清单 10-4。它能跑，但几乎不能说明任何行为。

**代码清单 10-4：表面达标但价值很低的测试**

```python
def test_chat():
    service = ChatService()
    result = service.chat("hello", "user1", None)
    assert result is not None
```

问题一目了然：没有描述具体行为，输入数据缺少语义，只断言结果不为空，也没有覆盖边界情况。更好的测试应该遵循 AAA 模式（Arrange、Act、Assert），命名使用 `test_<expected>_when_<condition>` 格式，用 fixture 隔离测试环境，并覆盖正常路径和边界情况。

代码清单 10-5 展示了一个更可靠的测试写法。它不只是让覆盖率增加，而是在描述业务行为。

**代码清单 10-5：用 AAA 模式描述聊天服务行为**

```python
class TestChatServiceChat:
    @pytest.mark.asyncio
    async def test_returns_valid_response_when_valid_message(self, chat_service, valid_chat_request):
        # Arrange
        chat_service.emotion_service.analyze = AsyncMock(
            return_value={"emotion": "sad", "intensity": 0.7}
        )

        # Act
        response = await chat_service.chat(valid_chat_request)

        # Assert
        assert isinstance(response, ChatResponse)
        assert response.emotion == "sad"

    @pytest.mark.asyncio
    async def test_raises_value_error_when_empty_message(self, chat_service):
        request = ChatRequest(message="", user_id="user_001")

        with pytest.raises(ValueError, match="消息不能为空"):
            await chat_service.chat(request)
```

表 10-3 可以作为 AI 生成测试的质量检查表。它比“有没有测试”更重要。

**表 10-3：AI 生成测试的质量检查表**

| 检查项 | 不合格信号 |
| --- | --- |
| 测试名称是否说明行为 | `test_chat`、`test_case_1` 这类名称 |
| 是否覆盖正常路径和边界路径 | 只测 happy path |
| 是否断言关键业务结果 | 只写 `assert result is not None` |
| 是否独立运行 | 测试间依赖顺序或共享状态 |
| 是否只测试公开行为 | 直接测试私有方法，重构时容易碎 |

自动生成测试还有一个容易被忽视的隐患：测试套件会随着时间逐步劣化。每次任务都让 Codex 顺手补一点测试，如果没有边界，几个月后测试目录里可能堆满慢、脆、重复、和当前行为关系不大的用例。防止这种劣化，需要同时建立微观和宏观两层防护栏。

表 10-4 把这两层防护栏放在一起。微观层关注单个测试写法是否健康，宏观层关注整个测试套件是否仍然可维护。

**表 10-4：防止测试套件劣化的两层防护栏**

| 层级 | 应该禁止什么 | 更稳的做法 |
| --- | --- | --- |
| 微观层 | 单元测试中调用 `subprocess` | 测迁移逻辑本身，而不是调用外部命令 |
| 微观层 | 硬编码绝对路径 | 使用 `tmp_path` 等 fixture |
| 微观层 | 直接测试私有方法 | 测公开行为，避免重构时测试跟着碎 |
| 宏观层 | 生成与当前任务无关的推测性测试 | 只补能解释当前风险的测试 |
| 宏观层 | 为了让测试通过而修改被测代码 | 先确认测试是否合理，再改实现 |
| 宏观层 | 测试互相依赖或整体过慢 | 每个测试可独立运行，单元测试保持快速反馈 |

### 10.3.2 用 Fake 替代过度 Mock

传统测试常依赖 `patch` 和 `Mock()` 隔离依赖，但 Mock 有几个硬伤：路径容易随重构失效，类型不安全，过度 Mock 会让测试只验证“Mock 被调用”，而不是验证业务行为。对于稳定依赖，更好的选择是 Fake：一个预构建的内存实现，遵循与真实实现相同的接口，运行快，也更接近真实交互。

代码清单 10-6 展示了一个简化的 Fake LLM 客户端。它保留调用历史，也能返回预设响应，适合验证业务逻辑。

**代码清单 10-6：用于测试的 Fake LLM 客户端**

```python
class FakeLLMClient:
    def __init__(self, responses: Optional[list[dict]] = None):
        self._responses = responses or [{"emotion": "neutral", "intensity": 0.5}]
        self.call_history: list[dict] = []

    async def chat(self, messages: list[dict]) -> dict:
        response = self._responses.pop(0)
        self.call_history.append({"messages": messages, "response": response})
        return response
```

图 10-3 展示了更适合 AI 时代的测试分层：业务逻辑测试应该占主体，Fake 基础设施、集成冒烟、纯单元和全链路测试按需补充。它不是要推翻测试金字塔，而是提醒读者：不要让自动生成测试默认走向过度 Mock。

**图 10-3：AI 时代的测试金字塔（基于 Fake 而非过度 Mock）**

[drawio 源文件：图10-3_AI时代的测试金字塔.drawio](figures/图10-3_AI时代的测试金字塔.drawio)

### 10.3.3 覆盖率不是金标准

代码覆盖率有价值，但它不是测试质量的金标准。AI 生成测试尤其容易制造“覆盖率很好看，但断言很弱”的假象。更可靠的思路，是用变异测试、属性测试和人工审查共同判断测试是否真的能发现错误。

表 10-5 把三种质量度量放在一起。它的作用是帮助读者从“有没有跑过”转向“能不能发现问题”。

**表 10-5：测试质量的三类度量**

| 度量方式 | 解决什么问题 | 适用场景 |
| --- | --- | --- |
| 覆盖率 | 哪些代码被执行过 | 找未覆盖区域 |
| 变异测试 | 测试能否发现逻辑被破坏 | 评估断言强弱 |
| 属性测试 | 是否满足一组不变量 | 输入空间大、边界多的函数 |

代码清单 10-7 展示了变异测试的基本输出。真正值得看的不是覆盖率数字，而是哪些变异存活了下来。存活变异往往说明断言不够强，或者某条分支并没有被有效验证。

**代码清单 10-7：变异测试输出示例**

```text
$ mutmut run --paths-to-mutate=backend/services --tests-dir=tests/
Generated 124 mutants ...
98 killed
18 survived
6 timeout

$ mutmut results
$ mutmut show 47
```

按代码清单 10-7 的结果计算，变异得分可以写成 `killed / (killed + survived)`，也就是 `98 / (98 + 18) ≈ 84%`。这个数字比行覆盖率更接近测试是否真的能发现错误：`killed` 说明测试捕捉到了被故意破坏的逻辑，`survived` 则说明某些逻辑即使被改坏，现有测试也没有察觉。实操时不要只看总分，而要把存活的 18 个变异逐个用 `mutmut show` 展开，看它们对应的是断言过弱、分支未覆盖，还是业务规则本身没有被表达清楚。至于 `timeout`，它不应被简单算作通过或失败，而应该单独排查：有时是测试太慢，有时是变异触发了死循环或等待路径。

图 10-4 用三个项目对比了行覆盖率和变异得分。它要表达的不是“覆盖率没有意义”，而是覆盖率只能说明代码被执行过，不能说明断言是否能抓住错误。项目 A 的行覆盖率很高，但变异得分很低，说明测试大概率只是跑过代码；项目 C 的变异得分更高，才更接近“测试能发现问题”。

**图 10-4：行覆盖率与变异得分的对比**

[drawio 源文件：图10-4_行覆盖率与变异得分对比.drawio](figures/图10-4_行覆盖率与变异得分对比.drawio)

这也是为什么 AI 生成测试不能只追求“生成了多少”和“覆盖了多少”。更有效的做法，是把反馈继续喂回测试生成过程：先让测试能编译和运行，再让静态分析发现明显问题，最后用变异测试检查断言强度。GitHub Next 的 TestPilot 和后续一些反馈循环研究都说明，迭代式反馈比一次性生成更容易得到可用测试；但对工程团队来说，真正要落地的不是某个论文数字，而是把“生成测试之后还要验证测试”变成固定流程。

### 10.3.4 基于属性的测试：从枚举示例到验证不变量

基于属性的测试把关注点从具体示例转向不变量。以评分校验函数为例，传统测试通常枚举几个边界值；基于属性的测试（Property-Based Testing，简称 PBT）则描述一条更一般的性质：对任意 `1` 到 `5` 之间的整数，`validate_rating` 必须返回 `True`；对此范围以外的任意整数，必须返回 `False`。

Hypothesis 是 Python 生态中常用的基于属性的测试库。它会按照输入生成策略自动生成大量输入，并在发现失败用例时尝试把输入收缩到更小、更容易理解的反例。对 Codex 用户来说，这类测试的价值不只是“多跑一些输入”，而是把测试目标从“我想到的几个例子”提升为“这段业务逻辑必须始终满足什么性质”。这也解释了为什么一些大语言模型代码生成研究会把基于属性的测试当作反馈机制：属性比完整实现更抽象，更适合用来约束生成结果。

代码清单 10-8 对比了两种写法。前者只覆盖有限输入；后者让 Hypothesis 自动探索输入空间，并围绕“不变量”组织断言。

**代码清单 10-8：从示例驱动测试到属性测试**

```python
def test_rating_boundaries():
    assert service.validate_rating(1) is True
    assert service.validate_rating(5) is True
    assert service.validate_rating(0) is False


from hypothesis import given, strategies as st

@given(st.integers())
def test_rating_always_within_bounds(rating):
    result = service.validate_rating(rating)

    assert result in (True, False)
    if 1 <= rating <= 5:
        assert result is True
    else:
        assert result is False
```

### 10.3.5 测试影响分析：先跑最相关的测试

完整回归测试可能需要数十分钟，但大多数 PR 只影响代码的一小部分。测试影响分析的目标，是根据代码变更与测试用例的关系，只运行最可能受影响的测试。对 Codex 来说，这类分析很适合自动化：它可以读取 diff，找出直接修改文件、调用方、相关路由和测试文件，再给出建议测试集合。

更稳的做法，是让 Codex 同时参考三类信息：第一，当前 diff 修改了哪些文件、函数和路由；第二，这些文件的调用方和被调用方有哪些；第三，历史上哪些测试与这些模块一起失败过。这样得到的不是“少跑测试”的借口，而是一份可解释的优先级列表。PR 阶段可以先跑高相关测试，合并前、夜间任务或发布前仍然保留全量回归。

图 10-5 展示了测试影响分析的基本流程。它要解决的不是“永远不跑全量测试”，而是让 PR 级反馈更快，把全量测试留给更合适的节点。

**图 10-5：测试影响分析的基本流程**

[drawio 源文件：图10-5_测试影响分析的基本流程.drawio](figures/图10-5_测试影响分析的基本流程.drawio)

## 10.4 验证闭环：复现、修复与回归

一个严谨的 Bug 修复流程应该形成闭环：Bug 报告 -> 复现测试失败 -> 修复代码 -> 复现测试通过 -> 回归测试通过。Codex 可以自动执行大部分步骤，但你需要在关键节点介入确认。

### 10.4.1 把闭环写成可复用指令

代码清单 10-9 给出一个可复用的 Bug 修复指令模板。它把前面几节讲过的结构化报告、范围约束、复现测试和验证要求串到一起。

**代码清单 10-9：Bug 修复闭环的 Codex 指令模板**

```text
任务：修复以下 Bug，并保持最小修改范围。

错误信息：
- KeyError: 'intensity'
- 位置：backend/services/chat_service.py:142

要求：
1. 先生成一个会失败的复现测试。
2. 只修改必要文件，不做顺手重构。
3. 修复后运行复现测试，确认由失败变为通过。
4. 运行相关回归测试。
5. 输出 diff 摘要、已跑验证和剩余风险。
```

表 10-6 把闭环中的人工确认点列出来。它提醒读者：自动化可以推进步骤，但关键判断仍然要有人接住。

**表 10-6：Bug 修复闭环中的人工确认点**

| 节点 | 人要确认什么 |
| --- | --- |
| 复现测试失败 | 测试确实复现了目标 Bug，而不是造了另一个问题 |
| 修复 diff | 修改范围是否最小，是否有无关重构 |
| 复现测试通过 | 是否由本次修复导致通过 |
| 回归测试通过 | 失败是否与本次修改相关 |
| 提交前摘要 | 风险和未覆盖范围是否说清楚 |

### 10.4.2 用 git bisect 和 Codex 反查引入点

有些 Bug 不是“现在怎么修”这么简单，还需要回答“到底是哪次提交引入的”。当问题在某个版本之后突然出现，但没人能确定具体 commit 时，`git bisect` 很适合和 Codex 配合使用：Git 负责二分，测试脚本负责判断 good / bad，Codex 负责解读最终定位到的那个 commit。

代码清单 10-10 给出一个最小自动化脚本。脚本本身不需要让 Codex 参与每一步判断；更稳的方式是让可重复的测试脚本先完成二分，等定位到首个 bad commit 后，再让 Codex 在只读沙箱里解释 diff、分析根因并给出最小修复建议。

**代码清单 10-10：用 git bisect 定位引入 Bug 的提交**

```bash
cat > bisect_check.sh <<'SH'
#!/bin/bash
set -e
pytest tests/test_emotion_intensity_bug.py -x -q
SH

chmod +x bisect_check.sh
git bisect start HEAD v1.4.0
git bisect run ./bisect_check.sh
git bisect reset

codex exec --sandbox read-only \
  "读 commit <SHA> 的 diff，分析为什么引入 KeyError: 'intensity'，输出最小修复建议"
```

这类流程的关键，是把“判定是否复现”写成稳定脚本。只要脚本能可靠返回成功或失败，二分过程就可以自动收敛；Codex 的价值主要体现在解释最终 commit、整理因果链和生成修复建议上，而不是替代测试脚本做主观判断。

### 10.4.3 回归测试要分层

有效的回归测试需要分层：单元测试验证被修改模块的独立行为，集成测试验证模块间交互，端到端测试验证完整链路，快照测试防止 API 响应结构被意外改变。每层成本和收益不同。单元测试最快但覆盖面窄，端到端测试最慢但最接近真实场景。

表 10-7 给出一个简单分层。它的重点不是要求每次都跑全量，而是帮助 Codex 根据修改影响范围选择合适的验证层级。

**表 10-7：回归测试的分层策略**

| 测试层级 | 主要验证什么 | 什么时候优先运行 |
| --- | --- | --- |
| 单元测试 | 被修改函数或服务的局部行为 | 小范围逻辑修改 |
| 集成测试 | 模块间交互和数据流 | 修改服务层、数据库或 API |
| 端到端测试 | 用户主流程 | 修改跨前后端链路 |
| 快照测试 | API 响应结构 | 对外契约可能变化时 |
| 契约测试 | 前后端对接口格式的共同理解 | API 被多个消费者依赖时 |

### 10.4.4 契约测试是 API 的防断裂保险

快照测试能检测响应体结构变化，但无法证明前后端对 API 契约的理解是否一致。契约测试填补了这个空白：由消费者定义“我期望的接口格式”，提供者在 CI 中验证“我实际提供的接口是否满足消费者期望”。

对 Codex 用户来说，一个实用做法是让 Codex 基于 FastAPI 自动生成的 OpenAPI 规范生成契约测试。图 10-6 展示了这种验证链路：先做 Schema 验证，再做契约一致性验证，然后检查破坏性变更，最后补充语义正确性验证。

**图 10-6：基于 OpenAPI 的契约测试链路**

[drawio 源文件：图10-6_OpenAPI契约测试链路.drawio](figures/图10-6_OpenAPI契约测试链路.drawio)

回归测试套件不是一劳永逸的。功能移除后，对应测试也应删除；每次修 Bug 后，复现测试应纳入回归套件；测试套件变慢时，要分析执行时间分布，并决定是否并行化、分层运行或使用测试影响分析。

## 本章小结

Bug 修复最怕的不是慢，而是不精确：没有精确复现，就容易修错问题；没有约束修改范围，就容易把一次修复扩成一次重构；没有验证闭环，就很难判断问题是真的消失，还是被暂时遮住。

本章从一个 `KeyError: 'intensity'` 出发，把 Codex 放进完整的修复流程中：先把原始日志整理成结构化 Bug 报告，再沿调用栈追数据流，接着用失败测试锁定问题，用最小修改完成修复，最后通过回归测试、变异测试、基于属性的测试、契约测试和必要时的 `git bisect`，确认修复是否可靠。

真正要带走的不是某一种测试工具，而是一条工作原则：让 Codex 帮你加速定位和执行，但不要把判断外包出去。复现是否准确、修改是否越界、断言是否有力、回归范围是否足够，这些关键判断仍然需要人来确认。只有这样，Bug 修复才不会停留在“把报错消掉”，而会变成一条可复用、可审查、可交接的工程闭环。

下一章会进入更复杂的开发场景：当任务不只是修一个 bug，而是跨前后端完成一个新功能时，Codex 应该怎样帮助你拆分接口、控制变更范围，并把实现、测试和验证串成一条可审查的交付链路。
