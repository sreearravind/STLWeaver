# STLWeaver

AI-powered prompt-to-STL pipeline for generating printable 3D models with support-aware analysis.

---

## 🚀 Overview

**STLWeaver** converts natural language prompts into **print-ready STL files** by generating `build123d` CAD code with an LLM, validating that code through a security layer, and exporting analyzed geometry for 3D printing workflows.

The architecture combines multi-LLM support, sandboxed code execution, parametric CAD generation, and support-structure analysis so the pipeline focuses on both model creation and manufacturability.

---

## 🎯 Key Features

- 🧠 **Prompt → CAD → STL Pipeline**
  - Translates natural language prompts into `build123d`-based CAD workflows and STL output

- 🛠️ **Support Structure Intelligence**
  - Detects overhangs and analyzes support needs for downstream printing decisions

- 🔐 **Secure Code Execution**
  - Uses static validation and sandboxed execution to reduce unsafe generated code paths

- 🔁 **Iterative Error Correction**
  - Supports retry and refinement loops when generated CAD code fails validation or execution

- 🔌 **Multi-LLM Support**
  - Designed for multiple providers through LiteLLM-based orchestration

- 📦 **Printability-Focused Output**
  - Combines geometry analysis, mesh repair, and STL export preparation for printable results

---

## 🏗️ Architecture

```
User Prompt
↓
Client Interface (Web UI / CLI / REST API / Desktop)
↓
Orchestrator (FastAPI)
↓
LLM Manager + Prompt Engineering
↓
Security Layer (AST validation + sandbox execution)
↓
build123d Geometry Engine
↓
Support Structure Analyzer (`trimesh` + `numpy`)
↓
STL Export & Optimization
```

This architecture separates request orchestration, model generation, security validation, CAD execution, and printability analysis into modular stages so the pipeline can evolve without collapsing into a single opaque generation step.

---

## ⚙️ Tech Stack

| Layer | Technology | Purpose |
|------|------------|---------|
| API Framework | FastAPI | Request handling and orchestration |
| LLM Orchestration | LiteLLM | Multi-provider model integration |
| CAD Engine | build123d | Programmatic parametric geometry generation |
| Geometry Analysis | trimesh, numpy | Mesh analysis and support-related evaluation |
| Security Layer | AST validation + Docker sandbox | Generated code inspection and isolated execution |
| Async Jobs | Celery + Redis | Background processing and task coordination |
| Database | PostgreSQL | Job metadata and pipeline state |
| Object Storage | MinIO / S3 | STL and generated artifact storage |
| Monitoring | Prometheus + Grafana | Metrics and operational visibility |

---

## 🧩 How It Works

1. **User Input**
   - A user submits a natural language description through the client interface

2. **Request Orchestration**
   - FastAPI coordinates request state, routing, and downstream pipeline execution

3. **LLM Code Generation**
   - The LLM layer generates Python CAD code targeting `build123d`

4. **Security Validation**
   - Generated code is checked with static validation and executed in a restricted sandbox

5. **Geometry Creation**
   - Validated CAD code produces the 3D model geometry

6. **Support Analysis**
   - The geometry is analyzed for overhangs, support volume, and support-type recommendations

7. **STL Export**
   - The final model is repaired and exported as an STL for downstream printing workflows

---

## 📡 API Endpoints

The architecture document defines the following target REST API surface for the service layer:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/generate` | Submit a new prompt-to-STL generation job |
| `GET` | `/status/{job_id}` | Check job status and pipeline progress |
| `GET` | `/download/{job_id}` | Download the generated STL artifact |
| `GET` | `/health` | Health-check endpoint for service monitoring |
| `POST` | `/preview` | Generate a preview-oriented response without a full save flow |
| `GET` | `/providers` | List configured or supported LLM providers |

---

## 🧪 Example Request

```json
POST /generate

{
  "prompt": "Create a 50mm cube with a cylindrical hole through the center",
  "llm_provider": "openai",
  "analyze_supports": true
}
```

---

## 📊 Support Structure Intelligence

The architecture defines a support-analysis stage that evaluates generated geometry for printability signals such as:

* Overhang angles
* Critical regions (>45°)
* Support volume estimation
* Geometry complexity
* Support-type recommendation

### Recommended Support Types

* 🌳 Tree → complex or fine-detail geometries
* 🔲 Grid → larger flat overhang regions
* ➖ Line → simpler bridge-like structures
* ❌ None → self-supporting designs

---

## 🔐 Security Design

The target architecture uses a multi-stage security layer before generated CAD code is allowed to execute:

* AST-based code validation
* Import and unsafe-function restrictions
* Sandboxed Docker execution
* Read-only and resource-limited runtime controls
* No network access

---

## 🛠️ Installation

This repository is currently documentation-first and centered on the architecture definition in [Prompt_to_stl.md](E:\Projects\STLWeaver\STL_Weaver_context\Prompt_to_stl.md).

There is not yet an implementation scaffold in this workspace for:

- application entrypoints
- dependency manifests
- Docker Compose services
- automated test suites

At this stage, the recommended setup is to use the repository as a design and planning reference while the implementation structure is being added incrementally.

---

## 🐳 Run with Docker

Docker deployment is described in the architecture context as a target deployment model, but no Docker configuration is currently present in this repository workspace.

---

## 🧪 Testing

The architecture document includes a proposed testing strategy covering unit, integration, and load testing. The corresponding test files are not yet present in this repository workspace.

---

## 📈 Future Roadmap

### Phase 2

* Interactive design chat UI
* Real-time 3D preview
* Printer-specific optimization
* Print time and cost estimation
* Model sharing or marketplace workflows

### Phase 3

* Fine-tuning for domain-specific design generation
* Image-to-3D generation
* Multi-material STL generation
* Collaborative design system
* Print farm integration

---

## 🎯 Use Cases

* 3D printing hobbyists exploring prompt-driven model generation
* Early-stage mechanical or fixture prototyping workflows
* Educational demonstrations of LLM-assisted CAD pipelines
* Makerspaces and labs evaluating AI-assisted fabrication tooling
* Teams designing prompt-to-geometry systems for manufacturing workflows

---

## 🤝 Contribution

Contributions are welcome, especially around implementation planning, architecture refinement, and future service scaffolding.

* Open an issue to discuss architecture or scope changes
* Propose focused README or design-document improvements
* Submit implementation scaffolding in small, reviewable increments

---

## 📄 License

MIT

---

## 👨‍💻 Author

STLWeaver is currently maintained as an early-stage architecture and repository concept for AI-assisted CAD and manufacturable geometry generation.

---

## ⭐ Vision

STLWeaver is intended to evolve into a practical prompt-to-geometry platform where natural language, CAD generation, and printability analysis can be combined in a single workflow.

---
