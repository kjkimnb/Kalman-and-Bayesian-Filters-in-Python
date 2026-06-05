# -*- coding: utf-8 -*-
"""Supporting_Notebooks/ 下 5 个 notebook 的 markdown 译文"""

TRANSLATIONS_COMPUTING_PDFS = {
    1: """# 计算并绘制离散数据的 PDF

""",

    2: """我们来研究如何计算并绘制概率分布（probability distribution）。

首先，按正态分布（normal distribution）生成一些数据。我们使用 `numpy.random.normal` 来完成。参数命名不太直观：`loc` 是分布的均值（mean），`scale` 是标准差（standard deviation）。调用该函数可以生成任意数量的、服从给定均值与标准差的数据点。

""",

    4: """从打印结果可以看到，我们得到了 5000 个点，均值非常接近 3，标准差接近 2。

我们可以用 `scipy.stats.norm` 创建一个冻结函数（frozen function），再用它计算高斯（Gaussian）的 pdf（概率密度函数，probability density function）。

""",

    6: """但我们真正想绘制的是离散数据的 PDF，而不是理想化的函数。

有几种做法。首先可以利用 `matplotlib` 的 `hist` 方法，它对一组数据计算直方图（histogram）。通常 `hist` 计算落入每个 bin 的点数，如下所示：

""",

    8: """这对我们用处不大——我们要的是 PDF，而不是 bin 计数。好在 `hist` 提供了 `density` 参数，可以为我们绘制 PDF。

""",

    10: """我可能不想要柱状条，可以把 `histtype` 设为 `'step'` 以得到折线。

""",

    12: """为确认代码工作正常，我们再用黑色绘制理想化的高斯（Gaussian）曲线。

""",

    14: """还有另一种方法可以近似得到一组数据的分布：*核密度估计（kernel density estimate）* 使用核函数估计数据点的概率分布。SciPy 用 `gaussian_kde` 实现。不要被名字误导——Gaussian 指的是计算中使用的核类型。这对任意分布都适用，不限于高斯。本节我们用的是高斯分布，但很快就不会了，而同一函数仍然适用。

""",

    16: """## 蒙特卡洛模拟（Monte Carlo Simulations）

我们（好吧，是我）想这样做，是因为要用蒙特卡洛（Monte Carlo）模拟来计算分布。高斯通过线性函数传递时很容易计算，但通过非线性（nonlinear）函数传递时，解析计算则困难甚至不可能。粒子滤波（particle filter）等技术通过取大量样本点、将其通过非线性函数、再对变换后的点计算统计量来处理这一问题。我们也来这样做。

先从线性函数 $f(x) = 2x + 12$ 开始，以证明代码正确。我会调整数据的均值和标准差，使输出数字彼此不同，便于判断。例如，若公式把 $x$ 乘以 2，均值为 2，标准差为 2，某输出为 4，那是乘法因子、均值、标准差还是 bug 造成的？很难分辨。

""",

    18: """这与预期一致。输入为高斯 $\mathcal{N}(\mu=1, \sigma=1.4)$，函数为 $f(x) = 2x+12$。因此期望均值平移到 $f(\mu) = 2*1+12=14$。从图和打印结果可以看到确实如此。

在继续之前，你能解释标准差发生了什么吗？你可能以为新的 $\sigma$ 应像 $2(1.4) + 12=14.81$ 那样通过 $f(x)$ 传递。但这是不对的——标准差只受乘法因子影响，不受平移影响。稍想即可理解：我们把样本乘以 2，它们比原来分散两倍。标准差衡量分散程度，因此也应加倍。之后把分布平移 12 个单位，或 1200 万个单位都无所谓——分散程度仍是输入数据的两倍。

""",

    19: """## 非线性函数（Nonlinear Functions）

既然相信代码没问题，我们就用非线性函数来试。

""",

    21: """这里我把数据通过非线性函数 $f(x) = \cos(1.5x+2.1)\sin(\frac{x}{3}) - 1.6x$ 传递。该函数相当接近线性，但仍可看到它对采样数据 pdf 的改变程度。

背后有大量计算：变换 50000 个点再计算其 PDF。扩展卡尔曼滤波（Extended Kalman Filter, EKF）通过在均值处线性化函数，再通过线性方程传递高斯来绕过这一点。上面我们已经看到高斯通过线性函数多么容易。现在来试试。

可以在 $x$ 处对函数求导来线性化。可用 sympy 求导。

""",

    23: """现在可以在均值处求导数的值，得到函数的斜率。

""",

    25: """直线方程为 $y=mx+b$，因此新标准差应约为输入标准差的 $~1.67$ 倍。新均值可通过原函数传递得到，因为线性化函数就是在均值处求得的 $f(x)$ 斜率。斜率是切线，在 $x$ 处与函数相切，因此两者给出相同结果。下面绘制并与蒙特卡洛模拟结果比较。

""",

    27: """可以看出，EKF 的估计（红色）并不精确，但也是相当不错的近似。

""",
}

