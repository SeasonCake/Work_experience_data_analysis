# Hazard Risk Dashboard

**隐患排查与风险监控仪表板**

A comprehensive risk monitoring system that transforms scattered hazard data into actionable insights through advanced visualization including 3D surface plots.

---

## Project Background

Industrial safety teams often struggle with:
- **Scattered Data**: Hazard records dispersed across weekly reports
- **Hidden Patterns**: Difficulty identifying which areas pose the highest risk
- **Slow Response**: Manual data compilation delays decision-making

This system addresses these challenges by:
- Centralizing hazard data with standardized classification
- Providing real-time risk visualization across factory zones
- Enabling 80/20 analysis to prioritize critical issues

---

## Features

### Data Generation
- Weighted random distribution (Pareto principle)
- Historical data (2024 full year) + Recent data (2025-present)
- Seasonal variations and realistic rectification patterns
- Risk level distribution: High (5%), Medium (25%), Low (70%)

### Risk Analysis
- Pareto analysis (vital few identification)
- Area risk summary with 30-day window
- Quarterly trend tracking with rectification rate
- Overdue hazard monitoring (>90 days)

### Visualization
- **Factory Heatmap**: Polygon-based zone risk visualization with gradient colors
- **Pareto Chart**: 80/20 rule identification (vertical bar chart)
- **3D Surface Plot**: Risk response surface (Area × Time/Type × Risk Score)
- **Treemap**: Hierarchical hazard type distribution (90-day view)
- **Trend Chart**: Quarterly rectification rate vs. 85% target
- **Sortable Tables**: Alert table and full records with sorting functionality

---

## Tech Stack

| Category | Technologies |
|----------|-------------|
| Language | Python 3.8+ |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly (3D Surface, Treemap, Heatmap) |
| Data Generation | Faker |
| Export | openpyxl |

---

## Project Structure

```
Hazard-Risk-Dashboard/
├── README.md
├── requirements.txt
├── main.py                       # Main entry point
├── risk_analysis_demo.ipynb      # Jupyter Notebook demo
│
├── src/
│   ├── __init__.py
│   ├── data_generator.py         # Weighted data simulation
│   ├── risk_analyzer.py          # Risk analysis logic
│   ├── visualizer.py             # Chart generation (incl. 3D)
│   └── dashboard_generator.py    # HTML report builder
│
├── data/
│   ├── areas.json                # Factory zone configuration
│   └── hazards.csv               # Generated hazard records
│
└── outputs/
    ├── risk_dashboard_*.html     # Interactive dashboard
    ├── area_summary_*.xlsx       # Area risk report
    └── overdue_hazards_*.xlsx    # Overdue hazards list
```

---

## Quick Start

### 1. Install Dependencies
```bash
cd Hazard-Risk-Dashboard
pip install -r requirements.txt
```

### 2. Run the System
```bash
python main.py
```

### 3. View Results
The system will:
1. Generate ~4,000+ hazard records (2024-present)
2. Perform comprehensive risk analysis
3. Generate interactive HTML dashboard with sortable tables
4. Export Excel reports for area summary and overdue hazards
5. Auto-open the dashboard in your browser

---

## Data Schema

### Hazard Record
| Field | Type | Description |
|-------|------|-------------|
| hazard_id | string | Unique identifier (e.g., HZ-2024-R00001) |
| date | date | Discovery date |
| area_code | string | Zone identifier |
| hazard_category | string | Category (8 types) |
| hazard_type | string | Specific hazard type |
| risk_level | string | High/Medium/Low |
| risk_score | int | 1-10 risk score |
| status | string | 已整改/整改中/逾期 |
| rectify_date | date | Rectification completion date |
| responsible | string | Person responsible |

### Hazard Categories (8 types)
| Category | Weight | Example Types |
|----------|--------|---------------|
| 电气安全 | 22% | 临时用电, 配电箱隐患, 接地不良 |
| 消防安全 | 18% | 灭火器过期, 消防通道堵塞, 烟感故障 |
| 行走安全 | 15% | 地面湿滑, 通道障碍, 照明不足 |
| 化学品安全 | 15% | 泄漏风险, 标识缺失, 存储不当 |
| 机械安全 | 12% | 防护罩缺失, 设备故障, 传动部件裸露 |
| 个人防护 | 8% | PPE佩戴不规范, 防护用品缺失 |
| 作业安全 | 5% | 高处作业违规, 受限空间问题 |
| 特种设备 | 5% | 压力容器超期, 起重机械问题 |

### Factory Zones (9 areas)
| Zone | Risk Weight | Description |
|------|-------------|-------------|
| 硫酸车间 | 1.3 | High-risk chemical processing |
| 镍钴车间 | 1.2 | Heavy metal processing |
| 电解车间 | 1.1 | Electrolysis operations |
| 萃取车间 | 1.0 | Extraction processes |
| 公用工程 | 0.9 | Utility systems |
| 废水处理 | 0.8 | Wastewater treatment |
| 原料仓库 | 0.7 | Raw material storage |
| 成品仓库 | 0.6 | Finished goods storage |
| 中控室 | 0.5 | Control center (lowest risk) |

---

## Key Outputs

### Interactive Dashboard
- **Risk Overview**: Factory heatmap + Pareto analysis
- **Distribution & Trends**: Treemap + Quarterly rectification trend
- **3D Analysis**: Two surface plots (Area×Time, Area×Type)
- **Alert Tables**: Sortable by date, risk level, status, etc.

### Excel Reports
- `area_summary_*.xlsx`: Per-zone statistics and risk scores
- `overdue_hazards_*.xlsx`: Hazards exceeding rectification deadline

---

## Performance

| Metric | Value |
|--------|-------|
| Data Records | ~4,500 |
| Time Range | 2024-01 to Present |
| Generation Time | ~3s |
| Dashboard Size | ~150KB |

---

## License

MIT License
