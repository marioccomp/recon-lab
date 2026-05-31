import json 
from pathlib import Path
from datetime import datetime

from reconciliation import load_data, reconcile, build_summary, save_outputs

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INTERNAL_FILE = PROJECT_ROOT / "data" / "samples" /"internal_sample.csv"
EXTERNAL_FILE = PROJECT_ROOT / "data" / "samples" / "external_sample.csv"
OUTPUT_DIR = PROJECT_ROOT / "output"

def create_run_id():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def main():
    run_id = create_run_id()
    started_at = datetime.now()

    internal_df, external_df = load_data(INTERNAL_FILE, EXTERNAL_FILE)

    result_df = reconcile(internal_df, external_df)

    summary = build_summary(internal_df, external_df, result_df)

    finished_at = datetime.now()

    run = {
        "run_id": run_id,
        "status": "COMPLETED",
        "started_at": started_at.isoformat(timespec="seconds"),
        "finished_at": finished_at.isoformat(timespec="seconds"),
        "internal_file": str(INTERNAL_FILE),
        "external_file": str(EXTERNAL_FILE),
    }

    summary = {
        "run": run,
        **summary
    }

    save_outputs(result_df, summary, OUTPUT_DIR)

    print("Reconciliação finalizada.")
    print(f"Run ID: {run_id}")
    print(f"Salvei os arquivos em: {OUTPUT_DIR}")
    print(json.dumps(summary, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()
