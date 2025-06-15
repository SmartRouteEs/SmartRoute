import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_collection.feature_pipeline import process_traces_to_dual_output
from debug.data_check import check_data_integrity

if __name__ == "__main__":
    raw_df, enriched_df = process_traces_to_dual_output("data/processed/traces")

    print("\n✅ Données brutes :")
    check_data_integrity(raw_df)

    print("\n✅ Données enrichies (features) :")
    check_data_integrity(enriched_df)

    raw_df.to_csv("outputs/segments_processed.csv", index=False)
    enriched_df.to_parquet("outputs/features_dataset.parquet", index=False)