TRANSLATIONS_CONVERTING_MULTIVARIATE = {
    1: """# 将多元方程化为一元情形

多元卡尔曼滤波（multivariate Kalman filter）方程与一元滤波器的方程并不相似。然而，若状态与测量都是一维的，这些方程就退化为一元方程。本节将帮助你建立对卡尔曼滤波方程实际在做什么的直观理解。读本节并非理解全书其余部分的必要条件，但我建议仔细阅读，因为它应使后续内容更容易理解。

下面是预测（prediction）的多元方程。

$$
\\begin{aligned}
\\mathbf{\\bar{x}} &= \\mathbf{F x} + \\mathbf{B u} \\\\
\\mathbf{\\bar{P}} &= \\mathbf{FPF}^\\mathsf{T} + \\mathbf Q
\\end{aligned}
$$

对一元问题，状态 $\\mathbf x$ 只有一个变量，因此是 $1\\times 1$ 矩阵。运动 $\\mathbf{u}$ 也是 $1\\times 1$ 矩阵。因此 $\\mathbf{F}$ 与 $\\mathbf B$ 也必须是 $1\\times 1$ 矩阵，即它们都是标量，可写为

$$\\bar{x} = Fx + Bu$$

这里变量不加粗，表示它们不是矩阵或向量。

状态转移很简单——下一状态与当前状态相同，故 $F=1$。运动转移同样，$B=1$。于是

$$x = x + u$$

等价于上一章的高斯方程

$$ \\mu = \\mu_1+\\mu_2$$

希望一般过程已经清楚，下面我会稍快一些。我们有

$$\\mathbf{\\bar{P}} = \\mathbf{FPF}^\\mathsf{T} + \\mathbf Q$$

同样，由于状态只有一个变量，$\\mathbf P$ 与 $\\mathbf Q$ 也是 $1\\times 1$ 矩阵，可当作标量，得到

$$\\bar{P} = FPF^\\mathsf{T} + Q$$

已知 $F=1$。标量的转置仍是该标量，故 $F^\\mathsf{T} = 1$。于是

$$\\bar{P} = P + Q$$

等价于高斯方程

$$\\sigma^2 = \\sigma_1^2 + \\sigma_2^2$$

这证明：在维数为 1 时，多元预测方程与一元方程做的是同样的数学运算。

下面是更新（update）步的方程：

$$
\\begin{aligned}
\\mathbf{K}&= \\mathbf{\\bar{P}H}^\\mathsf{T} (\\mathbf{H\\bar{P}H}^\\mathsf{T} + \\mathbf R)^{-1} \\\\
\\textbf{y} &= \\mathbf z - \\mathbf{H \\bar{x}}\\\\
\\mathbf x&=\\mathbf{\\bar{x}} +\\mathbf{K\\textbf{y}} \\\\
\\mathbf P&= (\\mathbf{I}-\\mathbf{KH})\\mathbf{\\bar{P}}
\\end{aligned}
$$

同上，所有矩阵都变成标量。$H$ 定义如何从位置转换为测量。两者都是位置，无需转换，故 $H=1$。代入已知值并一步化为标量形式。$1\\times 1$ 矩阵的逆就是该值的倒数，因此把矩阵求逆写成除法。

$$
\\begin{aligned}
K &=\\frac{\\bar{P}}{\\bar{P} + R} \\\\
y &= z - \\bar{x}\\\\
x &=\\bar{x}+Ky \\\\
P &= (1-K)\\bar{P}
\\end{aligned}
$$

在继续证明之前，请看看这些方程，认识它们实现的简单概念。残差（residual）$y$ 无非是测量（measurement）减去预测（prediction）。增益（gain）$K$ 根据我们对上次预测与测量的确信程度进行缩放。新状态 $x$ 在旧 $x$ 基础上加上缩放后的残差。最后，根据对测量的确信程度更新不确定性。从算法上看，这应与上一章所做的完全一致。

下面完成代数证明。回忆一元更新步方程为：

$$
\\begin{aligned}
\\mu &=\\frac{\\sigma_1^2 \\mu_2 + \\sigma_2^2 \\mu_1} {\\sigma_1^2 + \\sigma_2^2}, \\\\
\\sigma^2 &= \\frac{1}{\\frac{1}{\\sigma_1^2} + \\frac{1}{\\sigma_2^2}}
\\end{aligned}
$$

这里设 $\\mu_1$ 为状态 $x$，$\\mu_2$ 为测量 $z$。于是 $\\sigma_1^2$ 为状态不确定性 $P$，$\\sigma_2^2$ 为测量噪声（measurement noise）$R$。代入得

$$\\begin{aligned} \\mu &= \\frac{Pz + Rx}{P+R} \\\\
\\sigma^2 &= \\frac{1}{\\frac{1}{P} + \\frac{1}{R}}
\\end{aligned}$$

先处理 $\\mu$。多元情形对应方程为

$$
\\begin{aligned}
x &= x + Ky \\\\
&= x + \\frac{P}{P+R}(z-x) \\\\
&= \\frac{P+R}{P+R}x + \\frac{Pz - Px}{P+R} \\\\
&= \\frac{Px + Rx + Pz - Px}{P+R} \\\\
&= \\frac{Pz + Rx}{P+R}
\\end{aligned}
$$

再看 $\\sigma^2$。多元情形对应方程为

$$ 
\\begin{aligned}
P &= (1-K)P \\\\
&= (1-\\frac{P}{P+R})P \\\\
&= (\\frac{P+R}{P+R}-\\frac{P}{P+R})P \\\\
&= (\\frac{P+R-P}{P+R})P \\\\
&= \\frac{RP}{P+R}\\\\
&= \\frac{1}{\\frac{P+R}{RP}}\\\\
&= \\frac{1}{\\frac{R}{RP} + \\frac{P}{RP}} \\\\
&= \\frac{1}{\\frac{1}{P} + \\frac{1}{R}}
\\quad\\blacksquare
\\end{aligned}
$$

我们已证明：只有一个状态变量时，多元方程与一元方程等价。本节末尾再提一点——我略过了 $H=1$ 与 $F=1$ 的断言。一般情况下它们并不成立。例如数字温度计可能以伏特给出测量，需转换为温度，用 $H$ 完成该转换。为保持说明简洁，我省略了这一点。把该推广加入上方方程、重做代数，仍会得到相同结果。\\\\\\""",
}

