# Social Media Forensics & OSINT Investigation — Test Commands

## Setup
```powershell
# Navigate to project
cd "-Social-Media-Forensics-OSINT-Investigation"

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Module 1: Username Search
```powershell
# Test username search across all platforms
python -c "
from src.osint.username_search import search_username
search_username('torvalds')
"
```
Expected output:
```
[✓] Twitter:   https://twitter.com/torvalds
[✓] GitHub:    https://github.com/torvalds
[✓] Reddit:    https://reddit.com/user/torvalds
[✗] Instagram: https://instagram.com/torvalds
```

---

## Module 2: Profile Extraction
```powershell
# Test GitHub profile extraction only
python -c "
from src.extractor.profile_extractor import ProfileExtractor
e = ProfileExtractor()
e.extract_github('torvalds')
"

# Test Reddit profile extraction only
python -c "
from src.extractor.profile_extractor import ProfileExtractor
e = ProfileExtractor()
e.extract_reddit('spez')
"

# Test full extraction and save for a username
python -c "
from src.extractor.profile_extractor import ProfileExtractor
e = ProfileExtractor()
e.extract_all('torvalds')
"
```
Expected output:
```
[+] GitHub profile extracted for: torvalds
[+] Profile saved -> data/processed/github_torvalds_TIMESTAMP.json
[+] Reddit profile extracted for: torvalds
[+] Profile saved -> data/processed/reddit_torvalds_TIMESTAMP.json
```

---

## Module 3: Network Graph Generation
```powershell
# Test GitHub network only
python -c "
from src.graph.network_graph import NetworkGraph
g = NetworkGraph()
g.load_github_network('torvalds', max_users=10)
g.detect_suspect_clusters()
g.visualize()
g.visualize_interactive()
"

# Test Reddit network only
python -c "
from src.graph.network_graph import NetworkGraph
g = NetworkGraph()
g.load_reddit_network('spez', max_posts=10)
g.detect_suspect_clusters()
g.visualize()
g.visualize_interactive()
"

# Test full network graph with save
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

# Open the interactive graph in browser
start data/graphs/network_<TIMESTAMP>.html
```
Expected output:
```
[+] Loaded 10 followers
[+] Loaded 0 following
[+] Network built: 11 nodes, 10 edges
[+] Found 1 connected cluster(s)
[+] Static graph saved  -> data/graphs/network_TIMESTAMP.png
[+] Interactive graph saved -> data/graphs/network_TIMESTAMP.html
[+] Graph data saved -> data/graphs/graph_data_torvalds_TIMESTAMP.json
```

---

## Module 4: Cache Recovery
```powershell
# Test availability check only
python -c "
from src.osint.cache_recovery import CacheRecovery
c = CacheRecovery()
c.check_availability('https://twitter.com/elonmusk')
"

# Test snapshot history only
python -c "
from src.osint.cache_recovery import CacheRecovery
c = CacheRecovery()
c.get_snapshot_history('https://github.com/torvalds', limit=10)
"

# Test deleted content detection only
python -c "
from src.osint.cache_recovery import CacheRecovery
c = CacheRecovery()
c.detect_deleted_content('https://twitter.com/torvalds')
"

# Test full cache recovery for a username
python -c "
from src.osint.cache_recovery import CacheRecovery
c = CacheRecovery()
c.recover_all('torvalds')
"
```
Expected output:
```
[+] Snapshot found: TIMESTAMP
[+] Found 10 historical snapshots
[!] Found 14 deleted/modified snapshots
[+] Cache recovery report saved -> data/processed/cache_recovery_torvalds_TIMESTAMP.json
```

---

## Module 5: Report Generator
```powershell
# Test HTML report generation
python -c "
from src.reports.report_generator import ReportGenerator
r = ReportGenerator()
r.generate_html('torvalds')
"

# Test JSON report generation
python -c "
from src.reports.report_generator import ReportGenerator
r = ReportGenerator()
r.generate_json('torvalds')
"

# Open the HTML report in browser
start data/reports/report_torvalds_<TIMESTAMP>.html
```
Expected output:
```
[+] Loaded: data/processed/github_torvalds_TIMESTAMP.json
[+] Loaded: data/processed/reddit_torvalds_TIMESTAMP.json
[+] Loaded graph: data/graphs/graph_data_torvalds_TIMESTAMP.json
[+] HTML report saved -> data/reports/report_torvalds_TIMESTAMP.html
[+] JSON report saved -> data/reports/report_torvalds_TIMESTAMP.json
```

---

## Full Pipeline Test
```powershell
# Run the complete investigation tool end to end
python main.py
```
When prompted, enter a username (e.g. torvalds) and the tool will:
```
1. Search username across all platforms
2. Extract profile data from GitHub and Reddit
3. Build and save network graphs
4. Run cache recovery across all platforms
5. Generate HTML and JSON forensic reports
```
All outputs saved to:
```
data/processed/   — profile extractions and cache recovery JSON files
data/graphs/      — network graph PNG and interactive HTML files
data/reports/     — final HTML and JSON forensic reports
```

---

## Verify No Issues
```powershell
# Check all requests.get are replaced with self.session.get in cache_recovery.py
Select-String -Path "src\osint\cache_recovery.py" -Pattern "requests.get"

# Check all output folders exist
Get-ChildItem data/

# Check latest report was generated
Get-ChildItem data/reports/
```