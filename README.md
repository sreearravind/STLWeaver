---

## AI-powered prompt-to-STL pipeline for generating printable 3D models with support-aware design.

---

## 🚀 Overview

**STLWeaver** is an intelligent pipeline that converts natural language prompts into **print-ready STL files** using AI-generated CAD code.

It integrates LLMs, parametric CAD modeling (`build123d`), and geometry analysis to ensure that generated models are not just creative—but also **manufacturable and printable**.

---

## 🎯 Key Features

- 🧠 **Prompt → CAD → STL Pipeline**
  - Converts text prompts into parametric 3D models

- 🛠️ **Support-Aware Design**
  - Detects overhangs and recommends optimal support structures

- 🔐 **Secure Code Execution**
  - Multi-layer sandboxing (AST validation + Docker execution)

- 🔁 **Iterative Error Correction**
  - Automatically fixes failed CAD generation attempts

- 🔌 **Multi-LLM Support**
  - OpenAI, Anthropic, DeepSeek, TogetherAI, Local models

- 📦 **Mesh Optimization**
  - STL repair, manifold correction, and export readiness

---

## 🏗️ Architecture

```

User Prompt
↓
LLM (Code Generation)
↓
Security Layer (AST + Sandbox)
↓
build123d Geometry Engine
↓
Support Structure Analyzer
↓
STL Export & Optimization

````

This system follows a modular architecture enabling scalability, extensibility, and production deployment. :contentReference[oaicite:0]{index=0}

---

## ⚙️ Tech Stack

| Layer | Technology |
|------|------------|
| API | FastAPI |
| LLM Integration | LiteLLM |
| CAD Engine | build123d |
| Geometry Analysis | trimesh, numpy |
| Security | Docker sandbox |
| Background Jobs | Celery + Redis |
| Database | PostgreSQL |
| Storage | MinIO / S3 |

---

## 🧩 How It Works

1. **User Input**
   - Natural language prompt (e.g., “Create a bracket with holes”)

2. **LLM Code Generation**
   - Generates Python CAD code using `build123d`

3. **Security Validation**
   - AST parsing + restricted execution environment

4. **Geometry Creation**
   - Executes CAD code → generates 3D model

5. **Support Analysis**
   - Detects overhangs (>45°)
   - Recommends support type (tree/grid/line)

6. **STL Export**
   - Mesh repair + optimized STL output

---

## 📡 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /generate` | Submit prompt for STL generation |
| `GET /status/{job_id}` | Check job status |
| `GET /download/{job_id}` | Download STL |
| `GET /health` | Health check |

---

## 🧪 Example Request

```json
POST /generate

{
  "prompt": "Create a 50mm cube with a cylindrical hole through the center",
  "llm_provider": "openai",
  "analyze_supports": true
}
````

---

## 📊 Support Structure Intelligence

STLWeaver analyzes:

* Overhang angles
* Critical regions (>45°)
* Support volume estimation
* Geometry complexity

### Recommended Support Types

* 🌳 Tree → Complex geometries
* 🔲 Grid → Flat overhangs
* ➖ Line → Simple bridges
* ❌ None → Self-supporting designs

---

## 🔐 Security Design

Multi-layer protection:

* AST-based code validation
* Restricted imports (no `os`, `sys`, etc.)
* Docker sandbox execution
* CPU + memory limits
* No network access

---

## 🛠️ Installation

```bash
git clone https://github.com/yourusername/stlweaver.git
cd stlweaver

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

uvicorn orchestrator:app --reload
```

---

## 🐳 Run with Docker

```bash
docker-compose up -d
```

---

## 🧪 Testing

```bash
pytest tests/ -v
```

---

## 📈 Future Roadmap

### Phase 2

* Interactive design chat UI
* Real-time 3D preview
* Printer-specific optimization

### Phase 3

* Image-to-3D generation
* Multi-material STL generation
* Collaborative design system

---

## 🎯 Use Cases

* 3D printing hobbyists
* Mechanical design prototyping
* Educational tools
* Makerspaces & labs
* AI-assisted CAD workflows

---

## 🤝 Contribution

Contributions are welcome!

* Fork the repo
* Create a feature branch
* Submit a pull request

---

## 📄 License

MIT License

---

## 👨‍💻 Author

Developed as part of an AI-driven computational manufacturing initiative focused on bridging **LLMs and ICME-based design workflows**.

---

## ⭐ Vision

STLWeaver aims to become a foundational layer for:

> “AI-assisted manufacturing where ideas directly become manufacturable geometry.”

---
