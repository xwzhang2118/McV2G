# McV2G

## 1. Project overview
McV2G is a graph neural network framework for predicting associations between single nucleotide polymorphisms (SNPs) and genes. It builds and trains a dual-graph model that leverages a real interaction graph and a feature-based (sequence/similarity) graph, and uses contrastive learning together with link prediction. The implementation uses PyTorch and PyTorch Geometric (PyG).

## 2. Repository structure
- `McV2G.py`: Main script (model definitions, training loop with 5-fold cross-validation, and prediction export).
- `environment.yml`: Conda environment export (Python 3.8, PyTorch, PyG, and related packages).
- `demo_data/`: Empty folder for your input data (data files are not tracked in git). You can also use any other directory via `--data_dir`.
- `Result/`: Prediction outputs are written here. Also contains `fig1.png` (method schematic).

## Method (Overview)
To address limitations in current studies, we propose McV2G, a multi-channel graph convolutional network (McGCN) framework for gene prioritization at GWAS variants. Specifically, McV2G is designed with three key points:

- (i) It explicitly models the synergistic effects of multiple loci rather than considering the impact of each SNP in isolation.
- (ii) It systematically integrates diverse types of genetic relationships by constructing an SNP–gene heterogeneous network and a prior sequence-similarity network, thereby capturing regulatory mechanisms at different levels.
- (iii) It introduces a McGCN to capture key genetic information from the SNP–gene heterogeneous network and the sequence-similarity prior network. The shared channel employs parameter sharing and a contrastive loss to achieve cross-network feature alignment. Meanwhile, the personalized channel incorporates a multi-level attention mechanism to capture key genetic information. Based on the above techniques, McV2G empowers the discovery of complex genetic relationships.

![Figure 1 — McV2G schematic](Result/fig1.png)

## 3. Requirements & dependencies
Recommended Python: 3.8+.

Primary packages:
- torch (PyTorch)
- torch-geometric (PyG)
- scikit-learn
- pandas
- numpy

You can recreate a working environment from the provided export:

```bash
conda env create -f environment.yml
conda activate Bio
```

Or install the core stack manually (adjust CUDA / PyTorch versions as needed):

```bash
python -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install numpy pandas scikit-learn
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install torch-geometric
```

If PyG installation fails, follow https://pytorch-geometric.readthedocs.io/.

## 4. Quick start: training
1. Place your data under `demo_data/` (or another folder and pass it with `--data_dir`).
2. Run:

```bash
python McV2G.py --dataset demo_data --data_dir demo_data --output_dir Result --epochs 200 --hidden_dim 256 --out_dim 128 --dropout 0.4 --num_heads 4 --num_layers 4 --learning_rate 0.007 --temperature 0.1 --patience 10 --t 0.1 --k 3
```

Predictions are saved to `Result/` (e.g. `prediction_0_demo_data.txt` … `prediction_4_demo_data.txt`), with columns `region gene pred_score rank`.

## 5. Troubleshooting
- CUDA not found: install a matching PyTorch CUDA build, or run with `--device cpu`.
- PyG install issues: pick wheels that match your PyTorch / CUDA versions.
- Data path issues: make sure `--data_dir` points to the folder where you placed the inputs.

## 6. License & contact
No license file is included in this repository. Please confirm licensing with the project owner before reuse or redistribution.
