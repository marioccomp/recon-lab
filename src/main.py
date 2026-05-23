import json 
from pathlib import Path

from reconciliation import load_data, reconcile, build_summary, save_outputs

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INTERNAL_FILE = PROJECT_ROOT / "data" / "samples" /"internal_sample.csv"
EXTERNAL_FILE = PROJECT_ROOT / "data" / "samples" / "external_sample.csv"
OUTPUT_DIR = PROJECT_ROOT / "output"

def main():
    internal_df, external_df = load_data(INTERNAL_FILE, EXTERNAL_FILE)

    result_df = reconcile(internal_df, external_df)

    summary = build_summary(internal_df, external_df, result_df)

    save_outputs(result_df, summary, OUTPUT_DIR)

    print("Reconciliação finalizada.")
    print(f"Salvei os arquivos em: {OUTPUT_DIR}")
    print(json.dumps(summary, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()
