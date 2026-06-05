# -*- coding: utf-8 -*-
"""08-Designing-Kalman-Filters.ipynb markdown 译文（第 2 部分）"""

TRANSLATIONS_08_PART2 = {
96: """`kinematic_kf` 是什么？`filterpy.common` 的 `kinematic_kf` 可创建任意维数与阶数的线性运动学（kinematic）滤波。本书不用它，因希望你大量练习创建卡尔曼滤波。此处仅为缩短示例并让你接触库的这一部分。

回到主题。可见估计跳了 3.4 km，预测（先验 prior）与测量误差超过 7 km。

如何避免？首先想到检查先验是否远离测量。为何先验而非当前估计？因为 update 后估计可能已接近坏测量（本例并非如此）。

注意：本可写 `prior[0:2] - z` 得误差，我用数学上正确的 $\\mathbf z - \\mathbf{Hx}$ 仅为说明。KalmanFilter 类在 `KalmanFilter.y` 存**新息（innovation）**。此处用 `kf.y` 代替上面计算的值以作说明：

""",

98: """本例测量距预测位置近 7 km。听起来「远」？若单位是千米、更新率 1 秒，意味着超过 25000 kph，不可能。若单位厘米、epoch 1 分钟，则可能 absurdly 小。

可加检查，考虑飞机性能极限：

```
vel = y / dt
if vel >= MIN_AC_VELOCITY and vel <= MAX_AC_VELOCITY:
    kf.update()
```
 
你认为合理且稳健吗？继续读前先尽量列出反对意见。


这不令我满意。 suppose 刚用猜测位置初始化滤波，会丢弃好测量且永远无法开始滤波。其次，忽略传感器与过程误差的知识。卡尔曼滤波在 $\\mathbf P$ 中维护当前精度。若 $\\mathbf P$ 暗示 $\\sigma_x = 10$ 米，而测量远 1 km，显然坏测量——距先验约 100 标准差。

绘制 $\\mathbf P$，画第一、二、三标准差。

""",

100: "前面章节 $\\mathbf P$ 是圆而非椭圆。代码中设 $\\mathbf R = \\bigl[ \\begin{smallmatrix}0.03 & 0 \\\\ 0 & 0.15\\end{smallmatrix}\\bigl ]$，使 $y$ 测量误差为 $x$ 的 5 倍。 有些人为，但后续章节协方差多为椭圆，有充分理由。\n\n这意味着什么？统计学说 99% 测量落在 3 标准差内；即 99% 应在此椭圆内。绘制测量与椭圆。\n",

102: """显然测量远超先验协方差；我们可能视为坏测量而不使用。如何做？

第一个想法是提取 $x$、$y$ 标准差写简单 if。这里用 `KalmanFilter` 的 `residual_of` 计算相对先验的残差。本例不必，因 `update()` 已赋值 `kf.y`；若丢弃测量则尚未 `update()`，`kf.y` 仍是上一 epoch 的新息。

介绍两个术语。我们在讨论**门控（gating）**。**门（gate）**是判断测量好坏的公式或算法。只有好测量通过门。此过程叫门控。

实践中测量非纯高斯，3 标准差门可能丢弃好测量。稍后详述；暂用 4 标准差

""",

104: "可见误差约 39 与 18 标准差。够吗？\n\n也许。但注意 if 形成包围椭圆的矩形区域。下图我画了一个 clearly 在 3 std 椭圆外却会被门接受、以及恰在 3 std 边界上的测量。\n",

106: "定义门还有别的方法。**马氏距离（mahalanobis distance）**是点到分布的统计距离。先看定义与数学，计算一些点的马氏距离。`filterpy.stats` 实现 `mahalanobis()`。\n",

108: "不知单位时，可与分别计算的 x、y 标准差误差 39、18 比较，可见相当接近。看上面所画点的值。\n",

110: """如将见，马氏距离计算点到分布的标量标准差*距离*，类似欧氏距离计算点到点标量距离。

上面单元格印证：3 std 边界上的点马氏距离 3.0，椭圆外为 3.6 std。

如何计算？定义为

$$D_m= \\sqrt{(\\mathbf x-\\mu)^\\mathsf T \\mathbf S^{-1} (\\mathbf x-\\mu)}$$

与欧氏距离很相似：

$$D_e= \\sqrt{(\\mathbf x-\\mathbf y)^\\mathsf T (\\mathbf x-\\mathbf y)}$$

若协方差 $\\mathbf S$ 为单位矩阵，马氏距离即欧氏距离。线性代数上：单位矩阵的逆仍为单位矩阵， effectively 各项乘 1。直观：若各维标准差为 1，均值周围半径 1 的圆上任意点在 1 std 圆上，欧氏距离也为 1 *单位*。

这 suggest 另一种解释。若协方差矩阵对角，马氏距离可视为*缩放*的欧氏距离，每项除以对角协方差。

$$D_m = \\sqrt{\\sum_{i-1}^N \\frac{(x_i - \\mu_i)^2}{\\sigma_i}}$$

二维为

$$D_m = \\sqrt {\\frac{1}{\\sigma_x^2}(x_0 - x_1)^2 + \\frac{1}{\\sigma_y^2}(y_0 - y_1)^2}$$

这应帮助理解马氏距离方程。不能除以矩阵，但乘逆* effectively* 相同（ 粗略）。两侧乘差 $\\mathbf y = \\mathbf x - \\mathbf \\mu$ 得协方差缩放的平方范数：$\\mathbf y^\\mathsf T \\mathbf S^{-1}\\mathbf y^\\mathsf T$。协方差项均平方，最后开方得标量距离，即协方差缩放的欧氏距离。

""",

111: """### 门控与数据关联策略（Gating and Data Association Strategies）

上面两门在文献中有时称矩形门与椭球门。还有更多替代，此处不展开。例如**机动门（maneuver gate）**定义物体可能机动的区域，考虑当前速度与机动能力。战斗机机动门似沿当前飞行方向延伸的锥；汽车为前方较窄的二维扇形；船更窄，因转向、加速能力 minimal。

该用哪种门控？无单一答案。取决于问题维数与算力。矩形门计算很便宜，机动门也不差太多，椭球门高维可能昂贵。但维数增加时矩形相对椭圆外溢面积显著增大。

这比你想的更重要。每个测量有噪声。 spurious 测量可能落*在*门内，被我们接受。超出椭圆的区域越大，门接受坏测量的概率越大。此处不做数学；5 维时矩形门接受坏测量的概率约为椭圆两倍。

若算力 concern 且 spurious 测量多，可用两门：大门矩形作第一遍，丢弃明显坏测量；少数通过的再做较贵的马氏距离。现代桌面处理器矩阵乘法时间通常不 significant；嵌入式芯片浮点弱时可能 matter。

**数据关联（data association）**是需专书的 vast 主题。典型例子：雷达跟踪。每次扫描多个回波，需形成航迹并拒绝噪声测量。很难。 suppose 第一次扫描 5 个测量，建 5 条潜在航迹。第二次 6 个测量。第一次任测与第二次任测可组合，30 条潜在航迹。也可能全是新飞机，再加 6 条。几个 epoch 后潜在航迹达百万、十亿。

给定数十亿航迹列表可计分。下一节给数学。可视化：3 个 epoch 呈「Z」形的航迹，无飞机能如此机动，概率极低。另一条直线但 impute 10000 kph 速度，极 improbable。另一条 200 kph 曲线，高概率。

故跟踪是门控、数据关联与剪枝。例如第二次雷达扫描刚发生。是否把所有可能组合成航迹？ 大概不应。若 sweep1 点 1 与 sweep2 点 3 推断速度 200 kph，可成航迹；若 5000 kph 则不必——太不可能。航迹增长后对有明确定义椭球或机动门，关联测量时可更有选择性地。

有关联方案：测量只关联一条航迹；或关联多条，反映不确定属于哪条。例如雷达视角下航迹可交叉，接近时单测关联哪架不确定，可短时间赋给两条，积累测量后再按概率改分配。

「十亿」远不足以描述组合爆炸。几秒就内存耗尽，再久需宇宙所有原子表示潜在航迹。实用算法须 积极剪枝，又需额外算力。

本书后文给出现代答案——**粒子滤波（particle filter）**，用统计采样解决组合爆炸。是我偏爱的方法，故不再详述本节其他技术。我对该领域最新研究 未能完全跟上最新，若需跟踪多目标或处理多 spurious 测量请自行调研。粒子滤波也有困难与局限。

推荐几本书与研究者：Samuel S. Blackman 的 *Multiple-Target Tracking with Radar Application* 是我读过表述最清楚的（1986，dated）。Yaakov Bar-Shalom 著作很多。Subhash Challa 等 *Fundamentals of Object Tracking* 较现代，覆盖各方法；数学 rigorous，滤波器呈现为贝叶斯 formulation 的积分集合，需自行转为工作算法。若掌握本书数学可读，但不 easy。Lawrence D. Stone 的 *Bayesian Multiple Target Tracking* 亦作贝叶斯推断，也偏理论， blithely 让你求复杂积分极大值，实践中可能用粒子滤波求解。

回到简单问题——跟踪单目标、 偶发坏测量。如何实现？相当直接：测量坏则丢弃，不 call update。会连续两次 `predict()`，没问题。不确定度会增大，少数 漏掉的更新 通常无妨。

门 cutoff 用多少？我不知道。理论说 3 std，实践 otherwise。需实验：收集数据，用不同门跑滤波，看何值最好。下一节给评估性能的数学。也许发现需接受 < 4.5 std 的所有测量。我见过 NASA 视频说用约 5–6 std 门。取决于问题与数据。

""",

112: """## 评估滤波器性能（Evaluating Filter Performance）

仿真中设计卡尔曼滤波很容易：你知道过程模型注入多少噪声，故 $\\mathbf Q$  琐碎。也知道测量仿真噪声，$\\mathbf R$ 同样 琐碎。

实践中设计更 ad hoc。真实传感器 rarely 达 spec，且 rarely 完美高斯。也易受环境噪声 fool，如电路噪声引起电压波动影响传感器输出。建过程模型与噪声更难。汽车建模很难：转向非线性、轮胎 slip、急刹急加速导致 slip、风推离航线。结果是卡尔曼滤波是系统的*不精确*模型。不精确导致 次优，最坏时完全发散。

因未知量，无法解析计算滤波矩阵正确值。先做最好估计，再用广泛仿真与真实数据测试。性能评估指导矩阵修改。我们已做过——展示 $\\mathbf Q$ 过大或过小的效果。

现在看更 分析性的评估方式。若卡尔曼滤波最优，估计误差（真实状态减估计状态）应满足：

    1. 估计误差均值为零
    2. 其协方差由滤波协方差矩阵描述
    
### 归一化估计误差平方（Normalized Estimated Error Squared, NEES）

第一种方法最强大，但仅仿真可行。仿真时知真实值或「真值（ground truth）」。任一步误差为真值 ($\\mathbf x$) 与滤波状态估计 ($\\hat{\\mathbf x}$) 之差：

$$\\tilde{\\mathbf x} = \\mathbf x - \\hat{\\mathbf x}$$

定义**归一化估计误差平方（NEES）**为

$$\\epsilon = \\tilde{\\mathbf x}^\\mathsf T\\mathbf P^{-1}\\tilde{\\mathbf x}$$

理解此式：若状态维数为 1，x、P 为标量，

$$\\epsilon = \\frac{x^2}{P}$$

若不清楚，回忆标量 $a$ 时 $a^\\mathsf T = a$，$a^{-1} =\\frac{1}{a}$。

协方差矩阵越小，同样误差 NEES 越大。协方差是滤波对自身误差的估计；相对估计误差若很小，说明表现比同样误差下协方差较大时更差。

得标量结果。若 $\\mathbf x$ 维 ($n \\times 1$)，计算维 ($1 \\times n$)($n \\times n$)($n \\times 1$) = ($1 \\times 1$)。如何处理此数？

数学超出本书，但形为 $\\tilde{\\mathbf x}^\\mathsf T\\mathbf P^{-1}\\tilde{\\mathbf x}$ 的随机变量称**自由度为 n 的卡方分布（chi-squared distributed with n degrees of freedom）**，故序列期望值应为 $n$。Bar-Shalom [1] 有 精彩讨论。

 通俗地说：取所有 NEES 平均，应小于 x 的维数。用本章前面例子验证：

""",

115: """`NEES` 在 FilterPy 中实现：

```python
from filterpy.stats import NEES
```

这是 极佳的度量，应尽可能使用，尤其生产代码中需运行中评估滤波。设计阶段我仍偏好绘残差，因更直观。

若仿真保真度有限，需用其他方法。

""",

116: """### 似然函数（Likelihood Function）

统计学中**似然（likelihood）**与概率很相似， subtle 差异对我们重要。**概率（probability）**是某事发生的 chance——公平骰子五次掷出三次 6 的概率？**似然**问反问题——给定五次中三次 6，骰子公平的可能性？

我们在**离散贝叶斯（Discrete Bayes）**章首次讨论似然函数。在滤波语境下，似然衡量给定当前状态下测量有多大可能。

对我们重要：有滤波输出，想知道在**高斯（Gaussian）**噪声与线性行为假设下滤波最优的可能性。似然低说明某假设错误。在**自适应滤波（Adaptive Filtering）**章将学如何利用此信息改进滤波；此处只学如何测量。

滤波的残差与系统不确定度定义为

$$\\begin{aligned}
\\mathbf y &= \\mathbf z - \\mathbf{H \\bar x}\\\\
\\mathbf S &= \\mathbf{H\\bar{P}H}^\\mathsf T + \\mathbf R
\\end{aligned}$$

由此计算似然：

$$
\\mathcal{L} = \\frac{1}{\\sqrt{2\\pi S}}\\exp [-\\frac{1}{2}\\mathbf y^\\mathsf T\\mathbf S^{-1}\\mathbf y]
$$

看起来复杂，但指数项是高斯方程。建议实现：

```python
from scipy.stats import multivariate_normal
hx = (H @ x).flatten()
S = H @ P @ H.T  + R
likelihood = multivariate_normal.pdf(z.flatten(), mean=hx, cov=S)
```

实践中略有不同。似然数学上难处理。常计算并使用**对数似然（log-likelihood）**，即似然的自然对数。有几处好处。首先 log 严格递增，在函数取最大值处与似然同点。求函数最大值通常求导；任意函数导数可能难，但 $\\frac{d}{dx} log(f(x))$ trivial，结果同 $\\frac{d}{dx} f(x)$。本书不用此性质，但滤波分析 至关重要。

`update()` 调用时计算似然与对数似然，可通过 `log_likelihood`、`likelihood` 数据属性访问。运行滤波：若干测量在预期范围内，再注入远离预期的测量：

""",

118: "似然在前几次迭代滤波收敛时增大。之后 波动 直到坏测量，此时降至零，表明若测量有效则滤波极 unlikely 最优。\n\n看对数似然如何 鲜明地显示滤波何时「变坏」。\n",

120: "为何末尾又回零？读答案前先想。滤波开始适应新测量，将状态移近测量。残差变小，状态与残差一致。\n",

121: """## 控制输入（Control Inputs）

在**离散贝叶斯（Discrete Bayes）**章我介绍用控制信号改善滤波。不再假设物体按迄今方式继续运动，而用控制输入知识预测位置。在**一元卡尔曼滤波（Univariate Kalman Filter）**章同样使用。卡尔曼滤波的 predict 方法曾为

```python
def predict(pos, movement):
    return (pos[0] + movement[0], pos[1] + movement[1])
```

上一章学到状态预测方程：

$$\\bar{\\mathbf x} = \\mathbf{Fx} + \\mathbf{Bu}$$

状态是向量，控制输入也须为向量。此处 $\\mathbf{u}$ 为控制输入，$\\mathbf{B}$ 将控制输入转为 $\\mathbf x$ 的变化。简单例子：状态 $x = \\begin{bmatrix} x & \\dot x\\end{bmatrix}$ 为受控机器人，控制输入为指令速度：

$$\\mathbf{u} = \\begin{bmatrix}\\dot x_\\mathtt{cmd}\\end{bmatrix}$$

为简单假设机器人 instant 响应输入变化。$\\Delta t$ 秒后新位置与速度为

$$\\begin{aligned}x &= x + \\dot x_\\mathtt{cmd} \\Delta t \\\\
\\dot x &= \\dot x_\\mathtt{cmd}\\end{aligned}$$

须用 $\\bar{\\mathbf x} = \\mathbf{Fx} + \\mathbf{Bu}$ 表示。

我用 $\\mathbf{Fx}$ 项提取上式 $x$，$\\mathbf{Bu}$ 项取其余：



$$\\begin{bmatrix}x\\\\\\dot x\\end{bmatrix} = \\begin{bmatrix}1 & 0\\\\0 & 0 \\end{bmatrix}\\begin{bmatrix}x\\\\\\dot x\\end{bmatrix} +
\\begin{bmatrix}\\Delta t \\\\ 1\\end{bmatrix}\\begin{bmatrix}\\dot x_\\mathtt{cmd}\\end{bmatrix}
$$


这是简化；典型控制输入是转向角变化、加速度变化，引入非线性，后续章节学习。

卡尔曼滤波其余部分照常设计。你已见过多次，不再赘述，下面示例。

""",

123: "## 传感器融合（Sensor Fusion）\n",

124: """g-h 滤波（g-h filter）章初讨论为两个秤（一准一不准）设计滤波。我们确定应始终包含不准秤的信息——永不丢弃任何信息。考虑有两个传感器测量系统。如何纳入卡尔曼滤波？

假设铁路上有火车或台车。轮上传感器计转数，可换算轨道距离。另有类 GPS 的「位置传感器」报告位置。下一节解释为何不只写 GPS。于是有两个测量，均报告沿轨位置。设轮传感器精度 1 m，位置传感器 10 m。如何合并进一个滤波？ 有些刻意，但飞机用传感器融合融合 GPS、INS、多普勒雷达、VOR、空速指示等。

惯性系统卡尔曼滤波很难，但融合两个或多个提供同一状态变量（如位置）测量的传感器 quite easy。相关矩阵是测量矩阵 $\\mathbf H$。回忆它告诉我们如何从滤波状态 $\\mathbf x$ 得到测量 $\\mathbf z$。设卡尔曼状态含火车位置与速度：

$$ \\mathbf x = \\begin{bmatrix}x \\\\ \\dot x\\end{bmatrix}$$

有两个位置测量，测量向量为轮与位置传感器的测量：

$$ \\mathbf z = \\begin{bmatrix}z_{wheel} \\\\ z_{ps}\\end{bmatrix}$$

设计 $\\mathbf H$ 将 $\\mathbf x$ 转为 $\\mathbf z$。二者都是位置，换算只是乘 1：

$$ \\begin{bmatrix}z_{wheel} \\\\ z_{ps}\\end{bmatrix} = \\begin{bmatrix}1 &0 \\\\ 1& 0\\end{bmatrix} \\begin{bmatrix}x \\\\ \\dot x\\end{bmatrix}$$

更清楚：若轮报告转数而非位置，1 转 2 米：

$$ \\begin{bmatrix}z_{rot} \\\\ z_{ps}\\end{bmatrix} = \\begin{bmatrix}0.5 &0 \\\\ 1& 0\\end{bmatrix} \\begin{bmatrix}x \\\\ \\dot x\\end{bmatrix}$$

设计测量噪声矩阵 $\\mathbf R$。设位置测量方差为轮的两倍，轮标准差 1.5 米：

$$
\\begin{aligned}
\\sigma_{wheel} &=  1.5\\\\
\\sigma^2_{wheel} &= 2.25 \\\\ 
\\sigma_{ps} &= 1.5*2 = 3 \\\\
\\sigma^2_{ps} &= 9.
\\end{aligned}
$$

卡尔曼滤波设计 基本完成。须设计 $\\mathbf Q$，与是否融合无关，我任选 arbitrary 值。

运行仿真。假设速度 10 m/s，更新率 0.1 秒。

""",

126: """可见蓝色为卡尔曼滤波结果。

上一例直觉上可能较难理解。看不同问题：二维跟踪物体，两个不同位置的雷达。各给距离与方位。各雷达读数如何影响结果？

这是非线性问题——需三角函数从距离方位算坐标，我们尚未学非线性卡尔曼滤波。故忽略代码，只看图表。后续章节  revisit 并学如何写代码。

目标在 (100, 100)。第一雷达 (50, 50)，第二 (150, 50)。第一测方位 45°，第二 135°。

先建卡尔曼滤波，绘初始协方差。我用**无迹卡尔曼滤波（Unscented Kalman Filter, UKF）**，后续章节覆盖。

""",

128: "x、y 位置同样不确定，协方差为圆。\n\n用第一雷达读数 update。方位误差标准差 0.5$^\\circ$，距离误差标准差 3。\n",

130: "可见误差对几何的影响。雷达站在目标左下。方位测量极准 $\\sigma=0.5^\\circ$，距离不准 $\\sigma=3$。虚线绿线示雷达读数。易见准确方位与不准距离如何塑造协方差椭圆形状。\n\n现在纳入第二雷达测量。第二站在 (150,50)，目标右下。继续前，想想纳入此读数后协方差如何变化。\n",

132: """可见第二雷达测量如何改变协方差。到目标角度与第一站正交，方位与距离误差效应互换。协方差矩阵方向转向第二站，且 importantly 尺寸显著变小。

协方差 always 纳入全部可用信息，含问题几何效应。此 formulation 易看清发生什么；一传感器给位置、二传感器给速度，或两传感器都给位置，同样发生。

传感器融合是 vast 主题，我的覆盖 simplistic 到 misleading。例如 GPS 用迭代最小二乘（iterated least squares）从卫星伪距确定位置，不用卡尔曼滤波。辅助 notebook [**Iterative Least Squares for Sensor Fusion**](http://nbviewer.ipython.org/urls/raw.github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python/master/Supporting_Notebooks/Iterative-Least-Squares-for-Sensor-Fusion.ipynb) 有述。

这是 GPS 接收机常见但非唯一做法。若是爱好者，我的覆盖或许够用。商用级滤波须 very careful 设计融合过程。需专书，按领域进一步学习。

""",

133: "### 练习：能否滤波 GPS 输出？（Exercise: Can you Filter GPS outputs?）\n",

134: "上一节让你对类 GPS 传感器应用卡尔曼滤波。能否对商用卡尔曼滤波的输出再应用卡尔曼滤波？你的滤波输出会比 GPS 更好、更差还是相同？\n",

135: "#### 解答（Solution）\n",

136: """商用 GPS 内置卡尔曼滤波，输出是该滤波产生的滤波估计。 suppose 有 GPS 稳定输出流，含位置与位置误差。能否把这两数据传入自己的滤波？

那么，该数据流特性是什么？更重要的是，卡尔曼滤波输入的根本要求是什么？

卡尔曼滤波输入须*高斯*且*时间独立（time independent）*。因我们要求**马尔可夫（Markov）**性质：当前状态只依赖前一状态与当前输入。这使递推形式可能。GPS 输出*时间相关*，因当前估计基于所有先前测量的递推估计。故信号非白、非时间独立；传入卡尔曼滤波即违反数学要求。答案：不能通过对商用 GPS 输出再跑 KF 得到更好估计。

另一种想法：卡尔曼滤波在最小二乘意义下最优。对最优解再经任意滤波不可能得到「更优」——逻辑不可能。最好信号不变仍最优，或被改变则不再最优。

爱好者整合 GPS、IMU 等 off-the-shelf 传感器时常遇此困难问题。

看效果。商用 GPS 报告位置与估计误差范围，误差来自卡尔曼的 $\\mathbf P$。滤波一些带噪数据，把滤波输出作新带噪输入，看结果。即 $\\mathbf x$ 供 $\\mathbf z$，$\\mathbf P$ 供测量协方差 $\\mathbf R$。为 exaggerate 效果，演示一次与两次迭代。第二次迭代无「意义」（无人会这么做），仅为说明。先代码与图。

""",

138: """可见再处理信号的滤波输出更 smooth，但也偏离轨迹。为何？卡尔曼要求信号非时间相关。但卡尔曼输出*是*时间相关的，因纳入所有先前测量。看最后一图（2 次迭代）：测量起始于若干大于轨迹的峰。滤波「记住」（ vague 术语，避数学）物体在轨迹上方。约 13 秒测量均低于轨迹，也纳入记忆，迭代输出 far below 轨迹。

换角度看：迭代输出*不是*用 $\\mathbf z$ 作测量，而是前一卡尔曼估计的输出。故绘滤波输出对前一滤波输出。

""",

140: "希望此做法的问题现已明显。下图可见 KF 跟踪前一滤波的不完美估计，并因先前测量记忆 引入延迟。\n",

141: "### 练习：证明位置传感器改善滤波（Exercise: Prove that the position sensor improves the filter）\n",

142: "设计方法证明：融合位置传感器与轮测量优于仅用轮。\n",

143: "#### 解答 1（Solution 1）\n",

144: "强制卡尔曼忽略位置传感器测量：将其测量噪声设为近无穷。重跑滤波，观察残差标准差。\n",

146: "可见几乎完全忽略位置传感器时滤波误差大于使用它时。\n",

147: "#### 解答 2（Solution 2）\n",

148: "更费事：写只接受一个测量的卡尔曼滤波。\n",

150: "此次运行标准差 0.523，融合测量为 0.391。\n",

151: """## 非平稳过程（Nonstationary Processes）

迄今假设卡尔曼各矩阵**平稳（stationary）**——随时间不变。例如机器人跟踪设 $\\Delta t = 1.0$ 秒，状态转移矩阵为

$$
\\mathbf F = \\begin{bmatrix}1& \\Delta t& 0& 0\\\\0& 1& 0& 0\\\\0& 0& 1& \\Delta t\\\\ 0& 0& 0& 1\\end{bmatrix} = \\begin{bmatrix}1& 1& 0& 0\\\\0& 1& 0& 0\\\\0& 0& 1& 1\\\\ 0& 0& 0& 1\\end{bmatrix}$$

若数据率不可预测地变？或两传感器不同速率？测量误差变？

处理 easy：改卡尔曼矩阵反映当前情况。回到狗跟踪，假设输入 时断时续。我们设计

$$\\begin{aligned}
\\mathbf{\\bar x} &= {\\begin{bmatrix}x\\\\\\dot x\\end{bmatrix}}^- \\\\
\\mathbf F &= \\begin{bmatrix}1&\\Delta t  \\\\ 0&1\\end{bmatrix} 
\\end{aligned}$$

初始化时设：

```python
dt = 0.1
kf.F = np.array([[1, dt],
                 [0, 1]])
```

每次测量 $\\Delta t$ 变化如何处理？easy——改相关矩阵。此例 `F` 变，须在 update/predict 循环内更新。`Q` 也依赖时间，每循环赋值。示例代码：

""",

153: "### 传感器融合：不同数据率（Sensor fusion: Different Data Rates）\n",

154: """两类传感器很少同速率输出。设位置传感器 3 Hz，轮 7 Hz。时序不 precise——有 jitter，测量可略早或略晚。再 complicate：轮提供速度而非位置估计。

可等待任一传感器数据包。收到后算距上次 update 时间。须改受影响矩阵。$\\mathbf F$、$\\mathbf Q$ 含 $\\Delta t$，每次 innovation 调整。

测量每次变，须改 $\\mathbf H$、$\\mathbf R$。位置传感器改 $\\mathbf x$ 的位置元素：

$$\\begin{aligned}
\\mathbf H &= \\begin{bmatrix}1 &0\\end{bmatrix} \\\\
\\mathbf R &= \\sigma_{ps}^2
\\end{aligned}$$

轮传感器改速度元素：

$$\\begin{aligned}
\\mathbf H &= \\begin{bmatrix}0 &1\\end{bmatrix} \\\\
\\mathbf R &= \\sigma_{wheel}^2
\\end{aligned}$$""",

156: "## 跟踪球（Tracking a Ball）\n",

157: """现在转向被跟踪物体物理受约束的情形。真空中的球须 obey 牛顿定律。恒定重力场中沿抛物线飞行。假设你熟悉公式推导：

$$
\\begin{aligned}
y &= \\frac{g}{2}t^2 + v_{y0} t + y_0 \\\\
x &= v_{x0} t + x_0
\\end{aligned}
$$

$g$ 为重力常数，$t$ 为时间，$v_{x0}$、$v_{y0}$ 为 x、y 初速。若以初速 $v$、仰角 $\\theta$ 抛出，

$$
\\begin{aligned}
v_{x0} = v \\cos{\\theta} \\\\
v_{y0} = v \\sin{\\theta}
\\end{aligned}
$$""",

158: "无真实数据，先写球的仿真。与往常一样，加与时间无关的噪声项以仿真带噪传感器。\n",

160: """故从 (0, 15) 出发、速度 100 m/s、角度 60° 的轨迹：

```python
traj = BallTrajectory2D(x0=0, y0=15, velocity=100, theta_deg=60)
```
    
每时间步调用 `traj.step(t)`。测试一下

""",

162: "看起来合理，继续（读者练习：更 robust 验证仿真）。\n",

163: "### 选择状态变量（Choose the State Variables）\n",

164: """我们可能想用狗跟踪的状态变量，但这不行。回忆卡尔曼状态转移须写为 $\\mathbf{\\bar x} = \\mathbf{Fx} + \\mathbf{Bu}$，即须从前一状态算当前状态。假设球在真空，x 方向速度恒定，y 方向加速度仅来自重力常数 $g$。用 well known **欧拉法（Euler's method）**离散牛顿方程，$\\Delta t$ 下：

$$\\begin{aligned}
x_t &=  x_{t-1} + v_{x(t-1)} {\\Delta t} \\\\
v_{xt} &= v_{x(t-1)} \\\\
y_t &= y_{t-1} + v_{y(t-1)} {\\Delta t} \\\\
v_{yt} &= -g {\\Delta t} + v_{y(t-1)} \\\\
\\end{aligned}$$

> **旁注（sidebar）**：*欧拉法逐步积分微分方程，假设 $t$ 时刻斜率（导数）恒定。此处位置导数为速度。每步 $\\Delta t$ 假设恒速，算新位置，再为下一步更新速度。有更准确方法如 Runge-Kutta，但每步有测量 update 状态时欧拉很准。若需 Runge-Kutta 须自写 `predict()` 计算 $\\mathbf x$ 状态转移，再用 $\\mathbf{\\bar P}=\\mathbf{FPF}^\\mathsf T + \\mathbf Q$ 更新协方差。*

这暗示 y 须纳入加速度，x 不必。可能的状态：

$$
\\mathbf x = 
\\begin{bmatrix}
x & \\dot x & y & \\dot y & \\ddot{y}
\\end{bmatrix}^\\mathsf T
$$

但加速度来自重力，为常数。与其让卡尔曼跟踪常数，不如把重力当作**控制输入（control input）**——已知方式改变系统行为的力，贯穿球的整个飞行。

状态预测 $\\mathbf{\\bar x} = \\mathbf{Fx} + \\mathbf{Bu}$。$\\mathbf{Fx}$ 为熟悉的状态转移，建模球位置与速度。向量 $\\mathbf{u}$ 指定滤波控制输入。对汽车是油门、刹车、方向盘等。对球，控制输入是重力。矩阵 $\\mathbf B$ 建模控制如何影响系统。对汽车 $\\mathbf B$ 将刹车、油门转为速度变化，方向盘转为位置与航向变化。球跟踪问题它计算重力引起的速度变化。细节稍后。目前状态设计为

$$
\\mathbf x = 
\\begin{bmatrix}x & \\dot x & y & \\dot y 
\\end{bmatrix}^\\mathsf T
$$""",

165: """### 设计状态转移函数（Design State Transition Function）

下一步设计状态转移函数，实现为矩阵 $\\mathbf F$，与前一状态相乘得先验 $\\bar{\\mathbf x} = \\mathbf{Fx}$。

不再赘述，与上一章一维类似。位置与速度状态方程：

$$
\\begin{aligned}
\\bar x &= (1*x) + (\\Delta t * v_x) + (0*y) + (0 * v_y) \\\\
\\bar v_x &= (0*x) +  (1*v_x) + (0*y) + (0 * v_y) \\\\
\\bar y &= (0*x) + (0* v_x)         + (1*y) + (\\Delta t * v_y)   \\\\
\\bar v_y &= (0*x) +  (0*v_x) + (0*y) + (1*v_y) 
\\end{aligned}
$$

无项含重力常数 $g$。上一节说明用卡尔曼控制输入 补偿重力。矩阵形式：

$$
\\mathbf F = \\begin{bmatrix}
1 & \\Delta t & 0 & 0 \\\\
0 & 1 & 0 & 0 \\\\
0 & 0 & 1 & \\Delta t \\\\
0 & 0 & 0 & 1
\\end{bmatrix}
$$""",

166: """### 设计控制输入函数（Design the Control Input Function）

用控制输入 补偿重力。项 $\\mathbf{Bu}$ 加到 $\\mathbf{\\bar x}$，表示 $\\mathbf{\\bar x}$ 因重力变化多少。可说 $\\mathbf{Bu}$ 含 $\\begin{bmatrix}\\Delta x_g & \\Delta \\dot{x_g} & \\Delta y_g & \\Delta \\dot{y_g}\\end{bmatrix}^\\mathsf T$。

离散方程可见重力只影响 y 速度。

$$\\begin{aligned}
x_t &=  x_{t-1} + v_{x(t-1)} {\\Delta t} \\\\
v_{xt} &= vx_{t-1}
\\\\
y_t &= y_{t-1} + v_{y(t-1)} {\\Delta t}\\\\
v_{yt} &= -g {\\Delta t} + v_{y(t-1)} \\\\
\\end{aligned}$$

故希望 $\\mathbf{Bu}$ 等于 $\\begin{bmatrix}0 & 0 & 0 & -g \\Delta t \\end{bmatrix}^\\mathsf T$。如何定义 $\\mathbf{B}$、$\\mathbf{u}$ 在一定程度上任意，只要乘积如此。例如 $\\mathbf{B}=1$，$\\mathbf{u} = \\begin{bmatrix}0 & 0 & 0 & -g \\Delta t \\end{bmatrix}^\\mathsf T$，但不太符合 $\\mathbf{B}$ 为控制函数、$\\mathbf{u}$ 为控制输入的定义。y 速度控制输入为 $-g$。一种定义：

$$\\mathbf{B} = \\begin{bmatrix}0&0&0&0 \\\\ 0&0&0&0 \\\\0&0&0&0 \\\\0&0&0&\\Delta t\\end{bmatrix}, \\mathbf{u} = \\begin{bmatrix}0\\\\0\\\\0\\\\-g\\end{bmatrix}$$

我觉得略 excess；也许 $\\mathbf{u}$ 含 x、y 两维控制， suggest

$$\\mathbf{B} = \\begin{bmatrix}0&0 \\\\ 0&0 \\\\0&0 \\\\0&\\Delta t\\end{bmatrix}, \\mathbf{u} = \\begin{bmatrix}0\\\\-g\\end{bmatrix}$$.

你也许偏好只给实际存在的控制；x 无控制输入，得

$$\\mathbf{B} = \\begin{bmatrix}0 \\\\ 0 \\\\0\\\\ \\Delta t\\end{bmatrix}, \\mathbf{u} = \\begin{bmatrix}-g\\end{bmatrix}$$.

我见过

$$\\mathbf{B} = \\begin{bmatrix}0&0&0&0 \\\\ 0&0&0&0 \\\\0&0&0&0 \\\\0&0&0&1\\end{bmatrix}, \\mathbf{u} = \\begin{bmatrix}0\\\\0\\\\0\\\\-g \\Delta t\\end{bmatrix}$$

结果正确，但我反对把 $\\Delta t$ 放进 $\\mathbf{u}$——时间不是控制输入，是用以把控制输入转为状态变化，那是 $\\mathbf{B}$ 的工作。

""",

167: """### 设计测量函数（Design the Measurement Function）

测量函数定义 $\\mathbf z = \\mathbf{Hx}$。假设传感器给球 (x,y) 位置，不能测速度或加速度。函数须为：

$$
\\begin{bmatrix}z_x \\\\ z_y \\end{bmatrix}= 
\\begin{bmatrix}
1 & 0 & 0 & 0 \\\\
0 & 0 & 1 & 0
\\end{bmatrix} 
\\begin{bmatrix}
x \\\\
\\dot x \\\\
y \\\\
\\dot y \\end{bmatrix}$$

其中

$$\\mathbf H = \\begin{bmatrix}
1 & 0 & 0 & 0 \\\\
0 & 0 & 1 & 0
\\end{bmatrix}$$""",

168: """### 设计测量噪声矩阵（Design the Measurement Noise Matrix）

与机器人一样，假设 x、y 误差独立。此处先设 x、y 测量误差方差均为 0.5 米平方：

$$\\mathbf R = \\begin{bmatrix}0.5&0\\\\0&0.5\\end{bmatrix}$$""",

169: """### 设计过程噪声矩阵（Design the Process Noise Matrix）

假设球在真空运动，应无过程噪声。4 个状态变量，需 4×4 协方差：

$$\\mathbf Q = \\begin{bmatrix}0&0&0&0\\\\0&0&0&0\\\\0&0&0&0\\\\0&0&0&0\\end{bmatrix}$$""",

170: """### 设计初始条件（Design the Initial Conditions）

测试状态转移时已做此步。回忆用三角函数算 x、y 初速，设 $\\mathbf x$：

```python
omega = radians(omega)
vx = cos(omega) * v0
vy = sin(omega) * v0

f1.x = np.array([[x, vx, y, vy]]).T
```
    
各步完成，可实现滤波并测试。先实现：

""",

172: "现在用球仿真类生成测量测试滤波器。\n",

174: "可见卡尔曼滤波 较好地跟踪球。但如前所述，这是 琐碎 例子，无过程噪声。真空中轨迹可任意精度预测；此例用卡尔曼滤波是 不必要的复杂。最小二乘曲线拟合结果相同。\n",

175: "## 空气中跟踪球（Tracking a Ball in Air）\n",

176: """本问题假设跟踪穿过地球大气的球。路径受风、阻力、球旋转影响。假设传感器为相机；未实现的代码做某种图像处理检测球位置，计算机视觉中常称** blob 检测（blob detection）**。但图像处理非完美；任一帧可能未检测到 blob 或检测到 spurious blob。也不假设知球的起始位置、角度或旋转；跟踪代码须根据提供的测量启动。主要简化是二维世界；假设球始终垂直于相机传感器平面运动。须在此简化，因尚未讨论如何从仅提供二维数据的相机提取三维信息。

""",

177: "### 实现空气阻力（Implementing Air Drag）\n",

178: """第一步实现空气中球的数学。有多种处理。 robust 解考虑球粗糙度（阻力随速度非线性依赖）、**马格努斯效应（Magnus effect）**（旋转使球一侧相对空气速度高于对侧，两侧阻力系数不同）、升力、湿度、空气密度等。假设读者对球物理细节不感兴趣，故限于非旋转棒球空气阻力。采用 Nicholas Giordano 与 Hisao Nakanishi *Computational Physics* [1997] 的数学。未考虑所有因素。最详细的是 Alan Nathan 网站 http://baseball.physics.illinois.edu/index.html。我计算机视觉工作中用他的数学，但不想被更复杂模型分心。

**重要**：继续前指出，你*不必*理解下一段物理才能进行卡尔曼滤波。目标是创建相当准确的真实棒球行为，以测试卡尔曼滤波在真实行为下的表现。真实应用中通常 不可能完全建模物理，我们用 纳入大尺度行为的过程模型，再调测量噪声与过程噪声直到滤波与数据配合良好。有风险：易 精细调参 使测试数据完美、略不同数据表现差。这或许是设计卡尔曼滤波最难部分，故称「黑艺术（black art）」。

我不喜欢无解释的实现，故现在推导空气中球的物理。若不感兴趣可跳过仿真实现。

空气中运动的球遇风阻。对球施加力，称**阻力（drag）**，改变飞行。Giordano 记为

$$F_{drag} = -B_2v^2$$

$B_2$ 为实验系数，$v$ 为速度。$F_{drag}$ 可分解为 x、y：

$$\\begin{aligned}
F_{drag,x} &= -B_2v v_x\\\\
F_{drag,y} &= -B_2v v_y
\\end{aligned}$$

若 $m$ 为球质量，由 $F=ma$ 得加速度：

$$\\begin{aligned} 
a_x &= -\\frac{B_2}{m}v v_x\\\\
a_y &= -\\frac{B_2}{m}v v_y
\\end{aligned}$$

Giordano 给出 $\\frac{B_2}{m}$ 函数，考虑空气密度、棒球横截面、粗糙度。基于风洞与若干简化假设的近似。SI 单位：速度 m/s，时间 s。

$$\\frac{B_2}{m} = 0.0039 + \\frac{0.0058}{1+\\exp{[(v-35)/5]}}$$

真空中球路径的欧拉离散：

$$\\begin{aligned}
x &= v_x \\Delta t \\\\
y &= v_y \\Delta t \\\\
v_x &= v_x \\\\
v_y &= v_y - 9.8 \\Delta t
\\end{aligned}$$

可将此力（加速度）纳入速度更新，减去该分量因阻力减速度。代码 很直接，须分解 x、y 分量。

不再赘述，计算物理超出本书。更高保真仿真须纳入海拔、温度、球 spin 等。Alan Nathan 前述工作若感兴趣可阅。意图是给仿真 impart 真实行为，以测试卡尔曼较简预测模型的反应。过程模型 never 完全匹配世界；设计好滤波须 仔细测试真实数据表现。

下面代码计算海平面、有风时棒球行为。同一次击球绘无风与 10 mph 顺风。棒球统计 universal 用美制（http://en.wikipedia.org/wiki/United_States_customary_units）。110 mph 为典型本垒打出口速度。

""",

180: """易见真空与空气中轨迹差异。我用与上文真空中球相同初速与发射角。真空计算约 240 米（近 800 ft）。空气中约 120 米，约 400 ft。400 ft 是强击本垒打的  realistic 距离，可相信仿真相当准确。

不再赘述，创建用上述数学产生更 realistic 轨迹的球仿真。阻力非线性意味着任意时刻球位置无解析解，须逐步计算。我用欧拉法传播；更准如 Runge-Kutta 留作读者练习。对我们所用时间步，两种方法精度差 small， modest 复杂 unnecessary。

""",

182: "现在用该模型产生的测量测试卡尔曼滤波。\n",

184: """绘两种卡尔曼设置输出。测量为绿圆，R=0.5 为细绿线，R=10 为粗蓝线。R 值仅为示测量噪声对输出的影响，非暗示正确设计。

可见两者都不很好。起初都 closely 跟踪测量，但随时间发散。因空气阻力状态模型非线性，卡尔曼假设线性。若记得 g-h 滤波章关于非线性的讨论：g-h 滤波总滞后于系统加速度。此处相同——加速度为负，卡尔曼 consistently 超调球位置。加速度持续则滤波无法追上，将继续发散。

如何改进？最好用法非线性卡尔曼滤波，后续章节会做。也有我称「工程（engineering）」解：卡尔曼假设球在真空，故无过程噪声。但球在空气中，大气对球施力。可将此力当过程噪声—— rigorous 上不佳（该力 绝非高斯），且可计算，不能举手说「随机」。但看此思路效果。

下面实现同前卡尔曼滤波，但过程噪声非零。绘 Q=.1 与 Q=0.01 两例。

""",

186: """第二个滤波 相当好地 跟踪测量。似有一点 lag，很小。

这是好技巧吗？通常不是，但取决于情况。此处球受力非线性 相当恒定。假设跟踪汽车——加减速随车速、转弯变化。过程噪声大于实际系统噪声时，滤波更偏重测量。测量噪声不大时或许可行。但看下一图，我增大了测量噪声。

""",

188: """输出 terrible。滤波别无选择只能更偏重测量而非过程（预测步），但测量 noisy 时输出  merely 跟踪噪声噪声。线性卡尔曼滤波此 固有局限导致非线性滤波版本的发展。

话虽如此，当然可用过程噪声处理系统小非线性。这是卡尔曼「黑艺术」一部分。传感器与系统模型 从不完美。传感器非高斯，过程模型 从不完美。可将测量误差与过程误差设高于理论值 掩盖一些，但 代价是次优。当然次优优于发散。但上图可见滤波输出可 非常差。也 非常常见 跑许多仿真测试后得某条件下表现很好的滤波，真实数据条件略异则极差。

暂置此问题——显然误用卡尔曼滤波。后续章节  revisit，看法非线性技术效果。某些领域线性卡尔曼可用于非线性问题，但通常须用本书余下技术之一。

""",

189: "## 参考文献（References）\n\n[1] Bar-Shalom, Yaakov, et al. *Estimation with Applications to Tracking and Navigation.* John Wiley & Sons, 2001.",
}
