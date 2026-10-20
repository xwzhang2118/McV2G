# McV2G

## 1. Project overview
McV2G is a graph neural network framework for predicting associations between single nucleotide polymorphisms (SNPs) and genes. It builds and trains a dual-graph model that leverages a real interaction graph and a feature-based (sequence/similarity) graph, and uses contrastive learning together with link prediction. The implementation uses PyTorch and PyTorch Geometric (PyG).

## 2. Repository structure (key files)
- `McV2G.py`: Main script containing model definitions and training loop with cross-validation (includes model classes, training, and evaluation logic).
- `Evaluation.py`: Script to compute ranking-based evaluation metrics (Precision@K, Recall@K, MAP@K, NDCG@K) from prediction outputs in `Result/`.
- `demo_data/`: Example dataset — a small demo pack with the files required by the scripts. Use it to verify installation and workflow; swap in your own data for actual analyses:
    - `adj_real_2.txt`: Real adjacency matrix (upper-triangular or symmetric format).
    - `data_2.pth`: PyTorch-saved graph object (e.g., `HeteroData`) used for the real graph.
    - `feature_str.txt`: Node features used for building a k-NN similarity graph (e.g., sequence features).
    - `node_feature.txt`: Node feature vectors for all nodes (SNPs first, then genes).
    - `snp_list_demo_data.txt`: List of test SNPs.
    - `snp_list.txt`: Full list of SNPs (used for indexing/splitting).
    - `demo_data_l2g.txt`: Reference SNP-to-gene associations (used for evaluation).
    - `test_edge_index.txt` / `test_edge_name.txt`: Index and name files for test edges.
- `Result/`: Output directory for prediction files. Example files: `prediction_0_demo_data.txt` ... `prediction_4_demo_data.txt` (one per repeat; produced from the sample demo run).

## Method (Overview)
The following summarizes the main idea of McV2G and points to a schematic (Figure 1) illustrating the framework.

To address limitations in current studies, we propose McV2G, a multi-channel graph convolutional network (McGCN) framework for gene prioritization at GWAS variants. Specifically, McV2G is designed with three key points:

- (i) It explicitly models the synergistic effects of multiple loci rather than considering the impact of each SNP in isolation.
- (ii) It systematically integrates diverse types of genetic relationships by constructing an SNP–gene heterogeneous network and a prior sequence-similarity network, thereby capturing regulatory mechanisms at different levels.
- (iii) It introduces a McGCN to capture key genetic information from the SNP–gene heterogeneous network and the sequence-similarity prior network. The shared channel employs parameter sharing and a contrastive loss to achieve cross-network feature alignment. Meanwhile, the personalized channel incorporates a multi-level attention mechanism to capture key genetic information. Based on the above techniques, McV2G empowers the discovery of complex genetic relationships.

![Figure 1 — McV2G schematic](Result/fig1.png)

## 3. Requirements & dependencies
Recommended Python: 3.8+.

Primary dependencies (high level):
- torch (PyTorch)
- torch-geometric (PyG) and its supplementary packages (`torch-scatter`, `torch-sparse`, `torch-cluster`, `torch-spline-conv`, etc.)
- scikit-learn
- pandas
- numpy

Note: PyTorch Geometric must be installed for a PyTorch/CUDA combination that matches your environment—use the official PyG installation instructions to pick correct wheels.

Example installation commands (adjust for your CUDA / PyTorch version):

```bash
# Create and activate a virtual environment
python -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
# Base Python packages
pip install numpy pandas scikit-learn
# Install PyTorch (replace with the proper CUDA version if needed)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
# Install PyG (follow the PyG docs for the correct wheel for your setup)
pip install torch-geometric
```

If `pip install torch-geometric` fails, follow the platform-specific installation instructions at https://pytorch-geometric.readthedocs.io/.

## 4. Quick start: training
The command below uses the **bundled example dataset** (`demo_data/`) so you can try the pipeline immediately. For real experiments, point `--data_dir` (and related inputs) to your own data in the same file layout.

Run training from the repository root (where `McV2G.py` and `demo_data/` are located):

```bash
python McV2G.py --dataset demo_data --data_dir demo_data --output_dir Result --epochs 200 --in_dim 128 --hidden_dim 256 --out_dim 128 --dropout 0.4 --num_heads 4 --num_layers 4 --learning_rate 0.007 --temperature 0.1 --patience 10 --t 0.1 --k 3
```

Notes on arguments:
- `--dataset`: name label for output files (default: `demo_data`; sample-data label only).
- `--data_dir`: dataset folder (default: `./demo_data`, the example pack).
- Other flags correspond to `args_parser()` inside `McV2G.py` and can be tuned as needed.

After training, the script will produce prediction files in `Result/` (for example `prediction_0_demo_data.txt`, etc.). These files are used by the evaluation script.

## 5. Evaluation
After predictions are produced in `Result/` (from the example or your own data), run:

```bash
python Evaluation.py
```

`Evaluation.py` will read `Result/prediction_{0..4}_demo_data.txt` files (the default naming for the sample demo) and compute the mean and standard deviation of Precision/Recall/MAP/NDCG at Top-1/3/5 across five repeats.

## 6. File and format conventions
- Prediction files (`Result/prediction_*.txt`) are space-separated with columns: `region gene post_prob rank`. `Evaluation.py` treats the first column as the region/SNP identifier.
- `demo_data/demo_data_l2g.txt` should contain columns `rsId` and `gene_symbol` (or `snp`/`gene`); `Evaluation.py` renames these as needed.

## 7. Troubleshooting
- CUDA not found: install a PyTorch build that includes CUDA matching your system, or run on CPU.
- PyG installation issues: use the PyG installation helper and choose the correct wheel for your PyTorch and CUDA versions.
- File path or parsing issues: `McV2G.py` constructs dataset paths relative to its file location. Ensure `demo_data/` exists and files use expected delimiters/encodings.
- Shape/type mismatch errors: verify `node_feature.txt` and `feature_str.txt` have the expected shapes and that SNP/gene indexing matches assumptions in `McV2G.py`.

## 8. License & contact
No license file is included in this repository. Please confirm licensing with the project owner before reuse or redistribution.
