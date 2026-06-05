#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Appendix E & G markdown translations."""

from pathlib import Path

from nb_translate_utils import ZH_CN, load_notebook, save_notebook, apply_markdown_translations

E = {
    0: "[目录（Table of Contents）](./table_of_contents.ipynb)",
    1: "# 集总卡尔曼滤波（Ensemble Kalman Filter, EnKF）",
    4: """> 我对集总滤波（ensemble filter）并不十分熟悉。我为本书实现了一个，并让它跑通了，但我从未在实际项目中使用过。不同资料给出的方程形式略有差异。若我按资料中的方程实现，滤波器就无法工作。有可能是我做错了什么。不过，在网上多处我也看到有人评论说，他们为了让滤波器工作，做了与我类似的事情。简而言之，我并不真正理解这个主题，但选择如实呈现我的不足，而不是一笔带过。我希望将来能掌握这一主题，并写出更权威的章节。本章末尾我记录了自己目前的困惑与问题。无论如何，若我被这些资料搞糊涂了，你也许也会，因此记录这些困惑或许能帮你避免同样的坑。


集总卡尔曼滤波（Ensemble Kalman Filter, EnKF）与上一章的无迹卡尔曼滤波（Unscented Kalman Filter, UKF）非常相似。若你记得，UKF 使用一组按确定性规则选取的加权 sigma 点，通过非线性状态函数与测量函数。sigma 点经过函数后，我们求其均值与协方差（covariance），并以此作为滤波器新的均值与协方差。这只是对真实值的近似，因而次优（suboptimal），但实践中滤波器往往非常准确。它常能比扩展卡尔曼滤波（Extended Kalman Filter, EKF）给出更精确的估计，且不必解析推导状态方程与测量方程的线性化。

集总卡尔曼滤波的工作方式类似，不同之处在于它用*蒙特卡洛（Monte Carlo）*方法选取大量 sigma 点。它源于地球物理科学，用于对海洋、大气等需要极大状态与系统规模的建模。SIAM News 上有一篇关于其在天气预报中发展的有趣文章 [1]。滤波器启动时，在滤波器初始状态附近随机生成大量点。该分布与滤波器协方差 $\\mathbf{P}$ 成比例。换言之，68% 的点落在均值一个标准差以内，95% 落在两个标准差以内，依此类推。我们在二维中看一下。将使用 `numpy.random.multivariate_normal()` 从均值 (5, 3) 及协方差

$$\\begin{bmatrix}
32 & 15 \\\\ 15 & 40
\\end{bmatrix}$$

所对应的多变量正态分布中随机抽取点。

我绘制了表示两个标准差的协方差椭圆，以说明点的分布情况。""",
    6: "## 算法",
    7: """如前所述，滤波器初始化时，从初始状态（$\\mathbf{x}$）与协方差（$\\mathbf{P}$）中抽取大量 sigma 点。此后算法与 UKF 非常相似。在预测（prediction）步，sigma 点通过状态转移函数，并加上少量噪声以体现过程噪声（process noise）。在更新（update）步，sigma 点通过测量函数映射到测量空间，并加上少量噪声以体现测量噪声（measurement noise）。再由协方差计算卡尔曼增益（Kalman gain）。

我们已提到 UKF 与 EnKF 的主要区别：UKF 按确定性规则选取 sigma 点。还有另一处区别，由上算法隐含：UKF 在每次预测步都会生成新的 sigma 点，点经非线性函数后，用*无迹变换（unscented transform）*重组为均值与协方差。EnKF 则持续传播最初创建的 sigma 点；我们只需计算均值与协方差作为滤波器输出！

来看滤波器方程。照例省略常见的下标与上标；这里表达的是算法，而非数学函数。$N$ 为 sigma 点个数，$\\chi$ 为 sigma 点集合。""",
    8: "### 初始化步",
    9: """$$\\boldsymbol\\chi \\sim \\mathcal{N}(\\mathbf{x}_0, \\mathbf{P}_0)$$

表示从滤波器初始均值与协方差中选取 sigma 点。代码中可能如下：

```python
N = 1000
sigmas = multivariate_normal(mean=x, cov=P, size=N)
```""",
    10: "### 预测步",
    11: """$$
\\begin{aligned}
\\boldsymbol\\chi &= f(\\boldsymbol\\chi, \\mathbf{u}) + v_Q \\\\
\\mathbf{x} &= \\frac{1}{N} \\sum_1^N \\boldsymbol\\chi
\\end{aligned}
$$

简短，但或许不够直观。第一行将所有 sigma 点通过用户提供的的状态转移函数，再按 $\\mathbf{Q}$ 矩阵分布加入噪声。Python 中可写为

```python
for i, s in enumerate(sigmas):
    sigmas[i] = fx(x=s, dt=0.1, u=0.)

sigmas += multivariate_normal(x, Q, N)
```

第二行由 sigma 点计算均值。Python 中可用 `numpy.mean` 简洁快速地完成。

```python
x = np.mean(sigmas, axis=0)
```""",
    12: """我们可选取计算均值的协方差。算法本身不必计算该值，但分析时常有用。方程为

$$\\mathbf{P} = \\frac{1}{N-1}\\sum_1^N[\\boldsymbol\\chi-\\mathbf{x}^-][\\boldsymbol\\chi-\\mathbf{x}^-]^\\mathsf{T}$$

$\\boldsymbol\\chi-\\mathbf{x}^-$ 是一维向量，因此用 `numpy.outer` 计算 $[\\boldsymbol\\chi-\\mathbf{x}^-][\\boldsymbol\\chi-\\mathbf{x}^-]^\\mathsf{T}$ 项。Python 中可写为

```python
    P = 0
    for s in sigmas:
        P += outer(s-x, s-x)
    P = P / (N-1)
```""",
    13: "### 更新步",
    14: """在更新步中，将 sigma 点通过测量函数，计算 sigma 点的均值与协方差，由协方差计算卡尔曼增益，再用卡尔曼增益缩放残差（residual）以更新卡尔曼状态。方程为

$$
\\begin{aligned}
\\boldsymbol\\chi_h &= h(\\boldsymbol\\chi, u)\\\\
\\mathbf{z}_{mean} &= \\frac{1}{N}\\sum_1^N \\boldsymbol\\chi_h \\\\ \\\\
\\mathbf{P}_{zz} &= \\frac{1}{N-1}\\sum_1^N [\\boldsymbol\\chi_h - \\mathbf{z}_{mean}][\\boldsymbol\\chi_h - \\mathbf{z}_{mean}]^\\mathsf{T} + \\mathbf{R} \\\\
\\mathbf{P}_{xz} &= \\frac{1}{N-1}\\sum_1^N [\\boldsymbol\\chi - \\mathbf{x}^-][\\boldsymbol\\chi_h - \\mathbf{z}_{mean}]^\\mathsf{T} \\\\
\\\\
\\mathbf{K} &= \\mathbf{P}_{xz} \\mathbf{P}_{zz}^{-1}\\\\ 
\\boldsymbol\\chi & = \\boldsymbol\\chi + \\mathbf{K}[\\mathbf{z} -\\boldsymbol\\chi_h + \\mathbf{v}_R] \\\\ \\\\
\\mathbf{x} &= \\frac{1}{N} \\sum_1^N \\boldsymbol\\chi \\\\
\\mathbf{P} &= \\mathbf{P} - \\mathbf{KP}_{zz}\\mathbf{K}^\\mathsf{T}
\\end{aligned}
$$""",
    15: """这与线性卡尔曼滤波（linear KF）和 UKF 非常相似。我们逐行说明。

第一行

$$\\boldsymbol\\chi_h = h(\\boldsymbol\\chi, u),$$

仅将 sigma 点通过测量函数 $h$。结果点记为 $\\chi_h$，以区别于 sigma 点。Python 中可写为

```python
sigmas_h = h(sigmas, u)
```""",
    16: """下一行计算测量 sigma 的均值。

$$\\mathbf{z}_{mean} = \\frac{1}{N}\\sum_1^N \\boldsymbol\\chi_h$$

Python 中写为

```python
z_mean = np.mean(sigmas_h, axis=0)
```
    
有了测量 sigma 的均值，即可计算每个测量 sigma 点的协方差，以及测量 sigma 点与 sigma 点之间的*交叉协方差（cross variance）*。由下式表达

$$
\\begin{aligned}
\\mathbf{P}_{zz} &= \\frac{1}{N-1}\\sum_1^N [\\boldsymbol\\chi_h - \\mathbf{z}_{mean}][\\boldsymbol\\chi_h - \\mathbf{z}_{mean}]^\\mathsf{T} + \\mathbf{R} \\\\
\\mathbf{P}_{xz} &= \\frac{1}{N-1}\\sum_1^N [\\boldsymbol\\chi - \\mathbf{x}^-][\\boldsymbol\\chi_h - \\mathbf{z}_{mean}]^\\mathsf{T}
\\end{aligned}$$

Python 中可写为

```python
P_zz = 0
for sigma in sigmas_h:
    s = sigma - z_mean
    P_zz += outer(s, s)
P_zz = P_zz / (N-1) + R

P_xz = 0
for i in range(N):
    P_xz += outer(self.sigmas[i] - self.x, sigmas_h[i] - z_mean)
P_xz /= N-1
```""",
    17: """卡尔曼增益的计算很直接：$\\mathbf{K} = \\mathbf{P}_{xz} \\mathbf{P}_{zz}^{-1}$。

Python 中为

```python
K = P_xz @ inv(P_zz)
```""",
    18: """接下来，用下式更新 sigma 点：

$$\\boldsymbol\\chi  = \\boldsymbol\\chi + \\mathbf{K}[\\mathbf{z} -\\boldsymbol\\chi_h + \\mathbf{v}_R]$$ 

这里 $\\mathbf{v}_R$ 是我们加到 sigma 点上的扰动。Python 中可实现为

```python
v_r = multivariate_normal([0]*dim_z, R, N)
for i in range(N):
    sigmas[i] += K @ (z + v_r[i] - sigmas_h[i])
```


最后一步是重新计算滤波器的均值与协方差。

```python
    x = np.mean(sigmas, axis=0)
    P = self.P - K @ P_zz @ K.T
```""",
    19: "## 实现与示例",
    20: """我在 `FilterPy` 库中实现了 EnKF。它在很多方面只是个玩具。用大量 sigma 点滤波性能很慢。此外，文献中对算法有许多细微变体。我写它主要是因为想学习这种滤波器。我未将其用于真实问题，也无法就如何将其用于其所适用的大规模问题提供建议。因此我将评论限于实现一个非常简单的滤波器：用它跟踪一维物体，并将输出与线性卡尔曼滤波比较。这是本书中已多次设计过的滤波器，故不再赘述。状态向量为

$$\\mathbf{x} = \\begin{bmatrix}x\\\\ \\dot{x}\\end{bmatrix}$$

状态转移函数为

$$\\mathbf{F} = \\begin{bmatrix}1&1\\\\0&1\\end{bmatrix}$$

测量函数为

$$\\mathbf{H} = \\begin{bmatrix}1&0\\end{bmatrix}$$

EnKF 面向非线性问题，因此不用矩阵实现状态转移与测量函数，而需提供 Python 函数。对本问题可写为：

```python
def hx(x):
    return np.array([x[0]])

def fx(x, dt):
    return F @ x
```

最后一点：EnKF 代码与 UKF 代码一样，对 $\\mathbf{x}$ 使用一维表示，而非线性卡尔曼滤波代码所用的二维列矩阵。

闲话少说，下面是代码。""",
    22: "不难看出，KF 与 EnKF 起初略有差异，但很快收敛到几乎相同的值。EnKF 是次优滤波器，不会产生 KF 的最优解。不过，我故意将 $N$ 选得很小（20），以保证 EnKF 输出明显次优。若选更合理的数目如 2000，在这张图上你将看不出两种滤波器输出的差别。",
    23: "## 未决问题",
    24: """以下应视为*我*的问题，而非文献中悬而未决的问题。不过，我直接抄录了该领域知名文献中的方程，它们并未解释这些差异。

首先，Brown [2] 中所有求和都乘以 $\\frac{1}{N}$，例如

$$ \\hat{x} = \\frac{1}{N}\\sum_{i=1}^N\\chi_k^{(i)}$$

Crassidis [3] 中同一方程（记号与 Brown 相同，尽管 Crassidis 的写法不同）为

$$ \\hat{x} = \\frac{1}{N-1}\\sum_{i=1}^N\\chi_k^{(i)}$$

协方差计算中的求和在两处文献中同样如此。Crassidis 在讨论滤波器协方差时指出，使用 $N-1$ 是为了得到无偏估计。给定 Crassidis 第 2 页关于均值与标准差的标准方程，对协方差而言这是合理的。

$$
\\begin{aligned}
\\mu &= \\frac{1}{N}\\sum_{i=1}^N[\\tilde{z}(t_i) - \\hat{z}(t_i)] \\\\
 \\sigma^2 &= \\frac{1}{N-1}\\sum_{i=1}^N\\{[\\tilde{z}(t_i) - \\hat{z}(t_i)] - \\mu\\}^2
\\end{aligned}
$$

然而，我看不出用 $N-1$ 计算均值的理由。若在滤波器中对均值使用 $N-1$，滤波器不收敛，状态实质上跟随测量而几乎不滤波。但我确实看到对协方差使用 $N-1$ 的理由，与 Brown 形成对比，这与 Crassidis 一致。同样，我的决定有实证支持——$N-1$ 在滤波器实现中有效，$N$ 则不行。

第二个问题与 $\\mathbf{R}$ 矩阵的使用有关。Brown 将 $\\mathbf{R}$ 加到 $\\mathbf{P}_{zz}$，而 Crassidis 及其他来源则不加。我在网上读到其他实现者的笔记，说加上 R 有助于滤波器，这在我看来合理且必要，因此我这样做。

第三个问题与协方差 $\\mathbf{P}$ 的计算有关。Crassidis 与 Brown 的方程再次不同。我选择了 Brown 中的实现，因为它似乎给出我预期的行为（$\\mathbf{P}$ 随时间收敛），且与线性 KF 的形式非常接近。相比之下，我发现 Crassidis 的方程似乎收敛性较差。

第四个问题与状态估计更新有关。Brown 中为

$$\\boldsymbol\\chi  = \\boldsymbol\\chi + \\mathbf{K}[\\mathbf{z} -\\mathbf{z}_{mean} + \\mathbf{v}_R]$$ 

而 Crassidis 中为

$$\\boldsymbol\\chi  = \\boldsymbol\\chi + \\mathbf{K}[\\mathbf{z} -\\boldsymbol\\chi_h + \\mathbf{v}_R]$$ 

在我看来 Crassidis 的方程更合理，且对线性问题产生与线性 KF 表现相近的滤波器，因此我选择了该形式。

我不愿说哪本书错了；完全可能是我漏掉了使各方程都成立的关键点。我只能说，按原文实现时我得不到能工作的滤波器。我定义的「工作」指：对线性问题表现与线性 KF 基本相同。通过阅读网上的实现笔记并对各种问题推理，我选择了本章的实现，它确实似乎工作正常。我尚未深入探索可能明确解释这些差异的大量原始文献。即使将来找到能调和各种差异的解释，我也希望以某种形式保留这些内容——若我被这些书搞糊涂，大概其他人也会。""",
    25: "## 参考文献",
    26: """- [1] Mackenzie, Dana. *Ensemble Kalman Filters Bring Weather Models Up to Date* Siam News,  Volume 36, Number 8, October 2003. http://www.siam.org/pdf/news/362.pdf

- [2]  Brown, Robert Grover, and Patrick Y.C. Hwang. *Introduction to Random Signals and Applied Kalman Filtering, With MATLAB® excercises and solutions.* Wiley, 2012.

- [3] Crassidis, John L., and John L. Junkins. *Optimal estimation of dynamic systems*. CRC press, 2011.""",
}

