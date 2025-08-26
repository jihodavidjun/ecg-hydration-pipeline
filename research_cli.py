#!/usr/bin/env python
import argparse
from research_pipeline import (
    load_subject_folder, stitch_if_multiple, last_minutes, plot_time, FS_EXG
)
import matplotlib.pyplot as plt

def main():
    ap = argparse.ArgumentParser(description="Research data loader (ECG hydration study)")
    ap.add_argument("--data-root", type=str, default="Data", help="Root folder containing Subject*/")
    ap.add_argument("--subject", type=int, required=True, help="Subject ID (e.g., 10,11,12,13)")
    ap.add_argument("--last-min", type=float, default=5.0, help="Plot last N minutes")
    args = ap.parse_args()

    files = load_subject_folder(args.data_root, args.subject)
    t, x = stitch_if_multiple(files, FS_EXG)
    t5, x5 = last_minutes(t, x, minutes=args.last_min, fs=FS_EXG)

    plot_time(t5, x5, title=f"Subject {args.subject} — last {args.last_min} min (Fs={FS_EXG} Hz)")
    print(f"Loaded Subject {args.subject}: {len(x)/FS_EXG:.1f} s total, showing {args.last_min} min.")
    plt.show()

if __name__ == "__main__":
    main()
