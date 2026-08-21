---
name: "content-os-pipeline"
description: "把一个自媒体选题按播种、发芽、成长、修剪四阶段推进。用户提到 Content OS、内容生产管线、从选题到初稿或修剪时调用。"
---

# Content OS Pipeline

这是仓库的总控 Skill。固定流程只有四段：

`播种（输入） → 发芽 → 成长（给初稿） → 修剪（dbs-content）`

## 路由

| 阶段 | 执行器 | 用户可见输出 | 人工门 |
|---|---|---|---|
| 播种 | `xhs-post-writer` | 选题、人群、变化、冲突 | 用户确认输入 |
| 发芽 | `xhs-post-writer` | 五张机制不同的芽，第五张固定为佛学/玄学视角 | 用户选择芽 |
| 成长 | `xhs-post-writer`，小红书时内部调用 `xiaohongshu-viral-director` | 完整初稿 V1 | 用户确认初稿 |
| 修剪 | 外部 `dbs-content` | 内容创作诊断报告 | 用户决定是否采用 |

## 状态机

一次只允许一个阶段处于进行中。

```text
seeded = false
sprouts_selected = false
draft_generated = false
trim_completed = false
```

合法迁移：

```text
输入选题
  -> seeded
用户说“发芽”
  -> 展示五张芽，第五张为佛学/玄学视角
用户选择芽并说“成长”
  -> 补足真实经历并输出完整初稿 V1
用户说“修剪”
  -> 调用 dbs-content 诊断
```

禁止：

- 播种后直接生成初稿。
- AI 替用户选择芽。
- 把真实经历拆成第五个页面节点。
- 把标题选择或编导报告拆成额外可见节点。
- 初稿未展示就进入修剪。
- 修剪阶段自动重写全文。

## 阶段一至三

完整读取并执行：

`../xhs-post-writer/SKILL.md`

小红书成长阶段由写作 Skill 内部读取：

`../xiaohongshu-viral-director/SKILL.md`

## 阶段四｜修剪

修剪只在用户看过完整初稿，并明确说“修剪、诊断、用 dbs-content 看看”后触发。

调用外部 `dbs-content`：

1. 将原始选题、所选芽和最新完整初稿一起交给 `dbs-content`。
2. 要求它按文字洁癖、封面/标题、表达效率、认知落差、AI辅助五维诊断。
3. 它只诊断，不代写，不自动修改文件。
4. 输出推荐形式、推荐平台、五维判断、第一步动作和一句话总结。
5. 等用户明确选择建议后，才由 `xhs-post-writer` 生成 V2。

如果当前环境没有安装 `dbs-content`，停止修剪并提示：

```bash
npx -y skills add dontbesilent2025/dbskill -g --all
```

不要假装已经调用。

## 修剪输入

```text
选题：
所选芽：
真实经历：
最新初稿：
用户特别关注的问题：
```

## 修剪输出

遵循 `dbs-content` 自己的固定报告结构。报告之后只问：

> 哪些诊断需要采用？你确认后我再生成 V2。

## 保存规则

- 所有阶段先在对话中展示。
- 用户明确说“保存、采用、写入”后才能修改文件。
- 默认只保存用户确认的稿件，不把诊断报告混入正文。
- 不保存用户隐私、账号、公司内部材料或未脱敏证据到公共仓库。
