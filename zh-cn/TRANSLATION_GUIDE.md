# 卡尔曼滤波教程中文翻译规范

本目录是《Kalman and Bayesian Filters in Python》的中文版。翻译由大模型完成，不使用机器翻译 API。

## 目录结构

```
zh-cn/
├── TRANSLATION_GUIDE.md      # 本文件：翻译规范
├── NOTEBOOK_STATUS.md        # 各 notebook 翻译进度
├── README.md                 # 中文版说明
├── nb_translate_utils.py     # 翻译辅助脚本
├── book_format.py            # 原书样式（不修改）
├── kf_book/                  # 原书代码库（不修改）
├── figs/                     # 图片资源（不修改）
├── experiments/*.py          # 实验脚本（不修改）
├── table_of_contents.ipynb   # 目录
├── 00-Preface.ipynb …        # 正文章节
├── Appendix-*.ipynb          # 附录
├── animations/               # 动画 notebook
├── Supporting_Notebooks/     # 辅助 notebook
└── experiments/              # 实验 notebook
```

## 翻译范围

| 单元格类型 | 是否翻译 | 说明 |
|-----------|---------|------|
| `markdown` | ✅ 翻译 | 正文、标题、说明文字 |
| `code` | ❌ 不改动 | 代码、注释、字符串均保持原样 |
| `raw` | ❌ 不改动 | LaTeX 目录命令等 |
| `output` | ❌ 不改动 | 执行输出保持原样 |

## 核心原则

### 1. 代码不动

所有 `code` 单元格逐字符保持与英文原版一致，包括：

- `import` 语句
- 变量名、函数名
- 字符串字面量（含 `print` 输出）
- 注释

### 2. 公式不动

所有 LaTeX 数学公式保持原样，不翻译、不改写：

- 行内公式 `$...$`
- 独立公式 `$$...$$`
- `aligned`、`begin/end` 等环境
- 公式中的符号、变量名

### 3. 关键术语：中英文并存

**数学名词、专业术语首次出现或重要出现处，必须保留英文，并附中文释义。**

推荐格式（任选一种，全书保持一致）：

- `卡尔曼滤波（Kalman filter）`
- `Kalman filter（卡尔曼滤波）`
- `扩展卡尔曼滤波（Extended Kalman Filter, EKF）`

**必须双语呈现的常见术语（示例，非穷尽）：**

| 英文 | 中文 |
|------|------|
| Kalman filter | 卡尔曼滤波 |
| Bayesian / Bayes filter | 贝叶斯 / 贝叶斯滤波 |
| Bayes' theorem | 贝叶斯定理 |
| Gaussian | 高斯（分布） |
| covariance | 协方差 |
| state / state vector | 状态 / 状态向量 |
| measurement | 测量 |
| process noise | 过程噪声 |
| measurement noise | 测量噪声 |
| prior / posterior | 先验 / 后验 |
| likelihood | 似然 |
| probability density function (PDF) | 概率密度函数 |
| Extended Kalman Filter (EKF) | 扩展卡尔曼滤波 |
| Unscented Kalman Filter (UKF) | 无迹卡尔曼滤波 |
| Particle filter | 粒子滤波 |
| g-h filter / α-β filter | g-h 滤波 / α-β 滤波 |
| smoothing | 平滑 |
| prediction / update | 预测 / 更新 |
| residual / innovation | 残差 / 新息 |
| Jacobian | 雅可比（矩阵） |
| Monte Carlo | 蒙特卡洛 |
| nonlinear | 非线性 |
| multimodal | 多模态 |
| sensor fusion | 传感器融合 |
| least squares | 最小二乘 |
| H-infinity filter | H∞ 滤波 |
| ensemble Kalman filter | 集总卡尔曼滤波 |

同一术语在章节内再次出现时，可仅用中文或仅用英文，但**章节首次出现必须有双语**。

### 4. 必须用英文保留、不翻译的内容

- 人名：Rudolf Emil Kálmán、Allen Downey 等
- 库名/包名：NumPy、SciPy、SymPy、matplotlib、FilterPy、Jupyter、IPython
- 文件名、路径、URL、GitHub 链接
- 代码块（` ``` ` 内全部内容）
- 行内代码（`` `...` `` 内全部内容）
- HTML 标签结构（可翻译标签内的可见文字）
- 已在公式中的符号

### 5. 讲解性文字：全中文

除上述术语外，叙述、解释、例题说明、章节导言等**全部译为通顺的中文**。

## 具体操作步骤（子任务执行）

对每个 notebook：

1. **复制**：从仓库根目录复制对应 `.ipynb` 到 `zh-cn/` 同路径
   ```bash
   cp ../table_of_contents.ipynb .
   # 或
   python3 nb_translate_utils.py copy table_of_contents.ipynb
   ```

2. **仅改 markdown**：用 `nb_translate_utils.py` 或手动编辑，只修改 `cell_type == "markdown"` 的 `source`

3. **检查**：
   - [ ] 所有 code 单元格与原版一致
   - [ ] 公式未被改动
   - [ ] 关键术语有中英文
   - [ ] 内部链接路径未改（如 `./01-g-h-filter.ipynb`）
   - [ ] 无机器翻译痕迹、无乱码占位符

4. **更新进度**：在 `NOTEBOOK_STATUS.md` 中将对应项标为 `done`

5. **可选冒烟测试**（主章节）：
   ```bash
   cd /workspace/zh-cn
   jupyter nbconvert --to notebook --execute <notebook>.ipynb --output /tmp/test.ipynb
   ```

## 标题翻译参考

| 英文 | 中文 |
|------|------|
| Preface | 前言 |
| Table of Contents | 目录 |
| Chapter N: ... | 第 N 章：... |
| Appendix A: ... | 附录 A：... |
| Supporting Notebooks | 辅助 Notebook |

## 禁止事项

- ❌ 使用 Google Translate 等机器翻译 API
- ❌ 修改 code / raw / output 单元格
- ❌ 翻译或改写 LaTeX 公式
- ❌ 删除英文专业术语
- ❌ 修改 `kf_book/`、`book_format.py` 等运行依赖

## 运行环境

在 `zh-cn/` 目录下启动 Jupyter，依赖与原版相同：

```bash
cd zh-cn
pip install -r requirements.txt
jupyter notebook
```

Notebook 通过 `import book_format` 和 `from kf_book import ...` 引用同目录下的支持库，路径与原版一致。
