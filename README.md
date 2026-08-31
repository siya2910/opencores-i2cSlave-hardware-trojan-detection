# OpenCores i2cSlave Hardware Trojan Detection Using LLM

This repository contains the OpenCores `i2cSlave` case study developed for a Hardware Trojan Detection framework combining structural RTL analysis, semantic feature extraction, and Large Language Model (LLM)-based reasoning.

## Objective

The objective of this experiment is to evaluate whether a Hardware Trojan inserted into an open-source RTL design can be identified using a combination of:

1. Structural circuit analysis
2. RTL semantic feature extraction
3. LLM-based security reasoning
4. Hybrid risk scoring

The OpenCores `i2cSlave` design is used as the reference hardware design.

---

## Project Structure

```text
i2cSlave/
│
├── clean/
│   ├── i2cSlave.v
│   ├── i2cSlaveTop.v
│   ├── i2cSlave_define.v
│   ├── registerInterface.v
│   ├── serialInterface.v
│   └── timescale.v
│
├── trojan/
│   ├── i2cSlave.v
│   ├── i2cSlaveTop.v
│   ├── i2cSlave_define.v
│   ├── registerInterface.v
│   ├── serialInterface.v
│   ├── timescale.v
│   ├── i2cSlave_trojan.json
│   └── i2cSlave_trojan_synth.v
│
├── results/
│   ├── synthesized netlists
│   ├── Yosys JSON representations
│   ├── structural feature results
│   ├── semantic feature results
│   └── LLM reasoning results
│
├── structural_analysis.py
├── semantic_features.py
├── structural_comparison.py
├── llm_reasoning.py
└── final_score.py
