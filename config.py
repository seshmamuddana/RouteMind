from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CSV_FILES = {
    "processed": ROOT / "processed_dataset.csv",
    "optimizer": ROOT / "improved_optimizer_results.csv",
    "nearest_neighbor": ROOT / "nearest_neighbor_results.csv",
    "constrained": ROOT / "constrained_optimizer_results.csv",
    "features": ROOT / "route_features.csv",
    "disruptions": ROOT / "route_disruptions.csv",
    "rerouting": ROOT / "realtime_rerouting_results.csv",
    "ai_decisions": ROOT / "ml_ai_route_decisions.csv",
    "ai_decisions_rules": ROOT / "ai_route_decisions.csv",
}
