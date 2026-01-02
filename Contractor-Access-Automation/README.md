# Contractor Access Automation System

**承包商人员准入自动化管理系统**

A Python-based automated system for contractor personnel access control and compliance monitoring in large industrial projects.

---

## Project Background

In large-scale industrial construction and operation projects, managing thousands of contractor personnel presents significant challenges:

- **Scale**: 3,000+ personnel requiring simultaneous access management
- **Credential Verification**: Certificate authenticity and validity checking
- **Blacklist Screening**: Rapid identification of prohibited personnel
- **Training Compliance**: Tracking safety training requirements and expirations
- **Multi-phase Operations**: Supporting both construction and operation phases

This system automates the entire access control workflow, reducing manual verification from 2 days to under 10 seconds while improving accuracy from 95% to 99.9%.

---

## Features

### Core Modules
- **Data Generation**: Simulates realistic contractor data using Faker library
- **Access Control Engine**: Multi-dimensional validation (blacklist, expiry, training, qualifications)
- **Certificate Monitoring**: Multi-level early warning system (7/30/90 days before expiry)
- **Interactive Dashboard**: Real-time visualization with Plotly charts

### Output Reports
- Qualified Personnel List (Excel) - Ready for badge/access card generation
- Alert Log (Excel) - Detailed compliance violation records  
- Expiry Monitor (Excel) - Certificate expiration tracking
- Dashboard (HTML) - Interactive visualization report

---

## Tech Stack

| Category | Technologies |
|----------|-------------|
| Language | Python 3.8+ |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly, Matplotlib |
| Data Generation | Faker |
| Excel I/O | openpyxl, xlsxwriter |

---

## Project Structure

```
Contractor-Access-Automation/
├── README.md                 # Project documentation
├── STRUCTURE.md              # Detailed structure description
├── LICENSE                   # MIT License
├── requirements.txt          # Python dependencies
├── main.py                   # Main entry point
│
├── src/                      # Source code
│   ├── data_generator.py     # Data simulation module (~620 lines)
│   ├── access_control.py     # Core validation engine (~485 lines)
│   ├── dashboard.py          # Dashboard generator (~1060 lines)
│   └── ocr_simulator.py      # OCR simulation module (~200 lines)
│
├── data/                     # Data files (auto-generated)
│   ├── simulated_contractors.xlsx
│   ├── blacklist.xlsx
│   ├── training_records.xlsx
│   └── entry_exit_records.xlsx
│
└── outputs/                  # Generated reports
    ├── dashboard_*.html
    ├── qualified_personnel_*.xlsx
    ├── alert_log_*.xlsx
    └── expiry_monitor_*.xlsx
```

---

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/SeasonCake/Work_experience_data_analysis.git
cd Work_experience_data_analysis/Contractor-Access-Automation
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the System
```bash
python main.py
```

The system will automatically:
1. Generate simulated data (3,000 personnel records)
2. Perform compliance checks
3. Generate reports in `outputs/` directory
4. Open the interactive dashboard in your browser

---

## Sample Output

```
================================================================================
承包商人员准入自动化检查系统
================================================================================
开始处理: 3000 人

================================================================================
检查完成！
================================================================================
[PASS] 通过人数: 2282 人 (76.1%)
[FAIL] 未通过人数: 718 人 (23.9%)

问题分类:
  [X] 证书过期: 185 人
  [X] 黑名单人员: 0 人
  [!] 培训未完成: 498 人
  [!] 资质不符: 77 人
================================================================================
```

---

## Key Algorithms

1. **Blacklist Lookup**: Hash-based O(1) time complexity
2. **Batch Processing**: Pandas vectorized operations for 3000+ records
3. **Multi-level Alerting**: 7-day, 30-day, 90-day warning thresholds
4. **Phase-based Training**: Differentiated requirements for construction vs. operation phases

---

## Performance

| Operation | Records | Time |
|-----------|---------|------|
| Data Generation | 3,000 | ~3s |
| Compliance Check | 3,000 | ~5s |
| Dashboard Generation | - | ~2s |
| **Total** | **3,000** | **~10s** |

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact

For questions or suggestions, please open an issue on GitHub.
