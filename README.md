# ECG Hydration Pipeline (Python)

This project is a **Python reimplementation** of my MATLAB ECG hydration study pipeline.  
It processes ECG data recorded under four conditions and extracts the **last 5 minutes** of each signal after filtering:

- **Subject 10** — water, **rest** (after a 30-minute break)  
- **Subject 11** — water, **final rep**  
- **Subject 12** — no water, **rest** (after a 30-minute break)  
- **Subject 13** — no water, **final rep**

The pipeline applies the same filters as my MATLAB code:  
- **60 Hz notch** filter  
- **band-pass FIR filter** (your research coefficients)  
- **baseline removal filter**  
- **normalization** to [0, 1]  

It can also be used on **any ECG CSV file** by passing a file path.  

---

## Repository Layout

Data/

Subject10/ EXG_.csv

Subject11/ EXG_.csv

Subject12/ EXG_.csv

Subject13/ EXG_.csv

research_pipeline.py # filtering + preprocessing functions

research_cli.py # CLI tool to run analysis

requirements.txt

README.md

## Setup

```bash
# macOS/Linux
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Usage
#### ! Make sure to run the script from your terminal or PowerShell to see the ECG plot.
### A) Jiho's Research Data
#### Subject 10: water, rest
```bash
python research_cli.py --subject 10 --last-min 5
```
#### Subject 11: water, final rep
```bash
python research_cli.py --subject 11 --last-min 5
```

#### Subject 12: no water, rest
```bash
python research_cli.py --subject 12 --last-min 5
```

#### Subject 13: no water, final rep
```bash
python research_cli.py --subject 13 --last-min 5
```

Each run will:

1. Load Data/SubjectXX/EXG_*.csv
2. Apply 60 Hz notch → band-pass → baseline-removal → normalization
3. Extract the final N minutes (default 5)
4. Plot the ECG window

### B) User's Personal Data
```bash
python research_cli.py --csv path/to/your_ecg.csv --last-min 5
```
Expected CSV format:

- Plain numeric CSV (no header).
- ECG channel is column 2 (Python index 1).
- Sampling rate default: 250 Hz (edit FS_EXG in research_pipeline.py if yours differs).

## Filtering details

The pipeline matches the MATLAB implementation used in my study:

- 60 Hz notch -> ```iirnotch(wo, wo/35)```
- band-pass FIR -> coefficients from MATLAB research filter (```b```, ```a=1```)
- baseline removal -> high-pass IIR with ```[1, -1] / [1, -0.9]```
- normalization -> ```(x - min) / (max - min)```

## Data notes

The Data/SubjectXX folders are structured for my study.

If you want to use your own data, provide a CSV with the same general format and run with --csv.

Private/raw ECG study data should not be committed to GitHub; keep them local.