TRANSLATIONS_INTERACTIONS = {
    1: """# 交互演示（Interactions）

这是书中交互演示的集合。若你阅读纸质版，或通过 Github 或 nbviewer 在线阅读，将无法运行这些交互。

因此我创建了本 notebook。若你的电脑未安装 IPython，可按以下方式运行交互：

1. 在浏览器中打开 try.juptyer.org，它会为你启动一个临时 notebook 服务器。

2. 点击 **New** 按钮，选择 `Python 3`。这会在浏览器中创建一个运行 Python 3 的新 notebook。

3. 从本 notebook 复制某个单元格的全部内容，粘贴到浏览器 notebook 的 code 单元格中。

4. 按 CTRL+ENTER 执行该单元格。

5. 尽情尝试！改代码、玩耍、实验、折腾。

你的服务器与 notebook 不会永久保存。关闭会话后数据即丢失。是的，按保存会显示正在保存，目录里也能看到文件，但那只是在 Docker 容器里，关闭窗口后会被删除。若想保留修改，请复制粘贴到外部文件。

当然，若已安装 IPython，可下载本 notebook 在本地运行。在下载文件的目录下于命令行输入

    ipython notebook
    
点击本文件名即可打开。

""",

    2: """# 试验 FPF'

卡尔曼滤波（Kalman filter）在预测（prediction）步用方程 $P^- = FPF^\\mathsf{T}$ 计算协方差矩阵（covariance matrix）的先验（prior），其中 $P$ 是协方差矩阵，$F$ 是系统转移函数。对牛顿系统 $x = \\dot{x}\\Delta t + x_0$，$F$ 可能形如

$$F = \\begin{bmatrix}1 & \\Delta t\\\\0 & 1\\end{bmatrix}$$

$FPF^\\mathsf{T}$ 通过位置（$x$）与速度（$\\dot{x}$）之间的相关性改变 $P$。本交互图可让你看到不同 $F$ 设计对该值的影响。例如：

* 若 $x$ 与 $\\dot{x}$ 不相关？（将 F01 设为 0）

* 若 $x = 2\\dot{x}\\Delta t + x_0$？（将 F01 设为 2）

* 若 $x = \\dot{x}\\Delta t + 2*x_0$？（将 F00 设为 2）

* 若 $x = \\dot{x}\\Delta t$？（将 F00 设为 0）

""",

    4: """# 协方差椭圆（Covariance Ellipse）

观察如下形式协方差矩阵的方差与协方差变化带来的影响：

$$\\begin{bmatrix}\\texttt{var}_x & \\texttt{cov}_xy \\\\ \\texttt{cov}_xy & \\texttt{var}_y\\end{bmatrix}$$

""",

    6: """# g-h 滤波（g-h Filter）

试验 g-h 滤波（g-h filter）各参数的不同取值。

""",
}

