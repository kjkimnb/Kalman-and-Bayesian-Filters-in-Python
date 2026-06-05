# -*- coding: utf-8 -*-
"""06-Multivariate-Kalman-Filters.ipynb markdown 译文 (part 1)"""

TRANSLATIONS_06_PART1 = {
0: "[目录](./table_of_contents.ipynb)\n",

1: """# 多元卡尔曼滤波（Multivariate Kalman Filters）

对多个随机变量滤波（Filtering Multiple Random Variables）

""",

4: "## 引言（Introduction）\n",

5: """我们现在可以学习并实现卡尔曼滤波（Kalman filter）的完整多元形式。上一章我们学习了多元高斯（multivariate Gaussian）如何表达多个随机变量之间的相关性，例如飞机的位置与速度。我们还学习了变量之间的相关性如何大幅改善后验（posterior）。若我们对位置和速度只有粗略了解，但它们相关，则新估计可以非常准确。

我更希望你通过若干算例建立对这些滤波器如何工作的直觉。我会略过许多问题。我展示的一些内容只适用于特殊情况，另一些会显得“神奇”——你不清楚我如何得出某结果。若我从严格、一般的方程开始，你会对着各项含义以及如何把其用到你的问题而挠头。后面章节我会给出更严格的数学基础，届时要么修正本章的近似，要么补充此处未涵盖的信息。

为使这成为可能，我们把问题限制在可用牛顿运动方程描述的一类子问题上。这类滤波器称为 *离散化连续时间运动学滤波器（discretized continuous-time kinematic filters）*。在 **卡尔曼滤波数学（Kalman Filter Math）** 一章，我们将为非牛顿系统发展数学。

""",

6: """## 牛顿运动方程（Newton's Equations of Motion）

牛顿运动方程告诉我们：给定系统的恒定速度 $v$，经过时间 $t$ 后的位置 $x$ 为：

$$x = vt + x_0$$

例如，若起始位置为 13，速度为 10 m/s，行驶 12 秒，最终位置为 133（$10\\times 12 + 13$）。

恒定加速度可纳入：

$$x = \\frac{1}{2}at^2 + v_0t + x_0$$

若假设恒定 jerk，则

$$x = \\frac{1}{6}jt^3 +  \\frac{1}{2}a_0 t^2 + v_0 t + x_0$$

这些方程由对微分方程积分得到。给定恒定速度 $v$，可用

$$x = vt + x_0$$

计算行驶距离，推导如下：

$$\\begin{aligned} v &= \\frac{dx}{dt}\\\\
dx &= v\\, dt \\\\
\\int_{x_0}^x\\, dx &= \\int_0^t v\\, dt\\\\
x - x_0 &= vt - 0\\\\
x &= vt + x_0\\end{aligned}$$


设计卡尔曼滤波时，你从描述系统动力学的一组微分方程开始。大多数微分方程组不能这样轻易积分。我们从牛顿方程开始，因为可以积分得到闭式解，使卡尔曼滤波更容易设计。额外好处是牛顿方程适合跟踪运动物体——卡尔曼滤波的主要用途之一。

""",

7: """## 卡尔曼滤波算法（Kalman Filter Algorithm）

算法与我们在各章使用的贝叶斯滤波（Bayesian filter）算法相同。更新（update）步稍复杂，讲到时再解释原因。

**初始化（Initialization）**

    1. 初始化滤波器状态
    2. 初始化我们对状态的信念（belief）
    
**预测（Predict）**

    1. 用过程模型预测下一时间步的状态
    2. 调整信念以反映预测中的不确定性    
**更新（Update）**

    1. 获得测量及其精度信念
    2. 计算估计状态与测量之间的残差（residual）
    3. 根据测量或预测谁更准确计算缩放因子
    4. 按缩放因子在预测与测量之间设定状态
    5. 根据对测量的确信程度更新状态信念
    
提醒一下，算法的图形表示如下：

""",

9: """一维卡尔曼滤波用一元高斯表示状态。自然，多元卡尔曼滤波用多元高斯表示状态。上一章我们学到多元高斯用向量表示均值、用矩阵表示协方差（covariance）。因此卡尔曼滤波需要用线性代数做估计。

我不希望你死记这些方程，但下面列出了一维与多元方程，它们相当相似。

<u>**预测（Predict）**</u>

$\\begin{array}{|l|l|l|}
\\hline
\\text{Univariate} & \\text{Univariate} & \\text{Multivariate}\\\\
& \\text{(Kalman form)} & \\\\
\\hline
\\bar \\mu = \\mu + \\mu_{f_x} & \\bar x = x + dx & \\bar{\\mathbf x} = \\mathbf{Fx} + \\mathbf{Bu}\\\\
\\bar\\sigma^2 = \\sigma_x^2 + \\sigma_{f_x}^2 & \\bar P = P + Q & \\bar{\\mathbf P} = \\mathbf{FPF}^\\mathsf T + \\mathbf Q \\\\
\\hline
\\end{array}$

暂不关心线性代数细节，可见：

$\\mathbf x,\\, \\mathbf P$ 是状态均值与协方差，对应 $x$ 与 $\\sigma^2$。

$\\mathbf F$ 是 *状态转移函数（state transition function）*。乘以 $\\bf x$ 即计算先验（prior）。

$\\mathbf Q$ 是过程协方差，对应 $\\sigma^2_{f_x}$。

$\\mathbf B$ 与 $\\mathbf u$ 对我们较新，用于建模系统的控制输入（control input）。

<u>**更新（Update）**</u>

$\\begin{array}{|l|l|l|}
\\hline
\\text{Univariate} & \\text{Univariate} & \\text{Multivariate}\\\\
& \\text{(Kalman form)} & \\\\
\\hline
& y = z - \\bar x & \\mathbf y = \\mathbf z - \\mathbf{H\\bar x} \\\\
& K = \\frac{\\bar P}{\\bar P+R}&
\\mathbf K = \\mathbf{\\bar{P}H}^\\mathsf T (\\mathbf{H\\bar{P}H}^\\mathsf T + \\mathbf R)^{-1} \\\\
\\mu=\\frac{\\bar\\sigma^2\\, \\mu_z + \\sigma_z^2 \\, \\bar\\mu} {\\bar\\sigma^2 + \\sigma_z^2} & x = \\bar x + Ky & \\mathbf x = \\bar{\\mathbf x} + \\mathbf{Ky} \\\\
\\sigma^2 = \\frac{\\sigma_1^2\\sigma_2^2}{\\sigma_1^2+\\sigma_2^2} & P = (1-K)\\bar P &
\\mathbf P = (\\mathbf I - \\mathbf{KH})\\mathbf{\\bar{P}} \\\\
\\hline
\\end{array}$

$\\mathbf H$ 是测量函数（measurement function）。本书尚未见到，稍后解释。若心理上去掉 $\\mathbf H$，应能看出这些方程也相似。

$\\mathbf z,\\, \\mathbf R$ 是测量均值与测量噪声协方差（measurement noise covariance），对应一维滤波中的 $z$ 与 $\\sigma_z^2$（一维方程中我用 $x$ 代替 $\\mu$ 以使记法尽量相似）。

$\\mathbf y$ 与 $\\mathbf K$ 是残差与卡尔曼增益（Kalman gain）。

细节与一维滤波不同，因为这里是向量与矩阵，但概念完全相同：

-  用高斯表示状态估计与误差
-  用高斯表示测量及其误差
-  用高斯表示过程模型
-  用过程模型预测下一状态（先验）
-  在测量与先验之间形成估计

作为设计者，你要设计状态 $\\left(\\mathbf x, \\mathbf P\\right)$、过程 $\\left(\\mathbf F, \\mathbf Q\\right)$、测量 $\\left(\\mathbf z, \\mathbf R\\right)$ 与测量函数 $\\mathbf H$。若系统有控制输入（如机器人），还要设计 $\\mathbf B$ 与 $\\mathbf u$。

""",

10: """我已把卡尔曼滤波方程编入 FilterPy 的 `predict` 与 `update` 函数。导入方式：

```python
from filterpy.kalman import predict, update
```

""",

11: """## 跟踪狗（Tracking a Dog）

回到我们屡试不爽的跟踪狗问题。这次纳入上一章的核心洞见，用 *隐变量（hidden variables）* 改善估计。我可以从数学开始，但不如边实现滤波边学。表面上数学与前几章不同、或许更复杂，但思想相同——我们只是相乘并相加高斯分布。

先写狗的仿真。仿真运行 `count` 步，每步狗向前移动约 1 米。每步速度按过程方差 `process_var` 变化。更新位置后，用假设传感器方差 `z_var` 计算测量。函数返回位置的 NumPy 数组与测量的数组。

""",

13: """## 预测步（Predict Step）

预测需要设计状态与协方差、过程模型与过程噪声，以及可选的控制输入。我们按顺序进行。

""",

14: """### 设计状态变量（Design State Variable）

此前我们用高斯在一维跟踪狗。均值 $(\\mu)$ 表示最可能位置，方差 ($\\sigma^2$) 表示位置的概率分布。位置是系统的 *状态（state）*，$\\mu$ 称为 *状态变量（state variable）*。

本题同时跟踪狗的位置与速度，需用状态向量 $\\mathbf x$ 及其协方差矩阵 $\\mathbf P$ 表示多元高斯。

状态变量可以是 *观测变量（observed variables）*——传感器直接测量，或 *隐变量（hidden variables）*——从观测变量推断。跟踪狗时传感器只读位置，故位置可观测、速度隐藏。我们很快会学习如何跟踪隐变量。

务必理解：同时跟踪位置与速度是设计选择，带有我们尚未探讨的含义与假设。例如也可跟踪加速度甚至 jerk。暂且回忆上一章：在协方差矩阵中包含速度使位置方差小得多。本章稍后讲滤波器如何估计隐变量。

一维章用标量表示狗的位置（如 $\\mu=3.27$）。上一章学会对多变量用多元高斯。若要指定位置 10.0 m、速度 4.5 m/s，写作：

$$\\mu = \\begin{bmatrix}10.0\\\\4.5\\end{bmatrix}$$

卡尔曼滤波用线性代数实现。用 $n\\times 1$ 矩阵（*向量（vector）*）存储 $n$ 个状态变量。跟踪狗时，$x$ 表示位置，$x$ 的一阶导数 $\\dot x$ 表示速度。我用牛顿点记号表示导数；$\\dot x$ 是 $x$ 对 $t$ 的一阶导数：$\\dot x = \\frac{dx}{dt}$。卡尔曼滤波方程用 $\\mathbf x$ 表示状态，定义：

$$\\mathbf x =\\begin{bmatrix}x \\\\ \\dot x\\end{bmatrix}$$

我们用 $\\mathbf x$ 代替 $\\mu$，但应认出这是多元高斯的均值。

也可写 $\\mathbf x =\\begin{bmatrix}x & \\dot x\\end{bmatrix}^\\mathsf T$，因为行向量的转置是列向量。文本中这种记法更省垂直空间。

$\\mathbf x$ 与位置 $x$ 碰巧同名。若在 y 轴跟踪狗，应写 $\\mathbf x =\\begin{bmatrix}y & \\dot y\\end{bmatrix}^\\mathsf T$，而非 $\\mathbf y =\\begin{bmatrix}y & \\dot y\\end{bmatrix}^\\mathsf T$。$\\mathbf x$ 是卡尔曼滤波文献中状态变量的标准名称，我们不会改成更有意义的名称。记法一致便于与同行交流。

编码如下。`x` 的初始化很简单：

""",

16: "我常在代码中用转置把行矩阵变成列向量，因为打字和阅读都更方便：\n",

18: "不过 NumPy 把一维数组识别为向量，因此可简化为使用一维数组。\n",

20: "数组元素类型相同，通常是 `float` 或 `int`。若列表全是 `int`，创建的数组也是 `int`，否则为 `float`。我常利用这一点，只把一个数写成浮点：\n",

22: "下面是一些例子。\n",

24: "Python 3.5+ 有矩阵乘法运算符 @，其中 `np.dot(A, B) == A @ B`。它不如你可能想的那么有用，因为要求 `A` 与 `B` 都是数组。本书数学中有些变量可以是标量，故 `@` 的用处常打折扣。\n",

26: "最后一行返回一维数组，但我写的卡尔曼滤波类能处理。事后看可能造成困惑，但确实可用。\n",

27: """### 设计状态协方差（Design State Covariance）

状态高斯的另一半是协方差矩阵 $\\mathbf P$。一维卡尔曼滤波中指定 $\\sigma^2$ 初值，滤波器在加入测量时更新其值。多维卡尔曼滤波同样：指定 $\\mathbf P$ 初值，滤波器在每个 epoch 更新。

需把方差设为合理值。例如，若对初位置很不确定，可选 $\\sigma_\\mathtt{pos}^2=500 m^2$。狗的最高速度约 21 m/s，若无其他速度信息，可设 $3\\sigma_\\mathtt{vel}=21$，即 $\\sigma_\\mathtt{vel}^2=7^2=49$。

上一章说明位置与速度相关。但狗的位置与速度相关程度如何？我不知道。如将见，滤波器会为我们计算，故我把协方差初值设为零。当然，若已知协方差应使用。

回忆协方差矩阵对角元是各变量方差，非对角元是协方差。于是：

$$
\\mathbf P = \\begin{bmatrix}500 & 0 \\\\ 0&49\\end{bmatrix}
$$

可用 `numpy.diag` 用对角值创建对角矩阵。线性代数中，对角矩阵非对角元为零。

""",

29: "也可以写成：\n",

31: "完成。我们已把滤波器状态表示为多元高斯并在代码中实现。\n",

32: """### 设计过程模型（Design the Process Model）

下一步设计 *过程模型（process model）*。它是描述系统行为的数学模型。滤波器用它预测离散时间步后的状态。用一组描述系统动力学的方程实现。

一维章用下式建模狗的运动：

$$ x = v \\Delta t + x_0$$

实现如下：

```python
def predict(pos, movement):
    return gaussian(pos.mean + movement.mean, 
                    pos.var + movement.var)
```

本章同样做法，但用多元高斯代替一元高斯。你可能想象类似实现：

$$ \\mathbf x = \\begin{bmatrix}5.4\\\\4.2\\end{bmatrix}, \\, \\, 
\\dot{\\mathbf x} =  \\begin{bmatrix}1.1\\\\0.\\end{bmatrix} \\\\
\\mathbf x = \\dot{\\mathbf x}t + \\mathbf x$$

但需推广。卡尔曼滤波方程适用于任意线性系统，不限于牛顿系统。也许你滤波的是化工厂管道系统，某管道流量由不同阀门设置的线性组合决定。

$$\\mathtt{pipe_1} = 0.134(\\mathtt{valve}_1) + 0.41(\\mathtt{valve}_2 - \\mathtt{valve}_3) + 1.34$$
$$\\mathtt{pipe_2} = 0.210(\\mathtt{valve}_2) - 0.62(\\mathtt{valve}_1 - \\mathtt{valve}_5) + 1.86$$

线性代数有强大方式表达方程组。考虑

$$\\begin{cases}
2x+3y=8\\\\4x-y=2
\\end{cases}$$

写成矩阵形式：

$$\\begin{bmatrix}2& 3 \\\\ 4&-1\\end{bmatrix} \\begin{bmatrix}x\\\\y\\end{bmatrix} = \\begin{bmatrix}8\\\\2\\end{bmatrix}$$

若做该方程的 [矩阵乘法（matrix multiplication）](https://en.wikipedia.org/wiki/Matrix_multiplication#General_definition_of_the_matrix_product)，结果就是上面两个方程。线性代数中写作 $\\mathbf{Ax}=\\mathbf B$，其中

$$\\mathbf{A} = \\begin{bmatrix}2& 3 \\\\ 4&-1\\end{bmatrix},\\, \\mathbf x = \\begin{bmatrix}x\\\\y\\end{bmatrix}, \\mathbf B=\\begin{bmatrix}8\\\\2\\end{bmatrix}$$

然后用 SciPy 的 `linalg` 包解 $\\mathbf x$：

""",

34: """我们用过程模型做 *新息（innovation）*，因为方程告诉我们给定当前状态的下一状态。卡尔曼滤波用线性方程实现，$\\mathbf{\\bar x}$ 是 *先验（prior）* 或预测状态：

$$\\mathbf{\\bar x} = \\mathbf{Fx}$$

显式写为

$$\\begin{bmatrix} \\bar x \\\\ \\dot{\\bar x}\\end{bmatrix} = \\begin{bmatrix}? & ? \\\\? & ?\\end{bmatrix}\\begin{bmatrix}x\\\\\\dot x\\end{bmatrix}$$

作为卡尔曼滤波设计者的任务，是指定 $\\mathbf F$ 使 $\\bar{\\mathbf x}  = \\mathbf{Fx}$ 对我们的系统做新息（预测）。每个状态变量需要一个方程。本题 $\\mathbf x = \\begin{bmatrix}x & \\dot x\\end{bmatrix}^\\mathtt{T}$，故需一个方程计算位置 $x$，另一个计算速度 $\\dot x$。位置新息方程已知：

$$\\bar x = x + \\dot x \\Delta t$$

速度方程呢？我们没有狗速度如何随时间变化的预测模型。此处假设各新息之间速度恒定。当然并不完全正确，但只要每个新息间速度变化不太大，你会看到滤波器表现很好。故：

$$\\bar{\\dot x} = \\dot x$$

得到过程模型

$$\\begin{cases}
\\begin{aligned}
\\bar x &= x + \\dot x \\Delta t \\\\
\\bar{\\dot x} &= \\dot x
\\end{aligned}
\\end{cases}$$

左边每个状态变量各有一个方程，正确。需写成 $\\bar{\\mathbf x}  = \\mathbf{Fx}$。重排项更易看出做法：

$$\\begin{cases}
\\begin{aligned}
\\bar x &= 1x + &\\Delta t\\, \\dot x \\\\
\\bar{\\dot x} &=0x + &1\\, \\dot x
\\end{aligned}
\\end{cases}$$

矩阵形式：

$$\\begin{aligned}
\\begin{bmatrix}\\bar x \\\\ \\bar{\\dot x}\\end{bmatrix} &= \\begin{bmatrix}1&\\Delta t  \\\\ 0&1\\end{bmatrix}  \\begin{bmatrix}x \\\\ \\dot x\\end{bmatrix}\\\\
\\mathbf{\\bar x} &= \\mathbf{Fx}
\\end{aligned}$$

$\\mathbf F$ 称为 *状态转移函数（state transition function）* 或 *状态转移矩阵（state transition matrix）*。后文章节它会是真函数而非矩阵，称函数更一般。

""",

36: """来测试！FilterPy 的 `predict` 方法通过计算 $\\mathbf{\\bar x} = \\mathbf{Fx}$ 做预测。调用看看。位置设为 10.0，速度 4.5 m/s。`dt = 0.1`，时间步 0.1 秒，故新息后新位置应为 10.45 米。速度应不变。

""",

38: "有效。若连续多次调用 `predict()`，每次都会更新值。\n",

40: "`predict()` 同时计算新息的均值与协方差。这是五次新息（预测）后的 $\\mathbf P$ 值，卡尔曼滤波方程中记为 $\\mathbf{\\bar P}$。\n",

42: """检查对角元可见位置方差变大。我们做了五次预测、无测量，不确定性增大。非对角元变为非零——滤波器检测到位置与速度的相关性！速度方差未变。

这里画预测前后的协方差。初值实线红色，先验（预测）虚线黑色。我调整了协方差与时间步以便更好说明变化。

""",

44: """可见椭圆中心小幅移动（从 10 到 11.35），因为位置变了。椭圆也拉长，显示位置与速度的相关性。滤波器如何计算 $\\mathbf{\\bar P}$ 的新值？依据什么？注意我每次把过程噪声 `Q` 设为零，不是因为我加了噪声。现在讲还稍早，但回忆迄今每个滤波器的预测步都伴随信息损失。这里亦然。覆盖面更广后再给细节。

""",

45: """### 设计过程噪声（Design Process Noise）

快速回顾 *过程噪声（process noise）*。汽车定速巡航行驶，应恒速。用 $\\bar x_k=\\dot x_k\\Delta t + x_{k-1}$ 建模。但受多种未知因素影响：巡航无法完美恒速；风、山坡、坑洼；乘客摇下车窗改变阻力等。

可用微分方程建模：

$$\\dot{\\mathbf x} = f(\\mathbf x) + w$$

$f(\\mathbf x)$ 建模状态转移，$w$ 是 *白过程噪声（white process noise）*。

**卡尔曼滤波数学** 一章会讲如何从微分方程组得到卡尔曼滤波矩阵。本章利用牛顿已为我们推导运动方程。目前只需知道：通过在协方差 $\\mathbf P$ 上加过程噪声协方差矩阵 $\\mathbf Q$ 计入噪声。不向 $\\mathbf x$ 加任何东西，因为噪声是 *白* 的——噪声均值为 0。均值为 0 则 $\\mathbf x$ 不变。

一维卡尔曼滤波用 `variance = variance + process_noise` 计算预测步方差。多元卡尔曼滤波同理，本质 `P = P + Q`。说“本质”是因为协方差方程还有与噪声无关的项，稍后见到。

推导过程噪声矩阵可能很费劲，留到卡尔曼数学章。目前知道 $\\mathbf Q$ 等于白噪声 $w$ 的期望值，$\\mathbf Q = \\mathbb E[\\mathbf{ww}^\\mathsf T]$。本章聚焦修改该矩阵如何改变滤波器行为的直觉。

FilterPy 提供计算本章运动学问题 $\\mathbf Q$ 的函数。`Q_discrete_white_noise` 有三个参数：`dim` 指定矩阵维数，`dt` 为时间步（秒），`var` 为噪声方差。简要地说，它在稍后讨论的假设下离散化给定时间段内的噪声。下列代码计算方差 2.35、时间步 1 秒的白噪声 $\\mathbf Q$：

""",

47: """### 设计控制函数（Design the Control Function）

卡尔曼滤波不只滤波数据，还允许纳入机器人、飞机等系统的控制输入。假设控制机器人，每时间步根据当前位置与期望位置发送转向与速度信号。卡尔曼滤波方程把这种知识纳入滤波，基于当前速度与驱动电机控制输入形成预测位置。记住，我们 *从不* 丢弃信息。

对线性系统，控制输入效应可用线性方程组描述，用线性代数表达为

$$\\Delta\\mathbf x = \\mathbf{Bu}$$

$\\mathbf u$ 是 *控制输入（control input）*，$\\mathbf B$ 是 *控制输入模型（control input model）* 或 *控制函数（control function）*。例如 $\\mathbf u$ 可能是控制轮子电机转速的电压，乘以 $\\mathbf B$ 得到 $\\Delta[\\begin{smallmatrix}x\\\\\\dot x\\end{smallmatrix}]$。换言之，它计算控制输入使 $\\mathbf x$ 变化多少。

因此先验均值的完整卡尔曼滤波方程为

$$\\mathbf{\\bar x} = \\mathbf{Fx} + \\mathbf{Bu}$$

调用 `KalmanFilter.predict()` 时计算的就是该方程。

你的狗可能训练听语音指令。现有证据表明我的狗完全没有控制输入，故把 $\\mathbf B$ 设为零。Python 写法：

""",

49: "把 $\\mathbf B$ 与 $\\mathbf u$ 设为零并非必须，因为 `predict` 默认用 0：\n",

52: """
#### 预测：小结（Prediction: Summary）

作为设计者，需指定矩阵：

* $\\mathbf x$, $\\mathbf P$：状态与协方差
* $\\mathbf F$,  $\\mathbf Q$：过程模型与噪声协方差
* $\\mathbf{B,u}$：可选，控制输入与函数

""",

53: """## 更新步（Update Step）

现在可实现滤波的更新步。只需再提供两个矩阵，且不难理解。

### 设计测量函数（Design the Measurement Function）

卡尔曼滤波在所谓 *测量空间（measurement space）* 中计算更新步。一维章我们 largely 忽略该问题因其增加复杂性。用报告位置的传感器跟踪狗，计算 *残差（residual）* 很简单——滤波器预测位置减测量：

$$ \\mathtt{residual} = \\mathtt{measured\\, \\, position} - \\mathtt{predicted\\, \\, position}$$

需计算残差，因为要乘以卡尔曼增益得到新估计。

若用输出电压对应温度读数的温度计跟踪温度，残差计算无意义——不能从电压减温度。

$$ \\mathtt{residual} = \\mathtt{voltage} - \\mathtt{temperature}\\;\\;\\;(NONSENSE!)$$


需把温度转换成电压才能做减法。对温度计可写：

```python
CELSIUS_TO_VOLTS = 0.21475
residual = voltage - (CELSIUS_TO_VOLTS * predicted_temperature)
```
    
卡尔曼滤波通过让你提供把状态转换为测量的 *测量函数（measurement function）* 推广该问题。

为何在测量空间工作？为何不把电压转成温度，让残差是温度差？

因为大多数测量 *不可逆（invertible）*。跟踪问题的状态含隐变量 $\\dot x$。无法把位置测量转换成含速度的状态。反之，含位置与速度的状态可平凡地转换成仅含位置的等价“测量”。必须在测量空间工作才能计算残差。

测量 $\\mathbf z$ 与状态 $\\mathbf x$ 都是向量，需用矩阵做转换。卡尔曼滤波执行该步的方程为：

$$\\mathbf y = \\mathbf z - \\mathbf{H \\bar x}$$

$\\mathbf y$ 是残差，$\\mathbf{\\bar x}$ 是先验，$\\mathbf z$ 是测量，$\\mathbf H$ 是测量函数。取先验，用 $\\mathbf H$ 乘转成测量，再从测量中减去。得到预测与测量在测量空间中的差！
<img src="./figs/residual_chart_with_h.png">

""",

54: """需设计 $\\mathbf H$ 使 $\\mathbf{H\\bar x}$ 产生测量。本题传感器测位置，$\\mathbf z$ 为一维向量：

$$\\mathbf z = \\begin{bmatrix}z\\end{bmatrix}$$

残差方程形如

$$
\\begin{aligned}
\\textbf{y} &= \\mathbf z - \\mathbf{H\\bar x}  \\\\
\\begin{bmatrix}y \\end{bmatrix} &= \\begin{bmatrix}z\\end{bmatrix} - \\begin{bmatrix}?&?\\end{bmatrix} \\begin{bmatrix}x \\\\ \\dot x\\end{bmatrix}
\\end{aligned}
$$

$\\mathbf H$ 须为 1×2 矩阵，使 $\\mathbf{Hx}$ 为 1×1。回忆 $m\\times n$ 乘 $n\\times p$ 得 $m\\times p$ 矩阵。

要把位置 $x$ 乘 1 得到对应位置测量。求对应测量不需要速度，故 $\\dot x$ 乘 0。

$$\\begin{aligned}
\\textbf{y} &= \\mathbf z - \\begin{bmatrix}1&0\\end{bmatrix} \\begin{bmatrix}x \\\\ \\dot x\\end{bmatrix} \\\\
&= [z] - [x]
\\end{aligned}$$

对本卡尔曼滤波设

$$\\mathbf H=\\begin{bmatrix}1&0\\end{bmatrix}$$

""",

56: "我们已设计滤波器的大部分。剩下为传感器噪声建模。\n",

57: """#### 设计测量（Design the Measurement）

测量用 $\\mathbf z$（测量均值）与 $\\mathbf R$（测量协方差）实现。

$\\mathbf z$ 很简单，含测量向量。只有一个测量：

$$\\mathbf z = \\begin{bmatrix}z\\end{bmatrix}$$

若有两个传感器或测量：

$$\\mathbf z = \\begin{bmatrix}z_1 \\\\ z_2\\end{bmatrix}$$


*测量噪声矩阵（measurement noise matrix）* 用协方差矩阵建模传感器噪声。实践中可能困难。复杂系统传感器多，相关性可能不清，噪声常非纯高斯。例如传感器在高温时偏高，噪声在均值两侧分布不均。稍后学习处理这些问题。

卡尔曼滤波方程用协方差矩阵 $\\mathbf R$ 表示测量噪声。矩阵维数为 $m{\\times}m$，$m$ 为传感器数。它是协方差矩阵以计入传感器间相关性。我们只有一个传感器，$\\mathbf R$ 为：

$$\\mathbf R = \\begin{bmatrix}\\sigma^2_z\\end{bmatrix}$$

若 $\\sigma^2_z$ 为 5 平方米，$\\mathbf R = \\begin{bmatrix}5\\end{bmatrix}$。

若有两个位置传感器，第一个方差 5 m$^2$，第二个 3 m$^2$，写作

$$\\mathbf R = \\begin{bmatrix}5&0\\\\0&3\\end{bmatrix}$$

方差在对角线上，因为这是 *协方差* 矩阵：方差在对角，协方差（若有）在非对角。此处假设两传感器噪声不相关，协方差为 0。

本题只有一个传感器，可实现为

""",

59: "通过调用 `update` 执行更新。\n",

61: "跟踪所有这些变量很繁琐，故 FilterPy 还用类 `KalmanFilter` 实现滤波。本书其余部分我用该类，但希望你见过这些函数的过程形式，因为我知道有些人不喜欢面向对象编程。\n",

62: """## 实现卡尔曼滤波（Implementing the Kalman Filter）

我已给出滤波器全部代码，现在集中在一处。先构造 `KalmanFilter` 对象。用 `dim_x` 指定状态变量数，`dim_z` 指定测量数。我们有两个随机状态变量、一个测量，写作：

```python
from filterpy.kalman import KalmanFilter
dog_filter = KalmanFilter(dim_x=2, dim_z=1)
```

这会创建对象，所有卡尔曼滤波矩阵为默认值：

""",

64: "现在用对本问题有效的值初始化滤波器矩阵与向量。我放在函数里，便于你为 `R`、`P`、`Q` 指定不同初值，省去重复劳动。我们会创建并运行许多滤波器。\n",

66: "`KalmanFilter` 把 `R`、`P`、`Q` 初始化为单位矩阵，故 `kf.P *= P` 可快速把所有对角元设为同一标量。现在创建滤波器：\n",

68: "可在命令行输入变量名，检查滤波器所有属性的当前值。\n",

70: "剩下写运行卡尔曼滤波的代码。\n",

}