G = {
    0: "[目录（Table of Contents）](./table_of_contents.ipynb)",
    1: "# 设计非线性卡尔曼滤波（Designing Nonlinear Kalman Filters）",
    4: "## 引言",
    5: "**作者注：我最初计划写一章比较各种方法的设计非线性章节。这可能会写也可能不会，目前本章没有实用内容，建议暂不阅读。**",
    6: "我们看到卡尔曼滤波（Kalman filter）能合理地跟踪球体。但如前所述，这是个可笑的示例；在真空中我们可以任意精确地预测轨迹；在此例中使用卡尔曼滤波是多余的复杂化。",
    7: "### 含空气阻力的卡尔曼滤波",
    8: """我将不再采用「步骤 1、步骤 2」式写法，而以你在非玩具工程问题中会用的更自然方式推进。我们已开发出在真空中出色跟踪球的卡尔曼滤波，但该模型未纳入空气阻力（air drag）效应。我们知道过程模型（process model）由 $\\textbf{F}$ 实现，因此立刻转向 $\\textbf{F}$。

概念上，$\\textbf{F}$ 所做的是

$$x' = Fx$$

无空气阻力时，我们有

$$
\\mathbf{F} = \\begin{bmatrix}
1 & \\Delta t & 0 & 0 & 0 \\\\
0 & 1 & 0 & 0 & 0 \\\\
0 & 0 & 1 & \\Delta t & \\frac{1}{2}{\\Delta t}^2 \\\\
0 & 0 & 0 & 1 & \\Delta t \\\\
0 & 0 & 0 & 0 & 1
\\end{bmatrix}
$$""",
    9: """对应于方程

$$ 
\\begin{aligned}
x &= x + v_x \\Delta t \\\\
v_x &= v_x \\\\
\\\\
y &= y + v_y \\Delta t + \\frac{a_y}{2} {\\Delta t}^2 \\\\
v_y &= v_y + a_y \\Delta t \\\\
a_y &= a_y
\\end{aligned}
$$""",
    10: """由上节可知，新的欧拉方程必须为

$$ 
\\begin{aligned}
x &= x + v_x \\Delta t \\\\
v_x &= v_x \\\\
\\\\
y &= y + v_y \\Delta t + \\frac{a_y}{2} {\\Delta t}^2 \\\\
v_y &= v_y + a_y \\Delta t \\\\
a_y &= a_y
\\end{aligned}
$$""",
    11: "## 更真实的二维位置传感器",
    12: """上一示例中的位置传感器并不很真实。通常没有能提供 (x,y) 坐标的「原始」传感器。我们有 GPS，但 GPS 本身已用卡尔曼滤波生成滤波输出；除非加入额外传感器提供更多信息，否则我们不应指望再通过另一个卡尔曼滤波改进信号。该问题稍后讨论。

考虑如下布置。在开阔场地放置两个已知位置的发射机，各发射可检测的信号。我们处理信号并确定与发射机的距离，带一定噪声。先看示意图。""",
    14: """我试图展示：红色发射机 A 位于 (-4,0)，蓝色发射机 B 位于 (4,0)。红蓝圆表示发射机到机器人的距离，圆环宽度体现各发射机 $1\\sigma$ 角度误差的影响。此处我给蓝色发射机更大的误差。机器人最可能的位置是两圆相交处，我用红蓝线标出。你会反对说有两个交点而非一个，设计测量函数时我们会看到如何处理。

这是极常见的传感器配置。飞机仍用此系统导航，称为 DME（Distance Measuring Equipment，测距设备）。如今 GPS 更常见，但我曾在飞机上工作，将此类传感器与 GPS、INS、高度计等一并融入滤波器。稍后讨论*多传感器融合（multi-sensor fusion）*；现在只处理这一简单配置。

第一步是设计状态变量（state variables）。假设机器人以恒定速度直线行驶。长时间内这未必成立，但短时段可接受。这与前一问题相同——我们要跟踪机器人的位置与速度。因此

$$\\mathbf{x} = 
\\begin{bmatrix}x\\\\v_x\\\\y\\\\v_y\\end{bmatrix}$$

下一步设计状态转移函数（state transition function）。也与前一问题相同，故直接给出

$$
\\mathbf{x}' = \\begin{bmatrix}1& \\Delta t& 0& 0\\\\0& 1& 0& 0\\\\0& 0& 1& \\Delta t\\\\ 0& 0& 0& 1\\end{bmatrix}\\mathbf{x}$$

下一步设计控制输入。我们没有，故设 ${\\mathbf{B}}=0$。

下一步设计测量函数 $\\mathbf{z} = \\mathbf{Hx}$。可用勾股定理建模测量。

$$
z_a = \\sqrt{(x-x_A)^2 + (y-y_A)^2} + v_a\\\\[1em]
z_b = \\sqrt{(x-x_B])^2 + (y-y_B)^2} + v_b
$$

其中 $v_a$、$v_b$ 为白噪声。

我们立刻看到问题：卡尔曼滤波面向线性方程，而上式显然非线性（nonlinear）。后续章节将讨论多种稳健处理非线性的方法，但眼下采用更简单的做法：若已知机器人近似位置，可在该点附近将这些方程线性化。我本可现在发展该技巧的广义数学，但先给出算例以便为后续发展提供背景。""",
    15: """我们不直接计算 $\\mathbf{H}$，而计算 $\\mathbf{H}$ 对机器人位置 $\\mathbf{x}$ 的偏导数。你可能熟悉偏导数概念；若不然，它表示 $\\mathbf{H}$ 随机器人位置如何变化。计算为 $\\mathbf{H}$ 的偏导数：

$$\\frac{\\partial \\mathbf{h}}{\\partial \\mathbf{x}} = 
\\begin{bmatrix}
\\frac{\\partial h_1}{\\partial x_1} & \\frac{\\partial h_1}{\\partial x_2} &\\dots \\\\
\\frac{\\partial h_2}{\\partial x_1} & \\frac{\\partial h_2}{\\partial x_2} &\\dots \\\\
\\vdots & \\vdots
\\end{bmatrix}
$$

先算第一个偏导。要求

$$\\frac{\\partial }{\\partial x} \\sqrt{(x-x_A)^2 + (y-y_A)^2}
$$

计算为

$$
\\begin{aligned}
\\frac{\\partial h_1}{\\partial x} &= ((x-x_A)^2 + (y-y_A)^2))^\\frac{1}{2} \\\\
&= \\frac{1}{2}\\times 2(x-x_a)\\times ((x-x_A)^2 + (y-y_A)^2))^{-\\frac{1}{2}} \\\\
&= \\frac{x_r - x_A}{\\sqrt{(x_r-x_A)^2 + (y_r-y_A)^2}} 
\\end{aligned}
$$

继续对两个距离方程关于 $x$、$y$、$dx$、$dy$ 求偏导，得到

$$\\frac{\\partial\\mathbf{h}}{\\partial\\mathbf{x}}=
\\begin{bmatrix}
\\frac{x_r - x_A}{\\sqrt{(x_r-x_A)^2 + (y_r-y_A)^2}} & 0 & 
\\frac{y_r - y_A}{\\sqrt{(x_r-x_A)^2 + (y_r-y_A)^2}} & 0 \\\\
\\frac{x_r - x_B}{\\sqrt{(x_r-x_B)^2 + (y_r-y_B)^2}} & 0 &
\\frac{y_r - y_B}{\\sqrt{(x_r-x_B)^2 + (y_r-y_B)^2}} & 0 \\\\
\\end{bmatrix}
$$

这相当繁琐，而方程已很简单。对更复杂系统，计算雅可比（Jacobian）可能极难甚至不可能。不过，可用 SymPy 模块 [1] 让 Python 代劳。SymPy 是 Python 符号数学库，能力超出本书范围，但可做代数、积分、微分、求微分方程解等。我们将用它计算雅可比！

先举简单例子。导入 SymPy，初始化漂亮打印（用 LaTeX 输出方程），再声明 NumPy 使用的符号。""",
    17: "注意我们对符号 `phi` 使用 LaTeX 表达式。非必须，但若这样做输出时会渲染为 LaTeX。现在做点数学：$\\sqrt{\\phi}$ 的导数是多少？",
    19: "我们可以因式分解方程。",
    21: "SymPy 功能众多，尽管我喜欢探索其特性，本书无法一一涵盖。下面计算我们的雅可比。",
    23: """简而言之，(0,0) 项是机器人 x 坐标与发射机 A 的 x 坐标之差，除以机器人与 A 的距离。(2,0) 类似，但是机器人与发射机的 y 坐标。底行对发射机 B 做同样计算。0 项对应状态变量的速度分量；距离测量自然不提供速度。

该矩阵中的值随机器人位置变化，因此不再是常数；滤波器每个时间步都需重新计算。

若仔细看，这不过是 x/dist 与 y/dist 的计算，故可不失一般性地改为三角形式：

$$\\frac{\\partial\\mathbf{h}}{\\partial\\mathbf{x}}=
\\begin{bmatrix}
-\\cos{\\theta_A} & 0 & -\\sin{\\theta_A} & 0 \\\\
-\\cos{\\theta_B} & 0 & -\\sin{\\theta_B} & 0
\\end{bmatrix}
$$

然而这带来巨大问题。我们不再计算 $\\mathbf{H}$，而是 $\\Delta\\mathbf{H}$，即 $\\mathbf{H}$ 的变化。若不经修改其余设计就把这代入卡尔曼滤波，输出将毫无意义。例如，我们用 $\\mathbf{Hx}$ 生成给定 $\\mathbf{x}$ 估计下的测量；但现在 $\\mathbf{H}$ 已在我们位置附近线性化，它包含的是测量函数的*变化*。

因此我们必须对状态变量使用 $\\mathbf{x}$ 的*变化*。于是必须回头重新设计状态变量。

>请注意，这在设计卡尔曼滤波时完全正常。教科书把此类例子呈现为*既成事实*，仿佛状态变量显然应是速度而非位置。或许做够这类问题后这的确显而易见，但那时为何还要读教科书？我常把一篇讲解读好几遍，琢磨他们为何做某选择，最后才意识到是因为下一页的某种后果。我的叙述更长，但反映设计滤波器时的真实过程：你做出看似合理的设计选择，推进时发现某些性质要求你重做先前的步骤。因此我将一定程度上放弃「步骤 1」「步骤 2」式写法，因为许多真实问题并非如此直截了当。""",
    24: """若状态变量包含机器人速度而非位置，我们如何跟踪机器人在哪？不能。以这种方式线性化的卡尔曼滤波使用所谓*标称轨迹（nominal trajectory）*——即假设一个位置并跟踪方向，再用速度与加速度的变化计算该轨迹的变化。还能怎样？回想两距离圆相交的图——有两个相交区域。若两发射机非常靠近，相交处会是两个很长的月牙形。按当前设计，仅靠到发射机的距离测量，该卡尔曼滤波无法知道你的真实位置。你也许已在想绕过此问题的方法。若如此，请继续关注，后续章节会提供这些技巧。一次性给出完整解法在我看来更易困惑而非洞察。

因此重新设计*状态转移函数（state transition function）*。假设恒速、无加速度，状态方程为
$$
\\dot{x}' = \\dot{x} \\\\
\\ddot{x}' = 0 \\\\
\\dot{y}' = \\dot{y} \\\\
\\dot{y}' = 0$$

由此得到*状态转移函数*

$$
\\mathbf{F} = \\begin{bmatrix}0 &1 & 0& 0\\\\0& 0& 0& 0\\\\0& 0& 0& 1\\\\ 0& 0& 0& 0\\end{bmatrix}$$

最后一项复杂之处来自我们输入的测量。$\\mathbf{Hx}$ 现在计算的是相对标称位置的测量*变化*，因此输入的测量不应是到 A、B 的距离，而应是测量距离相对标称位置的距离*变化*。

内容较多，我们逐段看代码。先定义函数，在每个时间步计算 $\\frac{\\partial\\mathbf{h}}{\\partial\\mathbf{x}}$。""",
    26: "现在需要创建模拟传感器。",
    28: "最后可以写卡尔曼滤波代码。我将发射机放在 x=-100 和 100，y 均为 -20。这样机器人移动时两发射机都能提供良好三角测量。机器人从 (0,0) 出发，每步移动 (1,1)。",
    30: "## 线性化卡尔曼滤波",
    31: "既然已看过线性化卡尔曼滤波的示例，我们可以更好地理解其数学。我们从假设某个函数 $\\mathbf f$ 开始",
    32: "## 示例：下落球",
    33: "**作者注：本节暂时跳过。**\n\n在 **Designing Kalman Filters** 一章中，我先考虑在真空中跟踪球，再在空气中跟踪。卡尔曼滤波在真空中表现很好，但在空气中偏离球的路径。来看输出；为避免在本章堆砌该章代码，已全部放在 `ekf_internal.py` 文件中。",
    35: """我们可以人为增大 $Q$ 迫使卡尔曼滤波跟踪球。这会使滤波器不信任其预测，并放大卡尔曼增益 $K$ 以强烈偏向测量。然而这不是有效做法。若卡尔曼滤波正确预测过程，我们不应通过谎称存在并不存在的过程误差来「欺骗」滤波器。某些问题、某些条件下或许能蒙混过关，但一般而言滤波器性能会次优。

回想 **Designing Kalman Filters** 一章，加速度为

$$a_x = (0.0039 + \\frac{0.0058}{1+\\exp{[(v-35)/5]}})*v*v_x \\\\
a_y = (0.0039 + \\frac{0.0058}{1+\\exp{[(v-35)/5]}})*v*v_y- g
$$

在学习本主题时，这些方程将*非常*难处理，因此暂时退到更简单的一维问题，使用不考虑阻力系数非线性的简化加速度方程：

$$\\begin{aligned}
\\ddot{y} &= \\frac{0.0034ge^{-y/20000}\\dot{y}^2}{2\\beta} - g \\\\
\\ddot{x} &= \\frac{0.0034ge^{-x/20000}\\dot{x}^2}{2\\beta}
\\end{aligned}$$

其中 $\\beta$ 为弹道系数（ballistic coefficient），数值越大表示阻力越小。""",
    36: """这仍是非线性的，因此需在现状态点将该方程线性化。若状态为位置与速度，需要 $\\mathbf{x}$ 的任意小变化方程，例如：

$$ \\begin{bmatrix}\\Delta \\dot{x} \\\\ \\Delta \\ddot{x} \\\\ \\Delta \\dot{y} \\\\ \\Delta \\ddot{y}\\end{bmatrix} = 
\\large\\begin{bmatrix}
\\frac{\\partial \\dot{x}}{\\partial x} & 
\\frac{\\partial \\dot{x}}{\\partial \\dot{x}} & 
\\frac{\\partial \\dot{x}}{\\partial y} & 
\\frac{\\partial \\dot{x}}{\\partial \\dot{y}} \\\\ 
\\frac{\\partial \\ddot{x}}{\\partial x} & 
\\frac{\\partial \\ddot{x}}{\\partial \\dot{x}}& 
\\frac{\\partial \\ddot{x}}{\\partial y}& 
\\frac{\\partial \\dot{x}}{\\partial \\dot{y}}\\\\
\\frac{\\partial \\dot{y}}{\\partial x} & 
\\frac{\\partial \\dot{y}}{\\partial \\dot{x}} & 
\\frac{\\partial \\dot{y}}{\\partial y} & 
\\frac{\\partial \\dot{y}}{\\partial \\dot{y}} \\\\ 
\\frac{\\partial \\ddot{y}}{\\partial x} & 
\\frac{\\partial \\ddot{y}}{\\partial \\dot{x}}& 
\\frac{\\partial \\ddot{y}}{\\partial y}& 
\\frac{\\partial \\dot{y}}{\\partial \\dot{y}}
\\end{bmatrix}\\normalsize
\\begin{bmatrix}\\Delta x \\\\ \\Delta \\dot{x} \\\\ \\Delta \\dot{y} \\\\ \\Delta \\ddot{y}\\end{bmatrix}$$

方程不同时含 x 与 y，故任何同时含二者的偏导必为零。我们还知 $\\large\\frac{\\partial \\dot{x}}{\\partial x}\\normalsize = 0$ 且 $\\large\\frac{\\partial \\dot{x}}{\\partial \\dot{x}}\\normalsize = 1$，故矩阵为

$$\\mathbf{F} = \\begin{bmatrix}0&1&0&0 \\\\
\\frac{0.0034e^{-x/22000}\\dot{x}^2g}{44000\\beta}&0&0&0
\\end{bmatrix}$$



""",
    39: """** orphan text
这种方法问题很多。首先当然是线性化不能给出精确答案。更重要的是，我们线性化的不是真实路径，而是滤波器对路径的估计。我们线性化该估计是因为它在统计上很可能正确；但当然不必正确。因此若滤波器输出很差，就会对错误估计线性化，几乎肯定导致更差的估计。此时滤波器会很快发散。这就是卡尔曼滤波「黑魔法」所在：我们试图线性化一个估计，无法保证滤波器稳定。大量卡尔曼滤波文献都致力于此问题。另一问题是须用解析方法线性化系统。对某些问题可能难以或无法找到解析解；有时能找到线性化，但计算代价很高。**


""",
    40: "## 参考文献",
    41: "[1] http://sympy.org",
}


def main():
    for name, trans in [
        ("Appendix-E-Ensemble-Kalman-Filters.ipynb", E),
        ("Appendix-G-Designing-Nonlinear-Kalman-Filters.ipynb", G),
    ]:
        path = ZH_CN / name
        nb = load_notebook(path)
        apply_markdown_translations(nb, trans)
        save_notebook(nb, path)
        print(f"已翻译: {name} ({len(trans)} cells)")


if __name__ == "__main__":
    main()
