# -*- coding: utf-8 -*-
"""06-Multivariate-Kalman-Filters.ipynb markdown 译文 (part 2)"""

TRANSLATIONS_06_PART2 = {
72: """这是滤波器的完整代码，大部分是样板。我使其足够灵活以支持本章多种用途，故略冗长。逐行看。

开头检查是否在 `zs` 中提供了测量数据。若没有，用前面写的 `compute_dog_data` 生成。

接下来用辅助函数创建卡尔曼滤波。

```python
# create the Kalman filter
 kf = pos_vel_filter(x0, R=R, P=P, Q=Q, dt=dt)
```

对每个测量只需执行卡尔曼滤波的更新与预测步。`KalmanFilter` 类提供 `update()` 与 `predict()`。`update()` 执行测量更新步，接受传感器测量。

若不保存结果，循环为：

```python
    for z in zs:
        kf.predict()
        kf.update(z)
```

每次 `predict` 与 `update` 修改状态变量 `x` 与 `P`。故 `predict` 后 `kf.x` 含先验；`update` 后含后验。状态与协方差保存在 `xs` 与 `cov`。

不能再简单了。更复杂的问题代码大体相同；工作主要在设置 `KalmanFilter` 矩阵；执行滤波本身很平凡。

其余代码可选绘图，然后返回保存的状态与协方差。

运行。50 个测量，噪声方差 10，过程方差 0.01。

""",

74: """要学的东西还很多，但我们已用 Rudolf Kalman 发表的同一理论与方程实现了卡尔曼滤波！非常类似的代码运行在你的 GPS、客机、机器人等内部。

第一幅图把卡尔曼滤波输出与测量及狗的实际位置（标为 *Track*）对比。初始稳定期后滤波器应紧密跟踪狗的位置。黑虚线间黄色阴影为滤波器方差的一个标准差，下段解释。

后两幅图显示 $x$ 与 $\\dot x$ 的方差。我画了 $\\mathbf P$ 对角元随时间变化。回忆协方差矩阵对角含各状态变量方差。故 $\\mathbf P[0,0]$ 是 $x$ 的方差，$\\mathbf P[1,1]$ 是 $\\dot x$ 的方差。可见两者很快收敛到小方差。

协方差矩阵 $\\mathbf P$ 告诉我们滤波器的 *理论* 性能，*假设* 我们告诉它的全部为真。回忆标准差是方差的平方根，约 68% 的高斯分布落在一个标准差内。若至少 68% 的滤波输出在一个标准差内，滤波器可能表现良好。上图我把一个标准差显示为两虚线间黄色区域。在我看来滤波器可能略超该界，或许需要调参。

一维章我们用比上面简单得多的代码滤除很噪的信号。但 realize 我们现在是很简单的例子——物体在一维空间运动、一个传感器。那大约是一维章代码的极限。相比之下，只改滤波器变量赋值，就能用本章代码实现很复杂的多维滤波。也许要在金融模型中跟踪 100 维。或有飞机带 GPS、INS、TACAN、雷达高度计、气压高度计与空速指示器，要把这些传感器融入预测三维空间位置、速度与加速度的模型。本章代码可以做到。

希望你更好感受高斯如何随时间变化，下面是每 7 个 epoch（时间步）画一次高斯的 3D 图。每 7 个分开足够看清各自。$t=0$ 的第一个高斯在左侧。

""",

76: """## Saver 类（The Saver Class）

`run()` 方法里我写了保存滤波结果的样板代码
```python
    xs, cov = [], []
    for z in zs:
        kf.predict()
        kf.update(z)
        xs.append(kf.x)
        cov.append(kf.P)

    xs, cov = np.array(xs), np.array(cov)
```

有简单办法避免。`filterpy.common` 提供 `Saver` 类，每次调用 `Saver.save()` 会保存 KalmanFilter 类的所有属性。看用法，再详谈。

""",

78: "`Saver` 对象现在含 KalmanFilter 所有属性的列表。`kf.x` 是滤波器当前状态估计，故 `s.x` 含循环内计算并保存的状态估计：\n",

80: "可用 `keys` 属性查看所有可用属性：\n",

82: """那里有许多尚未讨论的属性，但许多应熟悉。

此时你可写代码绘制任一变量。不过常更有用的是用 `np.array` 代替列表。调用 `Saver.to_array()` 会把列表转成 `np.array`。注意：若运行中某属性形状变化，`to_array` 会抛异常，因为 `np.array` 要求元素类型与大小相同。

再看 keys，`z` 是选项之一。有希望；测量 `z` 已为我们保存。把它与估计对比绘图。

""",

84: "虽用 `KalmanFilter` 演示，但对 FilterPy 实现的所有滤波类都有效。对你写的类可能也有效，因为它检查对象以取属性名。全书用该类保持代码可读简短。用 `Saver` 会减慢代码（背后很多事），但学习与探索时便利无可替代。\n",

85: """## 卡尔曼滤波方程（The Kalman Filter Equations）

现在学习 `predict()` 与 `update()` 如何计算。

关于记法。我是程序员，习惯读

```python
x = x + 1
``` 

两边不等，不是方程而是 *赋值（assignment）*。数学记法写作
$$x_k = x_{k-1} + 1$$

卡尔曼滤波方程布满上下标以保持数学一致。我觉得很难读。全书大多选用无下标赋值。作为程序员，你应理解我展示的是逐步实现算法的赋值。有具体例子后再展开。

""",

86: """### 预测方程（Prediction Equations）

卡尔曼滤波用这些方程计算 *先验（prior）*——系统预测的下一状态。计算先验均值 ($\\bar{\\mathbf x}$) 与协方差 ($\\bar{\\mathbf P}$)。

$$\\begin{aligned}
\\mathbf{\\bar x} &= \\mathbf{Fx} + \\mathbf{Bu}\\\\
\\mathbf{\\bar P} &= \\mathbf{FPF}^\\mathsf T + \\mathbf Q
\\end{aligned}$$

$\\underline{\\textbf{均值（Mean）}}$

$\\mathbf{\\bar x} = \\mathbf{Fx} + \\mathbf{Bu}$

提醒，线性方程 $\\mathbf{Ax} = \\mathbf b$ 表示方程组，$\\mathbf A$ 含系数，$\\mathbf x$ 是变量向量。做乘法 $\\mathbf{Ax}$ 计算方程组右端 $\\mathbf b$ 的值。

若 $\\mathbf F$ 含给定时间步的状态转移，积 $\\mathbf{Fx}$ 计算该转移后的状态。简单！同样 $\\mathbf B$ 是控制函数，$\\mathbf u$ 是控制输入，$\\mathbf{Bu}$ 计算控制对转移后状态的贡献。故先验 $\\mathbf{\\bar x}$ 为 $\\mathbf{Fx}$ 与 $\\mathbf{Bu}$ 之和。

等价一维方程为

$$\\bar\\mu = \\mu + \\mu_{move}$$

做矩阵乘法 $\\mathbf{Fx}$ 会为 $x$ 生成该方程。

显式说明。回忆上一章 $\\mathbf F$ 的值：

$$\\mathbf F = \\begin{bmatrix}1&\\Delta t  \\\\ 0&1\\end{bmatrix}$$

故 $\\mathbf{\\bar x} = \\mathbf{Fx}$ 对应线性方程组：

$$\\begin{cases}
\\begin{aligned}
\\bar x &= 1x + &\\Delta t\\, \\dot x \\\\
\\bar{\\dot x} &=0x + &1\\, \\dot x
\\end{aligned}
\\end{cases}$$

""",

87: """$\\underline{\\textbf{协方差（Covariance）}}$

$\\mathbf{\\bar P} = \\mathbf{FPF}^\\mathsf T + \\mathbf Q$

该方程不如均值直观，多花时间。

一维版本为：

$$\\bar\\sigma^2 = \\sigma^2 + \\sigma^2_{move}$$

把运动的方差加到估计方差以反映知识损失。多元高斯也要做类似事，但不那么简单。

不能简单写 $\\mathbf{\\bar P} = \\mathbf P + \\mathbf Q$。多元高斯中状态变量 *相关（correlated）*。含义？速度估计不完美，但用

$$\\bar x = \\dot x\\Delta t + x$$

把速度加到位置。因 $\\dot x$ 值不完美，和 $\\bar x = \\dot x\\Delta t + x$ 增加不确定性。位置与速度相关，不能简单加协方差矩阵。例如 $\\mathbf P$ 与 $\\mathbf Q$ 都是对角矩阵，和也是对角。但我们知位置与速度相关，非对角元应非零。

正确方程为

$$\\mathbf{\\bar P} = \\mathbf{FPF}^\\mathsf T + \\mathbf Q$$

$\\mathbf{ABA}^\\mathsf T$ 形式在线性代数中常见。可视为用外项 *投影* 中间项。全书会多次使用。我承认这对你可能像“魔法”方程。探索一下。

用下式初始化 $\\mathbf P$ 时

$$\\mathbf P = \\begin{bmatrix}\\sigma^2_x & 0 \\\\ 0 & \\sigma^2_v\\end{bmatrix}$$


$\\mathbf{FPF}^\\mathsf T$ 的值为：

$$\\begin{aligned}
\\mathbf{FPF}^\\mathsf T &= \\begin{bmatrix}1&\\Delta t\\\\0&1\\end{bmatrix}
\\begin{bmatrix}\\sigma^2_x & 0 \\\\  0 & \\sigma^2_{v}\\end{bmatrix}
\\begin{bmatrix}1&0\\\\\\Delta t&1\\end{bmatrix} \\\\
&= \\begin{bmatrix}\\sigma^2_x&\\sigma_v^2\\Delta t\\\\  0 & \\sigma^2_{v}\\end{bmatrix}
\\begin{bmatrix}1&0\\\\\\Delta t&1\\end{bmatrix} \\\\
&= \\begin{bmatrix}\\sigma^2_x +  \\sigma_v^2\\Delta t^2  &  \\sigma_v^2\\Delta t \\\\
\\sigma_v^2\\Delta t & \\sigma^2_{v}\\end{bmatrix}
\\end{aligned}$$

$\\mathbf P$ 初值无位置与速度协方差。位置由 $\\dot x\\Delta t + x$ 计算，故位置与速度相关。乘法 $\\mathbf{FPF}^\\mathsf T$ 计算协方差 $\\sigma_v^2 \\Delta t$。精确值不重要；应认出 $\\mathbf{FPF}^\\mathsf T$ 用过程模型自动计算位置与速度的协方差！

另一角度想 $\\mathbf{Fx}$ 乘法：把 $\\mathbf x$ 向前投影。$\\mathbf {FP}$ 似等价操作，但 $\\mathbf P$ 是矩阵而 $\\mathbf x$ 是向量。尾随 $\\mathbf F^\\mathsf T$ 项确保同时乘 $\\mathbf F$ 的行与列。$\\mathbf{FPF}^\\mathsf T$ 计算第二行是 $\\mathbf{FP}$ 的值。可见是上三角矩阵，因尚未完全纳入 $\\mathbf F$。

若有线性代数与统计经验，可能有帮助。预测引起的协方差可建模为预测步误差的期望，由下式给出。

$$\\begin{aligned}
\\bar{\\mathbf P} &= \\mathbb E[(\\mathbf{Fx - F\\bar \\mu})(\\mathbf{Fx - F\\bar\\mu})^\\mathsf T]\\\\
 &= \\mathbf F\\, \\mathbb E[\\mathbf{(x- \\bar\\mu)(x- \\bar\\mu)}^\\mathsf T]\\, \\mathbf F^\\mathsf T
\\end{aligned}$$

当然 $\\mathbb E[\\mathbf{(x- \\bar\\mu)(x- \\bar\\mu)}^\\mathsf T]$ 就是 $\\mathbf P$，得

$$\\bar{\\mathbf P} = \\mathbf{FPF}^\\mathsf T$$

看其效应。用滤波器的 $\\mathbf F$，把状态向前投影 6/10 秒。做五次以便看到 $\\mathbf{\\bar P}$ 如何持续变化。

""",

89: """可见速度 5 时，每 6/10 秒位置正确移动 3 单位。每步椭圆变宽，表示因每步加 $\\dot x\\Delta t$ 到 x 而损失位置信息。高度未变——模型说速度不变，对速度的信念不能变。随时间椭圆越来越倾斜。倾斜表示 *相关性（correlation）*。$\\mathbf F$ 用 $\\bar x = \\dot x \\Delta t + x$ 线性关联 $x$ 与 $\\dot x$。$\\mathbf{FPF}^\\mathsf T$ 正确把该相关性纳入协方差矩阵。

这是可改变 $\\mathbf F$ 设计、观察对 $\\mathbf P$ 形状影响的动画。`F00` 滑块影响 F[0,0]。`covar` 设位置与速度初协方差 ($\\sigma_x\\sigma_{\\dot x}$)。建议至少回答：

* 若 $x$ 与 $\\dot x$ 不相关？（F01 设 0，其余默认）
* 若 $x = 2\\dot x\\Delta t + x_0$？（F01 设 2，其余默认）
* 若 $x = \\dot x\\Delta t + 2x_0$？（F00 设 2，其余默认）
* 若 $x = \\dot x\\Delta t$？（F00 设 0，其余默认）

""",

91: """（若以静态形式阅读：在线运行说明见 https://git.io/vza7b。或点下方链接用 binder 打开本 notebook。）

http://mybinder.org/repo/rlabbe/Kalman-and-Bayesian-Filters-in-Python

""",

92: """### 更新方程（Update Equations）

更新方程比预测方程看起来乱， largely 因为卡尔曼滤波在测量空间计算更新。测量 *不可逆（invertible）*。例如考虑给出目标距离的传感器，无法把距离转换成位置——圆上无穷多位置产生同一距离。反之，给定位置（状态）总能算距离（测量）。

继续之前，回忆我们做很简单的事：在测量与预测之间选新估计，如下图：
<img src="./figs/residual_chart.png">

""",

93: """方程复杂因状态多维，但操作就是我们在做的。别让方程掩盖思想的简单性。

$\\underline{\\textbf{系统不确定性（System Uncertainty）}}$

$\\textbf{S} = \\mathbf{H\\bar PH}^\\mathsf T + \\mathbf R$

在测量空间工作，卡尔曼滤波须把协方差矩阵投影到测量空间。数学为 $\\mathbf{H\\bar PH}^\\mathsf T$，$\\mathbf{\\bar P}$ 是 *先验* 协方差，$\\mathbf H$ 是测量函数。


应认出 $\\mathbf{ABA}^\\mathsf T$ 形式——预测步用 $\\mathbf{FPF}^\\mathsf T$ 以状态转移函数更新 $\\mathbf P$。这里用测量函数同样形式更新。线性代数为我们换坐标系。

协方差进入测量空间后须计入传感器噪声。很简单——只加矩阵。结果称为 *系统不确定性（system uncertainty）* 或 *新息协方差（innovation covariance）*。

忽略 $\\mathbf H$ 项，该方程等价于一维卡尔曼增益分母：

$$K = \\frac {\\bar\\sigma^2} {\\bar\\sigma^2 + \\sigma_z^2}$$

对比系统不确定性与协方差方程

$$\\begin{aligned}
\\mathbf{S} &= \\mathbf{H\\bar PH}^\\mathsf T + \\mathbf R\\\\
\\mathbf{\\bar P} &= \\mathbf{FPF}^\\mathsf T + \\mathbf Q
\\end{aligned}$$

各方程用函数 $\\mathbf H$ 或 $\\mathbf F$ 把 $\\mathbf P$ 放入不同空间，再加该空间关联的噪声矩阵。

$\\underline{\\textbf{卡尔曼增益（Kalman Gain）}}$

$\\mathbf K = \\mathbf{\\bar PH}^\\mathsf T \\mathbf{S}^{-1}$

回想残差图。有预测与测量后，须在两者之间选估计。若更确信测量，估计更靠近测量；若更确信预测，估计更靠近预测。

一维章用下式缩放均值

$$
\\mu =\\frac{\\bar\\sigma^2 \\mu_z + \\sigma_\\mathtt{z}^2 \\bar\\mu} {\\bar\\sigma^2 + \\sigma_\\mathtt{z}^2}$$

简化为

$$\\mu = (1-K)\\bar\\mu + K\\mu_\\mathtt{z}$$

得

$$K = \\frac {\\bar\\sigma^2} {\\bar\\sigma^2 + \\sigma_z^2}$$

$K$ 是 *卡尔曼增益（Kalman gain）*，0 到 1 的实数。务必理解它如何在预测与测量之间选均值。卡尔曼增益是 *百分比* 或 *比率*——若 K 为 .9，取 90% 测量、10% 预测。

多元卡尔曼滤波 $\\mathbf K$ 是向量而非标量。方程：$\\mathbf K = \\mathbf{\\bar PH}^\\mathsf T \\mathbf{S}^{-1}$。这是 *比率* 吗？可把矩阵逆想成线性代数的倒数。矩阵无除法，但这样理解有用。故可读 $\\textbf{K}$ 为

$$\\begin{aligned} \\mathbf K &\\approx \\frac{\\mathbf{\\bar P}\\mathbf H^\\mathsf T}{\\mathbf{S}} \\\\
\\mathbf K &\\approx \\frac{\\mathsf{uncertainty}_\\mathsf{prediction}}{\\mathsf{uncertainty}_\\mathsf{measurement}}\\mathbf H^\\mathsf T
\\end{aligned}$$

卡尔曼增益方程根据对预测与测量的信任程度计算比率。我们在各章都做同样的事。方程复杂因在多维用矩阵，但概念简单。$\\mathbf H^\\mathsf T$ 项不太直观，稍后解释。忽略该项，卡尔曼增益方程与一维相同：用先验不确定性除以先验与测量不确定性之和。

$\\underline{\\textbf{残差（Residual）}}$

$\\mathbf y = \\mathbf z - \\mathbf{H\\bar{x}}$

设计测量函数 $\\mathbf H$ 时已讲过。测量函数把状态转成测量。故 $\\mathbf{Hx}$ 把 $\\mathbf x$ 转成等价测量。完成后从测量 $\\mathbf z$ 减去得残差——测量与预测之差。

一维方程为

$$y = z - \\bar x$$

显然计算同样的事，只是一维。

$\\underline{\\textbf{状态更新（State Update）}}$

$\\mathbf x = \\mathbf{\\bar x} + \\mathbf{Ky}$

沿残差选新状态，由卡尔曼增益缩放。缩放由 $\\mathbf{Ky}$ 完成，既缩放残差又用 $\\mathbf K$ 中的 $\\mathbf H^\\mathsf T$ 转回状态空间。加到先验，方程：$\\mathbf x =\\mathbf{\\bar x} + \\mathbf{Ky}$。写出 $\\mathbf K$ 看完整计算：

$$\\begin{aligned}
\\mathbf x &= \\mathbf{\\bar x} + \\mathbf{Ky} \\\\
&= \\mathbf{\\bar x} + \\mathbf{\\bar PH}^\\mathsf T \\mathbf{S}^{-1}\\mathbf y \\\\
&\\approx \\mathbf{\\bar x} + \\frac{\\mathsf{uncertainty}_\\mathsf{prediction}}{\\mathsf{uncertainty}_\\mathsf{measurement}}\\mathbf H^\\mathsf T \\mathbf y
\\end{aligned}$$

或许更好 *看* 比率的方式是重写估计方程：

$$\\begin{aligned}
\\mathbf x &= \\mathbf{\\bar x} + \\mathbf{Ky} \\\\
&= \\mathbf{\\bar x} +\\mathbf K(\\mathbf z - \\mathbf{H\\bar x}) \\\\
&= (\\mathbf I - \\mathbf{KH})\\mathbf{\\bar x} + \\mathbf{Kz}
\\end{aligned}$$

与一维形式的相似应明显：
$$\\mu = (1-K)\\bar\\mu + K\\mu_\\mathtt{z}$$

$\\underline{\\textbf{协方差更新（Covariance Update）}}$

$\\mathbf P = (\\mathbf{I}-\\mathbf{KH})\\mathbf{\\bar P}$

$\\mathbf{I}$ 是单位矩阵，多维中表示 $1$。$\\mathbf H$ 是测量函数，为常数。方程可想成 $\\mathbf P = (1-c\\mathbf K)\\mathbf P$。$\\mathbf K$ 是预测与测量使用比例。若 $\\mathbf K$ 大则 $(1-\\mathbf{cK})$ 小，$\\mathbf P$ 变小。若 $\\mathbf K$ 小则 $(1-\\mathbf{cK})$ 大，$\\mathbf P$ 相对更大。即按卡尔曼增益的某因子调整不确定性大小。

该方程可能数值不稳定，FilterPy 不用。减法可破坏对称性并随时间导致浮点误差。稍后分享更复杂但更稳定的形式。

""",

94: """### 不用 FilterPy 的示例（An Example not using FilterPy）

FilterPy 隐藏实现细节。通常你会感激，但让我们不用 FilterPy 实现上一个滤波。需把矩阵定义为变量，显式实现卡尔曼滤波方程。

初始化矩阵：

""",

97: """结果与 FilterPy 版相同。偏好由你。我不喜欢用 `x`、`P` 等污染命名空间；`dog_filter.x` 对我而言更可读。

更重要的是，该例要求你记住并编写卡尔曼滤波方程。迟早会出错。FilterPy 版确保代码正确。另一方面，若定义有误，如把 $\\mathbf H$ 做成列向量而非行向量，FilterPy 的错误信息比显式代码更难调试。

FilterPy 的 KalmanFilter 类还提供平滑（smoothing）、批处理、衰减记忆滤波、最大似然计算等。无需显式编程即可获得。

""",

98: """### 小结（Summary）

我们学了卡尔曼滤波方程。汇总供复习。要学很多，但希望你逐项认出一维滤波的亲缘。在 *卡尔曼数学* 章会说明，若把 $\\mathbf x$ 维数设为 1，这些方程回到一维滤波方程。不是“像”一维滤波——是其多维实现。

$$
\\begin{aligned}
\\text{Predict Step}\\\\
\\mathbf{\\bar x} &= \\mathbf{F x} + \\mathbf{B u} \\\\
\\mathbf{\\bar P} &= \\mathbf{FP{F}}^\\mathsf T + \\mathbf Q \\\\
\\\\
\\text{Update Step}\\\\
\\textbf{S} &= \\mathbf{H\\bar PH}^\\mathsf T + \\mathbf R \\\\
\\mathbf K &= \\mathbf{\\bar PH}^\\mathsf T \\mathbf{S}^{-1} \\\\
\\textbf{y} &= \\mathbf z - \\mathbf{H \\bar x} \\\\
\\mathbf x &=\\mathbf{\\bar x} +\\mathbf{K\\textbf{y}} \\\\
\\mathbf P &= (\\mathbf{I}-\\mathbf{KH})\\mathbf{\\bar P}
\\end{aligned}
$$

分享文献中常见的一种形式。记法系统很多，但可了解预期。

 $$
\\begin{aligned}
\\hat{\\mathbf x}_{k\\mid k-1} &= \\mathbf F_k\\hat{\\mathbf x}_{k-1\\mid k-1} + \\mathbf B_k \\mathbf u_k  \\\\
\\mathbf P_{k\\mid k-1} &=  \\mathbf F_k \\mathbf P_{k-1\\mid k-1} \\mathbf F_k^\\mathsf T + \\mathbf Q_k \\\\        	
\\tilde{\\mathbf y}_k &= \\mathbf z_k - \\mathbf H_k\\hat{\\mathbf x}_{k\\mid k-1}\\\\
\\mathbf{S}_k &= \\mathbf H_k \\mathbf P_{k\\mid k-1} \\mathbf H_k^\\mathsf T + \\mathbf R_k \\\\
\\mathbf K_k &= \\mathbf P_{k\\mid k-1}\\mathbf H_k^\\mathsf T \\mathbf{S}_k^{-1}\\\\
\\hat{\\mathbf x}_{k\\mid k} &= \\hat{\\mathbf x}_{k\\mid k-1} + \\mathbf K_k\\tilde{\\mathbf y}_k\\\\
\\mathbf P_{k|k} &= (I - \\mathbf K_k \\mathbf H_k) \\mathbf P_{k|k-1}
\\\\\\end{aligned}
$$

该记法用贝叶斯 $a\\mid b$ 记法，表示在 $b$ 的证据下 $a$。帽号表示估计。故 $\\hat{\\mathbf x}_{k\\mid k}$ 表示在步 $k$（第一个 $k$）的证据下步 $k$ 的状态 $\\mathbf x$ 的估计（第二个 $k$）。即后验。$\\hat{\\mathbf x}_{k\\mid k-1}$ 表示在步 $k-1$ 估计下步 $k$ 的 $\\mathbf x$ 估计。即先验。

该记法抄自 [Wikipedia](https://en.wikipedia.org/wiki/Kalman_filter#Details) [[1]](#[wiki_article])，让数学家精确表达。正式发表新结果需要该精度。作为程序员我觉得相当难读。我习惯把变量变化想成程序运行，不为每次计算用不同变量名。文献无统一格式，各作者选择不同。我在不同书与论文间快速切换有困难，故采用 admittedly 不太精确的记法。数学家可能给我写严厉邮件，但希望程序员与学生为简化记法而高兴。

**符号（Symbology）** 附录列出各作者记法。还有另一困难：不同作者用不同变量名。$\\mathbf x$ 相当 universal，之后各说各话。常见用 $\\mathbf{A}$ 表示我所说的 $\\mathbf F$。须仔细阅读，希望作者定义变量（常不定义）。

若是试图理解论文方程的程序员，建议先去掉所有上标、下标与变音符号，换成单字母。若每天与这类方程打交道，此建议多余；但我阅读时通常想理解计算流。对我来说记住此步的 $P$ 是上步计算的更新 $P$ 值，远比记住 $P_{k-1}(+)$ 含义及其与 $P_k(-)$ 关系、与五分钟前读的论文记法关系容易得多。

""",

99: """## 练习：展示隐变量的效应（Exercise: Show Effect of Hidden Variables）

滤波器中速度是隐变量。若状态不用速度，滤波器表现如何？

写状态为 $\\mathbf x=\\begin{bmatrix}x\\end{bmatrix}$ 的卡尔曼滤波，与 $\\mathbf x=\\begin{bmatrix}x & \\dot x\\end{bmatrix}^\\mathsf T$ 的滤波对比。

""",

101: """### 解答（Solution）

我们已实现位置与速度的卡尔曼滤波，故提供代码、少注释，再绘图。

""",

103: """### 讨论（Discussion）

把速度纳入状态的滤波比只跟踪位置的滤波估计好得多。一维滤波无法估计速度或位置变化，故滞后于被跟踪物体。

一维卡尔曼滤波章中，预测方程有控制输入 `u`：

```python
    def predict(self, u=0.0):
        self.x += u
        self.P += self.Q
```

试试指定控制输入：

""",

105: "此处两滤波器表现相似，一维滤波或许跟踪更紧。但看实际速度 `vel` 与控制输入 `u` 不同时：\n",

107: "若跟踪我们同时控制的机器人，一维滤波可做得很好，因为控制输入使滤波器准确预测。但若被动跟踪，控制输入帮助不大，除非能准确 *先验* 猜测速度。这很少可能。\n",

108: """## 速度如何计算（How Velocity is Calculated）

尚未解释滤波器如何计算速度或任何隐变量。代入为滤波器矩阵算出的值可见发生什么。

先算系统不确定性。

$$\\begin{aligned}
\\textbf{S} &= \\mathbf{H\\bar PH}^\\mathsf T + \\mathbf R \\\\
&= \\begin{bmatrix} 1 & 0\\end{bmatrix}
\\begin{bmatrix}\\sigma^2_x & \\sigma_{xv} \\\\ \\sigma_{xv} & \\sigma^2_v\\end{bmatrix}
\\begin{bmatrix} 1 \\\\ 0\\end{bmatrix} + \\begin{bmatrix}\\sigma_z^2\\end{bmatrix}\\\\
&= \\begin{bmatrix}\\sigma_x^2 & \\sigma_{xv}\\end{bmatrix}\\begin{bmatrix} 1 \\\\ 0\\end{bmatrix}+ \\begin{bmatrix}\\sigma_z^2\\end{bmatrix} \\\\
&= \\begin{bmatrix}\\sigma_x^2 +\\sigma_z^2\\end{bmatrix}
\\end{aligned}$$

有 $\\mathbf S$ 后可求卡尔曼增益：
$$\\begin{aligned}
\\mathbf K &= \\mathbf{\\bar PH}^\\mathsf T \\mathbf{S}^{-1} \\\\
&= \\begin{bmatrix}\\sigma^2_x & \\sigma_{xv} \\\\ \\sigma_{xv} & \\sigma^2_v\\end{bmatrix}
\\begin{bmatrix} 1 \\\\ 0\\end{bmatrix}
\\begin{bmatrix}\\frac{1}{\\sigma_x^2 +\\sigma_z^2}\\end{bmatrix} \\\\
&= \\begin{bmatrix}\\sigma^2_x  \\\\ \\sigma_{xv}\\end{bmatrix}
\\begin{bmatrix}\\frac{1}{\\sigma_x^2 +\\sigma_z^2}\\end{bmatrix} \\\\
&= \\begin{bmatrix}\\sigma^2_x/(\\sigma_x^2 +\\sigma_z^2)  \\\\ \\sigma_{xv}/(\\sigma_x^2 +\\sigma_z^2)\\end{bmatrix}
\\end{aligned}
$$

换言之，$x$ 的卡尔曼增益为

$$K_x = \\frac{VAR(x)}{VAR(x)+VAR(z)}$$

一维情形应很熟悉。

速度 $\\dot x$ 的卡尔曼增益为
$$K_{\\dot x} = \\frac{COV(x, \\dot x)}{VAR(x)+VAR(z)}$$

效应？回忆状态计算为

$$\\begin{aligned}\\mathbf x 
&=\\mathbf{\\bar x}+\\mathbf K(z-\\mathbf{Hx)} \\\\
&= \\mathbf{\\bar x}+\\mathbf Ky\\end{aligned}$$

残差 $y$ 是标量，故乘以 $\\mathbf K$ 的每个元素。故

$$\\begin{bmatrix}x \\\\ \\dot x\\end{bmatrix}=\\begin{bmatrix}\\bar x \\\\ \\bar{\\dot x}\\end{bmatrix} + \\begin{bmatrix}K_x \\\\ K_{\\dot x}\\end{bmatrix}y$$

得方程组：

$$\\begin{aligned}x& = \\bar x + yK_x\\\\
\\dot x &= \\bar{\\dot x} + yK_{\\dot x}\\end{aligned}$$

预测 $\\bar x$ 为 $x + \\bar x \\Delta t$。若预测完美则残差 $y=0$（忽略测量噪声），速度估计不变。若速度估计很差则预测很差，残差大：$y >> 0$。此时用 $yK_{\\dot x}$ 更新速度估计。$K_{\\dot x}$ 与 $COV(x,\\dot x)$ 成正比。故速度按位置误差乘以位置与速度协方差的比例更新。相关性越高修正越大。

$COV(x,\\dot x)$ 是 $\\mathbf P$ 的非对角元。回忆那些值由 $\\mathbf{FPF}^\\mathsf T$ 计算。故位置与速度协方差在预测步计算。速度的卡尔曼增益与该协方差成正比，根据上一 epoch 速度多不准乘以与该协方差成正比的值调整速度估计。

总之，这些线性代数方程可能陌生，但计算其实很简单。本质上与 g-h 滤波做的相同。本章常数不同，因为我们计入过程模型与传感器噪声，但数学相同。

""",

109: """## 调整滤波器（Adjusting the Filter）

开始改变参数看各种变化的影响。对卡尔曼滤波这是很正常的做法。很难、往往不可能精确建模传感器。不完美模型意味着滤波输出不完美。工程师花大量时间调参使滤波器与真实传感器配合良好。现在花时间学习这些变化的影响。学每种变化的效果会培养设计直觉。设计卡尔曼滤波既是科学也是艺术。我们用数学建模物理系统，模型不完美。

看测量噪声 $\\mathbf R$ 与过程噪声 $\\mathbf Q$ 的效应。想看不同 $\\mathbf R$、$\\mathbf Q$ 设置的效果，我给测量方差 225 平方米。很大，但放大图上各种设计选择的效果，更易认出发生什么。第一个实验保持 $\\mathbf R$ 不变、改变 $\\mathbf Q$。

""",

111: """第一幅图的滤波器应紧密跟随含噪测量。第二幅图滤波器应明显偏离测量，更接近直线。为何 ${\\mathbf Q}$ 这样影响图？

回忆 *过程不确定性（process uncertainty）* 的含义。考虑跟踪球：真空中可用数学准确建模，但有风、变空气密度、温度、带缝线旋转球与不完美表面，模型会偏离现实。

第一种情况 `Q_var=20 m^2`，很大。物理上告诉滤波器“我不信任运动预测步”，因为我们说速度方差为 20。严格说这是说有很多未用 $\\small{\\mathbf F}$ 建模的外部噪声，结果是几乎不信任运动预测。滤波器会算速度 ($\\dot x$)，但 largely 忽略，因为我们说计算极不可信。故滤波器只能信任测量，紧密跟随测量。

第二种 `Q_var=0.02 m^2`，很小。物理上说“信任预测，很好！”。严格说过程噪声很小（方差 0.02 $m^2$），过程模型很准。滤波器忽略部分测量因其上下跳动，与可信速度预测不符。

现在设 `Q_var` 为 $0.2\\, m^2$，`R_var` 提到 $10,000\\, m^2$。告诉滤波器测量噪声很大。

""",

113: """效应可能微妙。我们造了次优滤波器，因实际测量噪声方差是 225 $m^2$，不是 10,000 $m^2$。把滤波器噪声方差设很高迫使滤波器偏向预测而非测量。可导致看起来很平滑很好的结果。上图轨迹可能极好，因紧密跟随理想路径。但开头的“很好”行为应让你警惕——滤波器尚未收敛 ($\\mathbf P$ 仍大)，不应能如此接近实际位置。可见 $\\mathbf P$ 未收敛，因整图着黄色背景表示 $\\mathbf P$ 大小。看坏初猜的影响：初位置猜 50 m、初速度 1 m/s。

""",

115: "可见滤波器无法获得轨迹。虽得到合理测量，但假设测量很差，最终每步从坏位置向前预测。若以为较小测量噪声会有类似结果，把 `R` 设回正确值 225 $m^2$。\n",

117: """可见滤波器最初几个迭代挣扎获得轨迹，然后准确跟踪狗。事实上几乎最优——$\\mathbf Q$ 未最优设计，但 $\\mathbf R$ 最优。$\\mathbf Q$ 经验法则：设在 $\\frac{1}{2}\\Delta a$ 到 $\\Delta a$ 之间，$\\Delta a$ 是采样周期间加速度最大变化量。仅适用于本章假设——加速度恒定且各时间段不相关。卡尔曼数学章讨论多种设计 $\\mathbf Q$ 的方法。

某种程度上改变 ${\\mathbf R}$ 或 ${\\mathbf Q}$ 可得类似外观，但劝你不要“魔法”调参直到喜欢输出。始终思考这些赋值的物理含义，根据对所滤波系统的了解改变 ${\\mathbf R}$ 和/或 ${\\mathbf Q}$。用大量仿真和/或真实数据试跑支撑。

""",

118: "## 协方差矩阵的详细考察（A Detailed Examination of the Covariance Matrix）\n\n重温画轨迹。我在 `zs_var_275` 中硬编码数据与噪声，避免受随机数生成器摆布。从 `P=500` 开始。\n",

120: """看输出，滤波器输出开头有很大尖峰。我们设 $\\text{P}=500\\, \\mathbf{I}_2$（2×2 对角为 500 的简写）。现在有足够信息理解含义及滤波器如何处理。左上角 500 对应 $\\sigma^2_x$；故说 `x` 标准差约 $\\sqrt{500}$，约 22.36 m。约 99% 样本在 $3\\sigma$ 内，故 $\\sigma^2_x=500$ 告诉滤波器预测（先验）可能偏差达 67 米。误差大，故测量尖峰时滤波器不信任自己的估计，剧烈跳动以纳入测量。随后 $\\mathbf P$ 快速收敛到更现实的值。

看背后数学。卡尔曼增益方程为

$$\\mathbf K = \\mathbf{\\bar P} \\mathbf H^\\mathsf T\\mathbf{S}^{-1} \\approx \\frac{\\mathbf{\\bar P}\\mathbf H^\\mathsf T}{\\mathbf{S}} 
\\approx \\frac{\\mathsf{uncertainty}_\\mathsf{prediction}}{\\mathsf{uncertainty}_\\mathsf{measurement}}\\mathbf H^\\mathsf T
$$

是预测与测量不确定性的比率。此处预测不确定性大，故 $\\mathbf K$ 大（标量时近 1）。$\\mathbf K$ 乘残差 $\\textbf{y} = \\mathbf z - \\mathbf{H \\bar x}$（测量减预测），大 $\\mathbf K$ 偏向测量。故若 $\\mathbf P$ 相对传感器不确定性 $\\mathbf R$ 大，滤波器主要从测量形成估计。


现在看较小初值 $\\mathbf P = 1.0\\, \\mathbf{I}_2$ 的效应。

""",

122: """初看 *似乎* 不错。图无前图尖峰；滤波器开始跟踪测量、无需时间稳定到信号。但若看 P 的图，可见位置方差初尖峰，且从未真正收敛。差设计导致长收敛时间与次优结果。

故尽管滤波器紧密跟踪实际信号，不能结论“魔法”是用小 $\\mathbf P$。是的，可避免卡尔曼滤波花时间准确跟踪，但若对初测量真不确定，可能导致很差结果。若跟踪活物，开始前可能对位置很不确定。若滤温度计输出，对第一次与第 1000 次测量同样确信。滤波器表现好须把 $\\mathbf P$ 设为真正反映数据知识的值。

看坏初估计 coupled 很小 $\\mathbf P$。初估计 x = 100 m（狗实际从 0 m 开始），但设 `P=1` m$^2$。对 $\\mathbf P$ 明显错误，估计偏 100 m 却告诉滤波器 $3\\sigma$ 误差为 3 m。

""",

124: "可见初估计很差，滤波器需很长时间才开始收敛到信号。因为我们强烈相信初估计 100 m，而该信念错误。\n",

126: """此时卡尔曼滤波对初状态很不确定，故更快收敛到信号。约 5 到 6 个 epoch 后输出良好。以迄今理论这大约最好。但该场景略人工；若开始跟踪时不知物体在哪，不会把滤波器初始化为任意值如 0 m 或 100 m。下文 **滤波器初始化（Filter Initialization）** 节讨论。

再为狗做一个卡尔曼滤波，在同一图上画协方差椭圆与位置。

""",

128: """若在 Jupyter Notebook 或网上阅读，这是滤波数据的动画。我调了参数以便容易看到 $\\mathbf P$ 随滤波进展的变化。
<img src='animations/multivariate_track1.gif'>

""",

129: """输出略乱，但应能看出发生什么。两图都为每点画协方差矩阵。从协方差 $\\mathbf P=(\\begin{smallmatrix}20&0\\\\0&20\\end{smallmatrix})$ 开始，表示对初信念很不确定。收到第一个测量后滤波器更新信念，方差不再那么大。上图第一个椭圆（最左）应略扁。随滤波器继续处理测量，协方差椭圆很快变形，直到变成长窄、沿运动方向倾斜的椭圆。

物理含义：椭圆 x 轴是位置不确定性，y 轴是速度不确定性。高于宽的椭圆表示速度比位置更不确定。宽而窄的椭圆表示位置不确定性高、速度低。倾斜量显示两变量相关程度。

第一图 `R=5` $m^2$，最终椭圆宽于高。若不清楚，我打印了右下角最后椭圆的方差。

对比第二图 `R=0.5` $m^2$，最终椭圆高于宽。第二图所有椭圆比第一图小得多。合理，因为小 $\\small\\mathbf R$ 意味着测量噪声小。噪声小意味着预测准，故对位置信念强。

""",

130: """## 问题：解释椭圆差异（Question: Explain Ellipse Differences）

为何 $\\mathbf R=5 m^2$ 的椭圆比 $\\mathbf R=0.5 m^2$ 更倾向水平？提示：从椭圆物理含义想，不是从数学。若不确定，把 $\\mathbf R$ 改成很大很小如 100 $m^2$ 与 0.1 $m^2$，观察变化并思考含义。

""",

131: """### 解答（Solution）

x 轴是位置，y 轴是速度。竖直或近竖直的椭圆说位置与速度无相关，对角椭圆说相关很强。这样说结果似乎 unlikely。倾斜变化，但相关性不应随时间变。但这是滤波器 *输出* 的度量，不是真实物理世界的描述。$\\mathbf R$ 很大时告诉滤波器测量噪声大。此时卡尔曼增益 $\\mathbf K$ 偏向预测而非测量，预测来自速度状态变量。故 $x$ 与 $\\dot x$ 相关性强。反之 $\\mathbf R$ 小时告诉滤波器测量很可信，$\\mathbf K$ 偏向测量。若测量近乎完美，滤波器为何还用预测？若不多用预测，报告的相关性就很小。

**这是必须理解的关键点！** 卡尔曼滤波是真实世界系统的数学模型。报告相关性小 *并不意味着* 物理系统无相关，只是数学模型中 *线性* 相关少。它报告的是测量与预测各纳入模型的多少。

用极大测量误差把观点说透。设 $\\mathbf R=200\\, m^2$。看图前先想会怎样。

""",

133: """希望结果符合预期。椭圆很快变很宽、不高。因为卡尔曼滤波 mostly 用预测而非测量产生滤波结果。也可看到滤波器输出缓慢获得轨迹。滤波器假设测量极噪，故很慢更新 $\\dot x$ 的估计。

继续看这些图直到掌握如何解释协方差矩阵 $\\mathbf P$。面对 $9{\\times}9$ 矩阵可能 overwhelming——81 个数要解释。拆开看——对角是各状态变量方差，非对角元是两方差与缩放因子 $p$ 的乘积。无法在屏幕上画 $9{\\times}9$ 矩阵，故须在这简单 2D 情况培养直觉与理解。

>画协方差椭圆时，代码中务必用 `ax.set_aspect('equal')` 或 `plt.axis('equal')`（前者可设 xlim、ylim）。若坐标轴刻度不同，椭圆会画变形。例如椭圆画得高于宽，实际可能宽于高。

""",

134: """## 滤波器初始化（Filter Initialization）


初始化方案很多。下列方法在多数情况表现良好。该方案等到第一个测量 $\\mathbf z_0$ 再初始化。由此用 $\\mathbf x_0 = \\mathbf z_0$ 算 $\\mathbf x$ 初值。若 $\\mathbf z$ 与 $\\mathbf x$ 大小、类型、单位通常不同，可用测量函数如下。

已知

$$\\mathbf z = \\mathbf{Hx}$$

故

$$\\begin{aligned}
\\mathbf H^{-1}\\mathbf{Hx} &= \\mathbf H^{-1}\\mathbf z \\\\
\\mathbf x &= \\mathbf H^{-1}\\mathbf z\\end{aligned}$$

矩阵求逆要求方阵，但 $\\mathbf H$ 很少方阵。SciPy 用 `scipy.linalg.pinv` 计算 Moore-Penrose 伪逆，代码可能像

""",

136: """问题域专门知识可能导致不同计算，但这是可行方法之一。例如若状态含速度，可取前两个位置测量、算差作为初速度。

还需计算 $\\mathbf P$。因问题而异，一般对相同项用测量误差 $\\mathbf R$，其余项用最大值。也许不清楚。本章用位置与速度作状态跟踪物体，测量是位置。则初始化 $\\mathbf P$ 为

$$\\mathbf P = \\begin{bmatrix}\\mathbf R_0 & 0 \\\\0 & vel_{max}^2\\end{bmatrix}$$

$\\mathbf P$ 对角是各状态变量方差，故填入合理值。$\\mathbf R_0$ 是位置的合理方差，最大速度平方是速度的合理方差。平方因为方差是平方：$\\sigma^2$。

须真正理解工作领域，用最佳可用信息初始化。例如跟踪赛马，初测量可能很差，位置远离起跑门。我们知道马必须从起跑门出发；用初测量初始化会导致次优。此场景应始终把卡尔曼滤波初始化为马的起跑门位置。

""",

137: """## 批处理（Batch Processing）

卡尔曼滤波设计为递归算法——新测量到来立即形成新估计。但常有已采集数据集要滤波。卡尔曼滤波可批处理模式运行，一次滤所有测量。在 `KalmanFilter.batch_filter()` 中实现。内部只是循环测量并收集结果状态与协方差估计到数组。简化逻辑并方便收集所有输出到数组。我常用该函数，但等到章末才介绍，以便你非常熟悉必须运行的预测/更新循环。

先把测量收集到数组或列表。也许在 CSV：

```python
zs = read_altitude_from_csv('altitude_data.csv')
```

或用生成器：

```python
zs = [some_func(i) for i in range(1000)]
```

然后调用 `batch_filter()`。

```python
Xs, Ps, Xs_prior, Ps_prior = kfilter.batch_filter(zs)
```

函数接受测量列表、滤波，返回状态估计 (Xs)、协方差矩阵 (Ps) 及对应先验 (Xs_prior, Ps_prior) 的 NumPy 数组。

完整示例如下。

""",

139: "批处理滤波接受可选 `filterpy.common.Saver` 对象。若提供，滤波器所有属性也会保存。便于检查除状态与协方差外的值。这里画残差看是否像以 0 为中心的噪声。快速目视检查滤波器是否设计良好。若偏离 0 或不像噪声，滤波器设计差和/或过程非高斯。后文详谈。此处演示 `Saver` 类。\n",

141: """## 平滑结果（Smoothing the Results）

本书有平滑一章；此处不重复。但使用如此简单、输出改善如此深刻，用几个例子撩一下。平滑章不算难；你已足够准备现在阅读。

假设跟踪直线行驶的汽车。得到暗示汽车开始左转的测量。卡尔曼滤波把状态估计略移向测量，但无法判断这是特别噪的测量还是真正开始转弯。

若有未来测量可判断是否转弯。假设后续测量继续左转，可确信转弯开始。反之若后续继续直线，可知测量噪、应 largely 忽略。估计不再介于测量与预测之间，而完全纳入测量或忽略，取决于未来测量暗示的物体运动。

`KalmanFilter` 实现该算法的一种形式，称为 *RTS 平滑器（RTS smoother）*，以算法发明者 Rauch、Tung、Striebel 命名。方法为 `rts_smoother()`。传入 `batch_filter` 步计算的均值与协方差，返回平滑后的均值、协方差与卡尔曼增益。

""",

143: """输出很棒！图中两点很明显。第一，RTS 平滑器输出比 KF 输出平滑得多。第二，几乎总是比 KF 输出更准确（**平滑（Smoothing）** 章将详查该论断）。对隐变量速度的改善更 dramatic：

""",

145: "下一练习探讨原因。\n",

146: """## 练习：对比速度（Exercise: Compare Velocities）

既然画速度，看“原始”速度——可用相邻测量相减近似，即时刻 1 的速度约 `xs[1] - xs[0]`。把原始值与卡尔曼滤波和 RTS 滤波估计的值对比绘图并讨论。

""",

148: "### 解答（Solution）\n",

150: """可见噪声淹没信号，原始值 essentially 无用。滤波器单独维护速度估计。卡尔曼增益 $\\mathbf K$ 是多维的。例如可能为 $\\mathbf K = [0.1274, 0.843]^\\mathsf T$。第一个值缩放位置残差，第二个缩放速度残差。协方差矩阵告诉滤波器位置与速度如何相关，各自被最优滤波。

展示这一点是为了重申用卡尔曼滤波计算速度、加速度甚至更高阶量的重要性。即使测量准确到愿直接用未滤波值，我也用卡尔曼滤波，因为它给出准确的速度与加速度估计。

""",

151: """## 讨论与小结（Discussion and Summary）

多元高斯（multivariate Gaussians）让我们同时处理多个维度，既有空间也有其他（速度等）。关键洞见：隐变量能显著提高滤波精度，因为它们与观测变量相关。

我给出了 *可观测性（observability）* 的直观定义。可观测性由卡尔曼博士为线性系统提出，背后有相当理论。它回答能否通过观测系统输出确定系统状态。我们的问题较易判断，更复杂系统可能需要严格分析。维基百科 [Observability](https://en.wikipedia.org/wiki/Observability) 有概述；需深入学习可看 [[2]](#References)。

隐变量有一重要警告。很容易构造估计隐变量的滤波器。我可写估计被跟踪汽车颜色的滤波器。但无法从位置算颜色，颜色估计将是 nonsense。设计者须验证这些变量被正确估计。若无速度传感器却在估计速度，须测试速度估计是否正确；不要盲信。例如速度有周期分量——像正弦波。若采样时间小于频率 2 倍，无法准确估计速度（奈奎斯特定理）。想象采样周期等于速度频率。滤波器会报告速度恒定，因为在正弦波同一点采样。系统。

初始化对隐变量是特别难的问题。坏初始化滤波器通常能恢复观测变量，但可能挣扎并失败于隐变量。估计隐变量是强大工具，也是危险工具。

我建立了一系列设计卡尔曼滤波的步骤。它们不是卡尔曼滤波文献的 usual 部分，只作指南而非处方。难题设计是迭代过程。猜状态向量，确定测量与状态模型，跑测试，再按需改设计。

$\\mathbf R$ 与 $\\mathbf Q$ 的设计往往相当难。我让它显得挺科学。传感器高斯噪声 $\\mathcal{N}(0, \\sigma^2)$，故设 $\\mathbf R=\\sigma^2$。简单！这是 dirty lie。传感器不是高斯。书开头是体重秤。设 $\\sigma=1$ kg，称 0.5 kg 的东西。理论说会得到负测量，但秤永远不会报小于零的重量。真实传感器通常有 *厚尾（fat tails）*（*峰度 kurtosis*）与 *偏斜（skew）*。如秤，一个或两个尾部可能被截断。

$\\mathbf Q$ 情况更严峻。希望你对我轻描淡写给狗运动赋噪声矩阵持怀疑态度。谁能说狗下一步做什么？我 GPS 里的卡尔曼滤波不知道山坡、外界风或我糟糕的驾驶。但滤波器需要精确数字概括所有这些，且在我沙漠越野和 F1 冠军在赛道驾驶时都要工作。

这些问题让一些研究者与工程师轻蔑地把卡尔曼滤波称为“泥球”。换言之，不总 hold together。另一术语——卡尔曼滤波可能变得 *自满（smug）*。估计完全基于你告诉它的噪声值。那些值可导致过度自信的估计。$\\mathbf P$ 越来越小而滤波器实际越来越不准！最坏情况滤波器发散。研究非线性滤波时会大量见到。我们很快会。

卡尔曼滤波是世界的数学模型。输出准确度不超过该模型。为使数学可处理我们做了假设：假设传感器与运动模型有高斯噪声，假设一切线性。若成立，卡尔曼滤波在最小二乘意义下 *最优（optimal）*——无法比滤波器给出更好的估计。但这些假设几乎从不成立，故模型必然受限，工作中的滤波器很少最优。

后文处理非线性。现在须理解线性滤波器矩阵设计更多是实验而非纯数学。用数学定初值，然后实验。若世界有大量未计入噪声（风等），可能须加大 $\\mathbf Q$。太大则滤波器无法快速响应变化。**自适应滤波（Adaptive Filters）** 章有实时改变滤波器设计的替代技巧，目前须找一组适用于滤波器将遇条件的值。特技飞机噪声矩阵，学员飞行员与专家飞行员可能不同，因动力学差异大。

""",

152: "## 参考文献（References）\n",

153: """- <A name="[wiki_article]">[1]</A> 'Kalman Filters'. Wikipedia
https://en.wikipedia.org/wiki/Kalman_filter#Details

- [2] Grewal, Mohinder S., Andrews, Angus P. *Kalman Filtering: Theory and Practice Using MATLAB*. Third Edition. John Wiley & Sons. 2008.

""",
}
