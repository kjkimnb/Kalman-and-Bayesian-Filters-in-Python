# -*- coding: utf-8 -*-
"""10-Unscented-Kalman-Filter.ipynb markdown 译文（第 2 部分）"""

TRANSLATIONS_10_PART2 = {
85: """实现测量函数。将先验转为到两站的测量数组。我不喜全局变量，但把站址放在全局 `sa_pos`、`sb_pos` 以演示与 $h()$ 共享数据：

""",

87: "编写构造滤波器、运行并绘图的样板代码：\n",

89: """看起来不错。航迹开头误差大，滤波器收敛后估计良好。

 revisit 角度非线性：目标放在两传感器之间 (0,0)，均值角近零，残差计算非线性。角低于 0 时测量函数得近 $2\\pi$ 的大正角，预测与测量残差近 $2\\pi$ 而非近 0，滤波无法准确工作，见下例。

""",

91: "性能不可接受。`FilterPy` 的 UKF 可指定计算残差的函数处理此类非线性；本章最后示例演示。\n",

92: "## 传感器误差与几何的影响（Effects of Sensor Error and Geometry）\n",

93: """传感器相对被跟踪对象的几何关系施加物理限制，设计滤波器时极难处理。若 VOR 径向 nearly parallel，小角误差 translate 成大距离误差；且非线性——*x* 与 *y* 方向误差随实际方位变化。散点图显示 1°$\\sigma$ 误差在两种方位下的误差分布。

""",

95: "## 练习：解释滤波性能（Exercise: Explain Filter Performance）\n",

96: "小角误差时位置误差很大。解释为何上面目标跟踪问题 UKF 仍相对好。分别答单传感器与多传感器。\n",

97: "### 解答（Solution）\n",

98: """非常重要，读答案前尽量自己答。答不出可能要 revisit **多元卡尔曼滤波（Multivariate Kalman Filters）** 章 earlier 材料。

成功有多因素。先考虑单传感器：单次测量位置可能范围极大。但目标在动，UKF 计入这一点。画移动目标连续几次测量：

""",

100: """单次测量位置误差很大。连续测量图显示明显趋势——目标明显向右上移动。卡尔曼滤波算增益时用测量函数计入误差分布。本例误差约 45° 线，滤波器会 discount 该方向误差；正交方向几乎无误差，增益也会考虑。

图因每位置更新画 100 次测量而显得容易，运动 obvious。卡尔曼滤波每次更新只有一次测量，无法像绿虚线那样好拟合。

方位不给距离信息。设初始估计距传感器 1000 km（实际 7.07 km）且 $\\mathbf P$ 很小，1° 误差 translate 17.5 km 位置误差。滤波器无法收敛到真实目标，因错误地非常确信位置且测量无距离信息。

""",

101: """再看加第二传感器。两图显示不同站址效果。用方、三角符号表两传感器，同色同形画各传感器误差分布，再算两 noisy 方位的 $(x,y)$ 用红点显示 $x$、$y$ 上 noisy 测量分布。

""",

103: """第一图传感器 nearly orthogonal 于目标初始位置，得 lovely “x” 形交点。可见 $x$、$y$ 误差随目标移动变化——目标远离传感器、靠近 B 站 $y$ 坐标时红点呈强椭圆。

第二图飞机起始于一站附近再飞过第二站。误差交点 very non-orthogonal，位置误差 spread 很大。

""",

104: """## UKF 的实现（Implementation of the UKF）

FilterPy 已实现 UKF，但学会方程到代码仍有教益。实现 UKF 较直接。先写计算 sigma 点均值与协方差的代码。

sigma 点与权重存矩阵：

$$ 
\\begin{aligned}
\\text{weights} &= 
\\begin{bmatrix}
w_0& w_1 & \\dots & w_{2n}
\\end{bmatrix} 
\\\\
\\text{sigmas} &= 
\\begin{bmatrix}
\\mathcal{X}_{0,0} & \\mathcal{X}_{0,1} & \\dots & \\mathcal{X}_{0,n-1} \\\\
\\mathcal{X}_{1,0} & \\mathcal{X}_{1,1} &  \\dots & \\mathcal{X}_{1,n-1} \\\\
\\vdots & \\vdots &  \\ddots & \\vdots \\\\
\\mathcal{X}_{2n,0} & \\mathcal{X}_{2n,1} & \\dots & \\mathcal{X}_{2n,n-1}
\\end{bmatrix}
\\end{aligned}
$$


子标多，二维例 ($n$=2) 如下：

""",

106: """均值 sigma 点在第一行，位置 (0,0) 等于均值 (0,0)。第二 sigma 点 (0.173, 0.017)，依此类推。共 $2n+1=5$ 行，每行一个 sigma 点。$n=3$ 则 3 列 7 行。

行-列 vs 列-行存 sigmas  somewhat arbitrary；我选行格式便于 `sigmas[i]` 指第 i 个 sigma 点，而非 `sigmas[:, i]`。

""",

107: """### 权重（Weights）

NumPy 算权重容易。Van der Merwe 缩放 sigma 点：

$$
\\begin{aligned}
\\lambda&=\\alpha^2(n+\\kappa)-n \\\\ 
W^m_0 &= \\frac{\\lambda}{n+\\lambda} \\\\
W^c_0 &= \\frac{\\lambda}{n+\\lambda} + 1 -\\alpha^2 + \\beta \\\\
W^m_i = W^c_i &= \\frac{1}{2(n+\\lambda)}\\;\\;\\;i=1..2n
\\end{aligned}
$$
    
代码：

```python
lambda_ = alpha**2 * (n + kappa) - n
Wc = np.full(2*n + 1,  1. / (2*(n + lambda_))
Wm = np.full(2*n + 1,  1. / (2*(n + lambda_))
Wc[0] = lambda_ / (n + lambda_) + (1. - alpha**2 + beta)
Wm[0] = lambda_ / (n + lambda_)
```

`lambda_` 用下划线因 `lambda` 是 Python 保留字；尾下划线是 Pythonic  workaround。

""",

108: """### Sigma 点（Sigma Points）

方程：

$$
\\begin{cases}
\\mathcal{X}_0 = \\mu \\\\
\\mathcal{X}_i = \\mu +  \\left[\\sqrt{(n+\\lambda)\\Sigma} \\right]_i, & i=1..n \\\\
\\mathcal{X}_i = \\mu - \\left[\\sqrt{(n+\\lambda)\\Sigma}\\right]_{i-n} & i=(n+1)..2n
\\end{cases}
$$

理解 $\\left[\\sqrt{(n+\\lambda)\\Sigma}  \\right]_i$ 后 Python 不难。

$\\sqrt{(n+\\lambda)\\Sigma}$ 是矩阵（$\\Sigma$ 是矩阵）。下标 $i$ 选第 i 行。矩阵平方根无唯一定义。一种定义：$\\Sigma = SS$ 则 $S = \\sqrt{\\Sigma}$。

我们选数值性质更易计算的替代：$S$ 满足

$$
\\Sigma = \\mathbf{SS}^\\mathsf T
$$

因用 [*Cholesky 分解（Cholesky decomposition）*](https://en.wikipedia.org/wiki/Cholesky_decomposition) [5] 计算 $\\mathbf S$。它分解 Hermitian 正定矩阵为三角矩阵及其共轭转置，可上或下三角：

$$A=LL^{∗} \\\\ A=U^{∗}U$$

星号表共轭转置；实数可写：

$$A=LL^\\mathsf T \\\\ A=U^\\mathsf T U$$

$\\mathbf P$ 具这些性质，故 $\\mathbf S = \\text{cholesky}(\\mathbf P)$ 可看作 $\\mathbf P$ 的平方根。

SciPy 在 `scipy.linalg` 提供 `cholesky()`。Fortran/C/C++ 可用 LAPACK 等。Matlab 有 `chol()`。

默认 `scipy.linalg.cholesky()` 返回上三角，故代码按行访问，中心 sigma 点受整行非零影响。若自实现平方根须注意。文献中 UKF 有按列取的，适用于下三角 Cholesky 或对称算法行/列无关。

""",

110: """sigma 点可实现为：

```python
sigmas = np.zeros((2*n+1, n))
U = scipy.linalg.cholesky((n+lambda_)*P) # sqrt

sigmas[0] = X
for k in range (n):
    sigmas[k+1]   = X + U[k]
    sigmas[n+k+1] = X - U[k]
```

实现无迹变换。方程

$$\\begin{aligned}
\\mu &= \\sum_i w_i^m\\mathcal{X}_i \\\\
\\Sigma &= \\sum_i w_i^c{(\\mathcal{X}_i-\\mu)(\\mathcal{X}_i-\\mu)^\\mathsf{T}}
\\end{aligned}
$$

均值和用

```python
x = np.dot(Wm, sigmas)
```

NumPy 重度用户可能陌生。NumPy 底层 C/Fortran，比纯 Python 快 20–100 倍。须避免 for 循环，用内置函数。故用 `numpy.dot(x, y)` 而非 for 求积和。两向量点积为逐元素积之和。1D 与 2D 数组传入则算内积和：

""",

112: """剩下算 $\\mathbf P = \\sum_i w_i{(\\mathcal{X}_i-\\mu)(\\mathcal{X}_i-\\mu)^\\mathsf{T}} + \\mathbf Q$：

```python
kmax, n = sigmas.shape
P = zeros((n, n))
for k in range(kmax):
    y = sigmas[k] - x
    P += Wc[k] * np.outer(y, y) 
P += Q
```

NumPy 特性：`x` 与 `sigmas[k]` 一维，差亦一维。NumPy 不算 1D 数组转置，`[1,2,3]` 转置仍是 `[1,2,3]`。故用 `np.outer(y,y)` 算 1D $\\mathbf{y}$ 的 $\\mathbf{yy}^\\mathsf{T}$。替代：

```python
y = (sigmas[k] - x).reshape(kmax, 1) # convert into 2D array
P += Wc[K] * np.dot(y, y.T)
```

较慢且非惯用法，不用。

""",

113: '''### 预测步（Predict Step）

预测步按上法生成权重与 sigma 点，每个经 $f$：

$$\\boldsymbol{\\mathcal{Y}} = f(\\boldsymbol{\\chi})$$

用无迹变换算预测均值与协方差。下面假设为类方法，存滤波所需矩阵与向量。

```python
def predict(self, sigma_points_fn):
    """ Performs the predict step of the UKF. On return, 
    self.xp and self.Pp contain the predicted state (xp) 
    and covariance (Pp). 'p' stands for prediction.
    """

    # calculate sigma points for given mean and covariance
    sigmas = sigma_points_fn(self.x, self.Pp)

    for i in range(self._num_sigmas):
        self.sigmas_f[i] = self.fx(sigmas[i], self._dt)

    self.xp, self.Pp = unscented_transform(
                       self.sigmas_f, self.Wm, self.Wc, self.Q)
```

''',

114: "### 更新步（Update Step）\n",

115: """更新步经 `h(x)` 将 sigmas 转到测量空间。

$$\\mathcal{Z} = h(\\mathcal{Y})$$

用无迹变换算这些点均值与协方差，再算残差与卡尔曼增益。互协方差：

$$\\mathbf P_{xz} =\\sum_{i=0}^{2n} w^c_i(\\boldsymbol{\\mathcal Y}_i-\\mu)(\\boldsymbol{\\mathcal Z}_i-\\mu_z)^\\mathsf T$$

用残差与增益更新状态：

$$\\begin{aligned}
K &= \\mathbf P_{xz} \\mathbf P_z^{-1}\\\\
{\\mathbf x} &= \\mathbf{\\bar x} + \\mathbf{Ky}
\\end{aligned}$$

新协方差：

$$ \\mathbf P = \\mathbf{\\bar P} - \\mathbf{KP}_z\\mathbf{K}^\\mathsf{T}$$

可实现为类方法（存必要矩阵与数据）：

```python
def update(self, z):
    # rename for readability
    sigmas_f = self.sigmas_f
    sigmas_h = self.sigmas_h

    # transform sigma points into measurement space
    for i in range(self._num_sigmas):
        sigmas_h[i] = self.hx(sigmas_f[i])

    # mean and covariance of prediction passed through UT
    zp, Pz = unscented_transform(sigmas_h, self.Wm, self.Wc, self.R)

    # compute cross variance of the state and the measurements
    Pxz = np.zeros((self._dim_x, self._dim_z))
    for i in range(self._num_sigmas):
        Pxz += self.Wc[i] * np.outer(sigmas_f[i] - self.xp,
                                    sigmas_h[i] - zp)

    K = np.dot(Pxz, inv(Pz)) # Kalman gain

    self.x = self.xp + np.dot(K, z - zp)
    self.P = self.Pp - np.dot(K, Pz).dot(K.T)
```

""",

116: """### FilterPy 的实现（FilterPy's Implementation）

FilterPy 代码 somewhat 泛化。可指定不同 sigma 点算法、状态残差计算（角度 modular 不能直接减）、矩阵平方根函数等。见帮助文档。

https://filterpy.readthedocs.org/#unscented-kalman-filter

""",

117: """## 批处理（Batch Processing）

卡尔曼滤波递归——估计基于当前测量与先验。但常有已采集数据要滤波，可 *批处理（batch）* 模式一次滤全部测量。

测量放入数组或 list：

```python
zs = read_altitude_from_csv()
```

调用 `batch_filter()`：

```python
Xs, Ps = ukf.batch_filter(zs)
```

函数接受测量 list/数组，滤波后返回整段状态估计 `Xs` 与协方差 `Ps`。

完整示例见上文雷达跟踪。

""",

119: """## 平滑结果（Smoothing the Results）

跟踪汽车。含噪测量暗示开始左转，但状态函数预测直行。卡尔曼滤波只能 somewhat 移向含噪测量，无法判断是噪声还是真转弯。

若采集数据后处理， questionable 测量之后还有数据告知是否转弯。若后续测量持续左转，可确定非纯噪声而是转弯开始。

此处不推导数学与算法，只示如何调用 `FilterPy`。实现的是 *RTS 平滑器（RTS smoother）*，以 Rauch、Tung、Striebel 命名。

例程 `UnscentedKalmanFilter.rts_smoother()`。用法 trivial：传入 `batch_filter` 的均值与协方差，得平滑均值、协方差与卡尔曼增益。

""",

121: "由图可见位置改善小，速度改善好，高度 spectacular。位置差很小，故打印最后 5 点 UKF 与平滑结果之差。若能后处理，建议始终用 RTS 平滑器。\n",

122: """## 选择 Sigma 参数（Choosing the Sigma Parameters）

文献对 $\\alpha$、$\\beta$、$\\kappa$ 选择较缺。Van der Merwe 论文信息最多但不 exhaustive。探索其作用。

Van der Merwe 建议高斯问题 $\\beta=2$、$\\kappa=3-n$。由此出发变 $\\alpha$。令 $n=1$ 减小数组、避免矩阵开方。

""",

124: """怎么回事？均值为 0 时算法选 sigma 点 0、3、-3，为何？回忆方程：

$$\\begin{aligned}
\\mathcal{X}_0 &= \\mu\\\\
\\mathcal{X}_i &= \\mu \\pm \\sqrt{(n+\\lambda)\\Sigma}
\\end{aligned}$$

$n=1$ 化为标量，避免矩阵开方。对我们的值：

$$\\begin{aligned}
\\mathcal{X}_0 &= 0 \\\\
\\mathcal{X}_i &= 0 \\pm \\sqrt{(1+2)\\times 3} \\\\
&= \\pm 3
\\end{aligned}$$

$\\alpha$ 越大 sigma 点越 spread。设 absurd 值：

""",

126: """sigma 点 spread 到 100 标准差。若数据高斯，会纳入距均值许多标准差的数据；非线性问题 unlikely 好结果。但若分布非高斯、fat tails？可能须从尾部采样得好估计，故增大 $\\kappa$ 合理（非 200 那种 absurd 只为 stark 展示）。

类似地，分布几乎无尾——像倒抛物线——可能须把 sigma 点拉向均值，避免在无真实数据区域采样。

再看权重变化。$k+n=3$ 时均值权重 0.6667，两外侧 0.1667。$\\alpha=200$ 时均值权重约 0.99999，外侧约 0.000004。权重方程：

$$\\begin{aligned}
W_0 &= \\frac{\\lambda}{n+\\lambda} \\\\
W_i &= \\frac{1}{2(n+\\lambda)}
\\end{aligned}$$

$\\lambda$ 越大，均值权重 $\\lambda/(n+\\lambda)$ 趋 1，其余趋 0。与协方差大小无关。采样越远权重越小；很近则各点权重相近。

Van der Merwe 建议约束 $\\alpha$ 在 $0 \\gt \\alpha \\ge 1$，推荐 $10^{-3}$。试试：

""",

128: "## 机器人定位——完整算例（Robot Localization - A Fully Worked Example）\n",

129: """该做 significant 问题了。多数书选简单题、简单答案，你会疑惑如何实现真实问题。本例不能教 tackle 任意问题，但说明设计实现滤波器须考虑的事。

机器人定位：机器人在环境中移动，传感器检测地标。可能是自动驾驶车视觉识别树、建筑；可能是扫地或仓库机器人。

四轮布局同汽车，转前轮机动，绕后轴枢转前进——非线性，须建模。

传感器给出景观中已知目标近似距离与方位——非线性，因距离方位求位置需开方与三角函数。

过程与测量模型均非线性。UKF 可处理二者，暂定 UKF 适合。

""",

130: "### 机器人运动模型（Robot Motion Model）\n",

131: """一阶近似：汽车前进时转前轮。车头沿轮向移动，绕后轴枢转。受摩擦打滑、轮胎随速行为、内外轮半径不同等影响而复杂。精确转向需复杂微分方程。

卡尔曼滤波尤其低速机器人，较简 *自行车模型（bicycle model）* 表现好。示意：

""",

133: """前轮相对轴距指向 $\\alpha$。短时间前进，后轮更前且略内转，蓝阴影轮胎示意。短时间可近似绕半径 $R$ 转弯。转角 $\\beta$：

$$\\beta = \\frac{d}{w} \\tan{(\\alpha)}$$

转弯半径

$$R = \\frac{d}{\\beta}$$

后轮前进距离 $d=v\\Delta t$。

机器人朝向 $\\theta$，转弯前位置 $C$：

$$\\begin{aligned}
C_x &= x - R\\sin(\\theta) \\\\
C_y &= y + R\\cos(\\theta)
\\end{aligned}$$

前进 $\\Delta t$ 后新位置与朝向：

$$\\begin{aligned} \\bar x &= C_x + R\\sin(\\theta + \\beta) \\\\
\\bar y &= C_y - R\\cos(\\theta + \\beta) \\\\
\\bar \\theta &= \\theta + \\beta
\\end{aligned}
$$

代入 $C$ 得

$$\\begin{aligned} \\bar x &= x - R\\sin(\\theta) + R\\sin(\\theta + \\beta) \\\\
\\bar y &= y + R\\cos(\\theta) - R\\cos(\\theta + \\beta) \\\\
\\bar \\theta &= \\theta + \\beta
\\end{aligned}
$$

对转向模型不感兴趣可略过细节。重要的是运动模型非线性，须用卡尔曼滤波处理。

""",

134: """### 设计状态变量（Design the State Variables）

维护位置与朝向：

$$\\mathbf x = \\begin{bmatrix}x & y & \\theta\\end{bmatrix}^\\mathsf{T}$$

可把速度纳入模型，但数学已 quite challenging。

控制输入 $\\mathbf{u}$ 为指令速度与转向角：

$$\\mathbf{u} = \\begin{bmatrix}v & \\alpha\\end{bmatrix}^\\mathsf{T}$$

""",

135: """### 设计系统模型（Design the System Model）

非线性运动模型加白噪声：

$$\\bar x = x + f(x, u) + \\mathcal{N}(0, Q)$$

用上文机器人运动模型，可写：

""",

137: "用该函数实现状态转移 `f(x)`。\n",

138: "UKF 设计使 $\\Delta t$ 小。机器人慢速时预测 reasonably 准。$\\Delta t$ 大或动力学很非线性会失败，须用 Runge Kutta 等数值积分。**卡尔曼滤波数学（Kalman Filter Math）** 章简述数值积分。\n",

139: """### 设计测量模型（Design the Measurement Model）

传感器对多个已知地标给含噪方位与距离。测量模型须将状态 $\\begin{bmatrix}x & y&\\theta\\end{bmatrix}^\\mathsf{T}$ 转为到地标的距离与方位。地标位置 $p$，距离

$$r = \\sqrt{(p_x - x)^2 + (p_y - y)^2}$$

传感器给出相对机器人朝向的方位，须减去机器人朝向：

$$\\phi = \\tan^{-1}(\\frac{p_y - y}{p_x - x}) - \\theta$$

测量函数

$$\\begin{aligned}
\\mathbf{z}& = h(\\mathbf x, \\mathbf P) &+ \\mathcal{N}(0, R)\\\\
&= \\begin{bmatrix}
\\sqrt{(p_x - x)^2 + (p_y - y)^2} \\\\
\\tan^{-1}(\\frac{p_y - y}{p_x - x}) - \\theta 
\\end{bmatrix} &+ \\mathcal{N}(0, R)
\\end{aligned}$$

*实现* 节将讨论的困难尚未实现。

""",

140: """### 设计测量噪声（Design Measurement Noise）

距离与方位测量噪声独立合理，故

$$\\mathbf R=\\begin{bmatrix}\\sigma_{range}^2 & 0 \\\\ 0 & \\sigma_{bearing}^2\\end{bmatrix}$$

""",

141: "### 实现（Implementation）\n",

142: """编码前还有问题：残差 $y = z - h(x)$。设 $z$ 方位 $1^\\circ$，$h(x)$ 为 $359^\\circ$，相减得 $-358^\\circ$，正确角差 $2^\\circ$。须写代码正确算方位残差。

""",

145: """状态向量方位在索引 2，测量在索引 1，须分别写函数。机器人机动时可见地标数变，须处理可变测量数。测量残差函数接收每地标一个测量的数组。

""",

147: """实现测量模型。方程
$$h(\\mathbf x, \\mathbf P)
= \\begin{bmatrix}
\\sqrt{(p_x - x)^2 + (p_y - y)^2} \\\\
\\tan^{-1}(\\frac{p_y - y}{p_x - x}) - \\theta 
\\end{bmatrix}$$

$\\tan^{-1}(\\frac{p_y - y}{p_x - x}) - \\theta$ 可能超出 $[-\\pi, \\pi)$，应归一化角度。

函数接收地标数组，输出 `[dist_to_1, bearing_to_1, dist_to_2, bearing_to_2, ...]`。

""",

149: """困难未结束。无迹变换对状态与测量向量求平均，均含方位。角度集平均无唯一方式。359$^\\circ$ 与 3$^\\circ$ 平均？直觉 1$^\\circ$， naive $\\frac{1}{n}\\sum x$ 得 181$^\\circ$。

常见做法：对 sin、cos 之和取 arctan。

$$\\bar{\\theta} = atan2\\left(\\frac{\\sum_{i=1}^n \\sin\\theta_i}{n}, \\frac{\\sum_{i=1}^n \\cos\\theta_i}{n}\\right)$$

`UnscentedKalmanFilter.__init__()` 有 `x_mean_fn`（状态均值）与 `z_mean_fn`（测量均值）。实现为：

""",

151: """这些函数利用 NumPy 三角函数对数组运算、`dot` 逐元素乘。NumPy 底层 C/Fortran，`sum(dot(sin(x), w))` 比 Python 循环快得多。

完成后可实现 UKF。设计滤波器时并非一次 sitting 从零写完上述函数。先基本 UKF 固定地标，验证，再填 piece：“若见不同地标？”→ 测量函数接受地标数组。“方位残差？”→ 角度归一化。“角度均值？”→ 查 Wikipedia 实现。勿气馁：能设计多少设计多少，再逐个 solve。

UKF 实现已见过，此处两点新：构造 sigma 点与滤波器时传入残差与均值函数。

```python
points = SigmaPoints(n=3, alpha=.00001, beta=2, kappa=0, 
                     subtract=residual_x)

ukf = UKF(dim_x=3, dim_z=2, fx=fx, hx=Hx, dt=dt, points=points,
         x_mean_fn=state_mean, z_mean_fn=z_mean,
         residual_x=residual_x, residual_z=residual_h)
```

须向 `f(x, dt)`、`h(x)` 传额外数据。想用 `move(x, dt, u, wheelbase)` 作 `f(x, dt)`，`Hx(x, landmarks)` 作 `h(x)`。在 `predict()`、`update()` 用关键字传入：

```python
            ukf.predict(u=u, wheelbase=wheelbase)        
            ukf.update(z, landmarks=landmarks)
```

其余运行仿真绘图。`landmarks` 存地标坐标。仿真机器人每秒更新 10 次，UKF 每秒一次。未用 Runge Kutta 积分，小步长使仿真更准。

""",

154: """其余代码运行仿真绘图。`landmarks` 存地标坐标。仿真机器人每秒 10 次，UKF 每秒一次，原因：未用 Runge Kutta，窄时间步仿真更准；嵌入式处理器有限，卡尔曼滤波只能按需频率运行。

""",

155: """### 转向机器人（Steering the Robot）

上例转向仿真不 realistic，速度与转向角不变，对卡尔曼滤波问题不大。可实现复杂 PID 机器人仿真，这里用 NumPy `linspace` 生成变化转向指令，并加更多地标（机器人走得更远）。

""",

158: "不确定性很快很小。协方差椭圆为 $6\\sigma$，仍难见。可在起点附近只供两个地标引入更多误差；机器人远离地标时误差增大。\n",

160: """## 讨论（Discussion）

本章印象取决于你过去实现多少非线性卡尔曼滤波。若首次接触，$2n+1$ sigma 点与写 $f(x)$、$h(x)$ 或觉 finicky；我因角度 modular 数学花了不少时间。若已实现 EKF（扩展卡尔曼滤波），或许兴奋——UKF 写函数概念 basic，EKF 同题数学难得多；许多问题 EKF 无闭式解，须迭代。

UKF 相对 EKF 优势不仅在实现较易（尚未学 EKF，但 EKF 在单点 linearize，UKF 用 $2n+1$ 样本）。UKF 常比 EKF 准，尤其强非线性。UKF 不保证总优于 EKF，但实践至少相当、通常 much better。

故建议总是先实现 UKF。若滤波 divergence 有真实后果（人身、金钱、电厂），须 sophisticated 分析与实验选最佳滤波——超出本书，应读研究生课程。 

最后，我说 UKF 为 sigma 点滤波 *the* 方式并不真。本书选 Julier 缩放无迹滤波、Van der Merwe 2004 论文参数化。搜 Julier、Van der Merwe、Uhlmann、Wan 可见一族 sigma 点滤波，选点加权各异。选择不止这些——例如 SVD 卡尔曼滤波用奇异值分解（SVD）求分布近似均值协方差。本章是 sigma 点滤波入门，非 definitive 论述。

""",

161: "## 参考文献（References）\n",

162: """- [1] Rudolph Van der Merwe. "Sigma-Point Kalman Filters for Probabilistic Inference in Dynamic State-Space Models" dissertation (2004).

- [2] Simon J. Julier. "The Scaled Unscented Transformation". Proceedings of the American Control Conference 6. IEEE. (2002)

- [3] http://www.esdradar.com/brochures/Compact%20Tracking%2037250X.pdf

- [4] Julier, Simon J.; Uhlmann, Jeffrey "A New Extension of the Kalman  Filter to Nonlinear Systems". Proc. SPIE 3068, Signal Processing, Sensor Fusion, and Target Recognition VI, 182 (July 28, 1997)

- [5] Cholesky decomposition. Wikipedia. http://en.wikipedia.org/wiki/Cholesky_decomposition

""",
}
