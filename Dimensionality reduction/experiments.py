import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE, MDS
import umap
from pyDRMetrics.pyDRMetrics import DRMetrics
import itertools

# ---------- Load and combine embeddings ----------
df_summary = pd.read_parquet("embeddings.summary.parquet")
df_title = pd.read_parquet("embeddings.title.parquet")

summary_embeddings = np.vstack(df_summary['0'].values)
title_embeddings = np.vstack(df_title['0'].values)

X = 0.9 * summary_embeddings + 0.1 * title_embeddings

results = []

def print_result(method, params, drm):
    result = {
        "Method": method,
        "Params": params,
        "Trustworthiness": drm.AUC_T,
        "Continuity": drm.AUC_C,
        "Qlocal": drm.Qlocal,
        "Qglobal": drm.Qglobal,
        "QNN AUC": drm.AUC,
        "LCMC (peak)": max(drm.LCMC)
    }
    results.append(result)
    
    print(
        f"{method} | {params} → "
        f"Trust={result['Trustworthiness']:.4f}, "
        f"Cont={result['Continuity']:.4f}, "
        f"Qlocal={result['Qlocal']:.4f}, "
        f"Qglobal={result['Qglobal']:.4f}, "
        f"AUC={result['QNN AUC']:.4f}, "
    )



# ---------- PCA ----------
print("Running PCA...")
pca = PCA(n_components=2)
Z_pca = pca.fit_transform(X)
Xr_pca = pca.inverse_transform(Z_pca)
drm = DRMetrics(X, Z_pca, Xr_pca)
print_result("PCA", "", drm)


# ---------- t-SNE ----------
perplexities = [15, 30, 50, 100, 200, 300, 400]
learning_rates = [250, 500, 750, 1000]
n_iters = [1000, 2000, 3000]
print("\nRunning t-SNE combinations...")

# Create all parameter combinations
combinations = itertools.product(perplexities, learning_rates, n_iters)

for p, lr, n_iter in combinations:
    print(f"t-SNE → perplexity={p}, learning_rate={lr}, n_iter={n_iter}")
    tsne = TSNE(
        n_components=2,
        perplexity=p,
        learning_rate=lr,
        max_iter=n_iter,
        init='pca',
        method='barnes_hut',
        random_state=42
    )
    Z = tsne.fit_transform(X)
    drm = DRMetrics(X, Z, None)
    print_result("t-SNE", f"perp={p}, lr={lr}, iter={n_iter}", drm)

# ---------- MDS ----------
max_iters = [500, 1000, 1250, 1500, 1750, 2000]

print("\nRunning MDS combinations...")
for mi in max_iters:
    print(f"  MDS → max_iter={mi}")
    mds = MDS(
        n_components=2,
        max_iter=mi,
        random_state=42,
    )
    Z = mds.fit_transform(X)
    drm = DRMetrics(X, Z, None)
    print_result("MDS", f"n_init={ni}, max_iter={mi}", drm)


# # ---------- UMAP ----------
n_neighbors = [15, 30, 50, 100, 200, 300, 400]
min_dists = [0, 0.2, 0.4, 0.6, 0.8, 1]
metrics = ['cosine', 'euclidean']

for i, (nn, md, metric) in enumerate(itertools.product(n_neighbors, min_dists, metrics)):
    
    print(f"  UMAP → n_neighbors={nn}, min_dist={md}, metric={metric}")
    reducer = umap.UMAP(
        n_components=2,
        n_neighbors=nn,
        min_dist=md,
        metric=metric,
        random_state=42
    )
    Z = reducer.fit_transform(X)
    drm = DRMetrics(X, Z, None)
    print_result("UMAP", f"nn={nn}, min_dist={md}, metric={metric}", drm)


# ---------- t-SNE (opt-SNE style) ----------
print("\nRunning opt-SNE-style t-SNE...")

alpha = 12  # exaggeration factor
N = X.shape[0]
eta = N / alpha

opt_tsne_params = {
    "n_components": 2,
    "perplexity": 30,       # fixed as a balance (can be looped if needed)
    "learning_rate": eta,   # adaptive
    "n_iter": 750,          # reduced, early stopping simulation
    "init": 'pca',
    "method": 'barnes_hut',
    "early_exaggeration": alpha,
    "n_iter_without_progress": 100,  # basic early stopping
    "random_state": 42,
    "verbose": 1
}

tsne = TSNE(**opt_tsne_params)
Z = tsne.fit_transform(X)
drm = DRMetrics(X, Z, None)
print_result("opt-SNE", f"perp=50, eta={eta:.0f}, exaggeration={alpha}, iter=750", drm)



# ---------- Final Sorted Results ----------
df_results = pd.DataFrame(results)
df_results = df_results.sort_values(by="Qglobal", ascending=False)
pd.set_option("display.max_rows", None)
print("\n=== Sorted Dimensionality Reduction Metrics ===")
print(df_results[["Method", "Params", "Qglobal", "QNN AUC"]].round(4))
