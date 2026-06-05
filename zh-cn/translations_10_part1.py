# -*- coding: utf-8 -*-
"""10-Unscented-Kalman-Filter.ipynb markdown 译文（第 1 部分）"""

TRANSLATIONS_10_PART1 = {
0: "[目录](./table_of_contents.ipynb)\n",

1: "# 无迹卡尔曼滤波（Unscented Kalman Filter, UKF）\n",

4: """上一章讨论了非线性系统带来的困难。非线性可能出现在两处。可能在测量中，例如雷达测量到目标的斜距（slant range）。由斜距计算 x、y 坐标需要开方：

$$x=\\sqrt{\\text{slant}^2 - \\text{altitude}^2}$$

非线性也可能出现在过程模型中——例如跟踪空中飞行的球，空气阻力导致非线性行为。标准卡尔曼滤波（Kalman filter）对此类问题表现很差或完全失效。

上一章展示过类似下图。我略改方程以突出非线性效应。

""",

6: """我从输入抽取 500,000 个样本，经非线性变换后建立结果直方图。这些点称为 *sigma 点（sigma points）*。由输出直方图可计算均值与标准差，得到更新后的（尽管近似的）高斯分布。

下面展示数据经 `f(x)` 变换前后的散点图。

""",

8: """数据本身看起来是高斯的，确实如此——即围绕均值零散布的白噪声。相比之下 `g(data)` 有明确结构：两条带，中间有大量点；带外也有散点，负侧更多。

你或许想到：这种采样过程正是我们问题的解法。若每次更新生成 500,000 点、经函数变换再算均值与方差，这就是 *蒙特卡洛（Monte Carlo）* 方法，集总滤波（ensemble filter）与粒子滤波（particle filter）等会采用。采样无需专门知识，也不要求闭式解。无论函数多么非线性或行为多么糟糕，只要 sigma 点足够多就能建立准确输出分布。

“足够多”是难点。上图用 500,000 个 sigma 点，输出仍不光滑。更糟的是这只是一维；所需点数随维数幂次增长。一维若需 500 点，二维需 $500^2=250{,}000$，三维需 $500^3=125{,}000{,}000$，依此类推。此法可行但计算极贵。集总滤波与粒子滤波用 clever 技巧大幅降维，负担仍很大。无迹卡尔曼滤波（UKF）也用 sigma 点，但用确定性方法选点，计算量锐减。

""",

9: "## Sigma 点——从分布采样（Sigma Points - Sampling from a Distribution）\n",

10: """从二维协方差椭圆看问题。选 2D 只因易绘图；可推广到任意维数。假设任意非线性函数，从第一个协方差椭圆随机取点，经非线性函数变换并画新位置，再算变换点的均值与协方差，作为均值与概率分布的估计。

""",

12: """左侧椭圆表示两状态变量的 $1\\sigma$ 分布。箭头表示若干随机采样点经任意非线性函数变换到新分布。右侧半透明椭圆表示该点集的均值与方差 *估计*。

""",

13: """编写函数，将 10,000 个从高斯分布随机抽取的点

$$\\mu = \\begin{bmatrix}0\\\\0\\end{bmatrix}, 
\\Sigma=\\begin{bmatrix}32&15\\\\15&40\\end{bmatrix}$$

通过非线性系统：

$$\\begin{cases}\\begin{aligned}\\bar x&=x+y\\\\
\\bar y&= 0.1x^2 + y^2\\end{aligned} \\end{cases}$$ 

""",

15: "该图显示该函数的强非线性，以及若像扩展卡尔曼滤波（Extended Kalman Filter, EKF）那样线性化会产生的大误差（下一章学习）。\n",

16: """## 快速示例（A Quick Example）

我很快会进入 UKF 选 sigma 点与计算的数学。先看一个例子了解“终点”。

UKF 可用多种算法生成 sigma 点。FilterPy 提供若干算法，例如：

""",

18: "稍后会更清楚：该对象为给定均值与协方差生成加权 sigma 点。先看一例，点的大小表示权重：\n",

20: """可见 5 个点以均值 (3, 17) 为中心呈奇特分布。用 5 点似乎 absurd 却能与 500,000 随机点一样好甚至更好，但确实如此！

现在实现滤波器。先做一维标准线性滤波；尚未准备好非线性。设计与迄今所学差别不大，但有一点不同：`KalmanFilter` 用矩阵 $\\mathbf F$ 计算状态转移。矩阵意味着 **线性** 代数，适用于线性问题而非非线性。因此不用矩阵而提供函数，如上。`KalmanFilter` 还用矩阵 $\\mathbf H$ 实现测量函数，将状态转为等价测量。矩阵隐含线性，故同样提供函数。或许已清楚为何称 $\\mathbf H$ 为“测量函数”：线性卡尔曼滤波中它是矩阵，只是快速计算恰好线性的函数。

不再赘述，下面是一维跟踪问题的状态转移与测量函数，状态 $\\mathbf x = [x \\, \\, \\dot x]^ \\mathsf T$：

""",

22: """明确：这是线性例子，线性问题不必用 UKF，但从最简单例子开始。注意 `fx()` 用方程组而非矩阵乘法计算 $\\mathbf{\\bar x}$，说明可在此实现任意非线性函数，不限于线性方程。

其余设计相同：设计 $\\mathbf P$、$\\mathbf R$、$\\mathbf Q$。你知道怎么做，完成滤波器并运行。

""",

24: """这里新内容不多：须创建生成 sigma 点的对象，用函数代替 $\\mathbf F$、$\\mathbf H$ 矩阵，其余与以前相同。这应给你信心啃一点数学与算法，理解 UKF 在做什么。

""",

25: """## 选择 Sigma 点（Choosing Sigma Points）

章初用 500,000 随机 sigma 点计算高斯经非线性函数后的分布。均值相当准，但每步 500,000 点会使滤波极慢。最少能用多少采样点？问题 formulation 对点有何约束？假设对非线性函数无特殊知识，要找适用于任意函数的通用算法。

从最简单情况入手。**恒等函数**：$f(x)=x$。若算法对恒等函数都不行，滤波无法收敛。即一维输入为 1，输出也须为 1；若输出为 1.1，下一步 1.1 输入可能得 1.23，滤波发散。

最少点数是每维一个，线性卡尔曼滤波即如此。对分布 $\\mathcal{N}(\\mu,\\sigma^2)$，输入为 $\\mu$ 本身。线性可行，非线性则不够。

或许每维一个点但 somehow 改变。但若把 $\\mu+\\Delta$ 传入 $f(x)=x$ 不收敛。不改 $\\mu$ 就是标准卡尔曼滤波。须结论：一个样本不行。

下一个数目是 2。高斯对称，且恒等函数可能希望一个样本点是输入均值。两点须选均值再加另一点，另一点引入可能不想要的 asymmetry，难使 $f(x)=x$ 工作。

再下一个是 3 点：选均值及均值两侧各一点，见下图。

""",

27: """可将这些点经非线性 $f(x)$ 算均值与方差。均值可取 3 点平均，但不够 general。强非线性问题可能中心点权重大得多，或外侧点权重大。

更 general：加权均值 $\\mu = \\sum_i w_i\\, f(\\mathcal{X}_i)$，花体 $\\mathcal{X}$ 为 sigma 点。权重和须为 1。任务是选 $\\mathcal{X}$ 与权重，使其算得变换 sigma 点的均值与方差。

若对均值加权，协方差（covariance）也加权合理。均值 ($w^m$) 与协方差 ($w^c$) 可用不同权重。下面方程用上下标留索引空间：

$$\\begin{aligned}
\\mathbf{Constraints:}\\\\
1 &= \\sum_i{w_i^m} \\\\
1 &= \\sum_i{w_i^c} \\\\
\\mu &= \\sum_i w_i^mf(\\mathcal{X}_i) \\\\
\\Sigma &= \\sum_i w_i^c{(f(\\mathcal{X})_i-\\mu)(f(\\mathcal{X})_i-\\mu)^\\mathsf{T}}
\\end{aligned}
$$

前两个方程约束权重和为 1。第三个是加权均值。第四个若陌生，回忆两随机变量协方差：

$$COV(x,y) = \\frac{\\sum(x-\\bar x)(y-\\bar{y})}{n}$$

这些约束无唯一解。例如减小 $w^m_0$ 可增大 $w^m_1$、$w^m_2$ 补偿。均值与协方差权重可同可异。约束甚至不要求任一点是输入均值，尽管“ nice ”如此。

我们想要满足约束、 preferably 每维仅 3 点的算法。继续前请确意思路清楚。下面是同一协方差椭圆上三种不同 sigma 点布置，点大小与权重成正比。

""",

29: """点不必在椭圆长、短轴上；约束不要求。我画成等间距，约束也不要求。

sigma 点的布置与权重影响如何采样分布。近的点采样局部效应，强非线性问题可能更好。远或偏离椭圆轴的点采样非局部与非高斯行为，但可通过权重缓解：点虽远若权重很小，仍纳入分布知识而不让非线性产生坏估计。

请理解 sigma 点有无穷多种选法。此处约束只是一种。例如并非所有算法都要求权重和为 1。本书偏好的算法就没有该性质。

""",

30: """## 无迹变换（The Unscented Transform）

暂设已有选 sigma 点与权重的算法。如何用 sigma 点实现滤波？

*无迹变换（unscented transform）* 是算法核心，却 remarkably 简单：sigma 点 $\\boldsymbol{\\chi}$ 经非线性函数得变换点集。

$$\\boldsymbol{\\mathcal{Y}} = f(\\boldsymbol{\\chi})$$

再计算变换点的均值与协方差，成为新估计。下图示意无迹变换；右侧绿色椭圆为变换 sigma 点的均值与协方差。

""",

32: """sigma 点均值与协方差为：

$$\\begin{aligned}
\\mu &= \\sum_{i=0}^{2n} w^m_i\\boldsymbol{\\mathcal{Y}}_i \\\\
\\Sigma &= \\sum_{i=0}^{2n} w^c_i{(\\boldsymbol{\\mathcal{Y}}_i-\\mu)(\\boldsymbol{\\mathcal{Y}}_i-\\mu)^\\mathsf{T}}
\\end{aligned}
$$

应熟悉——即上面约束方程。

简言之，无迹变换从任意概率分布采样点，经任意非线性函数，对每个变换点产生高斯。希望你能想象如何用于非线性卡尔曼滤波。一旦有高斯，已有数学工具即可用！

“unscented” 名字可能困惑，无数学含义，是发明者玩笑说算法不“臭”，名字便留下。

""",

33: """### 无迹变换的精度（Accuracy of the Unscented Transform）

早前用 50,000 点经非线性函数求分布均值。现在用 5 个 sigma 点经同一函数，用无迹变换算均值。用 FilterPy 的 *MerweScaledSigmaPoints()* 创建 sigma 点、`unscented_transform` 做变换（稍后讲）。章首第一个例子用 `JulierSigmaPoints`；二者选点方式不同，稍后解释。

""",

35: """结果 remarkable：仅 5 点均值精度惊人。$x$ 误差 -0.097，$y$ 误差 0.549。对比线性化（EKF 所用，下一章）$y$ 误差超 43。生成 sigma 点的代码对非线性函数一无所知，只知初始分布均值与协方差。换完全不同非线性函数仍生成同样 5 点。

我承认选了使无迹变换相对 EKF  striking 的非线性函数。但物理世界充满强非线性，UKF 能应对。并非刻意找“碰巧好”的函数。下一章见传统方法在强非线性上的 struggle。该图是我建议尽可能用 UKF 或类似现代方法的基础。

""",

36: "## 无迹卡尔曼滤波（The Unscented Kalman Filter）\n\n现在给出 UKF 算法。\n",

37: """### 预测步（Predict Step）

UKF 预测步用过程模型 $f()$ 计算先验（prior）。$f()$ 假设非线性，故按某函数生成 sigma 点 $\\mathcal{X}$ 及权重 $W^m, W^c$：

$$\\begin{aligned}
\\boldsymbol\\chi &= \\text{sigma-function}(\\mathbf x, \\mathbf P) \\\\
W^m, W^c &= \\text{weight-function}(\\mathtt{n, parameters})\\end{aligned}$$

每个 sigma 点经 $f(\\mathbf x, \\Delta t)$，按过程模型前推，形成新先验 sigma 点 $\\boldsymbol{\\mathcal Y}$：

$$\\boldsymbol{\\mathcal{Y}} = f(\\boldsymbol{\\chi}, \\Delta t)$$

用 *无迹变换* 对变换 sigma 点算先验均值与协方差：

$$\\mathbf{\\bar x}, \\mathbf{\\bar P} = 
UT(\\mathcal{Y}, w_m, w_c, \\mathbf Q)$$

无迹变换方程：

$$\\begin{aligned}
\\mathbf{\\bar x} &= \\sum_{i=0}^{2n} w^m_i\\boldsymbol{\\mathcal Y}_i \\\\
\\mathbf{\\bar P} &= \\sum_{i=0}^{2n} w^c_i({\\boldsymbol{\\mathcal Y}_i - \\mathbf{\\bar x})(\\boldsymbol{\\mathcal Y}_i-\\mathbf{\\bar x})}^\\mathsf{T}} + \\mathbf Q
\\end{aligned}
$$

下表比较线性卡尔曼滤波与 UKF（为可读性略去下标 $i$）：

$$\\begin{array}{l|l}
\\text{Kalman} & \\text{Unscented} \\\\
\\hline 
& \\boldsymbol{\\mathcal Y} = f(\\boldsymbol\\chi) \\\\
\\mathbf{\\bar x} = \\mathbf{Fx} & 
\\mathbf{\\bar x} = \\sum w^m\\boldsymbol{\\mathcal Y}  \\\\
\\mathbf{\\bar P} = \\mathbf{FPF}^\\mathsf T + \\mathbf Q  & 
\\mathbf{\\bar P} = \\sum w^c({\\boldsymbol{\\mathcal Y} - \\mathbf{\\bar x})(\\boldsymbol{\\mathcal Y} - \\mathbf{\\bar x})}^\\mathsf T}+\\mathbf Q
\\end{array}$$

""",

38: """### 更新步（Update Step）

卡尔曼滤波在测量空间更新，须用你定义的测量函数 $h(x)$ 将先验 sigma 点转为测量：

$$\\boldsymbol{\\mathcal{Z}} = h(\\boldsymbol{\\mathcal{Y}})$$

用无迹变换算这些点的均值与协方差。下标 $z$ 表示测量 sigma 点的均值与协方差。

$$\\begin{aligned}
\\boldsymbol\\mu_z, \\mathbf P_z &= 
UT(\\boldsymbol{\\mathcal Z}, w_m, w_c, \\mathbf R) \\\\
\\boldsymbol\\mu_z &= \\sum_{i=0}^{2n} w^m_i\\boldsymbol{\\mathcal Z}_i \\\\
\\mathbf P_z &= \\sum_{i=0}^{2n} w^c_i{(\\boldsymbol{\\mathcal Z}_i-\\boldsymbol{\\mu}_z)(\\boldsymbol{\\mathcal Z}_i-\\boldsymbol{\\mu}_z)^\\mathsf T} + \\mathbf R
\\end{aligned}
$$

接着算残差（residual）与卡尔曼增益（Kalman gain）。测量 $\\mathbf z$ 的残差易算：

$$\\mathbf y = \\mathbf z - \\boldsymbol\\mu_z$$

卡尔曼增益先算状态与测量的 [互协方差（cross covariance）](https://en.wikipedia.org/wiki/Cross-covariance)：

$$\\mathbf P_{xz} =\\sum_{i=0}^{2n} w^c_i(\\boldsymbol{\\mathcal Y}_i-\\mathbf{\\bar x})(\\boldsymbol{\\mathcal Z}_i-\\boldsymbol\\mu_z)^\\mathsf T$$

卡尔曼增益：

$$\\mathbf{K} = \\mathbf P_{xz} \\mathbf P_z^{-1}$$

把逆看作矩阵的 *一种* 倒数，可见卡尔曼增益是简单比值：

$$\\mathbf{K} \\approx \\frac{\\mathbf P_{xz}}{\\mathbf P_z} 
\\approx \\frac{\\text{belief in state}}{\\text{belief in measurement}}$$

最后用残差与增益更新状态：

$$\\mathbf x = \\bar{\\mathbf x} + \\mathbf{Ky}$$

新协方差：

$$ \\mathbf P = \\mathbf{\\bar P} - \\mathbf{KP_z}\\mathbf{K}^\\mathsf{T}$$

本节有几个方程需先接受，但应能看出与线性卡尔曼滤波的关系。线性代数略异，算法仍是全书一贯的贝叶斯算法。

下表比较线性 KF 与 UKF：

$$\\begin{array}{l|l}
\\textrm{Kalman Filter} & \\textrm{Unscented Kalman Filter} \\\\
\\hline 
& \\boldsymbol{\\mathcal Y} = f(\\boldsymbol\\chi) \\\\
\\mathbf{\\bar x} = \\mathbf{Fx} & 
\\mathbf{\\bar x} = \\sum w^m\\boldsymbol{\\mathcal Y}  \\\\
\\mathbf{\\bar P} = \\mathbf{FPF}^\\mathsf T+\\mathbf Q  & 
\\mathbf{\\bar P} = \\sum w^c({\\boldsymbol{\\mathcal Y} - \\mathbf{\\bar x})(\\boldsymbol{\\mathcal Y} - \\mathbf{\\bar x})}^\\mathsf T}+\\mathbf Q \\\\
\\hline 
& \\boldsymbol{\\mathcal Z} =  h(\\boldsymbol{\\mathcal{Y}}) \\\\
& \\boldsymbol\\mu_z = \\sum w^m\\boldsymbol{\\mathcal{Z}} \\\\
\\mathbf y = \\mathbf z - \\mathbf{Hx} &
\\mathbf y = \\mathbf z - \\boldsymbol\\mu_z \\\\
\\mathbf S = \\mathbf{H\\bar PH}^\\mathsf{T} + \\mathbf R & 
\\mathbf P_z = \\sum w^c{(\\boldsymbol{\\mathcal Z}-\\boldsymbol\\mu_z)(\\boldsymbol{\\mathcal{Z}}-\\boldsymbol\\mu_z)^\\mathsf{T}} + \\mathbf R \\\\ 
\\mathbf K = \\mathbf{\\bar PH}^\\mathsf T \\mathbf S^{-1} &
\\mathbf K = \\left[\\sum w^c(\\boldsymbol{\\mathcal Y}-\\bar{\\mathbf x})(\\boldsymbol{\\mathcal{Z}}-\\boldsymbol\\mu_z)^\\mathsf{T}\\right] \\mathbf P_z^{-1} \\\\
\\mathbf x = \\mathbf{\\bar x} + \\mathbf{Ky} & \\mathbf x = \\mathbf{\\bar x} + \\mathbf{Ky}\\\\
\\mathbf P = (\\mathbf{I}-\\mathbf{KH})\\mathbf{\\bar P} & \\mathbf P = \\bar{\\mathbf P} - \\mathbf{KP_z}\\mathbf{K}^\\mathsf{T}
\\end{array}$$

""",

39: """## Van der Merwe 缩放 Sigma 点算法（Van der Merwe's Scaled Sigma Point Algorithm）

选 sigma 点算法很多。2005 年前后研究与工业界多采纳 Rudolph Van der Merwe 2004 博士论文 [1] 版本。多种问题表现好，性能与精度平衡佳。是 Simon J. Julier [2] 发表的 *缩放无迹变换（Scaled Unscented Transform）* 的 slight 重述。

该 formulation 用 3 参数控制 sigma 点分布与权重：$\\alpha$、$\\beta$、$\\kappa$。推导方程前先看例：在一、二标准差协方差椭圆上画 sigma 点，按均值权重缩放。

""",

41: "可见 sigma 点在一、二标准差之间；$\\alpha$ 越大点越 spread。$\\alpha$ 越大，均值（中心）权重越高，其余越低——符合直觉：离均值越远权重越小。权重与点如何选取尚未知，但选择 reasonable。\n",

42: """### Sigma 点计算（Sigma Point Computation）

第一个 sigma 点是输入均值，即上图椭圆中心，记 $\\boldsymbol{\\chi}_0$。

$$ \\mathcal{X}_0 = \\mu$$

为记号方便定义 $\\lambda = \\alpha^2(n+\\kappa)-n$，$n$ 为 $\\mathbf x$ 维数。其余 sigma 点：

$$ 
\\boldsymbol{\\chi}_i = \\begin{cases}
\\mu + \\left[ \\sqrt{(n+\\lambda)\\Sigma}\\right ]_{i}& i=1..n \\\\
\\mu - \\left[ \\sqrt{(n+\\lambda)\\Sigma}\\right]_{i-n} &i=(n+1)..2n\\end{cases}
$$
下标 $i$ 选矩阵第 i 行向量。

即缩放协方差、开方，通过对称加减均值。矩阵开方稍后讨论。

### 权重计算（Weight Computation）

该 formulation 对均值与协方差用两套权重。$\\mathcal{X}_0$ 均值权重：

$$W^m_0 = \\frac{\\lambda}{n+\\lambda}$$

$\\mathcal{X}_0$ 协方差权重：

$$W^c_0 = \\frac{\\lambda}{n+\\lambda} + 1 -\\alpha^2 + \\beta$$

其余 $\\boldsymbol{\\chi}_1 ... \\boldsymbol{\\chi}_{2n}$ 均值与协方差权重相同：

$$W^m_i = W^c_i = \\frac{1}{2(n+\\lambda)}\\;\\;\\;i=1..2n$$

为何“正确”未必显然，也无法证明对所有非线性问题 ideal。但可见 sigma 点与协方差矩阵平方根成比例，方差平方根即标准差，故 spread 约 $\\pm 1\\sigma$ 乘缩放因子。分母有 $n$，维数越多点越 spread、权重越小。

**重要说明：** 通常这些权重和不为 1。我常收到此问。权重和大于 1 甚至为负是预期的，下文详述。


### 参数的合理选择（Reasonable Choices for the Parameters）

高斯问题 $\\beta=2$ 较好，$\\kappa=3-n$（$n$ 为 $\\mathbf x$ 维数），$0 \\le \\alpha \\le 1$，$\\alpha$ 越大 sigma 点离均值越远。

""",

43: """## 使用 UKF（Using the UKF）

通过算例建立使用 UKF 的信心。从线性问题开始——你已会用线性卡尔曼滤波求解。UKF 为 non-linear 设计，但线性问题上与线性卡尔曼滤波同样最优。写 2D 匀速模型跟踪物体，聚焦相同处（大部分相同！）与不同处。

设计卡尔曼滤波须指定 $\\bf{x}$、$\\bf{F}$、$\\bf{H}$、$\\bf{R}$、$\\bf{Q}$。做过多次，下面给矩阵少作讨论。匀速模型，$\\bf{x}$ 为

$$ \\mathbf x = \\begin{bmatrix}x &  \\dot x & y & \\dot y \\end{bmatrix}^\\mathsf{T}$$

此状态顺序下状态转移矩阵为

$$\\mathbf F = \\begin{bmatrix}1 & \\Delta t & 0 & 0 \\\\
0&1&0&0 \\\\
0&0&1&\\Delta t\\\\
0&0&0&1
\\end{bmatrix}$$

实现牛顿方程

$$\\begin{aligned}
x_k &= x_{k-1} + \\dot x_{k-1}\\Delta t \\\\
y_k &= y_{k-1} + \\dot y_{k-1}\\Delta t
\\end{aligned}$$

传感器给位置不给速度，测量函数为

$$\\mathbf H = \\begin{bmatrix}1&0&0&0 \\\\ 0&0&1&0
\\end{bmatrix}$$

传感器读数米制，$x$、$y$ 误差 $\\sigma=0.3$ 米，测量噪声矩阵

$$\\mathbf R = \\begin{bmatrix}0.3^2 &0\\\\0 & 0.3^2\\end{bmatrix}$$

假设过程噪声可用离散白噪声模型——每段时间加速度恒定。可用 `FilterPy` 的 `Q_discrete_white_noise()`，复习矩阵为

$$\\mathbf Q = \\begin{bmatrix}
\\frac{1}{4}\\Delta t^4 & \\frac{1}{2}\\Delta t^3 \\\\
\\frac{1}{2}\\Delta t^3 & \\Delta t^2\\end{bmatrix} \\sigma^2$$

我的实现：

""",

45: """应无意外。现在实现 UKF。纯教学；线性问题用 UKF 无益处。`FilterPy` 用类 `UnscentedKalmanFilter`。

先实现 `f(x, dt)` 与 `h(x)`。`f(x, dt)` 为状态转移，`h(x)` 为测量函数，对应线性滤波器的 $\\mathbf F$、$\\mathbf H$。

下面是合理实现。各应返回 1D NumPy 数组或 list。可比 `f`、`h` 起更可读名字。

""",

47: """接着指定如何计算 sigma 点与权重。上文给出 Van der Merwe 版，选择很多。FilterPy 用类 `SigmaPoints`，须实现方法：

```python
def sigma_points(self, x, P)
```

并含属性 `Wm`、`Wc`，分别用于均值与协方差权重。

FilterPy 从 `SigmaPoints` 派生 `MerweScaledSigmaPoints` 并实现上述方法。

创建 UKF 时传入 $f()$、$h()$ 与 sigma 点对象，例如：

```python
from filterpy.kalman import MerweScaledSigmaPoints
from filterpy.kalman import UnscentedKalmanFilter as UKF

points = MerweScaledSigmaPoints(n=4, alpha=.1, beta=2., kappa=-1)
ukf = UKF(dim_x=4, dim_z=2, fx=f_cv, hx=h_cv, dt=dt, points=points)
```

其余与线性卡尔曼滤波相同。用同样测量，算两解差异标准差。

""",

49: """标准差约 0.013 米，相当小。

UKF 实现与线性卡尔曼滤波差别不大：用非线性函数 `f()`、`h()` 代替 $\\mathbf F$、$\\mathbf H$ 矩阵，理论与实现其余相同。`predict()`、`update()` 代码不同，设计者视角问题 formulation 与滤波器设计非常相似。

""",

50: """## 跟踪飞机（Tracking an Airplane）

第一个非线性问题：用雷达传感器跟踪飞机。为与上一例相似，跟踪二维——地面一维加飞行高度。各维独立，无一般性损失。

雷达发射无线电或微波，波束路径上物体会反射信号。测往返时间得 *斜距（slant distance）*。方位由天线 *方向增益（directive gain）* 计算。

由斜距与仰角计算飞机 (x,y) 位置见下图：

""",

52: """*仰角（elevation angle）* $\\epsilon$ 是地面视线之上的角度。

假设飞机恒定高度飞行，状态向量三变量：

$$\\mathbf x = \\begin{bmatrix}\\mathtt{distance} \\\\\\mathtt{velocity}\\\\ \\mathtt{altitude}\\end{bmatrix}=    \\begin{bmatrix}x \\\\ \\dot x\\\\ y\\end{bmatrix}$$

""",

53: """状态转移函数为线性

$$\\mathbf{\\bar x} = \\begin{bmatrix} 1 & \\Delta t & 0 \\\\ 0& 1& 0 \\\\ 0&0&1\\end{bmatrix}
\\begin{bmatrix}x \\\\ \\dot x\\\\ y\\end{bmatrix}
$$

可计算为：

""",

55: """设计测量函数。与线性卡尔曼滤波一样，测量函数将滤波器先验转为测量。须把飞机位置与速度转为相对雷达站的仰角与距离。

距离用勾股定理：

$$\\text{range} = \\sqrt{(x_\\text{ac} - x_\\text{radar})^2 + (y_\\text{ac} - y_\\mathtt{radar})^2}$$

仰角 $\\epsilon$ 为 $y/x$ 的反正切：

$$\\epsilon = \\tan^{-1}{\\frac{y_\\mathtt{ac} - y_\\text{radar}}{x_\\text{ac} - x_\\text{radar}}}$$

须定义 Python 函数。函数可拥有变量存雷达位置——本题可硬编码或用全局，此处为灵活性。

""",

57: """有一非线性未考虑：角度 modular。残差是测量与投影到测量空间的先验之差。359° 与 1° 角差为 2°，但 359° - 1° = 358°。UKF 在无迹变换中对加权值求和，问题更严重。暂将传感器与目标放在避开这些非线性区域的位置。后文示如何处理。

须仿真雷达与飞机。此时应驾轻就熟，代码不再讨论。

""",

59: """军用雷达距离 RMS 精度 1 米、仰角 1 mrad [3]。这里假设 5 米距离、0.5° 角精度，使滤波更具挑战。

$\\mathbf Q$ 设计需讨论。状态 $\\begin{bmatrix}x & \\dot x & y\\end{bmatrix}^\\mathtt{T}$。前两个为沿程距离与速度，可用 `Q_discrete_white_noise` 算 Q 左上。第三为高度，假设与 $x$ 独立，$\\mathbf Q$ 分块：

$$\\mathbf Q = \\begin{bmatrix}\\mathbf Q_\\mathtt{x} & \\boldsymbol 0 \\\\ \\boldsymbol 0 & Q_\\mathtt{y}\\end{bmatrix}$$

初始飞机在雷达正上方，100 m/s。典型测高雷达可能每 3 秒更新，epoch 取该值。

""",

61: " impress 与否因人而异，但我印象深刻！扩展卡尔曼滤波章将解同一问题，却需大量数学。\n",

62: "### 跟踪机动飞机（Tracking Maneuvering Aircraft）\n",

63: "上一例结果好，但假设飞机不变高度。若一分钟后开始爬升，滤波结果如下。\n",

65: """滤波器无法跟踪变化的高度。设计须改什么？

希望你会答“把爬升率加入状态”：

$$\\mathbf x = \\begin{bmatrix}\\mathtt{distance} \\\\\\mathtt{velocity}\\\\ \\mathtt{altitude} \\\\ \\mathtt{climb\\, rate}\\end{bmatrix}=  \\begin{bmatrix}x \\\\\\dot x\\\\ y \\\\ \\dot y\\end{bmatrix}$$

状态转移函数仍线性，须改为：

$$\\mathbf{F} = \\begin{bmatrix} 1 & \\Delta t & 0 &0 \\\\ 0& 1& 0 &0\\\\ 0&0&1&\\Delta t \\\\ 0&0&0&1\\end{bmatrix}
\\begin{bmatrix}x \\\\\\dot x\\\\ y\\\\ \\dot y\\end{bmatrix} 
$$

测量函数不变，但须因 $\\mathbf x$ 维数改变而调整 $\\mathbf Q$。

""",

68: "高度估计引入较多噪声，但现已准确跟踪高度。\n",

69: "### 传感器融合（Sensor Fusion）\n",

70: """传感器融合示例。某多普勒系统给出 2 m/s RMS 速度估计。与雷达一样，并非教完整多普勒滤波；须考虑信噪比、大气、几何等。

上例雷达精度可估速度约 1 m/s。为说明融合效果，将距离误差改为 $\\sigma=500$ 米，算估计速度标准差。跳过最初几次测量（收敛期 artificially 大偏差）。

不用多普勒时的标准差：

""",

72: """多普勒须把 $x$、$y$ 速度纳入测量。`ACSim` 类在 `vel` 存速度。卡尔曼更新时 `update` 传入含斜距、仰角、$\\dot x$、$\\dot y$ 的 list：

$$z = [\\mathtt{slant\\_range},\\, \\text{elevation angle},\\, \\dot x,\\, \\dot y]$$

测量四个值，测量函数也须返回四个。斜距与仰角同前，$\\dot x$、$\\dot y$ 由状态估计给出，不必再算。

""",

74: "现在实现滤波器。\n",

76: """融合速度传感器后标准差从 3.5 m/s 降至 1.3 m/s。

传感器融合（sensor fusion）是大话题，这里较 simplistic。典型导航中传感器提供 *互补（complementary）* 信息：GPS 每秒较准位置、速度差；惯性系统 50Hz 很准速度、位置差。 strengths 与 weaknesses 正交，引出 *互补滤波（Complementary filter）*：融合 GPS 慢速准确位置与惯性高速速度，得高速准确位置与速度估计。高速速度在 GPS 更新间积分得准确高速位置。

""",

77: """### 多位置传感器（Multiple Position Sensors）

上一融合题较 toy。现在做更“真”的题。GPS 之前，船与飞机用 VOR、LORAN、TACAN、DME 等测距测向系统。信标发无线电波，传感器从信号提取到信标距离和/或方位。例如飞机两 VOR 接收机，各调不同台，显示 *径向（radial）*——地面 VOR 到飞机方向。飞行员用航图求径向交点定位置。

手动精度低。卡尔曼滤波位置估计准得多。假设两传感器各给目标方位，如下图。 perimeter 宽度与 $3\\sigma$ 噪声成正比。飞机须高概率落在两 perimeter 交集中。

""",

79: "传感器到目标方位计算为：\n",

81: "滤波器以向量接收两传感器测量。代码接受任意可迭代容器，这里用 Python list。可实现为：\n",

83: "假设飞机匀速模型。换 pace，显式算新位置而非矩阵向量乘：\n",
}
