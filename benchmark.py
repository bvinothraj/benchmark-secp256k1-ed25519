"""
Benchmark ed25519 vs. secp256k1
"""
import sys
import platform
import time
import csv
from cryptography.hazmat.primitives.asymmetric import ed25519
from ecdsa import SigningKey, SECP256k1

ITERATIONS = 1000
message = b"benchmark test message"


def benchmark_ed25519(results):
    def generate_key_ed25519(results: dict):
        # --- Ed25519 Key Generation ---
        start = time.time()
        for _ in range(ITERATIONS):
            ed25519.Ed25519PrivateKey.generate()
        end = time.time()
        results["Ed25519 KeyGen"] = (end - start) / ITERATIONS * 1e6
        return results

    def sign_message_ed25519(results: dict):
        # Use one generated keypair for signing/verification
        ed_private = ed25519.Ed25519PrivateKey.generate()

        # --- Ed25519 Signing ---
        start = time.time()
        for _ in range(ITERATIONS):
            ed_private.sign(message)
        end = time.time()
        results["Ed25519 Signing"] = (end - start) / ITERATIONS * 1e6
        return results

    def verify_message_ed25519(results: dict):
        # --- Ed25519 Verification ---
        ed_private = ed25519.Ed25519PrivateKey.generate()
        ed_public = ed_private.public_key()
        sig = ed_private.sign(message)
        start = time.time()
        for _ in range(ITERATIONS):
            ed_public.verify(sig, message)
        end = time.time()
        results["Ed25519 Verification"] = (end - start) / ITERATIONS * 1e6
        return results

    results = generate_key_ed25519(results)
    results = sign_message_ed25519(results)
    results = verify_message_ed25519(results)

    return results


def benchmark_secp256k1(results):
    def generate_key_secp256k1(results: dict):
        # --- secp256k1 Key Generation ---
        start = time.time()
        for _ in range(ITERATIONS):
            SigningKey.generate(curve=SECP256k1)
        end = time.time()
        results["secp256k1 KeyGen"] = (end - start) / ITERATIONS * 1e6
        return results

    def sign_message_secp256k1(results: dict):
        # Use one generated keypair for signing/verification
        secp_private = SigningKey.generate(curve=SECP256k1)

        # --- secp256k1 Signing ---
        start = time.time()
        for _ in range(ITERATIONS):
            secp_private.sign(message)
        end = time.time()
        results["secp256k1 Signing"] = (end - start) / ITERATIONS * 1e6
        return results

    def verify_message_secp256k1(results: dict):
        # --- secp256k1 Verification ---
        secp_private = SigningKey.generate(curve=SECP256k1)
        secp_public = secp_private.verifying_key

        sig = secp_private.sign(message)
        start = time.time()
        for _ in range(ITERATIONS):
            secp_public.verify(sig, message)
        end = time.time()
        results["secp256k1 Verification"] = (end - start) / ITERATIONS * 1e6
        return results

    results = generate_key_secp256k1(results)
    results = sign_message_secp256k1(results)
    results = verify_message_secp256k1(results)
    return results


def print_benchmark_results(results: dict):
    # Group by operation type
    ops = ['KeyGen', 'Signing', 'Verification']

    print(f"{'Operation':<12} {'Ed25519':<12} {'secp256k1':<12} {'Ratio':<8}")
    print("-" * 48)

    for op in ops:
        ed_key = f"Ed25519 {op}"
        secp_key = f"secp256k1 {op}"
        ed_val = results[ed_key]
        secp_val = results[secp_key]
        ratio = secp_val / ed_val
        print(f"{op:<12} {ed_val:<12.2f} {secp_val:<12.2f} {ratio:.1f}x")


def save_csv_benchmark_results(results: dict, filename='benchmark_results.csv'):
    # Save results to CSV
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Operation", "Time (µs/op)"])
        for k, v in results.items():
            writer.writerow([k, v])

    print(f"Benchmark results saved to '{filename}'")


def capture_environment(filename='env_info.csv'):
    """Capture environment information, print to console, and save to CSV."""

    def collect_env_info():
        """Collect system information and return as a list of [key, value] pairs."""
        env_info = [
            ['Python_version', sys.version.replace('\n', ' ').strip()],
            ['Platform', platform.platform()],
            ['Processor', platform.processor()],
            ['Architecture', ', '.join(platform.architecture())],
            ['CPU_count', str(platform.os.cpu_count())]
        ]
        return env_info

    def print_info_to_console(info_list):
        """Print environment information to console from a list of [key, value] pairs."""
        print('\n======ENVIRONMENT======')
        for key, value in info_list:
            print(f'{key}: {value}')

    def write_info_to_csv(info_list, filename):
        """Write environment information to CSV file from a list of [key, value] pairs."""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(['Property', 'Value'])

            # Write data
            writer.writerows(info_list)

        print(f"Environment information saved to '{filename}'")

    # Execute the workflow
    env_info = collect_env_info()
    print_info_to_console(env_info)
    write_info_to_csv(env_info, filename)


def main():
    results = {}
    results = benchmark_ed25519(results)
    results = benchmark_secp256k1(results)
    print_benchmark_results(results)
    save_csv_benchmark_results(results)
    capture_environment()


if __name__ == "__main__":
    main()