TRANSLATIONS_ITERATIVE_LS = {
    0: """# 传感器融合的迭代最小二乘（Iterative Least Squares for Sensor Fusion）

""",

    2: """卡尔曼滤波（Kalman filter）的一大用途是*传感器融合（sensor fusion）*。例如，我们可能同时有位置传感器与速度传感器，希望合并两者数据得到最优状态估计。本节讨论另一种情况：多个传感器提供同类型测量。

全球定位系统（Global Positioning System, GPS）的设计保证地球任意时刻任意地点至少可见 6 颗卫星。GPS 接收机知道卫星相对地球在天空中的位置。每个历元（epoch，时刻）接收机从每颗卫星收到信号，由此可推导到该卫星的*伪距（pseudorange）*。更细地说，接收机收到标识卫星的信号以及发射时刻的时间戳。GPS 卫星载有原子钟，时间戳极其准确。信号以光速传播，真空中为常数，理论上 GPS 可通过测量信号到达时间给出极其精确的距离测量。但存在若干问题。首先，信号并非在真空中传播，而是穿过大气层，会发生弯曲，路径并非直线，到达时间比理论更长。其次，GPS *接收机*板载时钟并不精确，精确时间间隔不易得到。第三，在许多环境中信号会经建筑物、树木等反射，路径更长，或出现*多径（multipaths）*，接收机同时收到来自太空的原始信号与反射信号。

用图形说明。为便于绘图，我在 2D 中演示，当然可推广到三维。我们知道每颗卫星位置及到各星的距离（该距离称为*伪距*；原因稍后讨论）。距离无法精确测量，因此测量带有噪声，我用线条粗细表示。下面是四颗卫星的四条伪距读数示例。为便于可视化交点，我把卫星布置成与实际 GPS 星座不太相符的配置，误差大小也未按距离比例绘制，同样是为便于观察。

""",

    4: """在 2D 中，有时两次测量就足以确定唯一解。距离圆有两个交点，但第二个交点往往物理上不可实现（在太空中或地下）。不过 GPS 还需解算时间，2D 定位需要第三次测量。

GPS 是 3D 系统，需解空间三维与时间一维，共 4 个未知量。理论上 4 颗卫星即可，但通常至少可见 6 颗，往往更多。系统因此是*超定（overdetermined）*的。最后，由于测量噪声，伪距圆并不精确相交。

若你熟悉线性代数，会知道这在科学计算中极为常见，有多种求解超定系统的方法。GPS 接收机定位最常用的是*迭代最小二乘（iterative least squares）*算法，常缩写为 ILS。如你所知，若误差为高斯（Gaussian），最小二乘（least squares）给出最优解。换言之，我们要最小化超定系统残差（residual）的平方。

先从一些应已熟悉的定义开始。首先，新息（innovation）定义为

$$\\delta \\mathbf{\\bar{z}}= \\mathbf z - h(\\mathbf{\\bar{x}})$$

其中 $\\mathbf z$ 是测量，$h(\\bullet)$ 是测量函数，$\\delta \\mathbf{\\bar{z}}$ 是新息，在 FilterPy 中缩写为 $y$。换言之，这就是线性卡尔曼滤波更新步中的 $\\mathbf{y} = \\mathbf z - \\mathbf{H\\bar{x}}$。

接下来，*测量残差（measurement residual）*为

$$\\delta \\mathbf z^+ = \\mathbf z - h(\\mathbf x^+)$$

我不常用加号上标，因为很快会使方程难读，但 $\\mathbf x^+$ 是*后验（a posteriori）*状态估计，即预测或未知的未来状态。线性卡尔曼滤波的预测步计算该值。此处它表示 ILS 算法在每次迭代中将要计算的 $x$。

这些方程给出如下线性代数关系：

$$\\delta \\mathbf z^- = \\mathbf H\\delta \\mathbf x + \\delta \\mathbf z^+$$

$\\mathbf H$ 是测量函数，定义为

$$\\mathbf H = \\frac{d\\mathbf H}{d\\mathbf x} = \\frac{d\\mathbf z}{d\\mathbf x}$$

通过求导并令其为零可求方程最小值。此处要最小化残差平方，方程为

""",

    5: """$$ \\frac{\\partial}{\\partial \\mathbf x}({\\delta \\mathbf z^+}^\\mathsf{T}\\delta \\mathbf z^+) = 0,$$

其中

$$\\delta \\mathbf z^+=\\delta \\mathbf z^- - \\mathbf H\\delta \\mathbf x.$$

这里我改用矩阵 $\\mathbf H$ 作为测量函数。要用线性代数执行 ILS，每步须计算对应每次迭代中 $h(\\mathbf{x^-})$ 的矩阵 $\\mathbf H$。对此类问题 $h(\\bullet)$ 通常非线性，因此每步都需线性化（稍后详述）。

出于各种原因，你可能希望某些测量权重大于其他。例如问题几何可能更利于正交测量，或某些测量噪声更大。可用方程

$$ \\frac{\\partial}{\\partial \\mathbf x}({\\delta \\mathbf z^+}^\\mathsf{T}\\mathbf{W}\\delta \\mathbf z^+) = 0$$

对第一个方程求解 ${\\delta \\mathbf x}$（推导见下一节）得

$${\\delta \\mathbf x} = {{(\\mathbf H^\\mathsf{T}\\mathbf H)^{-1}}\\mathbf H^\\mathsf{T} \\delta \\mathbf z^-}
$$

第二个方程给出

$${\\delta \\mathbf x} = {{(\\mathbf H^\\mathsf{T}\\mathbf{WH})^{-1}}\\mathbf H^\\mathsf{T}\\mathbf{W} \\delta \\mathbf z^-}
$$

方程超定，无法精确求解，因此采用迭代：先猜初始位置，用该猜测通过上式计算 $\\delta \\mathbf x$，加到初始猜测上，新状态再代入方程得到另一个 $\\delta \\mathbf x$，如此迭代直到测量残差差值足够小。

""",

    6: """### ILS 方程推导

""",

    7: """我将在代码中实现 ILS，但先推导 $\\delta \\mathbf x$ 的方程。可跳过推导，但若你懂基本线性代数与偏微分方程，推导颇有教益且不难。

将 $\\delta \\mathbf z^+=\\delta \\mathbf z^- - \\mathbf H\\delta \\mathbf x$ 代入偏微分方程得

$$ \\frac{\\partial}{\\partial \\mathbf x}(\\delta \\mathbf z^- -\\mathbf H \\delta \\mathbf x)^\\mathsf{T}(\\delta \\mathbf z^- - \\mathbf H \\delta \\mathbf x)=0$$

展开为

$$ \\frac{\\partial}{\\partial \\mathbf x}({\\delta \\mathbf x}^\\mathsf{T}\\mathbf H^\\mathsf{T}\\mathbf H\\delta \\mathbf x - 
{\\delta \\mathbf x}^\\mathsf{T}\\mathbf H^\\mathsf{T}\\delta \\mathbf z^- - 
{\\delta \\mathbf z^-}^\\mathsf{T}\\mathbf H\\delta \\mathbf x +
{\\delta \\mathbf z^-}^\\mathsf{T}\\delta \\mathbf z^-)=0$$

""",

    8: """我们知道

$$\\frac{\\partial \\mathbf{A}^\\mathsf{T}\\mathbf B}{\\partial \\mathbf B} = \\frac{\\partial \\mathbf B^\\mathsf{T}\\mathbf{A}}{\\partial \\mathbf B} = \\mathbf{A}^\\mathsf{T}$$

因此第三项为

$$\\frac{\\partial}{\\partial \\mathbf x}{\\delta \\mathbf z^-}^\\mathsf{T}\\mathbf H\\delta \\mathbf x = {\\delta \\mathbf z^-}^\\mathsf{T}\\mathbf H$$

第二项为

$$\\frac{\\partial}{\\partial \\mathbf x}{\\delta \\mathbf x}^\\mathsf{T}\\mathbf H^\\mathsf{T}\\delta \\mathbf z^-={\\delta \\mathbf z^-}^\\mathsf{T}\\mathbf H$$

我们还知道
$$\\frac{\\partial \\mathbf B^\\mathsf{T}\\mathbf{AB}}{\\partial \\mathbf B} = \\mathbf B^\\mathsf{T}(\\mathbf{A} + \\mathbf{A}^\\mathsf{T})$$

因此第一项变为

$$
\\begin{aligned}
\\frac{\\partial}{\\partial \\mathbf x}{\\delta \\mathbf x}^\\mathsf{T}\\mathbf H^\\mathsf{T}\\mathbf H\\delta \\mathbf x &= {\\delta \\mathbf x}^\\mathsf{T}(\\mathbf H^\\mathsf{T}\\mathbf H + {\\mathbf H^\\mathsf{T}\\mathbf H}^\\mathsf{T})\\\\
&= {\\delta \\mathbf x}^\\mathsf{T}(\\mathbf H^\\mathsf{T}\\mathbf H + \\mathbf H^\\mathsf{T}\\mathbf H) \\\\
&= 2{\\delta \\mathbf x}^\\mathsf{T}\\mathbf H^\\mathsf{T}\\mathbf H
\\end{aligned}$$

第四项为

$$ \\frac{\\partial}{\\partial \\mathbf x}
{\\delta \\mathbf z^-}^\\mathsf{T}\\delta \\mathbf z^-=0$$

代入展开后的偏微分方程得

$$
 2{\\delta \\mathbf x}^\\mathsf{T}\\mathbf H^\\mathsf{T}\\mathbf H -
 {\\delta \\mathbf z^-}^\\mathsf{T}\\mathbf H - {\\delta \\mathbf z^-}^\\mathsf{T}\\mathbf H
 =0
$$

$${\\delta \\mathbf x}^\\mathsf{T}\\mathbf H^\\mathsf{T}\\mathbf H -
 {\\delta \\mathbf z^-}^\\mathsf{T}\\mathbf H = 0$$
 
$${\\delta \\mathbf x}^\\mathsf{T}\\mathbf H^\\mathsf{T}\\mathbf H =
 {\\delta \\mathbf z^-}^\\mathsf{T}\\mathbf H$$

两边乘以 $(\\mathbf H^\\mathsf{T}\\mathbf H)^{-1}$ 得

$${\\delta \\mathbf x}^\\mathsf{T} =
{\\delta \\mathbf z^-}^\\mathsf{T}\\mathbf H(\\mathbf H^\\mathsf{T}\\mathbf H)^{-1}$$

两边取转置得

$$\\begin{aligned}
{\\delta \\mathbf x} &= ({{\\delta \\mathbf z^-}^\\mathsf{T}\\mathbf H(\\mathbf H^\\mathsf{T}\\mathbf H)^{-1}})^\\mathsf{T} \\\\
&={{(\\mathbf H^\\mathsf{T}\\mathbf H)^{-1}}^T\\mathbf H^\\mathsf{T} \\delta \\mathbf z^-} \\\\
&={{(\\mathbf H^\\mathsf{T}\\mathbf H)^{-1}}\\mathbf H^\\mathsf{T} \\delta \\mathbf z^-}
\\end{aligned}$$

出于各种原因，你可能希望某些测量权重大于其他。可用方程

$$ \\frac{\\partial}{\\partial \\mathbf x}({\\delta \\mathbf z}^\\mathsf{T}\\mathbf{W}\\delta \\mathbf z) = 0$$

在上式推导中加上 $\\mathbf{W}$ 项，得到

$${\\delta \\mathbf x} = {{(\\mathbf H^\\mathsf{T}\\mathbf{WH})^{-1}}\\mathbf H^\\mathsf{T}\\mathbf{W} \\delta \\mathbf z^-}
$$

""",

    9: """### 实现迭代最小二乘

""",

    10: """我们的目标是实现
$${\\delta \\mathbf x} = {{(\\mathbf H^\\mathsf{T}\\mathbf H)^{-1}}\\mathbf H^\\mathsf{T} \\delta \\mathbf z^-}
$$
的迭代解。

首先须计算 $\\mathbf H$，其中 $\\mathbf H =  d\\mathbf z/d\\mathbf x$。为便于解读，在 2D 中演示。对 $n$ 颗卫星，$\\mathbf H$ 展开为

$$\\mathbf H = \\begin{bmatrix}
\\frac{\\partial p_1}{\\partial x_1} & \\frac{\\partial p_1}{\\partial y_1} \\\\
\\frac{\\partial p_2}{\\partial x_2} & \\frac{\\partial p_2}{\\partial y_2} \\\\
\\vdots & \\vdots \\\\
\\frac{\\partial p_n}{\\partial x_n} & \\frac{\\partial p_n}{\\partial y_n}
\\end{bmatrix}$$

对 $x$ 的偏导线性化 $\\mathbf H$ 为

$$ \\frac{estimated\\_x\\_position - satellite\\_x\\_position}{estimated\\_range\\_to\\_satellite}$$

$y$ 的方程只需把 $x$ 换成 $y$。

算法如下。

    def ILS:
        guess position
        while not converged:
            compute range to satellites for current estimated position
            compute H linearized at estimated position
            compute new estimate delta from (H^T H)'H^T dz
            new estimate = current estimate + estimate delta
            check for convergence
            

""",

    12: """我们来思考一下。第一次迭代本质上就是在做线性卡尔曼滤波更新步的计算：

$$\\begin{aligned}
\\mathbf y &= \\mathbf z - \\mathbf{Hx}\\\\
\\mathbf x &= \\mathbf x + \\mathbf{Ky}
\\end{aligned}$$

其中卡尔曼增益（Kalman gain）等于 1。尽管初始猜测 (900, 90) 非常不准，计算得到的 $\\mathbf x$ 为 (805.4, 205.3)，已非常接近真实值 (800, 200)，但仍非完美。三次迭代后 ILS 找到了精确答案。希望这能说明为何用 ILS 而非卡尔曼滤波做传感器融合——结果更好。当然，我们起步猜测很差；若猜测更好呢？

""",

    14: """第一次迭代改进了估计，但仍可通过继续迭代改善。

我在测量中未注入噪声，以测试并展示滤波器的理论性能。现在看看注入噪声后的表现。

""",

    16: """可见，噪声使我们无法得到精确解，但仍能快速收敛到比第一次迭代更准确的解。

这远非迭代最小二乘算法的完整介绍，更谈不上 GNSS 中从 GPS 伪距计算位置的方法。文献中有 QR 分解、SVD 等多种求解超定系统的技术。对非平凡任务，你可能需要查阅文献，并根据具体传感器配置、噪声水平、精度要求与可承受计算量设计算法。

""",
}

