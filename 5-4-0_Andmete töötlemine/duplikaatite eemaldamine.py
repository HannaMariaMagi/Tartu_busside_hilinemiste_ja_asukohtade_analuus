import os
import pandas as pd

folder_path = '../busside_paevased_andmed'
chunk_size = 100_000

for filename in os.listdir(folder_path):
    if filename.startswith(("2024-03", "2024-02")) and filename.endswith(".csv"):
        file_path = os.path.join(folder_path, filename)
        seen = set()
        output_chunks = []
        original_row_count = 0
        deduplicated_row_count = 0

        for chunk in pd.read_csv(file_path, chunksize=chunk_size, dtype=str):
            original_row_count += len(chunk)
            chunk['__dedup_key__'] = chunk.astype(str).agg('|'.join, axis=1)
            is_new = ~chunk['__dedup_key__'].isin(seen)
            seen.update(chunk.loc[is_new, '__dedup_key__'])
            filtered_chunk = chunk.loc[is_new].drop(columns='__dedup_key__')
            deduplicated_row_count += len(filtered_chunk)
            output_chunks.append(filtered_chunk)

        pd.concat(output_chunks, ignore_index=True).to_csv(file_path, index=False)
        removed = original_row_count - deduplicated_row_count
        print(f"{filename}: removed {removed} duplicate rows (kept {deduplicated_row_count})")
