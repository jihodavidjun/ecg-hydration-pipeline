import os, glob
import numpy as np
import pandas as pd
from scipy.signal import iirnotch, filtfilt
import matplotlib.pyplot as plt

FS_EXG = 250  # Hz 
CH_EXG = 1    # 0-based index

# === Bandpass coefficients ('b' & 'a') ===
B_BP = np.array([
    -0.000187830184206340,-0.000205456041853291,-8.64057295452613e-05,0.000234938106149921,
     0.000787322828783533, 0.00153305158366326, 0.00234705727203288, 0.00301420392436277,
     0.00325208908216934,  0.00276166534082112, 0.00130116641212287, -0.00122845080648299,
    -0.00470423015041083, -0.00872851920245046,-0.0126215652355866,-0.0154716371701053,
    -0.0162444264117259,  -0.0139408664255059, -0.00778038794719607, 0.00262217964633411,
     0.0171209674455062,   0.0349757093199774,  0.0548809558645369,  0.0750922598049386,
     0.0936356537755463,   0.108570111841377,   0.118261039548750,   0.121618807015993,
     0.118261039548750,    0.108570111841377,   0.0936356537755463,  0.0750922598049386,
     0.0548809558645369,   0.0349757093199774,  0.0171209674455062,  0.00262217964633411,
    -0.00778038794719607, -0.0139408664255059, -0.0162444264117259, -0.0154716371701053,
    -0.0126215652355866,  -0.00872851920245046,-0.00470423015041083,-0.00122845080648299,
     0.00130116641212287,  0.00276166534082112, 0.00325208908216934, 0.00301420392436277,
     0.00234705727203288,  0.00153305158366326, 0.000787322828783533, 0.000234938106149921,
    -8.64057295452613e-05,-0.000205456041853291,-0.000187830184206340
], dtype=np.float64)
A_BP = np.array([1.0], dtype=np.float64)

# === Baseline removal (b_br, a_br) ===
B_BR = np.array([1.0, -1.0], dtype=np.float64)
A_BR = np.array([1.0, -0.9], dtype=np.float64)

def load_subject_folder(data_root: str, subject_id: int) -> list[str]:
    import os, glob
 
    cand1 = os.path.join(data_root, f"Subject{subject_id}")
    cand2 = os.path.join(data_root, f"Subject {subject_id}")
    subj_path = cand1 if os.path.isdir(cand1) else cand2

    pattern = os.path.join(subj_path, "[Ee][Xx][Gg]*.csv")
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No CSV files for Subject{subject_id} under {data_root}")
    return files

def read_exg_column(csv_path: str, ch_index: int = CH_EXG) -> np.ndarray:
    """Read one column from CSV (0-based index). Strips trailing NaN rows like MATLAB."""
    df = pd.read_csv(csv_path, header=None)
    # Trim rows with NaNs at the end
    while df.tail(1).isna().any(axis=None):
        df = df.iloc[:-1, :]
    sig = df.iloc[:, ch_index].values.astype(np.float64)
    return sig

def preprocess_signal(raw: np.ndarray, fs: int = FS_EXG) -> np.ndarray:
    """Apply 60 Hz notch, bandpass (given FIR), then baseline removal, then normalize 0..1."""
    wo = 60.0 / (fs / 2.0) 
    bw = wo / 35.0
    b_notch, a_notch = iirnotch(wo, bw)
    x = filtfilt(b_notch, a_notch, raw)

    # Bandpass FIR to mimic zero-phase
    x = filtfilt(B_BP, A_BP, x)

    # Baseline removal
    x = filtfilt(B_BR, A_BR, x)

    # Normalize
    xmin, xmax = np.nanmin(x), np.nanmax(x)
    if xmax > xmin:
        x = (x - xmin) / (xmax - xmin)
    else:
        x = np.zeros_like(x)
    return x.astype(np.float32)

def stitch_if_multiple(files: list[str], fs: int = FS_EXG) -> tuple[np.ndarray, np.ndarray]:
    """If multiple CSVs, concat back-to-back in time. """
    signals = []
    for f in files:
        sig = read_exg_column(f)
        sig = preprocess_signal(sig, fs)
        signals.append(sig)
    # simple concatenation with continuous time
    x = np.concatenate(signals)
    t = np.arange(len(x), dtype=np.float64) / fs
    return t, x

def last_minutes(t: np.ndarray, x: np.ndarray, minutes: float, fs: int = FS_EXG) -> tuple[np.ndarray, np.ndarray]:
    n_win = int(minutes * 60 * fs)
    if len(x) <= n_win:
        return t, x
    x2 = x[-n_win:]
    t2 = t[-n_win:] - t[-n_win] # re-zero
    return t2, x2

def plot_time(t: np.ndarray, x: np.ndarray, title="ECG (normalized)"):
    plt.figure()
    plt.plot(t, x, lw=0.8)
    plt.xlabel("Time (s)"); plt.ylabel("ECG (norm)"); plt.title(title); plt.tight_layout()
    