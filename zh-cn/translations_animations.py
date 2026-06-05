#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply markdown translations for animations/*.ipynb."""

from __future__ import annotations

from nb_translate_utils import apply_markdown_translations, load_notebook, save_notebook

INTRO_DISCRETE = (
    "本 notebook 用于为「离散贝叶斯滤波（Discrete Bayes Filter）」章节生成动画。"
    "它并非本书面向阅读的正式内容，但你当然可以自由查看源代码并进行修改。"
    "若你想自行运行动画，请参阅书中的 examples 子目录，其中包含多个 Python 脚本，"
    "可在 IDE 或命令行中运行与修改。"
    "本模块将动画保存为 GIF 文件，过程较慢且交互性不强。\n"
    "\n"
    "在 Windows 上需安装 ffmpeg：\n"
    "\n"
    "    $ conda install -c conda-forge ffmpeg\n"
    "    \n"
    "我不清楚在 Linux 或 macOS 上该如何配置。"
)

INTRO_KALMAN = (
    "本 notebook 用于为「一维卡尔曼滤波（One-Dimensional Kalman Filter）」章节生成动画。"
    "它并非本书面向阅读的正式内容，但你当然可以自由查看源代码并进行修改。"
    "若你想自行运行动画，请参阅书中的 examples 子目录，其中包含多个 Python 脚本，"
    "可在 IDE 或命令行中运行与修改。"
    "本模块将动画保存为 GIF 文件，过程较慢且交互性不强。"
)

INTRO_MULTIVARIATE = (
    "本 notebook 用于为「多元卡尔曼滤波（Multivariate Kalman Filter）」章节生成动画。"
    "它并非本书面向阅读的正式内容，但你当然可以自由查看源代码并进行修改。"
    "若你想自行运行动画，请参阅书中的 examples 子目录，其中包含多个 Python 脚本，"
    "可在 IDE 或命令行中运行与修改。"
    "本模块将动画保存为 GIF 文件，过程较慢且交互性不强。"
)

NOTEBOOKS: dict[str, dict[int, str]] = {
    "animations/discrete_bayes_animations.ipynb": {
        0: "# 离散贝叶斯动画（Discrete Bayes Animations）",
        2: INTRO_DISCRETE,
    },
    "animations/Kalman_Filters_Animations.ipynb": {
        2: INTRO_KALMAN,
    },
    "animations/multivariate_animations.ipynb": {
        1: INTRO_MULTIVARIATE,
    },
    # Gaussians_Animations.ipynb and particle_animate.ipynb: img-only markdown, no changes
}


def main() -> None:
    for rel_path, translations in NOTEBOOKS.items():
        nb = load_notebook(__import__("pathlib").Path(rel_path))
        apply_markdown_translations(nb, translations)
        save_notebook(nb, __import__("pathlib").Path(rel_path))
        print(f"已翻译: {rel_path} ({len(translations)} 个 markdown 单元格)")


if __name__ == "__main__":
    main()
