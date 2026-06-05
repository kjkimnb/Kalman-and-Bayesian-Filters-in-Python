# -*- coding: utf-8 -*-
"""08-Designing-Kalman-Filters.ipynb markdown 译文（第 1 部分）"""

TRANSLATIONS_08_PART1 = {
0: "[目录](./table_of_contents.ipynb)\n",

1: "# 设计卡尔曼滤波（Designing Kalman Filters）\n",

4: "## 引言（Introduction）\n",

5: """在上一章我们处理的是「教科书式」问题——易于陈述、几行代码即可实现、便于教学。真实世界的问题很少如此简单。本章我们将处理更贴近现实的例子，并学习如何评估滤波器性能。

我们将从在二维空间（如场地或仓库）中跟踪机器人开始。先用一个简单的带噪传感器，输出带噪的 $(x,y)$ 坐标，需滤波以生成二维轨迹。掌握这一概念后，我们会加入更多传感器，再引入控制输入。

随后转向非线性问题。世界是非线性的，而卡尔曼滤波（Kalman filter）是线性的。有时可用于轻度非线性问题，有时不行。我会展示两种情况的例子，为本书余下学习非线性技术的内容铺垫。

""",

6: "## 跟踪机器人（Tracking a Robot）\n",

7: """第一次尝试跟踪机器人，与前面章节的二维狗跟踪问题非常相似。不再是输出走廊位置的传感器，而是提供二维空间中位置带噪测量的传感器。每个时刻 $t$ 它给出传感器在场地中带噪位置的 $(x,y)$ 坐标对。

与真实传感器交互的代码超出本书范围，因此与之前一样，我们编写传感器的简单仿真。随着深入，我们会开发多种传感器，每种更复杂；编程时我会在函数名后加编号。

先从非常简单的传感器开始：模拟物体沿直线运动。初始化时给定初始位置、速度与噪声标准差。每次调用 `read()` 将位置推进一个时间步并返回新测量。

""",

9: "快速测试，确认其按预期工作。\n",

11: "看起来正确。斜率为 1/2，与速度 (2, 1) 一致，数据似乎起始于 (6, 4) 附近。它并不逼真——仍是「教科书式」表示。继续时我们会加入更贴近真实行为的复杂因素。\n",

12: "### 选择状态变量（Choose the State Variables）\n",

13: """与往常一样，第一步是选择状态变量（state variables）。我们在二维跟踪，传感器在两个维度都有读数，因此已知两个**观测变量（observed variables）** $x$ 与 $y$。若只用这两个变量建卡尔曼滤波，性能不会很好，因为我们忽略了速度能提供的信息。我们想把速度纳入方程，表示为

$$\\mathbf x = 
\\begin{bmatrix}x & \\dot x & y & \\dot y\\end{bmatrix}^\\mathsf T$$

这种排列并无特殊之处。我也可以用 $\\begin{bmatrix}x & y & \\dot x &  \\dot y\\end{bmatrix}^\\mathsf T$ 或其他顺序，只要在其余矩阵中保持一致。我喜欢位置与速度相邻，这样位置与速度之间的协方差（covariance）留在协方差矩阵的同一子块。在我的形式下 `P[1,0]` 是 $x$ 与 $\\dot x$ 的协方差；另一种形式则在 `P[2, 0]`。维度增多时会更麻烦。

暂停一下：如何识别**隐变量（hidden variables）**？本例 在一定程度上明显，因为我们已做过一维情形；其他问题则未必。没有简单答案。首先要问：传感器数据的物理含义及其一阶、二阶导数是什么？因为若固定时间步读取传感器，求一阶、二阶导数在数学上很 trivial（琐碎）：一阶导数就是相邻两次读数之差。跟踪情形下，相邻位置之差显然是速度。

此外可考虑如何组合两个或多个传感器的数据以得到更多信息。这打开**传感器融合（sensor fusion）**领域，后面章节会有例子。目前只需认识到：选择合适的状态变量对滤波器性能至关重要。选定隐变量后，必须大量测试，确保能为它们产生有效信息。卡尔曼滤波只运行你给的模型；若模型无法为隐变量产生好信息，输出将 nonsense。

""",

14: """### 设计状态转移函数（Design State Transition Function）

下一步是设计状态转移函数（state transition function）。回忆：状态转移函数实现为矩阵 $\\mathbf F$，与系统前一状态相乘得到下一状态：

$$\\mathbf{\\bar x} = \\mathbf{Fx}$$

不再赘述，与上一章一维情形非常相似。状态转移方程为

$$
\\begin{aligned}
x &= 1x + \\Delta t \\dot x + 0y + 0 \\dot y \\\\
v_x &= 0x + 1\\dot x + 0y + 0 \\dot y \\\\
y &= 0x + 0\\dot x + 1y + \\Delta t \\dot y \\\\
v_y &= 0x + 0\\dot x + 0y + 1 \\dot y
\\end{aligned}
$$

这样排列既显示数值也显示 $\\small\\mathbf F$ 的行列组织。转为矩阵-向量形式：

$$
\\begin{bmatrix}x \\\\ \\dot x \\\\ y \\\\ \\dot y\\end{bmatrix} = \\begin{bmatrix}1& \\Delta t& 0& 0\\\\0& 1& 0& 0\\\\0& 0& 1& \\Delta t\\\\ 0& 0& 0& 1\\end{bmatrix}\\begin{bmatrix}x \\\\ \\dot x \\\\ y \\\\ \\dot y\\end{bmatrix}$$

下面用 Python 实现。非常简单；此处新之处仅是将 `dim_z` 设为 2。第 4 步会说明原因。

""",

16: """### 设计过程噪声矩阵（Design the Process Noise Matrix）

FilterPy 可为我们计算 $\\mathbf Q$ 矩阵。为简单起见，假设噪声为离散时间维纳过程——每个时间段内恒定。此假设允许用方差指定模型在步与步之间变化多少。若不清楚，请回顾卡尔曼滤波数学（Kalman Filter Math）一章。

""",

18: "这里假设 x 与 y 的噪声独立，故任意 x 与 y 变量之间的协方差应为零。这样可先计算一维的 $\\mathbf Q$，再用 `block_diag` 复制到 x、y 轴。\n",

19: """### 设计控制函数（Design the Control Function）

我们尚未给机器人加控制，此步无事可做。`KalmanFilter` 类将 `B` 初始化为零，假设无控制输入，因此无需写代码。若愿意，可显式设 `tracker.B` 为 0，但可见它已是该值。

""",

21: """### 设计测量函数（Design the Measurement Function）

测量函数 $\\mathbf H$ 定义如何从状态变量得到测量：$\\mathbf z = \\mathbf{Hx}$。本例有 (x,y) 测量，故设计 $\\mathbf z$ 为 $\\begin{bmatrix}x & y\\end{bmatrix}^\\mathsf T$，维数 2×1。状态变量 4×1。回忆 M×N 矩阵乘 N×P 得 M×P，可推 $\\textbf{H}$ 所需尺寸：

$$(2\\times 1) = (a\\times b)(4 \\times 1) = (2\\times 4)(4\\times 1)$$

故 $\\textbf{H}$ 为 2×4。

填 $\\textbf{H}$ 的值很容易：测量是机器人位置，即状态 $\\textbf{x}$ 的 $x$、$y$。为稍增趣味，决定改变单位：测量以英尺返回，而我们希望用米。$\\textbf{H}$ 从状态到测量，换算为 $\\mathsf{feet} = \\mathsf{meters} / 0.3048$。得到

$$\\mathbf H =
\\begin{bmatrix} 
\\frac{1}{0.3048} & 0 & 0 & 0 \\\\
0 & 0 & \\frac{1}{0.3048} & 0
\\end{bmatrix}
$$

对应线性方程

$$
\\begin{aligned}
z_x &= (\\frac{x}{0.3048}) + (0* v_x) + (0*y) + (0 * v_y) = \\frac{x}{0.3048}\\\\
z_y &= (0*x) + (0* v_x) + (\\frac{y}{0.3048}) + (0 * v_y) = \\frac{y}{0.3048}
\\end{aligned}
$$

问题简单，本可直接写方程而不做上述量纲分析。但记住：卡尔曼滤波方程隐含所有矩阵的特定维数；设计迷失时，查看矩阵维数很有用。

下面是我的实现：

""",

23: """### 设计测量噪声矩阵（Design the Measurement Noise Matrix）

假设 $x$、$y$ 为独立**白噪声（white noise）**高斯（Gaussian）过程：x 的噪声与 y 的噪声无关，噪声正态分布、均值为 0。暂设 $x$、$y$ 方差均为 5 米$^2$。独立故无协方差，非对角为 0：

$$\\mathbf R = \\begin{bmatrix}\\sigma_x^2 & \\sigma_y\\sigma_x \\\\ \\sigma_x\\sigma_y & \\sigma_{y}^2\\end{bmatrix} 
= \\begin{bmatrix}5&0\\\\0&5\\end{bmatrix}$$

因有两个传感器输入，为 2×2；协方差矩阵对 $n$ 个变量恒为 $n{\\times}n$。Python 写法：

""",

25: "### 初始条件（Initial Conditions）\n",

26: """对本简单问题，设初始位置 (0,0)、速度 (0,0)。因纯属猜测，将协方差矩阵 $\\small\\mathbf P$ 设为大值。

$$ \\mathbf x = \\begin{bmatrix}0\\\\0\\\\0\\\\0\\end{bmatrix}, \\,
\\mathbf P = \\begin{bmatrix}500&0&0&0\\\\0&500&0&0\\\\0&0&500&0\\\\0&0&0&500\\end{bmatrix}$$

Python 实现：

""",

28: "### 实现滤波器（Implement the Filter）\n",

29: "设计完成，只需编写运行滤波器并按所需格式输出数据的代码。我们将运行 30 次迭代。\n",

31: """鼓励你调整 $\\mathbf Q$、$\\mathbf R$ 试玩。不过前几章已做过不少类似实验，且本章内容很多，我将转向更复杂情形，那里也会有机会调整这些值。

我用绿色绘制了 $x$、$y$ 的 $3\\sigma$ 协方差椭圆。能解释其形状吗？也许你期待倾斜椭圆，如前几章。若如此，回忆前几章绘的是 $x$ 对 $\\dot x$，而非 $x$ 对 $y$。$x$ 与 $\\dot x$ 相关，但 $x$ 与 $y$ 无关。故椭圆不倾斜。此外，$x$、$y$ 噪声建模为相同标准差。若设 R 为

$$\\mathbf R = \\begin{bmatrix}1&0\\\\0&.5\\end{bmatrix}$$

即告诉滤波器 x 比 y 噪声更大，椭圆将长于宽。

$\\mathbf P$ 的最终值包含状态变量间相关的一切信息。看对角线可得各变量方差：$\\mathbf P_{0,0}$ 为 x 方差，$\\mathbf P_{1,1}$ 为 $\\dot x$，$\\mathbf P_{2,2}$ 为 y，$\\mathbf P_{3,3}$ 为 $\\dot y$。可用 `numpy.diag()` 提取对角线。

""",

33: "协方差矩阵含四个可轻易辨认的 2×2 子块，源于 $x$ 与 $\\dot x$、$y$ 与 $\\dot y$ 的相关。左上为 $x$ 与 $\\dot x$ 的协方差。\n",

35: """协方差左上含 $x$、$\\dot x$ 的数据，由排列方式决定。回忆 $\\mathbf P_{i,j}$、$\\mathbf P_{j,i}$ 含 $\\sigma_i\\sigma_j$。

最后看 $\\mathbf P$ 左下全为 0。为何？考虑 $\\mathbf P_{3,0}$，存 $\\sigma_3\\sigma_0$，即 $\\dot y$ 与 $x$ 的协方差。二者独立，项为 0。其余项对应 similarly 独立的变量。

""",

37: "## 滤波器阶数（Filter Order）\n",

38: """我们迄今只研究跟踪位置与速度，效果良好，但仅因我挑选了适合该假设的问题。你现在已有足够经验，可从更一般角度考虑。

**阶数（order）**在此指准确建模系统所需的导数个数。不变系统（如建筑物高度）无变化，无需导数，阶为零，可写 $x = 312.5$。

一阶系统有一阶导数。位置变化率为速度：

$$ v = \\frac{dx}{dt}$$

积分为牛顿方程

$$ x = vt + x_0.$$

亦称**恒速（constant velocity）**模型。

二阶系统有二阶导数。位置二阶导数为加速度：

$$a = \\frac{d^2x}{dt^2}$$

积分为

$$ x = \\frac{1}{2}at^2 +v_0t + x_0.$$

亦称**恒加速度（constant acceleration）**模型。

""",

39: """等价看法：多项式的阶数。恒加速度模型有二阶导数，故为二阶；$x = \\frac{1}{2}at^2 +v_0t + x_0$ 也是二阶多项式。

设计状态变量与过程模型时，必须选择要建模的系统阶数。若跟踪恒速物体，真实过程 imperfect，短时间速度会有小幅变化。你可能认为最好用二阶滤波，让加速度项处理速度小幅变化。

实践中往往不好。为深入理解，我们看过程模型阶数与待滤波系统不匹配时的效果。

""",

40: "首先需要一个待滤波系统。我写一个类仿真恒速物体。几乎没有物理系统真正恒速，故每次更新将速度略改。再写传感器仿真高斯（Gaussian）噪声。代码如下，并绘图验证。\n",

42: """我对该图满意。轨迹因加入的系统噪声而不完全笔直——可能是行人沿街行走，或飞机受变风扰动。无 刻意加速度，故称恒速系统。你或许会问：既然确有微小加速度，为何不用二阶卡尔曼滤波？我们来验证。

如何设计零阶、一阶、二阶卡尔曼滤波？我们一直在做，只是没用这些术语。若概念已清楚可略读；否则我会充分展开每一类。

""",

43: "### 零阶卡尔曼滤波（Zero Order Kalman Filter）\n",

44: """零阶卡尔曼滤波即无导数的跟踪滤波。只跟踪位置，状态变量只有位置（无速度、加速度），状态转移函数也只考虑位置。矩阵形式下状态为

$$\\mathbf x = \\begin{bmatrix}x\\end{bmatrix}$$

状态转移很简单：位置不变，即 $x=x$；时刻 t+1 的 *x* 与 t 相同。矩阵形式：

$$\\mathbf F = \\begin{bmatrix}1\\end{bmatrix}$$

测量函数很简单：定义状态 $\\mathbf x$ 如何变为测量。假设测量为位置，状态只有位置，故

$$\\mathbf H = \\begin{bmatrix}1\\end{bmatrix}$$

下面写函数构造并返回零阶卡尔曼滤波。

""",

46: "### 一阶卡尔曼滤波（First Order Kalman Filter）\n",

47: """一阶卡尔曼滤波跟踪一阶系统，如位置与速度。上面狗跟踪问题已做过，应很清楚。再做一次。

一阶系统有位置与速度，状态需包含二者：

$$ \\mathbf x = \\begin{bmatrix}x\\\\\\dot x\\end{bmatrix}$$

设计状态转移。一个时间步的牛顿方程：

$$\\begin{aligned} x_t &= x_{t-1} + v\\Delta t \\\\
 v_t &= v_{t-1}\\end{aligned}$$
 
需转为线性方程

$$\\begin{bmatrix}x\\\\\\dot x\\end{bmatrix} = \\mathbf F\\begin{bmatrix}x\\\\\\dot x\\end{bmatrix}$$

设

$$\\mathbf F = \\begin{bmatrix}1 &\\Delta t\\\\ 0 & 1\\end{bmatrix}$$

即得上式。

最后设计测量函数，实现

$$\\mathbf z = \\mathbf{Hx}$$

传感器仍只读位置，应从状态取位置，速度、加速度置零：

$$\\mathbf H = \\begin{bmatrix}1 & 0 \\end{bmatrix}$$

下面函数构造并返回一阶卡尔曼滤波。

""",

49: "### 二阶卡尔曼滤波（Second Order Kalman Filter）\n",

50: """二阶卡尔曼滤波跟踪二阶系统，如位置、速度与加速度。状态为

$$ \\mathbf x = \\begin{bmatrix}x\\\\\\dot x\\\\\\ddot{x}\\end{bmatrix}$$

设计状态转移。一个时间步的牛顿方程：

$$\\begin{aligned} x_t &= x_{t-1} + v_{t-1}\\Delta t + 0.5a_{t-1} \\Delta t^2 \\\\
 v_t &= v_{t-1} + a_{t-1}\\Delta t \\\\
 a_t &= a_{t-1}\\end{aligned}$$
 
转为

$$\\begin{bmatrix}x\\\\\\dot x\\\\\\ddot{x}\\end{bmatrix} = \\mathbf F\\begin{bmatrix}x\\\\\\dot x\\\\\\ddot{x}\\end{bmatrix}$$

设

$$\\mathbf F = \\begin{bmatrix}1 & \\Delta t &.5\\Delta t^2\\\\ 
0 & 1 & \\Delta t \\\\
0 & 0 & 1\\end{bmatrix}$$

即得上式。

测量函数实现 $z = \\mathbf{Hx}$。传感器仍只读位置：

$$\\mathbf H = \\begin{bmatrix}1 & 0 & 0\\end{bmatrix}$$

下面函数构造并返回二阶卡尔曼滤波。

""",

52: """## 评估滤波器阶数（Evaluating Filter Order）

现在可对仿真运行各阶卡尔曼滤波并评估结果。

如何评估？可定性绘图、肉眼比较；严格方法用数学。回忆系统协方差矩阵 $\\mathbf P$ 含各状态变量的方差与协方差，对角线为方差。高斯（Gaussian）噪声下约 99% 测量落在 $3\\sigma$ 内。若不清楚请回顾高斯一章——这很重要。

因此可比较估计状态与真实状态的**残差（residual）**与由 $\\mathbf P$ 导出的标准差。滤波正确时约 99% 残差落在 $3\\sigma$ 内。这对所有状态变量成立，不仅是位置。

需说明：这只对仿真系统严格成立。真实传感器并非完美高斯，对真实数据可能需放宽到如 $5\\sigma$。

下面用一阶卡尔曼滤波跑一阶系统，用标准差看性能。你大概猜它会表现好，但我们仍要看。

首先写 routine 生成带噪测量。

""",

54: "再写 routine 执行滤波并将输出存入 `Saver` 对象。\n",

56: "现在可以运行滤波并查看结果。\n",

58: "滤波似乎表现良好，但难以精确判断。看残差是否有帮助。我们会经常做，故写函数绘图。\n",

61: """如何解读此图？锯齿线为**残差（residual）**——测量与预测位置之差。若无测量噪声且卡尔曼预测永远完美，残差恒为零；理想输出为 0 的水平线。可见残差围绕 0，说明噪声似为高斯（误差上下相当）。虚线间黄色区域为 1 标准差的理论性能，约 68% 误差应落在虚线内。残差在此范围内，滤波表现良好且未发散。

再看速度残差。

""",

63: "如预期，残差落在滤波理论性能内，可认为滤波对该系统设计良好。\n\n现在用零阶卡尔曼滤波做同样的事。代码与数学大体相同，只看结果，不多谈实现。\n",

65: """如预期，滤波有问题。回想 g-h 滤波（g-h filter）中纳入加速度的情形：g-h 滤波总滞后于输入，因项数不足以快速适应速度变化。每次 `predict()` 卡尔曼滤波假设位置不变——若当前位置 4.3，则预测下一时刻仍为 4.3。实际位置更接近 5.3。带噪测量可能是 5.4，滤波在 4.3 与 5.4 之间选估计，显著滞后于真实 5.3。下一步、再下一步亦然，滤波永远追不上。

这提出重要观点：「恒定」假设仅指离散样本之间恒定。滤波输出仍可随时间变化。

看残差。我们不跟踪速度，只能看位置残差。

""",

67: """可见滤波几乎立即发散。数秒后残差超过三倍标准差界。重要：协方差矩阵 $\\mathbf P$ 只报告在输入全正确假设下滤波器的*理论*性能。此卡尔曼滤波在发散，但 $\\mathbf P$ 暗示估计随时间越来越好（方差变小）。滤波器无法知道你向它谎报系统。有时称为*过度自信（smug）*滤波器。

本系统中发散立即且明显。许多系统中仅 gradual 或轻微。务必为系统查看此类图，确保性能在理论界内。

现在试二阶系统。你也许认为合理：运动有噪声 implying 有加速度，为何不用二阶模型？若无加速度，加速度应估计为 0 吧？实际如何？继续前先想想。

""",

69: """符合预期吗？

可见二阶滤波比一阶差。为何？该滤波建模加速度，大的测量变化被解释为加速度而非噪声，滤波紧密跟踪噪声。不仅如此，若噪声 consistently 在轨迹上方或下方，还会*超调（overshoot）*——滤波错误假设不存在的加速度，预测每步离轨迹更远。情况不妙。

轨迹看起来不算* 糟糕*。看残差。此处加 twist：二阶残差未发散或超三倍标准差，但对比一阶与二阶残差很有说明性，故同图画出。

""",

71: "二阶位置残差略差于一阶，但仍落在理论界内，无特别  alarming。\n\n再看速度残差。\n",

73: "故事很不同。二阶残差虽在理论界内，但远差于一阶。通常如此：滤波假设存在不存在的加速度，将测量噪声误当加速度，每步 predict 加入速度估计。加速度实际不存在，速度残差远大于最优。\n",

74: "还有一个 trick。我们有一阶系统，速度 大致 恒定。真实系统 never perfect，速度在时间段之间总有小幅变化。用一阶滤波时，用**过程噪声（process noise）**矩阵 $\\mathbf Q$  补偿这种变化。若改用二阶滤波，我们 补偿速度变化。或许过程噪声可为零，$\\mathbf Q$ 设 0！\n",

76: "肉眼看来滤波很快收敛到真实轨迹。成功！\n\n或许不是。过程噪声为 0 告诉滤波过程模型完美。看更长时间段的性能。\n",

78: """可见性能极差。轨迹图显示滤波长时间偏离；残差图更明显。约第 100 次更新前滤波 sharply 偏离理论性能。末尾*可能*在收敛，我怀疑不会。全程滤波报告越来越小方差。**不要信任滤波协方差矩阵来判断滤波是否表现良好**！

为何？过程噪声为 0 意味着只用过程模型，测量被忽略。物理系统*不*完美，滤波无法适应 imperfect 行为。

也许很小的过程噪声？试试。

""",

80: """残差图再次说明问题。轨迹看起来很好，但残差显示滤波长时间发散。

如何理解？你也许认为最后一图对你的应用「够好」，也许确实。但发散的滤波并不总会收敛。换数据集或表现不同的物理系统，滤波可能越来越远离测量。

从数据拟合角度想：给两点，拟合直线。

""",

82: """直线是唯一可能答案，且最优。给更多点可用**最小二乘（least squares）**拟合最佳直线，仍是最优（最小二乘意义）。

但若要求用更高阶多项式拟合两点？有无穷多解。例如无穷多条二阶抛物线过两点。当卡尔曼滤波阶数高于物理过程时，也有无穷多解可选。答案不仅非最优，还常发散且无法恢复。

最佳性能需滤波阶数与系统阶数匹配。许多情况容易——为冷冻室温度计设计滤波，零阶显然合适。跟踪汽车呢？恒速直线时一阶很好，但汽车转弯、加减速，二阶更好。这是自适应滤波（Adaptive Filtering）一章的问题。那里学习设计随被跟踪对象行为阶数变化的滤波器。

话虽如此，**较低阶滤波器可跟踪较高阶过程**，只要加足够过程噪声且离散化周期小（如每秒 100 样本通常 locally 线性）。结果非最优，但可很好；我通常先试此工具再考虑自适应滤波。看有加速度的例子。先仿真。

""",

84: "现在用二阶滤波滤波数据。\n",

86: """可见滤波在理论界内。

再用较低阶滤波。已演示较低阶会滞后，因未建模加速度。但可通过增大过程噪声（to an extent）account——滤波将加速度当过程模型中的噪声。结果 次优，但设计得当可不发散。过程噪声加多少非精确科学，需用代表数据实验。这里我乘以 10，得到好结果。

""",

88: "想想过程噪声远大于所需会怎样。大过程噪声告诉滤波更信测量，滤波将 closely  mimic 测量噪声。验证一下。\n",

90: """## 练习：状态变量设计（Exercise: State Variable Design）

如前所述，$\\mathbf x$ 中变量顺序可任意。例如一维恒加速度可定义为 $\\mathbf x = \\begin{bmatrix}\\ddot x & x & \\dot x\\end{bmatrix}^\\mathsf T$。难以想象为何如此，但可能。

做更合理的：为二维运动机器人设计二阶滤波，$\\mathbf x = \\begin{bmatrix}x & y & \\dot x & \\dot y \\end{bmatrix}^\\mathsf T$。本章一直用 $\\mathbf x = \\begin{bmatrix}x & \\dot x & y & \\dot y \\end{bmatrix}^\\mathsf T$。

为何选不同顺序？马上会看到，改 $\\mathbf x$ 顺序会改滤波器多数矩阵顺序。视你想查看的数据（如 $\\mathbf P$ 中的相关），不同顺序使查看更易或更难。

思考如何改。显然只需改卡尔曼矩阵反映新设计。

用下面模板试：

```python

N = 30 # number of iterations
dt = 1.0 # time step
R_std = 0.35
Q_std = 0.04

sensor = PosSensor((0, 0), (2, .5), noise_std=R_std)
zs = np.array([sensor.read() for _ in range(N)])

tracker = KalmanFilter(dim_x=4, dim_z=2)
# assign state variables here

xs, ys = [], []
for z in zs:
    tracker.predict()
    tracker.update(z)
    xs.append(tracker.x[0])
    ys.append(tracker.x[1])
plt.plot(xs, ys);
```

""",

91: "### 解答（Solution）\n",

92: """从 $\\mathbf F$ 开始。练熟后应能直接写出。若困难，按状态变量顺序写出 $\\mathbf F$ 方程组。

$$
x = 1x + 0y + 1\\dot x\\Delta t + 0 \\dot y\\Delta t \\\\
y = 0x + 1y + 0\\dot x\\Delta t + 1 \\dot y\\Delta t \\\\
\\dot x = 0x + 0y + 1\\dot x\\Delta t + 0 \\dot y\\Delta t \\\\
\\dot y = 0x + 0y + 0\\dot x\\Delta t + 1 \\dot y\\Delta t 
$$

抄系数得

$$\\mathbf F = \\begin{bmatrix}1&0&\\Delta t & 0\\\\0&1&0&\\Delta t\\\\0&0&1&0\\\\0&0&0&1\\end{bmatrix}$$

状态噪声也需重排。先想在新顺序下如何排列。可把状态变量竖横写在矩阵上看配对；notebook 里难做，此处略。

$$\\mathbf Q = 
\\begin{bmatrix}
\\sigma_x^2 & \\sigma_{xy} & \\sigma_{x\\dot x} & \\sigma_{x\\dot y} \\\\
\\sigma_{yx} & \\sigma_y^2 & \\sigma_{y\\dot x} & \\sigma_{y\\dot y} \\\\
\\sigma_{\\dot x x} & \\sigma_{\\dot x y} & \\sigma_{\\dot x}^2 & \\sigma_{\\dot x \\dot y} \\\\
\\sigma_{\\dot y x} & \\sigma_{\\dot y y} & \\sigma_{\\dot y \\dot x} & \\sigma_{\\dot y}^2
\\end{bmatrix}
$$

$x$ 与 $y$ 无相关，含二者的项置零：

$$\\mathbf Q = 
\\begin{bmatrix}
\\sigma_x^2 & 0 & \\sigma_{x\\dot x} & 0 \\\\
0 & \\sigma_y^2 & 0 & \\sigma_{y\\dot y} \\\\
\\sigma_{\\dot x x} & 0 & \\sigma_{\\dot x}^2 & 0 \\\\
0 & \\sigma_{\\dot y y} & 0 & \\sigma_{\\dot y}^2
\\end{bmatrix}
$$

看出模式后可更快设计 $\\mathbf Q$。

`Q_discrete_white_noise` 生成不同顺序的矩阵，我们可从中抄项，代码中会看到。

设计 $\\mathbf H$：将状态 $\\begin{bmatrix}x & y & \\dot x & \\dot y \\end{bmatrix}^\\mathsf T$ 转为测量 $\\mathbf z = \\begin{bmatrix}z_x & z_y\\end{bmatrix}^\\mathsf T$。

$$
\\begin{aligned}
\\mathbf{Hx} &= \\mathbf z \\\\
\\begin{bmatrix}?&?&?&?\\\\?&?&?&?\\end{bmatrix}\\begin{bmatrix}x \\\\ y \\\\ \\dot x \\\\ \\dot y \\end{bmatrix} &= \\begin{bmatrix}z_x \\\\ z_y\\end{bmatrix}
\\end{aligned}
$$

填矩阵：

$$
\\begin{bmatrix}1&0&0&0\\\\0&1&0&0\\end{bmatrix}\\begin{bmatrix}x \\\\ y \\\\ \\dot x \\\\ \\dot y \\end{bmatrix} = \\begin{bmatrix}z_x \\\\ z_y\\end{bmatrix}
$$

测量 $\\mathbf z = \\begin{bmatrix}z_x & z_y\\end{bmatrix}^\\mathsf T$ 未变，$\\mathbf R$ 不变。

最后 $\\mathbf P$，与 $\\mathbf Q$ 同顺序，已为我们设计好。

""",

94: """## 检测与拒绝坏测量（Detecting and Rejecting Bad Measurement）

卡尔曼滤波无法检测并拒绝坏测量。假设跟踪飞机，收到距当前位置 100 km 的测量。若用该值 update，新估计会大幅偏向测量。

运行仿真给出具体例子。100 个 epoch 后做一次测量为当前位置两倍的 update。`filterpy.common` 提供 `kinematic_kf`，可创建任意维数与阶数的线性运动学滤波。此处为简洁使用，本书其余部分不用，因希望你有大量编写滤波器的练习。

""",
}
