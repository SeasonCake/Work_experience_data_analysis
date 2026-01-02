# Project Structure

```
Contractor-Access-Automation/
│
├── README.md                    # Project documentation
├── STRUCTURE.md                 # This file - directory structure
├── LICENSE                      # MIT License
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── main.py                      # Main entry point (~380 lines)
│
├── src/                         # Source code modules
│   ├── data_generator.py        # Data simulation (~620 lines)
│   │   └── ContractorDataGenerator class
│   │       ├── generate_contractors_data()
│   │       ├── generate_training_records()
│   │       └── save_data()
│   │
│   ├── access_control.py        # Core validation engine (~485 lines)
│   │   └── AccessControlSystem class
│   │       ├── check_blacklist()
│   │       ├── check_expiry()
│   │       ├── check_training()
│   │       ├── comprehensive_check()
│   │       └── batch_check()
│   │
│   ├── dashboard.py             # Dashboard generator (~1060 lines)
│   │   └── DashboardGenerator class
│   │       ├── get_daily_summary()
│   │       ├── get_training_trend_by_phase()
│   │       ├── get_work_category_distribution()
│   │       └── generate_html_report()
│   │
│   └── ocr_simulator.py         # OCR simulation (~200 lines)
│       └── OCRSimulator class
│           ├── simulate_scan()
│           └── extract_info()
│
├── data/                        # Data files (auto-generated)
│   ├── simulated_contractors.xlsx   # Personnel data (3000 records)
│   ├── blacklist.xlsx               # Blacklist (5 records)
│   ├── training_records.xlsx        # Training records (~10000 records)
│   └── entry_exit_records.xlsx      # Entry/exit records (~5600 records)
│
└── outputs/                     # Generated reports (timestamped)
    ├── dashboard_YYYYMMDD_HHMMSS.html      # Interactive dashboard
    ├── qualified_personnel_*.xlsx          # Qualified personnel list
    ├── alert_log_*.xlsx                    # Alert/warning log
    └── expiry_monitor_*.xlsx               # Certificate expiry monitor
```

## Data Flow

```
┌─────────────────┐
│ data_generator  │ ──► Generate simulated data
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   data/*.xlsx   │ ──► Personnel, Training, Blacklist
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ access_control  │ ──► Validate credentials, Check compliance
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   dashboard     │ ──► Generate reports & visualization
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ outputs/*.xlsx  │ ──► Final reports ready for use
│ outputs/*.html  │
└─────────────────┘
```

## Module Details

### main.py
The orchestrator that coordinates all modules:
- Generates or loads data
- Runs access control checks
- Generates dashboard and reports
- Provides console output summary

### src/data_generator.py
Generates realistic simulated data:
- Personnel records with realistic Chinese names
- Certificate information with valid/expired/expiring dates
- Training records with quarterly distribution
- Entry/exit records tracking personnel flow

### src/access_control.py
Core validation engine:
- **Blacklist Check**: O(1) hash-based lookup
- **Expiry Check**: Certificate validity verification
- **Training Check**: Compliance verification
- **Comprehensive Check**: Multi-dimensional validation

### src/dashboard.py
Interactive visualization:
- Plotly-based charts (pie, bar, treemap)
- Real-time summary cards
- Searchable data tables
- Responsive dark theme design

### src/ocr_simulator.py
Simulates OCR document scanning:
- ID card recognition
- Certificate scanning
- Information extraction

## Running the Project

```bash
# First run - generates all data
python main.py

# Subsequent runs - uses existing data
python main.py

# To regenerate data, delete the data/ folder first
rm -rf data/
python main.py
```

## Output Files

| File | Description | Records |
|------|-------------|---------|
| dashboard_*.html | Interactive web dashboard | - |
| qualified_personnel_*.xlsx | Approved personnel list | ~2,200 |
| alert_log_*.xlsx | Violations and warnings | ~980 |
| expiry_monitor_*.xlsx | Certificate expiry tracking | ~290 |
