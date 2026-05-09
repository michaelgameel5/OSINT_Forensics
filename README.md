# Social Media Forensics & OSINT Investigation

A Python-based forensic investigation framework that archives social media content, extracts account metadata, generates network graphs showing suspect relationships, performs cross-platform username searches, and recovers deleted or hidden content through cache analysis.

---

## Project Requirements Implemented

| # | Requirement | Module |
|---|---|---|
| 1 | Social Media Content Archiving | `src/archiver/social_archiver.py` |
| 2 | User Profile Extraction | `src/extractor/profile_extractor.py` |
| 3 | Network Graph Generation | `src/graph/network_graph.py` |
| 4 | Username Cross-Platform Search | `src/osint/username_search.py` |
| 5 | Deleted Content Recovery via Cache | `src/osint/cache_recovery.py` |

---

## Project Structure

```
├── src/
│   ├── archiver/
│   │   └── social_archiver.py        # Selenium-based page archiver
│   ├── extractor/
│   │   └── profile_extractor.py      # GitHub and Reddit profile extractor
│   ├── graph/
│   │   └── network_graph.py          # Network graph builder and visualizer
│   ├── osint/
│   │   ├── username_search.py        # Cross-platform username search
│   │   └── cache_recovery.py         # Wayback Machine cache recovery
│   └── reports/
│       ├── report_generator.py       # HTML and JSON report generator
│       └── templates/
│           └── report_template.html  # Jinja2 HTML report template
├── data/
│   ├── raw/                          # Archived HTML snapshots
│   ├── processed/                    # Extracted profile and cache JSON files
│   ├── graphs/                       # Network graph PNG and HTML files
│   └── reports/                      # Final forensic reports
├── main.py                           # Full investigation pipeline entry point
├── run_tests.py                      # Python test runner
├── run_tests.ps1                     # PowerShell test runner
├── requirements.txt                  # Project dependencies
├── TESTS.md                          # Test commands documentation
└── README.md                         # This file
```

---

## Prerequisites

Make sure the following are installed on your machine before getting started:

| Tool | Download |
|---|---|
| Python 3.10 or higher | https://www.python.org/downloads/ |
| Git | https://git-scm.com/downloads |
| Google Chrome | https://www.google.com/chrome/ |

---

## Installation & Setup

### Step 1: Clone the Repository
```powershell
git clone https://github.com/michaelgameel5/-Social-Media-Forensics-OSINT-Investigation.git
cd "-Social-Media-Forensics-OSINT-Investigation"
```

### Step 2: Create a Virtual Environment
```powershell
python -m venv venv
```

### Step 3: Activate the Virtual Environment

On Windows:
```powershell
.\venv\Scripts\activate
```
On Mac/Linux:
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Create the Data Folders
```powershell
mkdir data\raw
mkdir data\processed
mkdir data\graphs
mkdir data\reports
```

---

## Running the Tool

### Run the Full Investigation Pipeline
```powershell
python main.py
```
When prompted, enter any username to investigate:
```
=== Social Media Forensics & OSINT Tool ===

Enter username to investigate: torvalds
```
The tool will automatically run all five modules in sequence and save all outputs to the `data/` folder.

---

## Running Individual Modules

### Module 1: Username Search
```powershell
python -c "
from src.osint.username_search import search_username
search_username('torvalds')
"
```

### Module 2: Profile Extraction
```powershell
# GitHub only
python -c "
from src.extractor.profile_extractor import ProfileExtractor
e = ProfileExtractor()
e.extract_github('torvalds')
"

# Reddit only
python -c "
from src.extractor.profile_extractor import ProfileExtractor
e = ProfileExtractor()
e.extract_reddit('torvalds')
"

# Both platforms and save
python -c "
from src.extractor.profile_extractor import ProfileExtractor
e = ProfileExtractor()
e.extract_all('torvalds')
"
```

### Module 3: Network Graph Generation
```powershell
python -c "
from src.graph.network_graph import NetworkGraph
g = NetworkGraph()
g.load_github_network('torvalds', max_users=10)
g.load_reddit_network('torvalds', max_posts=10)
g.detect_suspect_clusters()
g.visualize()
g.visualize_interactive()
g.save_graph_data('torvalds')
"
```

