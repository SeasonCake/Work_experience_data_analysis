# Work Experience Data Analysis

**工业安全数据分析与可视化项目集**

A collection of Python-based data analysis and visualization projects developed from real industrial safety management experience. These projects demonstrate the practical application of data engineering and visualization skills to solve real-world EHS (Environment, Health & Safety) challenges.

---

## Background

As a safety engineer in the chemical/manufacturing industry, I identified several pain points in daily operations:

1. **Contractor Management**: Manual verification of 3,000+ contractor personnel is time-consuming and error-prone
2. **Hazard Tracking**: Hazard data scattered across weekly reports makes it difficult to identify high-risk areas
3. **Compliance Monitoring**: Certificate expiration tracking relies on manual spreadsheet management

This project collection transforms these operational challenges into automated data analysis solutions, demonstrating the value of combining domain expertise with programming skills.

---

## Projects Overview

### 1. Contractor Access Automation
**承包商人员准入自动化系统**

Automates contractor personnel access control and compliance verification for large industrial projects.

| Metric | Value |
|--------|-------|
| Data Scale | 3,000+ personnel records |
| Processing Time | ~10 seconds (vs. 2 days manual) |
| Accuracy | 99.9% (vs. 95% manual) |
| Key Features | Blacklist check, Certificate validation, Training compliance |

**Technical Highlights:**
- Hash-based O(1) blacklist lookup
- Multi-level alert system (7/30/90 days)
- Phase-aware training requirements (construction vs. operation)
- Interactive HTML dashboard with Plotly

[View Project Details →](./Contractor-Access-Automation/)

---

### 2. Hazard Risk Dashboard
**隐患排查与风险可视化系统**

Transforms scattered hazard data into actionable risk insights through advanced visualization.

| Metric | Value |
|--------|-------|
| Data Scale | 4,500+ hazard records |
| Time Range | 2024-01 to Present |
| Key Features | Factory heatmap, Pareto analysis, 3D surface plot |
| Visualization | 9-zone polygon-based risk mapping |

**Technical Highlights:**
- Weighted data generation following Pareto principle
- 3D surface plot for multi-dimensional risk analysis
- Client-side sortable tables
- Quarterly rectification trend vs. 85% target

[View Project Details →](./Hazard-Risk-Dashboard/)

---

## Tech Stack

| Category | Technologies |
|----------|-------------|
| Language | Python 3.8+ |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly (3D, Treemap, Heatmap), Matplotlib |
| Data Generation | Faker (realistic simulation) |
| Export | openpyxl, HTML report generation |
| Version Control | Git, GitHub |

---

## Project Structure

```
Work_experience_data_analysis/
├── README.md                         # This file
│
├── Contractor-Access-Automation/     # Project 1
│   ├── README.md
│   ├── main.py
│   ├── contractor_analysis_demo.ipynb
│   ├── src/
│   ├── data/
│   └── outputs/
│
└── Hazard-Risk-Dashboard/            # Project 2
    ├── README.md
    ├── main.py
    ├── risk_analysis_demo.ipynb
    ├── src/
    ├── data/
    └── outputs/
```

---

## Quick Start

### Clone Repository
```bash
git clone https://github.com/SeasonCake/Work_experience_data_analysis.git
cd Work_experience_data_analysis
```

### Run Contractor Access System
```bash
cd Contractor-Access-Automation
pip install -r requirements.txt
python main.py
```

### Run Hazard Risk Dashboard
```bash
cd Hazard-Risk-Dashboard
pip install -r requirements.txt
python main.py
```

---

## Career Context

These projects represent a bridge between **industrial safety engineering** and **data engineering/analysis**:

| Previous Role | Transition Skills | Target Role |
|--------------|-------------------|-------------|
| Safety Engineer | Domain Knowledge + Python + Data Viz | Data Analyst/Engineer |
| EHS Compliance | Process Automation | Business Intelligence |
| Risk Assessment | Statistical Analysis | Data Science |

### Key Competencies Demonstrated

**Technical Skills:**
- Python programming (OOP, data structures)
- Data manipulation with Pandas/NumPy
- Interactive visualization with Plotly
- Report automation and generation
- Git version control

**Domain Knowledge:**
- Industrial safety regulations and compliance
- Contractor management processes
- Hazard classification and risk assessment
- Certificate and training management

**Problem-Solving:**
- Identifying automation opportunities
- Translating manual processes to code
- Designing user-friendly dashboards
- Balancing accuracy with performance

---

## Future Enhancements

- [ ] Database integration (SQLite/PostgreSQL)
- [ ] Web application deployment (Flask/Streamlit)
- [ ] API development for system integration
- [ ] Machine learning for risk prediction
- [ ] Real-time data streaming

---

## License

MIT License - see individual project directories for details.

---

## Contact

For questions, collaboration opportunities, or career discussions:
- GitHub: [@SeasonCake](https://github.com/SeasonCake)
