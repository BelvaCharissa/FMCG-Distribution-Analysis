# FMCG Distribution & Supply Chain Analytics

## Overview

FMCG Distribution & Supply Chain Analytics is an interactive analytics dashboard designed to evaluate and optimize distribution network performance in the Fast-Moving Consumer Goods (FMCG) industry.

The application integrates sales performance, delivery operations, inventory availability, and geographic data to provide actionable insights into distribution efficiency across the Jabodetabek region. The analysis covers 1,250 retail outlets and three Distribution Centers (DCs): Ciracas, Cikarang, and Bitung.

By translating operational data into visual insights, the dashboard helps identify distribution bottlenecks, prioritize outlets requiring intervention, and evaluate potential improvements in logistics and inventory management.

<img width="951" height="875" alt="image" src="https://github.com/user-attachments/assets/ccc817cb-738a-431d-be03-ed781f62c682" />

## Key Features

### 1. Interactive Distribution Map

Visualizes retail outlets and distribution centers across Jabodetabek to support geographic analysis of distribution performance.

Key capabilities:
- Display of 1,250 retail outlets and three distribution centers.
- Color-coded outlet markers based on operational urgency and stockout conditions.
- Outlet-level performance details, including 90-day revenue, stockout rate, average delivery delay, and recommended actions.

### 2. Operational Diagnostics

Identifies key distribution challenges by analyzing inventory availability, delivery performance, revenue contribution, and distribution center workload.

The dashboard highlights the following operational findings:

- **Regional Stockout Issues:** The southern subregion records a stockout rate of 35.5%, accompanied by an average delivery delay of 87.8 minutes.
- **Low-Efficiency Delivery Routes:** A group of 146 remote outlets contributes 11.1% of total revenue while experiencing an average delivery delay of 50.2 minutes.
- **Uneven Distribution Center Workload:** The Ciracas Distribution Center handles more than 58% of the network's total volume, indicating a potential imbalance in operational capacity.

These findings help identify areas where improvements in inventory planning, delivery allocation, and distribution network design may have the greatest impact.

### 3. Outlet Priority Matrix

Classifies retail outlets into four operational categories based on demand and stockout rates. This segmentation supports more targeted inventory and delivery decisions.

| Category | Conditions | Recommended Action |
|---|---|---|
| Top Priority | High demand, high stockout rate | Prioritize replenishment and investigate recurring stockouts. |
| Maintain Supply | High demand, low stockout rate | Maintain inventory availability and service levels. |
| Evaluate Delivery | Low demand, high stockout rate | Review delivery frequency, minimum order quantities, and replenishment policies. |
| Routine Monitoring | Low demand, low stockout rate | Continue routine monitoring and standard replenishment. |

The matrix helps distinguish outlets that require immediate intervention from those that can be managed through standard operating procedures.

### 4. What-If Scenario Simulation

Evaluates potential operational improvements through adjustable simulation parameters.

Users can modify delivery delay and safety stock assumptions to estimate their potential impact on:
- Recovered revenue from reduced stockouts and improved product availability.
- Fuel efficiency resulting from potential improvements in distribution operations.

The simulation supports scenario comparison and preliminary decision-making by illustrating how changes in operational assumptions may affect business outcomes.

*Simulation results represent model-based estimates and should not be interpreted as guaranteed real-world improvements.*

## Business Value

The dashboard is designed to support data-driven distribution decisions in four key areas:

- **Inventory Optimization:** Identify outlets with recurring stockouts and prioritize replenishment.
- **Logistics Efficiency:** Evaluate remote outlets and potential delivery allocation improvements.
- **Distribution Network Balancing:** Identify workload concentration across distribution centers.
- **Scenario Evaluation:** Estimate the potential business impact of alternative operational strategies before implementation.

## Technology Stack

The project uses Python for application development and data analysis, supported by interactive data visualization and geographic mapping components.

The specific libraries, mapping services, and data-processing tools depend on the implementation available in this repository.

## Getting Started

### Prerequisites

- Python 3.10 or a compatible version supported by the project.
- Git.
- Required Python packages listed in the project's dependency file, if provided.

### Installation

Clone the repository:

```bash
git clone https://github.com/BelvaCharissa/FMCG-Distribution-Analysis.git
```

Navigate to the project directory:

```bash
cd FMCG-Distribution-Analysis
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

If the repository does not include a `requirements.txt` file, install the dependencies specified by the project configuration.

### Run the Application

Start the application using the following command:

```bash
python app.py
```

Open the local URL displayed in the terminal to access the dashboard, if the application starts a local web server.

## Project Scope

This project focuses on distribution performance analytics, outlet prioritization, and operational scenario evaluation using sales, delivery, inventory, and geographic information.

The dashboard is intended as a decision-support tool for exploring operational patterns and identifying opportunities for improvement. The reliability of the insights depends on the quality of the underlying data, analytical assumptions, and simulation methodology.

## Repository

GitHub: https://github.com/BelvaCharissa/FMCG-Distribution-Analysis
