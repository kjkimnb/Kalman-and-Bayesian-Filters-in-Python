# -*- coding: utf-8 -*-
"""11-Extended-Kalman-Filters.ipynb markdown 译文"""

TRANSLATIONS_11 = {
0: "[目录](./table_of_contents.ipynb)\n",

1: "# 扩展卡尔曼滤波（Extended Kalman Filter, EKF）\n",

4: """我们已经建立了线性卡尔曼滤波（Kalman filter）的理论。随后两章我们接触了将卡尔曼滤波用于非线性问题的话题。本章将学习扩展卡尔曼滤波（Extended Kalman Filter, EKF）。EKF 在当前估计点处对系统进行线性化，然后用线性卡尔曼滤波对该线性化系统滤波。它是最早用于非线性问题的技术之一，至今仍是最常见的方法。

EKF 给滤波器设计者带来显著的数学挑战；这是全书最具挑战性的一章。我尽可能避免 EKF，转而采用为处理非线性问题而发展的其他技术。然而这一主题无法回避：该领域所有经典论文以及大多数当代论文都使用 EKF。即使你自己不用 EKF，也需要熟悉它才能阅读文献。

""",

5: """## 卡尔曼滤波的线性化（Linearizing the Kalman Filter）

卡尔曼滤波使用线性方程，因此不适用于非线性问题。问题可以在两方面非线性。第一，过程模型（process model）可能非线性。物体穿过大气下落时会遇到阻力，从而减小加速度。阻力系数随物体速度变化，由此产生的行为是非线性的——无法用线性方程建模。第二，测量（measurement）可能非线性。例如，雷达给出目标的距离和方位，我们用三角函数（非线性）计算目标位置。

对线性滤波器，过程模型与测量模型为：

$$\\begin{aligned}\\dot{\\mathbf x} &= \\mathbf{Ax} + w_x\\\\
\\mathbf z &= \\mathbf{Hx} + w_z
\\end{aligned}$$

其中 $\\mathbf A$ 是系统动力学矩阵（systems dynamic matrix）。用 **卡尔曼滤波数学（Kalman Filter Math）** 一章中的状态空间方法，可将这些方程化为
$$\\begin{aligned}\\bar{\\mathbf x} &= \\mathbf{Fx} \\\\
\\mathbf z &= \\mathbf{Hx}
\\end{aligned}$$

其中 $\\mathbf F$ 是 *基本矩阵（fundamental matrix）*。噪声项 $w_x$ 和 $w_z$ 并入矩阵 $\\mathbf R$ 和 $\\mathbf Q$。这种形式使我们能在给定第 $k$ 步测量和第 $k-1$ 步状态估计时计算第 $k$ 步状态。前面章节我用牛顿方程可描述的问题建立直觉并尽量减少数学；我们知道如何根据高中物理设计 $\\mathbf F$。


对非线性模型，线性表达式 $\\mathbf{Fx} + \\mathbf{Bu}$ 由非线性函数 $f(\\mathbf x, \\mathbf u)$ 取代，线性表达式 $\\mathbf{Hx}$ 由非线性函数 $h(\\mathbf x)$ 取代：

$$\\begin{aligned}\\dot{\\mathbf x} &= f(\\mathbf x, \\mathbf u) + w_x\\\\
\\mathbf z &= h(\\mathbf x) + w_z
\\end{aligned}$$

你或许会想，我们可以寻找一组新的卡尔曼滤波方程来最优地求解这些式子。但若你记得 **非线性滤波（Nonlinear Filtering）** 一章中的图示，高斯分布经过非线性函数后得到的概率分布不再是高斯分布，因此这条路行不通。

EKF 并不改变卡尔曼滤波的线性方程。相反，它在当前估计点对非线性方程进行 *线性化（linearize）*，并在线性卡尔曼滤波中使用该线性化结果。

*线性化* 顾名思义：在指定点找一条最贴近曲线的直线。下图在 $x=1.5$ 处对抛物线 $f(x)=x^2-2x$ 线性化。

""",

7: """若上图曲线是过程模型，则虚线表示在估计 $x=1.5$ 处对该曲线的线性化。

我们通过求导对系统线性化，导数给出曲线在某点的斜率：

$$\\begin{aligned}
f(x) &= x^2 -2x \\\\
\\frac{df}{dx} &= 2x - 2
\\end{aligned}$$

然后在 $x$ 处求值：

$$\\begin{aligned}m &= f'(x=1.5) \\\\&= 2(1.5) - 2 \\\\&= 1\\end{aligned}$$ 

微分方程组的线性化类似。对 $f(\\mathbf x, \\mathbf u)$ 和 $h(\\mathbf x)$ 分别求偏导，在点 $\\mathbf x_t$ 和 $\\mathbf u_t$ 处求值得到 $\\mathbf F$ 和 $\\mathbf H$。矩阵的偏导称为 [*雅可比（Jacobian）*](https://en.wikipedia.org/wiki/Jacobian_matrix_and_determinant)。由此得到离散状态转移矩阵与测量模型矩阵：

$$
\\begin{aligned}
\\mathbf F 
&= {\\frac{\\partial{f(\\mathbf x_t, \\mathbf u_t)}}{\\partial{\\mathbf x}}}\\biggr|_{{\\mathbf x_t},{\\mathbf u_t}} \\\\
\\mathbf H &= \\frac{\\partial{h(\\bar{\\mathbf x}_t)}}{\\partial{\\bar{\\mathbf x}}}\\biggr|_{\\bar{\\mathbf x}_t} 
\\end{aligned}
$$

由此得到 EKF 的下列方程。我用方框标出与线性滤波器的差异：

$$\\begin{array}{l|l}
\\text{linear Kalman filter} & \\text{EKF} \\\\
\\hline 
& \\boxed{\\mathbf F = {\\frac{\\partial{f(\\mathbf x_t, \\mathbf u_t)}}{\\partial{\\mathbf x}}}\\biggr|_{{\\mathbf x_t},{\\mathbf u_t}}} \\\\
\\mathbf{\\bar x} = \\mathbf{Fx} + \\mathbf{Bu} & \\boxed{\\mathbf{\\bar x} = f(\\mathbf x, \\mathbf u)}  \\\\
\\mathbf{\\bar P} = \\mathbf{FPF}^\\mathsf{T}+\\mathbf Q  & \\mathbf{\\bar P} = \\mathbf{FPF}^\\mathsf{T}+\\mathbf Q \\\\
\\hline
& \\boxed{\\mathbf H = \\frac{\\partial{h(\\bar{\\mathbf x}_t)}}{\\partial{\\bar{\\mathbf x}}}\\biggr|_{\\bar{\\mathbf x}_t}} \\\\
\\textbf{y} = \\mathbf z - \\mathbf{H \\bar{x}} & \\textbf{y} = \\mathbf z - \\boxed{h(\\bar{x})}\\\\
\\mathbf{K} = \\mathbf{\\bar{P}H}^\\mathsf{T} (\\mathbf{H\\bar{P}H}^\\mathsf{T} + \\mathbf R)^{-1} & \\mathbf{K} = \\mathbf{\\bar{P}H}^\\mathsf{T} (\\mathbf{H\\bar{P}H}^\\mathsf{T} + \\mathbf R)^{-1} \\\\
\\mathbf x=\\mathbf{\\bar{x}} +\\mathbf{K\\textbf{y}} & \\mathbf x=\\mathbf{\\bar{x}} +\\mathbf{K\\textbf{y}} \\\\
\\mathbf P= (\\mathbf{I}-\\mathbf{KH})\\mathbf{\\bar{P}} & \\mathbf P= (\\mathbf{I}-\\mathbf{KH})\\mathbf{\\bar{P}}
\\end{array}$$

对 EKF，我们通常不用 $\\mathbf{Fx}$ 传播状态，因为线性化会带来误差。典型做法是用合适的数值积分技术（如 Euler 或 Runge Kutta）计算 $\\bar{\\mathbf x}$，因此我写 $\\mathbf{\\bar x} = f(\\mathbf x, \\mathbf u)$。同理，残差（residual）计算中不用 $\\mathbf{H\\bar{x}}$，而采用更准确的 $h(\\bar{\\mathbf x})$。

我认为理解 EKF 的最好方式是从例子入手。稍后你可能想回来重读本节。

""",

8: """## 算例：跟踪飞机（Example: Tracking an Airplane）

本例用地面雷达跟踪飞机。上一章我们对同一问题实现了 UKF（无迹卡尔曼滤波，Unscented Kalman Filter）。现在为同一问题实现 EKF，以便比较滤波性能与实现工作量。

雷达发射无线电波束并扫描回波。波束路径上的物体会将部分信号反射回雷达。通过测量反射信号往返时间，系统可计算 *斜距（slant distance）*——从雷达到目标的直线距离。

雷达斜距 $r$、仰角 $\\epsilon$ 与飞机水平位置 $x$、高度 $y$ 的关系见下图：

""",

10: """由此得到等式：

$$\\begin{aligned}
\\epsilon &= \\tan^{-1} \\frac y x\\\\
r^2 &= x^2 + y^2
\\end{aligned}$$ 

""",

11: """### 设计状态变量（Design the State Variables）

假设飞机以恒定速度与高度飞行，测量为到飞机的斜距。因此需要 3 个状态变量——水平距离、水平速度与高度：

$$\\mathbf x = \\begin{bmatrix}\\mathtt{distance} \\\\\\mathtt{velocity}\\\\ \\mathtt{altitude}\\end{bmatrix}=    \\begin{bmatrix}x \\\\ \\dot x\\\\ y\\end{bmatrix}$$

""",

12: """### 设计过程模型（Design the Process Model）

假设飞机为牛顿运动学系统。前面章节用过该模型，一眼可认出我们需要的

$$\\mathbf F = \\left[\\begin{array}{cc|c} 1 & \\Delta t & 0\\\\
0 & 1 & 0 \\\\ \\hline
0 & 0 & 1\\end{array}\\right]$$

我把矩阵分块，表明左上块是 $x$ 的匀速模型，右下块是 $y$ 的恒定位移模型。

不过让我们练习如何求这些矩阵。我们用一组微分方程建模系统，需要形如

$$\\dot{\\mathbf x} = \\mathbf{Ax} + \\mathbf{w}$$
的方程，其中 $\\mathbf{w}$ 是系统噪声。

变量 $x$ 与 $y$ 独立，可分别计算。一维运动微分方程为：

$$\\begin{aligned}v &= \\dot x \\\\
a &= \\ddot{x} = 0\\end{aligned}$$

将其写成状态空间形式。若是二阶或更高阶微分系统，须先化为等价的一阶方程组。这里已是一阶，写成矩阵形式：

$$\\begin{aligned}\\begin{bmatrix}\\dot x \\\\ \\ddot{x}\\end{bmatrix} &= \\begin{bmatrix}0&1\\\\0&0\\end{bmatrix} \\begin{bmatrix}x \\\\ 
\\dot x\\end{bmatrix} \\\\ \\dot{\\mathbf x} &= \\mathbf{Ax}\\end{aligned}$$
其中 $\\mathbf A=\\begin{bmatrix}0&1\\\\0&0\\end{bmatrix}$。

回忆 $\\mathbf A$ 是 *系统动力学矩阵（system dynamics matrix）*，描述一组线性微分方程。由它须计算状态转移矩阵 $\\mathbf F$。$\\mathbf F$ 描述离散线性方程，在离散时间步 $\\Delta t$ 上计算 $\\mathbf x$。

常用做法是用矩阵指数的幂级数展开计算 $\\mathbf F$：

$$\\mathbf F(\\Delta t) = e^{\\mathbf A\\Delta t} = \\mathbf{I} + \\mathbf A\\Delta t  + \\frac{(\\mathbf A\\Delta t)^2}{2!} + \\frac{(\\mathbf A \\Delta t)^3}{3!} + ... $$


$\\mathbf A^2 = \\begin{bmatrix}0&0\\\\0&0\\end{bmatrix}$，故 $\\mathbf A$ 的更高次幂亦为 $\\mathbf{0}$。幂级数展开为：

$$
\\begin{aligned}
\\mathbf F &=\\mathbf{I} + \\mathbf At + \\mathbf{0} \\\\
&= \\begin{bmatrix}1&0\\\\0&1\\end{bmatrix} + \\begin{bmatrix}0&1\\\\0&0\\end{bmatrix}\\Delta t\\\\
\\mathbf F &= \\begin{bmatrix}1&\\Delta t\\\\0&1\\end{bmatrix}
\\end{aligned}$$

这与运动学方程结果相同！本练习除说明如何从线性微分方程求状态转移矩阵外并非必要。本章末尾将给出需要该技巧的例子。

""",

13: """### 设计测量模型（Design the Measurement Model）

测量函数将先验 $\\bar{\\mathbf x}$ 的状态估计转为斜距测量。由勾股定理：

$$h(\\bar{\\mathbf x}) = \\sqrt{x^2 + y^2}$$

斜距与地面位置的关系因平方根而非线性。我们在 $\\mathbf x_t$ 处求偏导进行线性化：

$$
\\mathbf H = \\frac{\\partial{h(\\bar{\\mathbf x})}}{\\partial{\\bar{\\mathbf x}}}\\biggr|_{\\bar{\\mathbf x}_t}
$$

矩阵的偏导称为雅可比（Jacobian），形式为

$$\\frac{\\partial \\mathbf H}{\\partial \\bar{\\mathbf x}} = 
\\begin{bmatrix}
\\frac{\\partial h_1}{\\partial x_1} & \\frac{\\partial h_1}{\\partial x_2} &\\dots \\\\
\\frac{\\partial h_2}{\\partial x_1} & \\frac{\\partial h_2}{\\partial x_2} &\\dots \\\\
\\vdots & \\vdots
\\end{bmatrix}
$$

即矩阵每个元素是函数 $h$ 对 $x$ 变量的偏导。对本题：

$$\\mathbf H = \\begin{bmatrix}{\\partial h}/{\\partial x} & {\\partial h}/{\\partial \\dot{x}} & {\\partial h}/{\\partial y}\\end{bmatrix}$$

逐项求解：

$$\\begin{aligned}
\\frac{\\partial h}{\\partial x} &= \\frac{\\partial}{\\partial x} \\sqrt{x^2 + y^2} \\\\
&= \\frac{x}{\\sqrt{x^2 + y^2}}
\\end{aligned}$$

以及

$$\\begin{aligned}
\\frac{\\partial h}{\\partial \\dot{x}} &=
\\frac{\\partial}{\\partial \\dot{x}} \\sqrt{x^2 + y^2} \\\\ 
&= 0
\\end{aligned}$$

以及

$$\\begin{aligned}
\\frac{\\partial h}{\\partial y} &= \\frac{\\partial}{\\partial y} \\sqrt{x^2 + y^2} \\\\ 
&= \\frac{y}{\\sqrt{x^2 + y^2}}
\\end{aligned}$$

得到

$$\\mathbf H = 
\\begin{bmatrix}
\\frac{x}{\\sqrt{x^2 + y^2}} & 
0 &
&
\\frac{y}{\\sqrt{x^2 + y^2}}
\\end{bmatrix}$$

这看似吓人，但退一步看，这些数学做的其实很简单：我们有到飞机斜距的非线性方程，而卡尔曼滤波只处理线性方程，因此需要找近似 $\\mathbf H$ 的线性方程。如上所述，在给定点求非线性方程斜率是良好近似。对卡尔曼滤波，“给定点”是状态变量 $\\mathbf x$，故须对斜距关于 $\\mathbf x$ 求导。线性卡尔曼滤波中 $\\mathbf H$ 是运行前算好的常数；EKF 中 $\\bar{\\mathbf x}$ 每步变化，故 $\\mathbf H$ 每步更新。

为更具体，下面写计算本题 $h$ 的雅可比的 Python 函数。

""",

15: "最后，给出 $h(\\bar{\\mathbf x})$ 的代码：\n",

17: "下面为雷达编写仿真。\n",

19: """### 设计过程噪声与测量噪声（Design Process and Measurement Noise）

雷达测量到目标的距离。取 $\\sigma_{range}= 5$ 米噪声，得

$$\\mathbf R = \\begin{bmatrix}\\sigma_{range}^2\\end{bmatrix} = \\begin{bmatrix}25\\end{bmatrix}$$


$\\mathbf Q$ 的设计需要讨论。状态 $\\mathbf x= \\begin{bmatrix}x & \\dot x & y\\end{bmatrix}^\\mathtt{T}$。前两个元素是位置（沿程距离）与速度，可用 `Q_discrete_white_noise` 计算 $\\mathbf Q$ 左上块。$\\mathbf x$ 第三元素是高度，假设与沿程距离独立，故 $\\mathbf Q$ 分块为：

$$\\mathbf Q = \\begin{bmatrix}\\mathbf Q_\\mathtt{x} & 0 \\\\ 0 & \\mathbf Q_\\mathtt{y}\\end{bmatrix}$$

""",

20: """### 实现（Implementation）

`FilterPy` 提供类 `ExtendedKalmanFilter`。它与我们一直用的 `KalmanFilter` 类似，但允许提供计算 $\\mathbf H$ 的雅可比及函数 $h(\\mathbf x)$ 的函数。

先导入滤波器并创建。`x` 维数为 3，`z` 维数为 1。

```python
from filterpy.kalman import ExtendedKalmanFilter

rk = ExtendedKalmanFilter(dim_x=3, dim_z=1)
```
创建雷达仿真：
```python
radar = RadarSim(dt, pos=0., vel=100., alt=1000.)
```
在飞机实际位置附近初始化滤波器：

```python
rk.x = array([radar.pos, radar.vel-10, radar.alt+100])
```

用上面泰勒展开第一项赋值系统矩阵：

```python
dt = 0.05
rk.F = eye(3) + array([[0, 1, 0],
                       [0, 0, 0],
                       [0, 0, 0]])*dt
```

为 $\\mathbf R$、$\\mathbf Q$、$\\mathbf P$ 赋合理值后，用简单循环运行滤波器。将计算 $\\mathbf  H$ 雅可比与 $h(x)$ 的函数传入 `update`：

```python
for i in range(int(20/dt)):
    z = radar.get_range()
    rk.update(array([z]), HJacobian_at, hx)
    rk.predict()
```

加上保存与绘图的样板代码，得到：

""",

22: """## 用 SymPy 计算雅可比（Using SymPy to compute Jacobians）

依你对导数的熟悉程度，求雅可比可能觉得困难。即便你觉得容易，稍难一点的问题也会使计算非常棘手。

如附录 A 所述，可用 SymPy 包为我们计算雅可比。

""",

24: "该结果与上面手算一致，且省力得多！\n",

25: """## 机器人定位（Robot Localization）

该做一道真实问题了。本节较难。不过多数书选简单教科书题、给出简单答案，你会疑惑如何解决现实世界问题。

我们考虑机器人定位（robot localization）。**无迹卡尔曼滤波（Unscented Kalman Filter）** 一章已实现过；若尚未阅读建议现在读。场景是机器人在环境中移动，用传感器检测地标。可能是自动驾驶车用计算机视觉识别树木、建筑等地标，也可能是扫地机器人或仓库机器人。

机器人采用与汽车相同的四轮布局，通过转动前轮机动，绕后轴枢转前进。这是非线性行为，必须建模。

机器人传感器测量到景观中已知目标的距离与方位，含噪声。由距离与方位求位置需要开方与三角函数，故非线性。

过程模型与测量模型均非线性。EKF 可处理二者，因此我们暂定 EKF 适合本题。

""",

26: """### 机器人运动模型（Robot Motion Model）

一阶近似下，汽车通过前进时转动前轮转向。车头沿车轮指向移动，绕后轴枢转。该简单描述受摩擦打滑、轮胎随速度不同行为、内外轮半径不同等因素影响而复杂。精确转向建模需要复杂微分方程组。

对较低速机器人应用，较简单的 *自行车模型（bicycle model）* 表现良好。模型示意如下：

""",

28: """在 **无迹卡尔曼滤波（Unscented Kalman Filter）** 一章我们推导出：

$$\\begin{aligned} 
\\beta &= \\frac d w \\tan(\\alpha) \\\\
x &= x - R\\sin(\\theta) + R\\sin(\\theta + \\beta) \\\\
y &= y + R\\cos(\\theta) - R\\cos(\\theta + \\beta) \\\\
\\theta &= \\theta + \\beta
\\end{aligned}
$$

其中 $\\theta$ 是机器人航向。

若对转向模型不感兴趣，不必细究该模型。重要的是运动模型非线性，须用卡尔曼滤波处理。

""",

29: """### 设计状态变量（Design the State Variables）

滤波器维护机器人位置 $x,y$ 与朝向 $\\theta$：

$$\\mathbf x = \\begin{bmatrix}x \\\\ y \\\\ \\theta\\end{bmatrix}$$

控制输入 $\\mathbf u$ 为速度 $v$ 与转向角 $\\alpha$：

$$\\mathbf u = \\begin{bmatrix}v \\\\ \\alpha\\end{bmatrix}$$

""",

30: """### 设计系统模型（Design the System Model）

系统建模为非线性运动模型加噪声。

$$\\bar x = f(x, u) + \\mathcal{N}(0, Q)$$



用上文机器人运动模型，可展开为

$$\\bar{\\begin{bmatrix}x\\\\y\\\\\\theta\\end{bmatrix}} = \\begin{bmatrix}x\\\\y\\\\\\theta\\end{bmatrix} + 
\\begin{bmatrix}- R\\sin(\\theta) + R\\sin(\\theta + \\beta) \\\\
R\\cos(\\theta) - R\\cos(\\theta + \\beta) \\\\
\\beta\\end{bmatrix}$$

对 $f(x,u)$ 求雅可比得 $\\mathbf F$。

$$\\mathbf F = \\frac{\\partial f(x, u)}{\\partial x} =\\begin{bmatrix}
\\frac{\\partial f_1}{\\partial x} & 
\\frac{\\partial f_1}{\\partial y} &
\\frac{\\partial f_1}{\\partial \\theta}\\\\
\\frac{\\partial f_2}{\\partial x} & 
\\frac{\\partial f_2}{\\partial y} &
\\frac{\\partial f_2}{\\partial \\theta} \\\\
\\frac{\\partial f_3}{\\partial x} & 
\\frac{\\partial f_3}{\\partial y} &
\\frac{\\partial f_3}{\\partial \\theta}
\\end{bmatrix}
$$

计算得

$$\\mathbf F = \\begin{bmatrix}
1 & 0 & -R\\cos(\\theta) + R\\cos(\\theta+\\beta) \\\\
0 & 1 & -R\\sin(\\theta) + R\\sin(\\theta+\\beta) \\\\
0 & 0 & 1
\\end{bmatrix}$$

可用 SymPy 复核。

""",

32: "看起来有点复杂。可用 SymPy 代入化简：\n",

34: """该形式验证雅可比计算正确。

现在看噪声。噪声在控制输入中，故在 *控制空间（control space）*。即我们命令特定速度与转向角，但须将其转为 $x, y, \\theta$ 的误差。真实系统中这可能随速度变化，每步预测都需重算。我选下列噪声模型；真实机器人须选能准确描述系统误差的模型。

$$\\mathbf{M} = \\begin{bmatrix}\\sigma_{vel}^2 & 0 \\\\ 0 & \\sigma_\\alpha^2\\end{bmatrix}$$

若是线性问题，用熟悉的 $\\mathbf{FMF}^\\mathsf T$ 从控制空间转到状态空间。运动模型非线性时，不求闭式解，而用雅可比线性化，记为 $\\mathbf{V}$。

$$\\mathbf{V} = \\frac{\\partial f(x, u)}{\\partial u} \\begin{bmatrix}
\\frac{\\partial f_1}{\\partial v} & \\frac{\\partial f_1}{\\partial \\alpha} \\\\
\\frac{\\partial f_2}{\\partial v} & \\frac{\\partial f_2}{\\partial \\alpha} \\\\
\\frac{\\partial f_3}{\\partial v} & \\frac{\\partial f_3}{\\partial \\alpha}
\\end{bmatrix}$$

这些偏导很难手算。用 SymPy 计算。

""",

36: """这应让你体会到 EKF 的数学多么快变得难以处理。

预测方程的最终形式为：

$$\\begin{aligned}
\\mathbf{\\bar x} &= \\mathbf x + 
\\begin{bmatrix}- R\\sin(\\theta) + R\\sin(\\theta + \\beta) \\\\
R\\cos(\\theta) - R\\cos(\\theta + \\beta) \\\\
\\beta\\end{bmatrix}\\\\
\\mathbf{\\bar P} &=\\mathbf{FPF}^{\\mathsf T} + \\mathbf{VMV}^{\\mathsf T}
\\end{aligned}$$

线性化并非预测 $\\mathbf x$ 的唯一方式。例如可用 *Runge Kutta* 等数值积分计算机器人运动。时间步较大时必须如此。EKF 不像卡尔曼滤波那样一刀切；真实问题须仔细用微分方程建模，再选最合适的求解方式，取决于精度、非线性程度、处理器预算与数值稳定性。

""",

37: """### 设计测量模型（Design the Measurement Model）

机器人传感器对景观中多个已知位置给出含噪声的距离与方位。测量模型须将状态 $\\begin{bmatrix}x & y&\\theta\\end{bmatrix}^\\mathsf T$ 转为到地标的距离与方位。若 $\\mathbf p$ 为地标位置，距离 $r$ 为

$$r = \\sqrt{(p_x - x)^2 + (p_y - y)^2}$$

传感器给出相对机器人朝向的方位，故须从方位中减去机器人朝向：

$$\\phi = \\arctan(\\frac{p_y - y}{p_x - x}) - \\theta$$


测量模型 $h$ 为


$$\\begin{aligned}
\\mathbf z& = h(\\bar{\\mathbf x}, \\mathbf p) &+ \\mathcal{N}(0, R)\\\\
&= \\begin{bmatrix}
\\sqrt{(p_x - x)^2 + (p_y - y)^2} \\\\
\\arctan(\\frac{p_y - y}{p_x - x}) - \\theta 
\\end{bmatrix} &+ \\mathcal{N}(0, R)
\\end{aligned}$$

显然非线性，须在 $\\mathbf x$ 处对 $h$ 求雅可比线性化。下面用 SymPy 计算。

""",

39: "下面写成 Python 函数，例如：\n",

41: "还需定义将系统状态转为测量的函数。\n",

43: """### 设计测量噪声（Design Measurement Noise）

合理假设距离与方位测量噪声独立，故

$$\\mathbf R=\\begin{bmatrix}\\sigma_{range}^2 & 0 \\\\ 0 & \\sigma_{bearing}^2\\end{bmatrix}$$

""",

44: """### 实现（Implementation）

用 `FilterPy` 的 `ExtendedKalmanFilter` 实现滤波器。其 `predict()` 用标准线性过程方程；我们的非线性，须用自定义 `predict()` 覆盖。还想用该类仿真机器人，故增加 `move()` 计算机器人位置，供 `predict()` 与仿真共用。

预测步矩阵很大。编写时我犯过几次错才跑通，靠 SymPy 的 `evalf` 才发现。`evalf` 用字典为变量赋具体值求 `Matrix`。卡尔曼滤波代码里也会演示。

首先，`evalf` 用字典指定值，例如矩阵含 `x`、`y` 时可写

```python
    M.evalf(subs={x:3, y:17})
```
    
为 `x=3`、`y=17` 求值。

其次，`evalf` 返回 `sympy.Matrix`。用 `numpy.array(M).astype(float)` 转为 NumPy 数组。`numpy.array(M)` 会得到 `object` 类型数组，不是我们想要的。

EKF 代码如下：

""",

46: """还有一问题：残差名义上为 $y = z - h(x)$，但测量含角度。设 $z$ 方位为 $1^\\circ$，$h(x)$ 为 $359^\\circ$，直接相减得 $-358^\\circ$，正确应为 $2^\\circ$。须写代码正确计算方位残差。

""",

48: """其余代码运行仿真并绘图，此时应无需多讲。变量 `landmarks` 存地标坐标。仿真机器人位置每秒更新 10 次，EKF 每秒只运行一次，原因有二：未用 Runge Kutta 积分运动微分方程，小时间步使仿真更准；嵌入式系统处理器有限，卡尔曼滤波只能按需频率运行。

""",

51: """地标画为实心方块。机器人路径为黑线。预测步协方差椭圆为浅灰，更新为绿色。为在此尺度可见，椭圆边界设为 $6\\sigma$。

可见运动模型引入大量不确定性，且误差多在运动方向，由蓝色椭圆形状可见。几步后滤波器融合地标测量，误差改善。

我在 UKF 章使用相同初始条件与地标。UKF 在误差椭圆上精度高得多；对 $\\mathbf x$ 估计二者大致相当。

再加一个地标。

""",

53: "航迹末端估计不确定性更小。仅用前两个地标可见多地标对不确定性的影响。\n",

55: "飞过地标后估计很快偏离机器人路径，协方差也迅速增大。只看一个地标会怎样：\n",

57: "如你所料，一个地标结果很差；反之，多地标可得很准的估计。\n",

59: """### 讨论（Discussion）

我说这是真实问题，某种程度上确实如此。我见过用更简单运动模型、雅可比更简单的讲法。另一方面，我的运动模型在几方面仍简化：用自行车模型；真车有两组轮胎、半径不同；轮胎抓地不完美；还假设机器人瞬时响应控制输入。Sebastian Thrun 在 *Probabilistic Robots* 中写道，该简化模型在跟踪真实车辆时滤波器仍表现良好。教训是：须有 reasonably accurate 的非线性模型，但不必完美也能工作。设计者须在模型保真度、数学难度与线性代数 CPU 时间之间权衡。

本题另一简化是假设已知地标与测量的对应关系。若用雷达，如何知道某回波对应场景中哪栋建筑？这指向 SLAM（同时定位与建图）算法——本书不展开。

""",

60: """## UKF 与 EKF（UKF vs EKF）


上一章用 UKF 解了本题。实现差异应很明显。即便运动模型简单，求状态与测量模型的雅可比也不轻松；换一题可能难以甚至无法解析求雅可比。相比之下，UKF 只需提供计算系统运动模型与测量模型的函数。

许多情况无法解析求雅可比，细节超出本书范围，须用数值方法，并不轻松，硕士阶段会花大量时间学。即便如此往往只擅长本领域——航空工程师熟 Navier Stokes，未必熟化学反应速率建模。

那么 UKF 容易，是否准确？实践中常优于 EKF。大量论文证明 UKF 在各领域优于 EKF 不难理解：EKF 在单点线性化系统与测量模型，UKF 用 $2n+1$ 个采样点。

看具体例子：$f(x)=x^3$，高斯分布穿过它。用蒙特卡洛（Monte Carlo）仿真得准确答案：按高斯随机抽 50,000 点，经 $f(x)$，算均值与方差。

EKF 在当前估计点 $x$ 求导得斜率，用该线性函数变换高斯。下图所示。

""",

62: "EKF 计算相当不准。对比 UKF 的表现：\n",

64: """可见 UKF 均值精确到小数点后两位。标准差略偏，也可用生成 sigma 点的 $\\alpha$、$\\beta$、$\\gamma$ 参数微调 UKF 的分布计算。这里 $\\alpha=0.001$、$\\beta=3$、$\\gamma=1$。可修改看效果，应能比我更好。但避免为特定测试过度调参；可能对某测试更好，泛化更差。

""",
}
