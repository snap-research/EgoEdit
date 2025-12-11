<div align="center">

<div style="display: flex; align-items: center; justify-content: center; gap: 20px;">
  <img src="assets/imgs/logo.png" width="120" alt="EgoEdit Logo"/>
  <h1 style="margin: 0;">EgoEdit: Dataset, Real-Time Streaming Model, and Benchmark for Egocentric Video Editing</h1>
</div>

<a href="https://snap-research.github.io/EgoEdit/"><img src="https://img.shields.io/badge/%F0%9F%8F%A0%20Project%20Page-gray.svg"></a>
<a href="https://arxiv.org/abs/2512.06065"><img src="https://img.shields.io/badge/%F0%9F%93%84%20arXiv-2512.06065-B31B1B.svg"></a>

[Runjia Li](https://runjiali-rl.github.io/)<sup>1,3</sup>,
[Moayed Haji Ali](https://moayedha.com/)<sup>1,2</sup>,
[Ashkan Mirzaei](https://ashmrz.github.io/)<sup>1</sup>,
[Chaoyang Wang](https://mightychaos.github.io/)<sup>1</sup>,
[Arpit Sahni](https://scholar.google.com/citations?user=IK3yBTYAAAAJ&hl=en)<sup>1</sup>,
[Ivan Skorokhodov](https://skor.sh/)<sup>1</sup>,
[Aliaksandr Siarohin](https://aliaksandrsiarohin.github.io/aliaksandr-siarohin-website/)<sup>1</sup>,
[Tomas Jakab](https://www.robots.ox.ac.uk/~tomj/)<sup>3</sup>,
[Junlin Han](https://junlinhan.github.io/)<sup>3</sup>,
[Sergey Tulyakov](https://stulyakov.com/)<sup>1</sup>,
[Philip Torr](https://www.robots.ox.ac.uk/~phst/)<sup>3</sup>,
[Willi Menapace](https://www.willimenapace.com/)<sup>1</sup>
<br>
<br>
<sup>1</sup>Snap Research, <sup>2</sup>Rice University, <sup>3</sup>University of Oxford

<img src="assets/imgs/teaser.gif" alt="EgoEdit Teaser" style="width: 100%; max-width: 900px; border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.5);"/>

</div>

## 📅 Release Schedule

| Status | Timeline | Milestone |
|:------:|:--------:|:----------|
| ✅ | **December 2025** | Final review completed |
| 🔄 | **TBD (soon) ** | Initial release of **EgoEditData** and **EgoEditBench** |




## 📖 Overview

We propose a framework for real-time egocentric video editing. Our system is composed of three main components:

- **EgoEditData**: A manually curated dataset of 100k video editing pairs focusing on the egocentric case. It features object substitution and removal under challenging hand occlusions, interactions, and large egomotion.
- **EgoEdit**: The first real-time autoregressive model for egocentric video editing. It runs in real time on a single H100 with **855ms first-frame latency**, enabling live augmented reality (AR) interactions.
- **EgoEditBench**: A comprehensive benchmark for the evaluation of egocentric video editing systems.

## ✨ Features

- **Real-Time Performance**: Designed to run efficiently on modern hardware (single H100) with low latency.
- **Challenging Scenarios**: Handles complex egocentric video challenges such as hand occlusions, object interactions, and significant camera motion.
- **High Fidelity**: Surpasses state of the art models like Editverse in editing faithfulness (via VLM evaluation) and aligns better with human judgment.


## :books: Citing

If you find this repository useful, please consider giving a star :star: and citation.

```
@article{li2025egoedit,
  title={EgoEdit: Dataset, Real-Time Streaming Model, and Benchmark for Egocentric Video Editing},
  author={Li, Runjia and Haji-Ali, Moayed and Mirzaei, Ashkan and Wang, Chaoyang and Sahni, Arpit and Skorokhodov, Ivan and Siarohin, Aliaksandr and Jakab, Tomas and Han, Junlin and Tulyakov, Sergey and others},
  journal={arXiv preprint arXiv:2512.06065},
  year={2025}
}
```



---
