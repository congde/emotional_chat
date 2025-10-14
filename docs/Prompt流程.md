# "心语"情感陪伴机器人 - 系统流程图

## 主流程图

```mermaid
flowchart TD
    Start([用户发送消息]) --> Input[接收用户输入]
    Input --> Validate{输入验证与安全检查}
    
    %% 安全检查分支
    Validate --> CheckCrisis{检查危机内容?<br/>自杀/自残等关键词}
    CheckCrisis -->|是| CrisisResponse[返回危机应对<br/>提供心理援助热线]
    CheckCrisis -->|否| CheckIntimate{检查亲密关系?<br/>表白/恋爱等关键词}
    
    CheckIntimate -->|是| IntimateResponse[返回边界设定<br/>说明AI身份局限]
    CheckIntimate -->|否| CheckSensitive{检查敏感话题?<br/>政治/宗教/性}
    
    CheckSensitive -->|是| SensitiveResponse[婉拒敏感话题<br/>引导回情感支持]
    CheckSensitive -->|否| BuildPrompt[构建完整Prompt]
    
    %% 正常流程
    BuildPrompt --> GetMemory[检索长期记忆<br/>向量数据库]
    GetMemory --> GetHistory[获取对话历史<br/>短期上下文]
    GetHistory --> CombinePrompt[组合系统Prompt<br/>记忆+历史+输入]
    
    CombinePrompt --> Generate[AI生成响应]
    Generate --> ResponseFlow[响应流程检查]
    
    %% 响应流程
    ResponseFlow --> Step1[第一步：共情<br/>识别并命名情绪]
    Step1 --> Step2[第二步：理解<br/>表达支持与认可]
    Step2 --> Step3[第三步：提问<br/>开放式问题引导]
    
    Step3 --> FormatCheck{格式检查}
    FormatCheck -->|符合要求| Output[输出响应<br/>3-4句话/口语化]
    FormatCheck -->|不符合| Reformat[重新格式化<br/>避免专业术语]
    Reformat --> Output
    
    %% 所有响应汇总
    CrisisResponse --> End([返回给用户])
    IntimateResponse --> End
    SensitiveResponse --> End
    Output --> SaveMemory[保存对话到记忆]
    SaveMemory --> End
    
    %% 样式设置
    classDef crisis fill:#ff6b6b,stroke:#c92a2a,color:#fff
    classDef intimate fill:#ffa94d,stroke:#e67700,color:#fff
    classDef sensitive fill:#ffd43b,stroke:#fab005,color:#000
    classDef normal fill:#51cf66,stroke:#2f9e44,color:#fff
    classDef process fill:#74c0fc,stroke:#1971c2,color:#fff
    
    class CrisisResponse,CheckCrisis crisis
    class IntimateResponse,CheckIntimate intimate
    class SensitiveResponse,CheckSensitive sensitive
    class Output,End normal
    class BuildPrompt,CombinePrompt,Generate,ResponseFlow process
```

## 响应流程详解

```mermaid
flowchart LR
    Input[用户输入] --> Emotion[第一步：共情<br/>识别情绪]
    Emotion --> Support[第二步：理解<br/>表达支持]
    Support --> Question[第三步：提问<br/>开放式引导]
    
    Emotion -.示例.-> E1["听起来你很焦虑"]
    Support -.示例.-> S1["这确实不容易"]
    Question -.示例.-> Q1["你愿意多说一点吗？"]
    
    style Emotion fill:#e3f2fd,stroke:#1976d2
    style Support fill:#f3e5f5,stroke:#7b1fa2
    style Question fill:#e8f5e9,stroke:#388e3c
```

## 安全检查优先级

```mermaid
flowchart TD
    Input[用户输入] --> P1{优先级1<br/>危机检查}
    P1 -->|检测到| Stop1[立即返回<br/>危机应对]
    P1 -->|通过| P2{优先级2<br/>亲密关系检查}
    P2 -->|检测到| Stop2[立即返回<br/>边界设定]
    P2 -->|通过| P3{优先级3<br/>敏感话题检查}
    P3 -->|检测到| Stop3[立即返回<br/>婉拒引导]
    P3 -->|通过| Safe[安全输入<br/>继续处理]
    
    style Stop1 fill:#ff6b6b,stroke:#c92a2a,color:#fff
    style Stop2 fill:#ffa94d,stroke:#e67700,color:#fff
    style Stop3 fill:#ffd43b,stroke:#fab005,color:#000
    style Safe fill:#51cf66,stroke:#2f9e44,color:#fff
```

## Prompt构建流程

```mermaid
flowchart LR
    A[系统Prompt<br/>角色+目标+准则] --> Combine[组合]
    B[长期记忆<br/>向量数据库检索] --> Combine
    C[对话历史<br/>短期上下文] --> Combine
    D[用户输入<br/>当前消息] --> Combine
    
    Combine --> Template[对话模板]
    Template --> Final[完整Prompt]
    
    style A fill:#e3f2fd,stroke:#1976d2
    style B fill:#f3e5f5,stroke:#7b1fa2
    style C fill:#fff9c4,stroke:#f9a825
    style D fill:#ffccbc,stroke:#d84315
    style Final fill:#c8e6c9,stroke:#388e3c
```

## 关键组件说明

| 组件 | 功能 | 关键词示例 |
|------|------|-----------|
| 危机检测 | 识别自杀/自残倾向 | 自杀、轻生、不想活了、割腕、跳楼 |
| 亲密关系检测 | 识别情感越界 | 爱上你、表白、做我女朋友、约会 |
| 敏感话题检测 | 识别不适当话题 | 政治、宗教、性生活 |
| 响应流程 | 三步法生成回应 | 共情 → 理解 → 提问 |
| 格式控制 | 确保输出质量 | 3-4句话、口语化、无专业术语 |

## 系统特点

1. **安全第一**：三层安全检查机制，确保用户安全
2. **温暖陪伴**：三步响应流程，营造安全倾诉空间
3. **边界清晰**：明确AI身份，不越界提供专业建议
4. **记忆增强**：结合长短期记忆，提供连贯体验
5. **格式规范**：统一输出标准，保持一致体验

