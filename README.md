# Ginga – Ginger Product Quality Inspection System

Ginga is an edge-AI product quality inspection system designed to classify ginger images directly on a Raspberry Pi.

The system combines a live camera, a TensorFlow Lite image classification model, a FastAPI backend, and a Reflex web interface to provide real-time ginger quality inspection.

## Features

* 📷 Live Raspberry Pi camera streaming
* 🤖 Edge AI image classification
* ⚡ TensorFlow Lite inference
* 🌐 FastAPI backend
* 🖥️ Reflex web interface
* 📊 Prediction confidence display
* 🔍 Camera-based inspection
* 🏠 Hostname-based access using `entra001.local`
* 💻 Designed to run locally on a Raspberry Pi
* 🔒 Image inference can run entirely on the edge device

## System Architecture

```text
                    ┌─────────────────────┐
                    │   Raspberry Pi      │
                    │                     │
                    │   Picamera2         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    FastAPI API      │
                    │      :8000          │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ TensorFlow Lite     │
                    │ Ginger Classifier   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Prediction +        │
                    │ Confidence          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Reflex Frontend     │
                    │      :3000          │
                    │ Backend/WebSocket   │
                    │      :8001          │
                    └─────────────────────┘
```

## Project Structure

```text
r4i-ginger-api/
│
├── backend/
│   ├── app/
│   │   ├── camera.py
│   │   ├── config.py
│   │   ├── inference.py
│   │   └── main.py
│   │
│   ├── models/
│   │   ├── class_names.json
│   │   └── r4i_ginger.tflite
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── assets/
│   │   └── ginja_logo_transparent_512.png
│   │
│   ├── r4i_frontend/
│   │   ├── api.py
│   │   ├── r4i_frontend.py
│   │   ├── state.py
│   │   └── styles.py
│   │
│   ├── requirements.txt
│   └── rxconfig.py
│
├── .gitignore
└── README.md
```

## Backend

The backend is built with FastAPI.

### API

The backend runs on:

```text
http://entra001.local:8000
```

Available endpoints include:

```text
GET  /
GET  /health
GET  /camera/frame
GET  /camera/stream
GET  /classes
GET  /system
POST /predict
POST /predict-camera
```

### Health Check

```bash
curl http://127.0.0.1:8000/health
```

The health endpoint reports:

* API status
* Model status
* Model input shape
* Model input data type
* Model output shape
* Number of classes

## Frontend

The frontend is built using Reflex.

Frontend:

```text
http://entra001.local:3000
```

Reflex backend/WebSocket:

```text
http://entra001.local:8001
```

The frontend communicates with the FastAPI backend using:

```text
http://entra001.local:8000
```

## AI Model

The current model is:

```text
backend/models/r4i_ginger.tflite
```

Input:

```text
256 × 256 × 3
```

Data type:

```text
float32
```

The model is optimized for local inference using TensorFlow Lite/LiteRT.

## Camera

The system uses Raspberry Pi Camera hardware through Picamera2.

The live camera stream is available through:

```text
/camera/stream
```

A single captured frame can be accessed through:

```text
/camera/frame
```

Camera-based prediction is available through:

```text
/predict-camera
```

## Installation

Clone the repository:

```bash
git clone https://github.com/kunluxzeal/Product-Quality-Inspection-.git
cd Product-Quality-Inspection-
```

### Backend

```bash
cd backend
pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend

Open another terminal:

```bash
cd frontend
pip install -r requirements.txt
```

Start Reflex:

```bash
reflex run
```

The application should then be available at:

```text
http://entra001.local:3000
```

## Raspberry Pi Deployment

The target deployment platform is a Raspberry Pi running Raspberry Pi OS/Debian Linux.

The system is designed for local edge deployment where:

```text
Camera → Raspberry Pi → AI inference → Web interface
```

No cloud inference service is required for the core classification workflow.

## Current Classification Pipeline

```text
Camera Image
     │
     ▼
Image Preprocessing
     │
     ▼
256 × 256 × 3
     │
     ▼
TensorFlow Lite Model
     │
     ▼
Class Probabilities
     │
     ▼
Predicted Ginger Class
     │
     ▼
Confidence
     │
     ▼
Ginga Web Interface
```

## Technology Stack

| Component        | Technology               |
| ---------------- | ------------------------ |
| Hardware         | Raspberry Pi             |
| Camera           | Picamera2                |
| Backend          | FastAPI                  |
| AI Model         | TensorFlow Lite / LiteRT |
| Frontend         | Reflex                   |
| Language         | Python                   |
| Image Processing | NumPy / Pillow           |
| API Server       | Uvicorn                  |
| Deployment       | Linux                    |

## Project Goal

The goal of Ginga is to provide an affordable edge-AI solution for automated ginger product quality inspection.

By performing inference locally on the Raspberry Pi, the system can reduce dependence on cloud services and provide a responsive inspection workflow suitable for environments where connectivity may be limited.

## Author

**Kunle Olujimi**

Embedded Systems & Edge AI Engineer

GitHub:

https://github.com/kunluxzeal

## License

This project is currently provided for development and research purposes.
