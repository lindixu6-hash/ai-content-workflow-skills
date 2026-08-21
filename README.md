# Content OS Pipeline

[![Agent Readiness](https://github.com/lindixu6-hash/ai-content-workflow-skills/actions/workflows/agent-readiness.yml/badge.svg)](https://github.com/lindixu6-hash/ai-content-workflow-skills/actions/workflows/agent-readiness.yml)

把一个模糊选题变成经过诊断的完整初稿，同时保留创作者的判断权。

```text
播种（输入） → 发芽 → 成长（给初稿） → 修剪（dbs-content）
     人确认       人选择芽          人确认初稿          人选择改法
```

这不是“一句话生成终稿”的提示词合集。它是一条有状态、有人工门、有证据约束的内容生产管线。

## 为什么做

普通 AI 写作容易把四件事混在一次回答里：找角度、补经历、搭结构、改文风。结果通常完整，但不像任何一个具体的人。

Content OS 把任务拆开：

- **播种**只确认写什么、写给谁、看完发生什么变化。
- **发芽**寻找五个因果机制不同的角度，第五个固定为佛学/玄学视角。
- **成长**把真实经历、内容策略和所选角度写成完整 V1。
- **修剪**调用 `dbs-content` 做诊断，不擅自替创作者重写。

## 四阶段

### 1. 播种（输入）

输入一个选题，得到目标人群、状态变化和核心冲突。

```text
使用 content-os-pipeline。
播种：我让 AI 帮我买了三件衣服，每件都很喜欢。
```

### 2. 发芽

生成五张机制不同的芽，第五张固定为佛学/玄学视角。每张包含可核验事实、与选题的关联和一句 Aha。用户自己选择，不由 AI 决定主线。

```text
发芽。
```

### 3. 成长（给初稿）

系统补足真实经历，在内部完成小红书编导，再一次性交付完整初稿 V1。真实经历和编导报告不会变成额外页面节点。

```text
选择第 2 张芽，成长。
我的真实经历是：……
```

### 4. 修剪

用户看过 V1 后，系统路由到 dontbesilent 的 `dbs-content`，从文字洁癖、封面/标题、表达效率、认知落差和 AI 辅助五个维度诊断。

```text
修剪。重点看开头和 AI 味。
```

修剪只给诊断和第一步动作。用户确认采用哪些建议后，写作引擎才生成 V2。

## 安装

### 1. 安装本仓库

在项目根目录执行：

```bash
git clone https://github.com/lindixu6-hash/ai-content-workflow-skills.git
mkdir -p .trae/skills
cp -R ai-content-workflow-skills/skills/content-os-pipeline .trae/skills/
cp -R ai-content-workflow-skills/skills/xhs-post-writer .trae/skills/
cp -R ai-content-workflow-skills/skills/xiaohongshu-viral-director .trae/skills/
```

其他支持 `SKILL.md` 的 Agent，把这三个目录复制到对应 Skills 目录即可。

### 2. 安装修剪依赖

`dbs-content` 来自 [dontbesilent2025/dbskill](https://github.com/dontbesilent2025/dbskill)，采用 CC BY-NC 4.0 许可，因此不复制到本 MIT 仓库。

```bash
npx -y skills add dontbesilent2025/dbskill -g --all
```

### 3. 校验管线

```bash
python3 tools/validate_pipeline.py
```

成功时会输出：

```json
{
  "stages": [
    "播种（输入）",
    "发芽",
    "成长（给初稿）",
    "修剪"
  ],
  "ok": true
}
```

## Skill 架构

| Skill | 职责 | 用户是否直接调用 |
|---|---|---|
| `content-os-pipeline` | 四阶段状态机与路由 | 是，推荐入口 |
| `xhs-post-writer` | 播种、发芽、成长初稿 | 可以 |
| `xiaohongshu-viral-director` | 小红书推荐流、搜索流和收藏资产设计 | 通常由成长阶段内部调用 |
| `dbs-content` | 修剪诊断 | 外部依赖，由总控调用 |

机器可读的阶段、依赖和人工门见 [`pipeline.json`](pipeline.json)。

生产边界、工具权限、上线阻塞项与十项质量评分见
[`agent-card.json`](agent-card.json)。CI 使用
[Agent Production Readiness Gate](https://github.com/lindixu6-hash/awesome-agentic-engineering)
验证最低上线分数，并独立运行 `draft-only` 风险 Profile 审计。当前 12/20
评分能通过项目设置的 10/20 兼容门槛，但由于总分不足且仍有 3 个显式上线阻塞项，
风险 Profile 会按预期失败；这两个结论不会互相覆盖。

## 关键约束

1. 一次只推进一个阶段。
2. AI 不替用户选择芽。
3. 真实经历不编造、不扩写成不存在的人生故事。
4. 标题和编导不额外占据流程节点。
5. 初稿必须完整展示，才能进入修剪。
6. 修剪不自动重写，采用哪些建议由用户决定。
7. 展示不等于写入，只有用户明确说“保存”才修改文件。
8. 私人语料、公司内部材料和未脱敏证据不进入公共仓库。

## 仓库结构

```text
.
├── pipeline.json
├── skills/
│   ├── content-os-pipeline/
│   ├── xhs-post-writer/
│   └── xiaohongshu-viral-director/
├── workflow/
│   └── WORKFLOW.md
├── templates/
└── tools/
    ├── validate_pipeline.py
    ├── compose_video.py
    └── verify_video.py
```

`templates/` 和视频工具是初稿之后的可选制作资产，不改变四阶段内容管线。

## License

本仓库代码和自有 Skills 使用 MIT License。

外部 `dbs-content` 不包含在本仓库中，其版权和许可归原项目所有。
