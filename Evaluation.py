import os
import numpy as np
import pandas as pd

K_VALUES = [1, 3, 5]
METRIC_BASES = ["Precision", "Recall", "MAP", "NDCG"]
NUM_REPEATS = 5

# =========================
# 1. defining evaluation metrics
# =========================
def precision_at_k(pred_genes, true_genes, k):
    hits = [gene in true_genes for gene in pred_genes[:k]]
    return np.sum(hits) / k

def recall_at_k(pred_genes, true_genes, k):
    hits = [gene in true_genes for gene in pred_genes[:k]]
    return np.sum(hits) / len(true_genes) if true_genes else 0

def map_at_k(pred_genes, true_genes, k):
    ap_sum = 0
    correct_predictions = 0
    for idx, gene in enumerate(pred_genes[:k], start=1):
        if gene in true_genes:
            correct_predictions += 1
            ap_sum += correct_predictions / idx
    return ap_sum / len(true_genes) if true_genes else 0

def ndcg_at_k(pred_genes, true_genes, k):
    dcg = 0
    idcg = 0
    for idx, gene in enumerate(pred_genes[:k]):
        if gene in true_genes:
            dcg += 1 / np.log2(idx + 2)  # idx+2 for DCG correction
    for idx in range(min(len(true_genes), k)):
        idcg += 1 / np.log2(idx + 2)
    return dcg / idcg if idcg > 0 else 0

# =========================
# 2. computing metrics for each snp (Top-1 / Top-3 / Top-5)
# =========================
def calculate_metrics_multi_k(prediction, reference, k_values=None):
    if k_values is None:
        k_values = K_VALUES
    results = []
    ref_dict = reference.groupby('snp')['gene'].apply(set).to_dict()
    max_k = max(k_values)

    for region, group in prediction.groupby('region'):
        pred_genes = group.sort_values('rank')['gene'].tolist()
        true_genes = ref_dict.get(region, set())
        if not true_genes:
            continue

        row = {'region': region}
        for k in k_values:
            row[f'Precision@{k}'] = precision_at_k(pred_genes, true_genes, k)
            row[f'Recall@{k}'] = recall_at_k(pred_genes, true_genes, k)
            row[f'MAP@{k}'] = map_at_k(pred_genes, true_genes, k)
            row[f'NDCG@{k}'] = ndcg_at_k(pred_genes, true_genes, k)
        results.append(row)

    return results

# =========================
# 3. main function
# =========================
if __name__ == '__main__':
    current_file_path = os.path.dirname(os.path.abspath(__file__))
    reference = pd.read_csv(os.path.join(current_file_path, 'STAD', 'STAD_l2g.txt'), sep='\t')
    # support both old (rsId/gene_symbol) and new (snp/gene) headers
    colmap = {}
    if 'rsId' in reference.columns and 'gene_symbol' in reference.columns:
        colmap = {'rsId': 'snp', 'gene_symbol': 'gene'}
    elif 'snp' in reference.columns and 'gene' in reference.columns:
        colmap = {}
    else:
        raise KeyError(f'Unexpected STAD_l2g columns: {list(reference.columns)}')
    if colmap:
        reference = reference.rename(columns=colmap)
    reference = reference[['snp', 'gene']]

    test_snp = pd.read_csv(os.path.join(current_file_path, 'STAD', 'snp_list_STAD.txt'), sep='\t')
    test_set = set(test_snp['SNP'])

    # Aggregate over five random repeats (mean ± std)
    repeat_vals = {f'{base}@{k}': [] for base in METRIC_BASES for k in K_VALUES}

    for repeat in range(NUM_REPEATS):
        filename = os.path.join(current_file_path, 'Result', f'prediction_{repeat}_STAD.txt')
        if not os.path.exists(filename):
            raise FileNotFoundError(f'Missing {filename}. Run McV2G.py first.')
        prediction = pd.read_csv(
            filename, sep=r'\s+', header=None, engine='python',
            names=['region', 'gene', 'post_prob', 'rank'],
        )
        prediction = prediction[prediction['region'].isin(test_set)]

        metrics = calculate_metrics_multi_k(prediction, reference, k_values=K_VALUES)
        metrics_df = pd.DataFrame(metrics)

        for col in repeat_vals:
            repeat_vals[col].append(metrics_df[col].mean())

    # output results: Top-1 / Top-3 / Top-5 over five repeats
    for k in K_VALUES:
        print(f'=== Top-{k} ===')
        for base in METRIC_BASES:
            vals = repeat_vals[f'{base}@{k}']
            print(f'{base}: {np.mean(vals):.3f} ± {np.std(vals):.3f}')
        print()
