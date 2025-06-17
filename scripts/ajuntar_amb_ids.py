import pandas as pd

# Paths to the parquet files
file_out = "out.parquet"
file_umap = "PCA.parquet"

# Read only the 'category' column from out.parquet
df_category = pd.read_parquet(file_out, columns=["category"])

# Read the UMAP embedding dataframe
df_umap = pd.read_parquet(file_umap)

# Join the dataframes column-wise
df_joined = pd.concat([df_umap, df_category], axis=1)


# Print the result
print(df_joined)

df_joined.to_parquet(file_umap, index=False)