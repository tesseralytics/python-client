"""List every dataset your plan can see, with coverage.

Run:
    export TESSERA_API_KEY="sk_..."
    python examples/01_list_datasets.py
"""

from __future__ import annotations

import tessera


def main() -> None:
    with tessera.TesseraClient() as client:
        catalog = client.datasets()
        print(f"catalog generated at {catalog.generated_at}\n")
        for ds in catalog.datasets:
            span = f"{ds.months.earliest} → {ds.months.latest}"
            print(f"{ds.name:<22} {ds.partition_count:>4} partitions  {span}")
            print(f"  coins: {', '.join(ds.coins)}")


if __name__ == "__main__":
    main()