### Module 4: Cache Recovery
```powershell
# Full cache recovery
python -c "
from src.osint.cache_recovery import CacheRecovery
c = CacheRecovery()
c.recover_all('torvalds')
"

# Snapshot history only
python -c "
from src.osint.cache_recovery import CacheRecovery
c = CacheRecovery()
c.get_snapshot_history('https://github.com/torvalds', limit=10)
"

# Deleted content only
python -c "
from src.osint.cache_recovery import CacheRecovery
c = CacheRecovery()
c.detect_deleted_content('https://github.com/torvalds')
"
```

### Module 5: Report Generator
```powershell
python -c "
from src.reports.report_generator import ReportGenerator
r = ReportGenerator()
r.generate_html('torvalds')
r.generate_json('torvalds')
"
```

---

## Running the Tests

### Python Test Runner (Recommended)
```powershell
python run_tests.py
```

### PowerShell Test Runner
```powershell
# Allow script execution if not already enabled
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run tests
.\run_tests.ps1
```

Expected output:
```
==================================================
  Social Media Forensics - Test Runner
  Target Username: torvalds
==================================================

--- Testing: Username Search ---
[PASS] Username Search

--- Testing: GitHub Profile Extraction ---
[PASS] GitHub Profile Extraction

...

==================================================
  TEST SUMMARY
==================================================
  Passed : 11
  Failed : 0
  Total  : 11
==================================================
```

---

## Output Structure

After running the tool, all outputs are saved here:

```
data/
├── processed/
│   ├── github_torvalds_TIMESTAMP.json        # GitHub profile data
│   ├── reddit_torvalds_TIMESTAMP.json        # Reddit profile data
│   └── cache_recovery_torvalds_TIMESTAMP.json # Cache recovery findings
├── graphs/
│   ├── network_TIMESTAMP.png                 # Static network graph image
│   ├── network_TIMESTAMP.html                # Interactive network graph
│   └── graph_data_torvalds_TIMESTAMP.json    # Raw graph node/edge data
└── reports/
    ├── report_torvalds_TIMESTAMP.html        # Full forensic HTML report
    └── report_torvalds_TIMESTAMP.json        # Full forensic JSON report
```

---

## Technologies Used

| Library | Purpose |
|---|---|
| Selenium | Headless browser for page archiving |
| NetworkX | Network graph construction and analysis |
| Matplotlib | Static graph visualization |
| PyVis | Interactive graph visualization |
| Requests | HTTP requests for API calls |
| BeautifulSoup4 | HTML parsing |
| Pandas | Data manipulation |
| Jinja2 | HTML report templating |
| urllib3 | Connection retry handling |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` not recognized | Use `python3` instead, or add Python to PATH during installation |
| `cd` fails with dash in folder name | Wrap in quotes: `cd "-Social-Media-Forensics-OSINT-Investigation"` |
| `pip install` fails | Make sure venv is activated — you should see `(venv)` in the terminal |
| ChromeDriver error | Run `pip install webdriver-manager` and update the driver line in `social_archiver.py` |
| Wayback Machine timeout | This is normal — the API is slow. The tool will skip and continue automatically |
| `ModuleNotFoundError` | Make sure you are running commands from the root project folder |
| PowerShell execution error | Run `Set-ExecutionPolicy RemoteSigned` as Administrator |

---

## Platforms Supported

| Platform | Username Search | Profile Extraction | Network Graph | Cache Recovery |
|---|---|---|---|---|
| GitHub | Yes | Yes | Yes | Yes |
| Reddit | Yes | Yes | Yes | Yes |
| Twitter | Yes | No | No | Yes |
| Instagram | Yes | No | No | Yes |

---

## Notes

- Twitter and Instagram cache recovery queries can be slow due to the volume of data archived by the Wayback Machine. The tool handles timeouts gracefully and continues automatically.
- The Wayback Machine API is a free public service and may occasionally be slow or unavailable during peak times.
- This tool is intended for legitimate forensic investigation and OSINT research purposes only.

## Running the GUI

The tool includes a Streamlit-based graphical interface.

### Step 1: Make sure dependencies are installed

```bash
pip install -r requirements.txt
```

### Step 2: Launch the GUI

```bash
streamlit run gui.py
```

This will open the tool in your browser at `http://localhost:8501` automatically.

### Step 3: Use the interface

1. Enter a **target username** in the left sidebar (e.g. `torvalds`)
2. Select which **modules** to enable using the checkboxes
3. Click **▶ RUN INVESTIGATION**
4. Results appear across the tabs — switch freely without losing data

> **Note:** The Wayback Machine queries (Cache Recovery tab) can be slow.  
> Twitter and Instagram results are approximate due to JS-rendering limitations.#   O S I N T _ F o r e n s i c s  
 