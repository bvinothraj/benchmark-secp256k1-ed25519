import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_and_validate_data(csv_path: str) -> pd.DataFrame:
    """Load CSV data and validate required columns and operations exist."""
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded benchmark data with {len(df)} rows")

        required_columns = ["Operation", "Time (µs/op)"]
        missing_columns = [
            col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        required_operations = [
            "Ed25519 KeyGen", "Ed25519 Signing", "Ed25519 Verification",
            "secp256k1 KeyGen", "secp256k1 Signing", "secp256k1 Verification"
        ]
        existing_operations = set(df["Operation"].values)
        missing_operations = [
            op for op in required_operations if op not in existing_operations]
        if missing_operations:
            raise ValueError(
                f"Missing required operations: {missing_operations}")

        return df

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Benchmark results file not found: {csv_path}")
    except pd.errors.EmptyDataError:
        raise ValueError("CSV file is empty")


def load_environment_details(csv_path: str) -> dict:
    """Load execution environment details into a dictionary."""
    try:
        df = pd.read_csv(csv_path)
        if not {"Property", "Value"}.issubset(df.columns):
            raise ValueError(
                "Environment details CSV must have 'Property' and 'Value' columns")

        details = dict(zip(df["Property"], df["Value"]))
        logger.info(f"Loaded environment details: {details.keys()}")
        return details

    except FileNotFoundError:
        logger.warning(f"Environment details file not found: {csv_path}")
        return {}
    except Exception as e:
        logger.warning(f"Could not load environment details: {e}")
        return {}


def extract_benchmark_times(df: pd.DataFrame) -> tuple[list[float], list[float]]:
    """Extract benchmark times for Ed25519 and secp256k1 operations."""
    operations = {
        'ed25519': ['Ed25519 KeyGen', 'Ed25519 Signing', 'Ed25519 Verification'],
        'secp256k1': ['secp256k1 KeyGen', 'secp256k1 Signing', 'secp256k1 Verification']
    }

    def get_times_for_curve(ops: list[str]) -> list[float]:
        times = []
        for op in ops:
            matching_rows = df.loc[df["Operation"] == op, "Time (µs/op)"]
            if matching_rows.empty:
                raise ValueError(f"No data found for operation: {op}")
            times.append(float(matching_rows.iloc[0]))
        return times

    return get_times_for_curve(operations['ed25519']), get_times_for_curve(operations['secp256k1'])


def create_benchmark_chart(ed_times: list[float], secp_times: list[float],
                           env_details: dict, output_path: str = "benchmark_comparison.png") -> None:
    """Create and save the benchmark comparison chart with environment details."""

    categories = ["Key Generation", "Signing", "Verification"]
    x = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 7))

    bars1 = ax.bar(x - width/2, ed_times, width,
                   label="Ed25519", color="#4CAF50", alpha=0.8)
    bars2 = ax.bar(x + width/2, secp_times, width,
                   label="secp256k1", color="#FF7043", alpha=0.8)

    ax.set_ylabel("Time (µs per operation)", fontsize=12)
    ax.set_title("Ed25519 vs secp256k1",
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            y_offset = max(height * 0.02, 5)
            ax.text(bar.get_x() + bar.get_width()/2, height + y_offset,
                    f"{height:.1f}", ha="center", va="bottom",
                    fontsize=9, fontweight='bold')

    add_value_labels(bars1)
    add_value_labels(bars2)

    y_max = max(max(ed_times), max(secp_times))
    ax.set_ylim(0, y_max * 1.15)

    # Add environment details below the plot
    if env_details:
        details_text = "\n".join([f"{k}: {v}" for k, v in env_details.items()])
        # Reserve space at the bottom
        plt.subplots_adjust(bottom=0.25)
        # Place text anchored below the axes
        fig.text(0.01, 0.02, details_text, ha="left", va="bottom",
                 fontsize=8, family="monospace")

    plt.savefig(output_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    logger.info(f"Chart saved to: {output_path}")
    plt.show()


def main():
    csv_file = "benchmark_results.csv"
    env_file = "env_info.csv"
    output_file = "benchmark_comparison.png"

    try:
        df = load_and_validate_data(csv_file)
        env_details = load_environment_details(env_file)
        ed_times, secp_times = extract_benchmark_times(df)
        create_benchmark_chart(ed_times, secp_times, env_details, output_file)

    except (FileNotFoundError, ValueError, pd.errors.EmptyDataError) as e:
        logger.error(f"Error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

    return True


if __name__ == "__main__":
    if not main():
        exit(1)
