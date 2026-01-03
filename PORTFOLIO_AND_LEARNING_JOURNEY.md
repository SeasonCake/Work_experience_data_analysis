# 数据分析学习历程与项目作品集

> 从安全工程师到数据分析师的转型之路  
> Portfolio & Learning Journey: Safety Engineer → Data Analyst/Engineer

---

## 目录

1. [证书与系统课程](#一证书与系统课程)
2. [实战项目作品](#二实战项目作品)
3. [学习笔记与练习](#三学习笔记与练习)
4. [技能总结](#四技能总结)
5. [职业转型叙事](#五职业转型叙事)

---

## 一、证书与系统课程

### 1.1 IBM Data Science Professional Certificate

| 信息 | 详情 |
|------|------|
| 平台 | Coursera |
| 颁发机构 | IBM |
| 完成时间 | 2025年8月 |
| 课程数量 | 12门 |
| 验证链接 | [查看证书](https://coursera.org/verify/professional-cert/9NWJOHC5PPTS) |

**课程列表**:
1. What is Data Science?
2. Tools for Data Science
3. Data Science Methodology
4. Python for Data Science, AI & Development
5. Python Project for Data Science
6. Databases and SQL for Data Science with Python
7. Data Analysis with Python
8. Data Visualization with Python
9. Machine Learning with Python
10. Applied Data Science Capstone ⭐
11. Generative AI: Elevate Your Data Science Career
12. Data Scientist Career Guide and Interview Preparation

**核心收获**:
- 完整数据科学工作流（采集→清洗→分析→建模→可视化）
- 机器学习模型开发与评估
- SQL数据库查询与Python集成
- 毕业项目：SpaceX Falcon 9 着陆预测系统

---

### 1.2 Python for Everybody Specialization

| 信息 | 详情 |
|------|------|
| 平台 | Coursera |
| 颁发机构 | University of Michigan |
| 完成时间 | 2025年5月 |
| 课程数量 | 5门 |
| 验证链接 | [查看证书](https://coursera.org/verify/specialization/809XIM6AYCJG) |

**课程列表**:
1. Programming for Everybody (Getting Started with Python)
2. Python Data Structures
3. Using Python to Access Web Data
4. Using Databases with Python
5. Capstone: Retrieving, Processing, and Visualizing Data with Python

**核心收获**:
- Python编程基础与数据结构
- Web数据抓取（BeautifulSoup, API）
- SQLite数据库操作
- 综合项目：数据检索与可视化

---

### 1.3 Kaggle Learning Courses

| 课程 | 内容 | 状态 |
|------|------|------|
| Python | 基础语法、函数、类 | ✅ 完成 |
| Intro to Machine Learning | ML入门、模型训练 | ✅ 完成 |
| Pandas | 数据处理、分析 | ✅ 完成 |
| Intermediate Machine Learning | 高级ML技术 | ✅ 完成 |
| Data Visualization | 数据可视化 | ✅ 完成 |
| Feature Engineering | 特征工程 | ✅ 完成 |
| Intro to SQL | SQL基础查询 | ✅ 完成 |
| Data Cleaning | 数据清洗 | ✅ 完成 |

---

## 二、实战项目作品

### 2.1 SpaceX Falcon 9 Landing Prediction

**IBM Applied Data Science Capstone Project**

| 项目信息 | 详情 |
|---------|------|
| GitHub | [IBM-Data-Science-Capstone-SpaceX](https://github.com/SeasonCake/IBM-Data-Science-Capstone-SpaceX) |
| 类型 | 毕业设计 |
| 数据来源 | SpaceX REST API + Wikipedia |

**项目概述**:
预测SpaceX Falcon 9第一级火箭能否成功着陆回收。着陆成功意味着火箭可复用，直接影响发射成本。

**技术亮点**:
```
数据采集 → 数据清洗 → EDA分析 → 交互可视化 → 机器学习预测
   ↓           ↓          ↓           ↓            ↓
REST API    Pandas     SQL查询     Folium地图    Decision Tree
Web爬虫     特征工程   Matplotlib   Plotly Dash   90.3% CV准确率
```

**关键发现**:
- KSC LC-39A发射场成功率最高
- Falcon 9 B5助推器表现最佳
- 载荷质量、轨道类型为关键影响因素
- Decision Tree最终测试准确率83.3%

**技术栈**: Python, Pandas, SQL, Matplotlib, Seaborn, Folium, Plotly Dash, Scikit-learn

---

### 2.2 承包商人员准入自动化系统

**Contractor Access Automation System**

| 项目信息 | 详情 |
|---------|------|
| GitHub | [Work_experience_data_analysis](https://github.com/SeasonCake/Work_experience_data_analysis) |
| 目录 | `/Contractor-Access-Automation` |
| 类型 | 工作经验转化项目 |
| 代码量 | ~2,500行 Python |

**业务背景**:
大型化工项目承包商管理痛点：
- 3000+人员，手工核查耗时长
- 黑名单比对易遗漏
- 证书到期监控滞后

**核心功能**:
```
五维度准入检查引擎
┌─────────────────────────────────────────────────────┐
│ [1] 黑名单比对   → Hash Set O(1)查找              │
│ [2] 证书有效期   → 三级预警 (7/30/90天)           │
│ [3] 证书真伪     → 格式校验                        │
│ [4] 培训状态     → 关联查询                        │
│ [5] 工种资质     → 规则匹配                        │
└─────────────────────────────────────────────────────┘
```

**效益量化**:
| 指标 | 手工方式 | 自动化 | 提升 |
|------|---------|--------|------|
| 3000人核查 | ~2天 | <10秒 | **17,000x** |
| 准确率 | ~95% | 99.9% | +4.9% |
| 预警时效 | 月底 | 实时 | 即时 |

**技术栈**: Python, Pandas, Plotly (Treemap, Bar, Pie), Faker, openpyxl

---

### 2.3 隐患排查与风险可视化系统

**Hazard Risk Dashboard**

| 项目信息 | 详情 |
|---------|------|
| GitHub | [Work_experience_data_analysis](https://github.com/SeasonCake/Work_experience_data_analysis) |
| 目录 | `/Hazard-Risk-Dashboard` |
| 类型 | 工作经验转化项目 |
| 代码量 | ~3,200行 Python |

**业务背景**:
工业安全隐患数据分析痛点：
- 隐患数据分散在周报中
- 无法识别高风险区域
- 整改率统计依赖手工

**可视化亮点**:
| 图表 | 用途 | 技术 |
|------|------|------|
| 厂区风险热力图 | 9区域多边形风险分布 | Plotly Scatter + 渐变色 |
| 帕累托图 | 识别关键隐患类型 | 柱状图 + 累计曲线 |
| 3D曲面图 | 区域×类型×风险 | Plotly Surface |
| 整改趋势图 | 季度整改率监控 | 组合图（柱+线）|
| Treemap | 隐患类型结构 | px.treemap |

**数据模型**:
- 9大厂区区域
- 12种隐患类型
- 3级风险等级
- 4500+模拟隐患记录

**技术栈**: Python, Pandas, NumPy, Plotly, HTML/CSS/JS

---

### 2.4 焊接工艺参数分析

**Welding Process Analysis**

| 项目信息 | 详情 |
|---------|------|
| 位置 | `焊接工艺分析_graphs/` |
| 类型 | 数据分析实践 |
| 数据来源 | PC-AlN焊接实验数据 |

**分析内容**:
| 图表类型 | 分析方法 |
|---------|---------|
| Q-Q图 | 正态性检验 (Shapiro-Wilk) |
| 残差图 | 回归模型诊断 |
| 3D曲面图 | 响应面分析 |
| 特征重要性 | 机器学习特征分析 |
| 相关性热力图 | 变量关联分析 |
| 统计控制图 | 质量控制分析 |

**关键发现**:
- 厚度是影响拉断力的最重要参数（相关系数0.594）
- 数据不服从正态分布（p ≤ 0.05）
- Random Forest特征重要性分析指导工艺优化

---

### 2.5 炉石传说伤害预测

**Fyrakk Damage Prediction - Hearthstone**

| 项目信息 | 详情 |
|---------|------|
| 位置 | `IBM_datacourse/Fyrakk_dmg_prediction_hearthstone/` |
| 类型 | 游戏数据分析 |
| 方法 | 蒙特卡洛模拟 + Decision Tree |

**项目概述**:
分析炉石传说法术卡牌组合，预测费拉克（Fyrakk）BOSS的伤害输出。

**技术方法**:
- 法术列表数据结构设计
- 随机抽卡模拟（蒙特卡洛）
- 伤害分布分析
- Decision Tree预测模型

---

## 三、学习笔记与练习

### 3.1 EDA数据分析方法总结

| 项目 | 说明 |
|------|------|
| GitHub | [workflow_with_eda_analysis_methods](https://github.com/SeasonCake/workflow_with_eda_analysis_methods) |
| 文件 | `EDA_analyst_demonstartion.ipynb` |

**内容**:
- 12种可视化技术
- 统计检验（ANOVA, Pearson, Chi-square）
- 5种ML模型对比
- 完整数据科学流程示范

**模型性能对比**:
| 模型 | R² Score | 最佳用途 |
|------|----------|---------|
| Linear Regression | 0.75 | 基线模型 |
| Polynomial Regression | 0.85 | 非线性关系 |
| Ridge Regression | 0.86 | 需要正则化 |
| Decision Tree | 0.78 | 可解释性 |
| Random Forest | **0.87** | 最佳性能 |

---

### 3.2 机器学习综合回顾

| 项目 | 说明 |
|------|------|
| GitHub | [IBM-Machine-Learning-Comprehensive-Recap](https://github.com/SeasonCake/IBM-Machine-Learning-Comprehensive-Recap) |
| Notebooks | 10个主题模块 |

**模块结构**:
```
01_ML_Fundamentals_and_Tools.ipynb
02_Regression_Methods_and_Regularization.ipynb
03_Classification_Algorithms.ipynb
04_Advanced_Algorithms_and_Ensemble_Methods.ipynb
05_Model_Evaluation_and_Metrics.ipynb
06_Model_Refinement_and_Tuning.ipynb
07_Data_Preprocessing_and_Pipelines.ipynb
08_Clustering_and_Dimensionality_Reduction.ipynb
09_Visualization_and_Analysis.ipynb
10_Capstone_Projects_and_Case_Studies.ipynb
```

**覆盖内容**:
- 监督学习：回归、分类、集成方法
- 无监督学习：聚类、降维（PCA, t-SNE, UMAP）
- 模型评估：交叉验证、ROC-AUC、混淆矩阵
- 工程实践：Pipeline、GridSearchCV、特征工程

---

### 3.3 SQL练习

| 位置 | `IBM_datacourse/SQL_practice/` |
|------|------------------------------|
| 内容 | HR数据库、医疗数据库练习 |

**数据集**:
- HR_Database (员工、部门、职位、历史)
- Medical_Database (患者、科室、手术)
- PETRESCUE (宠物救助)

**练习内容**:
- DDL: CREATE TABLE, ALTER
- DML: INSERT, UPDATE, DELETE
- DQL: SELECT, JOIN, 子查询, 聚合函数

---

### 3.4 日常学习笔记

**位置**: `IBM_datacourse/`

| 日期范围 | 主要内容 |
|---------|---------|
| 0522-0530 | Python基础、数据库操作 |
| 0601-0609 | API调用、数据清洗 |
| 0610-0620 | Pandas、NumPy实践 |
| 0621-0630 | 模型训练、EDA |
| 0701-0715 | 数据可视化、ML模型 |
| 0716-0730 | 高级ML、项目实践 |
| 0801-0810 | 综合复习、职业规划 |
| 0814-0818 | Kaggle竞赛学习 |

---

## 四、技能总结

### 4.1 技术能力矩阵

| 类别 | 技能 | 熟练度 | 项目应用 |
|------|------|--------|---------|
| **编程语言** | Python | ★★★★☆ | 全部项目 |
| **数据处理** | Pandas/NumPy | ★★★★☆ | 数据清洗、统计分析 |
| **可视化** | Plotly | ★★★★☆ | 交互式图表、3D可视化 |
| **可视化** | Matplotlib/Seaborn | ★★★★☆ | 静态图表、统计图 |
| **机器学习** | Scikit-learn | ★★★★☆ | 分类、回归、聚类 |
| **数据库** | SQL/SQLite | ★★★☆☆ | 数据查询、存储 |
| **Web开发** | HTML/CSS/JS | ★★★☆☆ | 交互式仪表板 |
| **版本控制** | Git/GitHub | ★★★☆☆ | 项目管理 |
| **数据模拟** | Faker | ★★★☆☆ | 测试数据生成 |

### 4.2 数据分析能力

| 能力领域 | 具体技能 |
|---------|---------|
| 探索性分析 | 描述统计、分布分析、相关性检验 |
| 统计检验 | ANOVA、t-test、Chi-square、正态性检验 |
| 特征工程 | 特征选择、编码、标准化、多项式特征 |
| 机器学习 | 线性/逻辑回归、决策树、随机森林、SVM |
| 模型评估 | 交叉验证、ROC-AUC、F1-score、R² |
| 数据可视化 | 热力图、3D图、Treemap、交互式仪表板 |

### 4.3 领域知识

| 领域 | 知识点 | 来源 |
|------|--------|------|
| 工业安全 | 承包商管理、准入控制 | 工作经验 |
| 合规管理 | 证书有效期、培训要求 | 工作经验 |
| 风险评估 | 隐患分级、整改追踪 | 工作经验 |
| 制造工艺 | 焊接参数、质量控制 | 工作相关 |

---

## 五、职业转型叙事

### 5.1 转型背景

```
安全工程师（3年）→ 数据分析/工程师
     ↓
发现痛点：手工报表、效率低下、缺乏数据驱动决策
     ↓
系统学习：Coursera证书（IBM + Michigan）+ Kaggle
     ↓
实践转化：将工作经验转化为数据分析项目
```

### 5.2 核心竞争力

| 优势 | 说明 |
|------|------|
| **领域知识** | 深入理解工业安全、合规管理业务场景 |
| **问题导向** | 从真实业务痛点出发设计解决方案 |
| **全栈能力** | 数据采集→分析→可视化→报表完整链路 |
| **量化思维** | 用数据说话，效益量化（17000x提升）|

### 5.3 简历项目描述模板

**承包商准入自动化系统** | Python, Pandas, Plotly
- 背景：针对化工项目3000+承包商人员管理效率低的问题
- 职责：设计五维度检查引擎，开发交互式仪表板
- 成果：核查时间从2天→10秒，效率提升17000倍

**隐患排查可视化系统** | Python, Plotly, Pandas
- 背景：解决工业安全隐患数据分散、风险识别滞后
- 职责：设计9区域风险热力图、帕累托分析、3D曲面可视化
- 成果：实现4500+隐患多维度分析，支持数据驱动决策

**SpaceX着陆预测系统** | Python, SQL, Scikit-learn
- 背景：IBM数据科学证书毕业项目
- 职责：完整数据科学流程实施（API采集→ML建模）
- 成果：Decision Tree模型达83.3%预测准确率

---

## GitHub仓库索引

| 仓库 | 内容 | 链接 |
|------|------|------|
| Work_experience_data_analysis | 工作经验转化项目 | [GitHub](https://github.com/SeasonCake/Work_experience_data_analysis) |
| IBM-Data-Science-Capstone-SpaceX | 毕业设计 | [GitHub](https://github.com/SeasonCake/IBM-Data-Science-Capstone-SpaceX) |
| IBM-Machine-Learning-Comprehensive-Recap | ML回顾 | [GitHub](https://github.com/SeasonCake/IBM-Machine-Learning-Comprehensive-Recap) |
| workflow_with_eda_analysis_methods | EDA方法总结 | [GitHub](https://github.com/SeasonCake/workflow_with_eda_analysis_methods) |

---

*文档更新日期: 2026-01-03*

