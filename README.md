# Reefshield

**AI-Powered Coral Reef Monitoring & Early Warning System**

Reefshield leverages 40+ years of NOAA Sea Surface Temperature (SST) satellite data to predict thermal stress events that threaten coral reefs worldwide. Using advanced time series forecasting, the system predicts SST anomalies 7 days in advance and sends real-time alerts when temperatures cross critical bleaching thresholds.

<img width="800" height="408" alt="Image" src="https://github.com/user-attachments/assets/4b415656-cd59-43d6-b3c4-bf69e9f72efa" />
---

## Problem Statement

Coral reefs are among the most biodiverse ecosystems on Earth, yet they face existential threats from rising ocean temperatures. Mass bleaching events occur when sea surface temperatures remain elevated for extended periods, but by the time traditional monitoring detects these events, it's often too late for intervention.

**Reefshield provides the critical early warning window needed for proactive reef management.**

---

## Key Features

- **7-Day Advance Prediction**: Time series forecasting models predict SST anomalies a week before they occur
- **Real-Time Alerting**: Automated notifications when temperatures approach or exceed bleaching thresholds
- **Historical Analysis**: Interactive visualization of 40+ years of NOAA satellite data
- **Location-Based Monitoring**: Track specific reef locations globally
- **Threshold Customization**: Configure alert thresholds based on local coral species resilience

---

## Architecture

### Backend
- **FastAPI** - High-performance async APIs for ML inference
- **NOAA SST Dataset** - 40+ years of satellite-derived sea surface temperature data
- **Time Series Models** - LSTM-based forecasting for temperature prediction
- **Alert System** - Real-time notification engine for threshold breaches

### Frontend
- **Next.js** - Modern React framework for interactive data visualization
- **Mapping Interface** - Geographic visualization of reef locations and temperature data
- **Dashboard** - Real-time SST trends, predictions, and alert management
- **Data Explorer** - Historical temperature analysis and pattern recognition

---
<img width="1897" height="1035" alt="Image" src="https://github.com/user-attachments/assets/6007f05d-0a05-4e5f-a437-f386210d4756" />

<img width="1893" height="1037" alt="Image" src="https://github.com/user-attachments/assets/47076461-4263-4580-a283-82c1550b5c6c" />

---
## Getting Started

### Prerequisites
```bash
Python 3.9+
Node.js 18+
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## Future Roadmap

- [ ] Multi-model ensemble for improved prediction accuracy
- [ ] Integration with additional environmental factors (pH, salinity, current patterns)
- [ ] Mobile app for field researchers
- [ ] Coral bleaching severity prediction (not just temperature)
- [ ] Community reporting system for ground-truth validation

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---
