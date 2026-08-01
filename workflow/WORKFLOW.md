# End-to-End Content Workflow

这套 Workflow 把一个模糊想法变成可发布的竖屏口播视频。它不是“一键生成”，而是让每个阶段都有明确输入、输出和人工检查点。

## 总览

```text
模糊想法
  ↓
xhs-post-writer：播种 → 发芽 → 成长
  ↓
人工确认 V1
  ↓
xhs-5d-review：五维修剪
  ↓
人工确认终稿
  ↓
竖屏拍摄 + 字幕
  ↓
HyperFrames 透明信息动画
  ↓
FFmpeg 人物原声合成
  ↓
ffprobe 成片验收
```

人只保留三个核心判断：

1. 讲什么。
2. 选择哪个观点。
3. 最终能不能发。

## 0. 环境

必需：

- 支持 `SKILL.md` 的 Agent 环境。
- Python 3.9+。
- FFmpeg 与 ffprobe。

可选：

- 剪映：生成字幕和做最终人工包装。
- HyperFrames：渲染 HTML 信息动画。

安装两个 Skill：

```bash
mkdir -p .trae/skills
cp -R skills/xhs-post-writer .trae/skills/
cp -R skills/xhs-5d-review .trae/skills/
```

检查视频工具：

```bash
python3 tools/verify_video.py --help
python3 tools/compose_video.py --help
```

## 1. 播种

输入：一个模糊选题、真实经历和想表达的情绪。

示例：

```text
开始播种：找不到真正热爱的事情，就去看手机相册。
```

输出：清晰的核心命题。此阶段不直接写终稿。

## 2. 发芽

输入：播种阶段确认的核心命题。

示例：

```text
开始发芽。
```

输出：五个机制不同的跨领域视角，每个视角包含事实、关联和 Aha。用户选择其中一至两个。

## 3. 成长

输入：用户选中的视角。

示例：

```text
选择 02 和 03，开始成长。
```

输出：可直接朗读的完整口播稿 V1。

硬检查点：必须先向用户完整展示 V1。未获得明确批准前，不写入文件，不进入审核。

如果内容用于介绍产品、Workflow、Skill 或教程，成长阶段还要检查以下销售链路没有被压缩掉：

```text
目标痛点 → 明确结果 → 真实证据 → 降低门槛 → 可信机制
→ 价值确认后再给免费/开源 → 明确领取动作
```

展示不等于采用。标题、正文和分镜只有在用户明确批准后，才能写入文件或进入视频生产。

## 4. 修剪

输入：用户已经确认的 V1。

示例：

```text
开始 5D Review。
```

输出五张独立表格：

1. 核心逻辑。
2. 结构逻辑。
3. AI 味。
4. 标题 Hook。
5. 共鸣传播。

每个问题必须包含完整原句、诊断、改句 A、改句 B 和亮点保留。用户决定采用哪些建议。

## 5. 拍摄与分镜

复制 `templates/storyboard.md`，逐句填写时间、人物画面、截图、动画和剪辑方式。

默认竖屏规范：

- 1080×1920，30fps。
- 人物占视觉权重约 70%，动画约 30%。
- 人脸保护区固定在人物所在一侧。
- 全屏动画仅用于证据、数据和关键机制，单次不超过 2.5 秒。
- 同一时刻只保留一个视觉主角。

拍摄时：

- 每个段落前后保留 0.5 秒。
- 同一机位录正常语速和快 10% 两遍。
- 第一帧直接开口，不加片头。
- 结尾说完后看镜头 1 秒。

## 6. 字幕

推荐做法：将口播素材导入剪映，使用自动识别字幕，再人工校对专有名词、英文和数字。

字幕与 HTML 信息动画职责不同：

- 字幕负责逐句可读。
- 信息动画只强调证据、概念和关系。
- 不要让动画重复整句字幕。

## 7. HyperFrames 透明动画

复制模板：

```bash
cp -R templates/hyperframes-overlay my-overlay
cd my-overlay
```

编辑 `index.html` 中的时间、文案和场景。模板默认：

- 1080×1920。
- 背景透明。
- 信息卡位于左侧。
- 右侧是人物保护区。
- 使用确定性的 `fromTo()` 时间线。

检查并渲染：

```bash
npx hyperframes lint
npx hyperframes check
npx hyperframes snapshot . --at 0,2,6,11.5
npx hyperframes render --output overlay.webm --fps 30
```

如果本地环境无法输出带透明通道的 WebM，也可以先输出普通视频，再根据项目需要使用抠像或其他透明视频方案。

## 8. 人物原声合成

将透明动画覆盖到人物视频：

```bash
python3 tools/compose_video.py \
  --base talking-head.mp4 \
  --overlay overlay.webm \
  --output final.mp4
```

默认行为：

- 保留原人物视频。
- 优先保留原音频。
- 输出 H.264、yuv420p、faststart MP4。
- 动画从左上角 `(0, 0)` 覆盖。
- 以较短轨道结束，避免输出黑帧。

如需移动覆盖层：

```bash
python3 tools/compose_video.py \
  --base talking-head.mp4 \
  --overlay overlay.webm \
  --output final.mp4 \
  --x 60 \
  --y 120
```

## 9. 成片验收

```bash
python3 tools/verify_video.py \
  --video final.mp4 \
  --expect-width 1080 \
  --expect-height 1920 \
  --expect-fps 30 \
  --require-audio
```

验收项：

- 文件可完整解码。
- 分辨率与帧率正确。
- 存在视频流和音频流。
- 时长符合口播素材。
- 人脸未被信息卡遮挡。
- 前两秒已经兑现标题承诺。

## 10. 发布后复盘

至少记录：

- 2 秒跳出率。
- 5 秒留存。
- 平均播放时长。
- 平均播放占比。
- 完播率。
- 点赞、评论、收藏和分享。

不要用一次播放量判断内容价值。先判断观众在哪一秒离开，再回到 Hook、承诺兑现和画面层级定位问题。