TRANSLATIONS_TAYLOR_SERIES = {
    1: """# 用泰勒级数线性化（Linearizing with Taylor Series）

泰勒级数（Taylor series）将函数表示为无穷项之和。各项是线性的，即使对非线性函数亦然，因此可用线性代数表达任意非线性函数。代价是：除非使用无穷多项，否则计算值是近似而非精确。

实函数或复函数 $f(x)$ 在 $x=a$ 处的泰勒级数为无穷级数

$$f(x) = f(a) + f'(a)(x-a) + \\frac{f''(a)}{2!}(x-a)^2 + \\, ...\\,  + \\frac{f^{(n)}(a)}{n!}(x-a)^n + \\, ...$$

其中 $f^{n}$ 是 $f$ 的 $n$ 阶导数。为计算 $f(x)=sin(x)$ 在 $x=0$ 处的泰勒级数，先求 $f$ 的各项：

$$\\begin{aligned}
f^{0}(x) &= sin(x) ,\\ \\  &f^{0}(0) &= 0 \\\\
f^{1}(x) &= cos(x),\\ \\  &f^{1}(0) &= 1 \\\\
f^{2}(x) &= -sin(x),\\ \\  &f^{2}(0) &= 0 \\\\
f^{3}(x) &= -cos(x),\\ \\  &f^{3}(0) &= -1 \\\\
f^{4}(x) &= sin(x),\\ \\  &f^{4}(0) &= 0 \\\\
f^{5}(x) &= cos(x),\\ \\  &f^{5}(0) &= 1
\\end{aligned}
$$

代入方程得

$$\\sin(x) = \\frac{0}{0!}(x)^0 + \\frac{1}{1!}(x)^1 + \\frac{0}{2!}(x)^2 + \\frac{-1}{3!}(x)^3 + \\frac{0}{4!}(x)^4 + \\frac{1}{5!}(x)^5 + ... $$

用代码验证：

""",

    3: """仅用三项已经不错。若好奇，可实现一个 Python 函数，计算任意项数的级数。

""",
}

NOTEBOOKS = {
    "Supporting_Notebooks/Computing_and_plotting_PDFs.ipynb": TRANSLATIONS_COMPUTING_PDFS,
    "Supporting_Notebooks/Converting-Multivariate-Equations-to-Univariate.ipynb": TRANSLATIONS_CONVERTING_MULTIVARIATE,
    "Supporting_Notebooks/Interactions.ipynb": TRANSLATIONS_INTERACTIONS,
    "Supporting_Notebooks/Iterative-Least-Squares-for-Sensor-Fusion.ipynb": TRANSLATIONS_ITERATIVE_LS,
    "Supporting_Notebooks/Taylor-Series.ipynb": TRANSLATIONS_TAYLOR_SERIES,
}
