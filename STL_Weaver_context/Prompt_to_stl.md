# AI Prompt to STL Pipeline - Complete Architecture Document

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Core Architecture](#core-architecture)
3. [Component Deep Dive](#component-deep-dive)
4. [Security Implementation](#security-implementation)
5. [Support Structure System](#support-structure-system)
6. [API Design](#api-design)
7. [Data Models](#data-models)
8. [Error Handling](#error-handling)
9. [Deployment Architecture](#deployment-architecture)
10. [Performance Optimization](#performance-optimization)
11. [Testing Strategy](#testing-strategy)
12. [Future Enhancements](#future-enhancements)

---

## System Overview

### Purpose
Convert natural language prompts into printable STL files with automatic support structure recommendation, using LLM-generated `build123d` Python code executed in a secure sandbox.

### Target Users
- 3D printing hobbyists
- Product designers
- Educators
- Makerspace operators

### Key Differentiators
- **Support structure intelligence** - Automatic overhang detection and support recommendation
- **Multi-LLM support** - Bring your own API key (OpenAI, Anthropic, DeepSeek, Local)
- **Secure execution** - Multi-layer sandboxing prevents malicious code execution
- **Iterative correction** - Automatic error recovery and code refinement

---

## Core Architecture

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Client Interface                               │
│                    (Web UI / CLI / REST API / Desktop)                   │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Orchestrator (FastAPI)                            │
│                    Request Routing & State Management                    │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        LLM Manager (LiteLLM)                             │
│         OpenAI │ Anthropic │ DeepSeek │ TogetherAI │ Local              │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Code Generator (Prompt Engineering)                   │
│         System Prompts │ Few-shot Examples │ Dynamic Context            │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Security Layer (Multi-stage)                          │
│      AST Analysis │ Import Validation │ Sandbox Execution                │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Geometry Engine (build123d)                           │
│            CAD Operations │ Boolean Ops │ Parametric Design              │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              Support Structure Analyzer (trimesh + numpy)                │
│     Overhang Detection │ Support Volume Calc │ Type Recommendation       │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      STL Exporter & Optimizer                           │
│    Mesh Repair │ Binary STL │ Quality Settings │ Slicer Integration     │
└─────────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **API Framework** | FastAPI | 0.104+ | Async request handling, OpenAPI docs |
| **LLM Orchestration** | LiteLLM | 1.0+ | Unified interface for 100+ LLMs |
| **CAD Engine** | build123d | 0.6+ | Programmatic CAD generation |
| **Geometry Processing** | trimesh | 3.23+ | Mesh analysis, support detection |
| **Security** | Docker SDK | 6.1+ | Containerized code execution |
| **Async Tasks** | Celery | 5.3+ | Background job processing |
| **Message Broker** | Redis | 7.0+ | Task queue & caching |
| **Database** | PostgreSQL | 15+ | Job storage, user data |
| **Object Storage** | MinIO / S3 | Latest | STL file storage |
| **Monitoring** | Prometheus + Grafana | Latest | Metrics & visualization |
| **Logging** | ELK Stack | 8.x | Centralized logging |

---

## Component Deep Dive

### 1. LLM Manager Component

```python
# llm_manager.py
from litellm import completion, acompletion
from typing import Optional, Dict, Any
import asyncio

class LLMManager:
    """Manages multiple LLM providers with unified interface"""
    
    SUPPORTED_PROVIDERS = {
        "openai": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
        "anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
        "deepseek": ["deepseek-chat", "deepseek-coder"],
        "together": ["llama-2-70b", "mistral-7b"],
        "local": ["ollama/llama2", "local/any-model"]
    }
    
    def __init__(self, default_provider: str = "openai"):
        self.default_provider = default_provider
        self.api_keys = {}  # Load from environment or database
        
    async def generate_code(
        self, 
        prompt: str, 
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """
        Generate build123d code from natural language prompt
        
        Returns:
            {
                "code": "generated python code",
                "model_used": "gpt-4",
                "tokens_used": 1250,
                "cost": 0.0025
            }
        """
        provider = provider or self.default_provider
        
        system_prompt = self._get_system_prompt()
        few_shot_examples = self._get_few_shot_examples()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": few_shot_examples},
            {"role": "user", "content": f"Generate code for: {prompt}"}
        ]
        
        response = await acompletion(
            model=f"{provider}/{model}" if model else provider,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key or self.api_keys.get(provider)
        )
        
        return {
            "code": self._extract_code(response.choices[0].message.content),
            "model_used": response.model,
            "tokens_used": response.usage.total_tokens,
            "cost": self._calculate_cost(response.usage, provider)
        }
    
    def _get_system_prompt(self) -> str:
        """Returns the system prompt that guides LLM to generate build123d code"""
        return """
        You are an expert Python programmer specializing in build123d for 3D CAD modeling.
        
        RULES:
        1. ONLY use build123d imports (from build123d import *)
        2. NEVER import os, sys, subprocess, or any dangerous modules
        3. ALWAYS wrap code in a function named 'create_model()' that returns a Part
        4. INCLUDE proper dimensions (all measurements in millimeters)
        5. USE parametric variables at the top of the function
        6. ADD comments explaining each major operation
        7. ENSURE models are manifold (watertight)
        8. AVOID zero-thickness features
        9. USE appropriate build123d operations: extrude, revolve, loft, sweep
        10. INCLUDE chamfers/fillets for printability when appropriate
        
        Example structure:
        ```python
        from build123d import *
        
        def create_model():
            # Parameters
            width = 50
            height = 30
            depth = 40
            
            # Create base
            with BuildPart() as context:
                Box(width, height, depth)
                # Add features...
                return context.part
        ```
        """
    
    def _get_few_shot_examples(self) -> str:
        """Returns few-shot examples for better code generation"""
        return """
        Example 1: Simple cube with hole
        User: "Create a 50mm cube with a 20mm cylindrical hole through the center"
        
        Response:
        ```python
        from build123d import *
        
        def create_model():
            # Parameters
            cube_size = 50
            hole_diameter = 20
            
            with BuildPart() as context:
                # Create the base cube
                Box(cube_size, cube_size, cube_size)
                
                # Create cylindrical hole
                with BuildSketch(context.faces().sort_by(Axis.Z)[-1]) as sketch:
                    Circle(hole_diameter / 2)
                
                extrude(amount=-cube_size, mode=Mode.SUBTRACT)
                
                return context.part
        ```
        
        Example 2: Parametric bracket
        User: "Create an L-shaped bracket 60mm wide, 40mm tall, 10mm thick with two 5mm mounting holes"
        
        Response:
        ```python
        from build123d import *
        
        def create_model():
            # Parameters
            width = 60
            height = 40
            thickness = 10
            hole_diameter = 5
            
            with BuildPart() as context:
                # Horizontal base
                Box(width, thickness, thickness, align=(Align.CENTER, Align.MIN, Align.MIN))
                
                # Vertical wall
                Box(thickness, thickness, height, align=(Align.CENTER, Align.MIN, Align.MIN))
                
                # Add mounting holes
                with Locations((width/4, 0, 0)):
                    Cylinder(hole_diameter/2, thickness, mode=Mode.SUBTRACT)
                with Locations((-width/4, 0, 0)):
                    Cylinder(hole_diameter/2, thickness, mode=Mode.SUBTRACT)
                
                return context.part
        ```
        """
```

### 2. Security Layer Implementation

```python
# security.py
import ast
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple, List
import docker
from docker.errors import ContainerError, ImageNotFound

class SecurityValidator:
    """Multi-layer security validation for generated code"""
    
    ALLOWED_IMPORTS = {
        'build123d', 'cadquery', 'math', 'numpy', 
        'typing', 'dataclasses', 'enum'
    }
    
    DANGEROUS_MODULES = {'os', 'sys', 'subprocess', 'socket', 
                         'requests', 'urllib', 'shutil', 'glob'}
    
    DANGEROUS_FUNCTIONS = {
        'eval', 'exec', 'compile', '__import__', 'open', 
        'file', 'input', 'raw_input', 'execfile', 'reload'
    }
    
    def __init__(self, use_docker: bool = True):
        self.use_docker = use_docker
        if use_docker:
            self.docker_client = docker.from_env()
    
    def validate_code(self, code: str) -> Tuple[bool, List[str]]:
        """
        First layer: Static analysis via AST
        Returns (is_safe, list_of_violations)
        """
        violations = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, [f"Syntax error: {e}"]
        
        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    if module_name in self.DANGEROUS_MODULES:
                        violations.append(f"Dangerous import: {module_name}")
                    elif module_name not in self.ALLOWED_IMPORTS:
                        violations.append(f"Unallowed import: {module_name}")
            
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module.split('.')[0] if node.module else ''
                if module_name in self.DANGEROUS_MODULES:
                    violations.append(f"Dangerous import from: {module_name}")
            
            # Check dangerous function calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.DANGEROUS_FUNCTIONS:
                        violations.append(f"Dangerous function call: {node.func.id}")
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in self.DANGEROUS_FUNCTIONS:
                        violations.append(f"Dangerous attribute call: {node.func.attr}")
            
            # Check attribute access
            elif isinstance(node, ast.Attribute):
                if node.attr in ['system', 'popen', 'popen2', 'popen3', 'popen4']:
                    violations.append(f"Dangerous attribute: {node.attr}")
        
        return len(violations) == 0, violations
    
    def execute_sandboxed(self, code: str, timeout: int = 30) -> Tuple[bool, str, bytes]:
        """
        Second layer: Sandboxed execution
        Returns (success, stdout, stderr)
        """
        if self.use_docker:
            return self._execute_in_docker(code, timeout)
        else:
            return self._execute_in_subprocess(code, timeout)
    
    def _execute_in_docker(self, code: str, timeout: int) -> Tuple[bool, str, bytes]:
        """Execute code in isolated Docker container"""
        
        dockerfile = """
        FROM python:3.11-slim
        
        RUN pip install build123d cadquery numpy trimesh
        
        WORKDIR /app
        COPY script.py /app/script.py
        
        RUN useradd -m -s /bin/bash sandbox
        USER sandbox
        
        CMD ["python", "-c", "import script; result = script.create_model(); print('SUCCESS')"]
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as script_file:
            script_file.write(code)
            script_file.flush()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.Dockerfile') as docker_file:
                docker_file.write(dockerfile)
                docker_file.flush()
                
                try:
                    # Build image
                    image, logs = self.docker_client.images.build(
                        path=tempfile.gettempdir(),
                        dockerfile=docker_file.name,
                        rm=True
                    )
                    
                    # Run container with restrictions
                    container = self.docker_client.containers.run(
                        image.id,
                        network_disabled=True,  # No network access
                        mem_limit='512m',       # Memory limit
                        nano_cpus=int(1e9),      # 1 CPU limit
                        read_only=True,          # Read-only filesystem
                        remove=True,
                        timeout=timeout,
                        detach=False
                    )
                    
                    return True, container.decode('utf-8'), b''
                    
                except ContainerError as e:
                    return False, '', e.stderr
                except Exception as e:
                    return False, '', str(e).encode()
    
    def _execute_in_subprocess(self, code: str, timeout: int) -> Tuple[bool, str, bytes]:
        """Fallback: Execute in restricted subprocess (less secure)"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
            f.write(code)
            f.flush()
            
            # Create restricted environment
            env = {
                'PATH': '/usr/local/bin:/usr/bin:/bin',
                'HOME': '/tmp/sandbox',
                'PYTHONPATH': ''
            }
            
            try:
                result = subprocess.run(
                    ['python', '-c', f'import {Path(f.name).stem}; create_model()'],
                    timeout=timeout,
                    capture_output=True,
                    text=True,
                    env=env,
                    cwd='/tmp/sandbox'  # Execute in safe directory
                )
                
                return result.returncode == 0, result.stdout, result.stderr.encode()
                
            except subprocess.TimeoutExpired:
                return False, '', b'Execution timeout'
            except Exception as e:
                return False, '', str(e).encode()
```

### 3. Geometry Engine & Support Structure System

```python
# geometry_engine.py
import build123d as bd
from build123d import *
import trimesh
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import tempfile

@dataclass
class SupportRecommendation:
    """Data structure for support structure recommendations"""
    needs_supports: bool
    critical_overhangs_count: int
    total_overhang_area: float  # mm²
    support_volume: float  # mm³
    recommended_type: str  # 'tree', 'grid', 'line', 'none'
    complexity: str  # 'low', 'medium', 'high'
    visualization_data: Dict  # For frontend display
    suggested_settings: Dict  # Printer-specific settings

class GeometryProcessor:
    """Handles build123d geometry generation and analysis"""
    
    def __init__(self):
        self.overhang_threshold = 45  # degrees - standard for FDM printers
        self.layer_height = 0.2  # mm - typical layer height
        
    def execute_generated_code(self, code: str) -> Optional[Part]:
        """
        Execute the generated build123d code and return the Part object
        """
        # Create a new namespace for execution
        namespace = {
            'build123d': bd,
            'Part': Part,
            # Add all build123d exports
            **{name: getattr(bd, name) for name in dir(bd) 
               if not name.startswith('_')}
        }
        
        try:
            # Execute the code
            exec(code, namespace)
            
            # Call the create_model function
            if 'create_model' in namespace:
                model = namespace['create_model']()
                return model
            else:
                raise ValueError("Generated code must contain 'create_model()' function")
                
        except Exception as e:
            raise RuntimeError(f"Execution failed: {str(e)}")
    
    def export_to_stl(self, part: Part, filepath: str, binary: bool = True):
        """Export Part to STL file"""
        part.export_stl(filepath, binary=binary)
    
    def repair_mesh(self, stl_path: str) -> str:
        """
        Repair common mesh issues using trimesh
        Returns path to repaired STL
        """
        mesh = trimesh.load(stl_path)
        
        # Fix common issues
        if not mesh.is_watertight:
            mesh = trimesh.repair.fill_holes(mesh)
        
        if not mesh.is_volume:
            mesh = trimesh.repair.fix_inversion(mesh)
        
        # Remove duplicate vertices
        mesh.merge_vertices()
        
        # Remove degenerate faces
        mesh.remove_degenerate_faces()
        
        # Export repaired mesh
        repaired_path = stl_path.replace('.stl', '_repaired.stl')
        mesh.export(repaired_path, 'stl')
        
        return repaired_path

class SupportStructureAnalyzer:
    """Analyzes geometry and recommends support structures"""
    
    def __init__(self, geometry_processor: GeometryProcessor):
        self.geometry_processor = geometry_processor
        self.overhang_angle_threshold = 45
        self.support_margin = 0.5  # mm gap between support and model
        
    def analyze_support_needs(self, part: Part) -> SupportRecommendation:
        """
        Main entry point for support structure analysis
        """
        # Export part to temporary STL for analysis
        with tempfile.NamedTemporaryFile(suffix='.stl') as tmp_file:
            self.geometry_processor.export_to_stl(part, tmp_file.name)
            mesh = trimesh.load(tmp_file.name)
            
            # Perform analysis
            overhang_faces = self._detect_overhangs(mesh)
            support_volume = self._calculate_support_volume(mesh, overhang_faces)
            support_type = self._recommend_support_type(mesh, overhang_faces)
            
            return SupportRecommendation(
                needs_supports=len(overhang_faces) > 0,
                critical_overhangs_count=self._count_critical_overhangs(overhang_faces),
                total_overhang_area=self._calculate_overhang_area(overhang_faces),
                support_volume=support_volume,
                recommended_type=support_type,
                complexity=self._assess_complexity(mesh, overhang_faces),
                visualization_data=self._generate_visualization_data(mesh, overhang_faces),
                suggested_settings=self._get_suggested_settings(support_type)
            )
    
    def _detect_overhangs(self, mesh: trimesh.Trimesh) -> List[int]:
        """
        Detect faces that exceed the overhang angle threshold
        Returns list of face indices that need supports
        """
        # Calculate face normals relative to build direction (Z-axis)
        build_direction = np.array([0, 0, 1])
        
        overhang_faces = []
        
        for face_idx, face in enumerate(mesh.faces):
            # Get face normal
            face_normal = mesh.face_normals[face_idx]
            
            # Calculate angle between face normal and build direction
            dot_product = np.dot(face_normal, build_direction)
            angle = np.arccos(np.clip(dot_product, -1, 1)) * 180 / np.pi
            
            # Face needs support if angle > threshold (overhang)
            if angle > self.overhang_angle_threshold:
                overhang_faces.append(face_idx)
        
        return overhang_faces
    
    def _calculate_support_volume(self, mesh: trimesh.Trimesh, 
                                   overhang_faces: List[int]) -> float:
        """
        Estimate the volume of support material needed
        """
        if not overhang_faces:
            return 0.0
        
        # Create a subset mesh of just overhang faces
        overhang_mesh = mesh.submesh([overhang_faces], append=True)
        
        # Project overhang area downward to calculate support volume
        # Simplified: area * average height of support structures
        overhang_area = self._calculate_overhang_area(overhang_faces)
        
        # Estimate average support height (distance from overhang to build plate)
        # Get minimum Z coordinate of overhang faces
        min_z = np.min(overhang_mesh.vertices[:, 2])
        
        # Support volume = area * height * density factor (typical: 0.3 for tree supports)
        support_volume = overhang_area * min_z * 0.3
        
        return support_volume
    
    def _calculate_overhang_area(self, overhang_faces: List[int]) -> float:
        """Calculate total area of overhanging faces"""
        # This would sum the area of each overhang face
        # Placeholder implementation
        return 0.0
    
    def _count_critical_overhangs(self, overhang_faces: List[int]) -> int:
        """Count overhangs exceeding 60 degrees (critical)"""
        # Implementation would filter faces with angle > 60°
        return len([f for f in overhang_faces if f])  # Simplified
    
    def _recommend_support_type(self, mesh: trimesh.Trimesh, 
                                 overhang_faces: List[int]) -> str:
        """
        Recommend support structure type based on geometry
        Returns: 'tree', 'grid', 'line', or 'none'
        """
        if not overhang_faces:
            return 'none'
        
        # Analyze characteristics
        overhang_mesh = mesh.submesh([overhang_faces], append=True)
        
        # Check if overhangs are large flat areas
        flat_areas = self._detect_large_flat_overhangs(overhang_mesh)
        
        # Check for intricate details
        intricate_details = self._detect_intricate_details(overhang_mesh)
        
        if intricate_details:
            return 'tree'  # Tree supports for complex geometry
        elif flat_areas:
            return 'grid'  # Grid supports for flat overhangs
        else:
            return 'line'  # Simple line supports for bridges
    
    def _detect_large_flat_overhangs(self, mesh: trimesh.Trimesh) -> bool:
        """Check if there are large flat overhanging surfaces"""
        # Simplified - would analyze face areas and normals
        return False
    
    def _detect_intricate_details(self, mesh: trimesh.Trimesh) -> bool:
        """Check for fine details that need tree supports"""
        # Simplified - would analyze edge length and curvature
        return True
    
    def _assess_complexity(self, mesh: trimesh.Trimesh, 
                           overhang_faces: List[int]) -> str:
        """Assess overall print complexity"""
        if len(overhang_faces) > 1000:
            return 'high'
        elif len(overhang_faces) > 100:
            return 'medium'
        else:
            return 'low'
    
    def _generate_visualization_data(self, mesh: trimesh.Trimesh, 
                                      overhang_faces: List[int]) -> Dict:
        """Generate data for frontend visualization of support needs"""
        # Create a colored mesh where overhangs are highlighted
        colors = np.ones((len(mesh.faces), 4)) * [0.5, 0.5, 0.5, 1.0]  # Gray default
        
        for face_idx in overhang_faces:
            colors[face_idx] = [1.0, 0.0, 0.0, 1.0]  # Red for overhangs
        
        return {
            'vertices': mesh.vertices.tolist(),
            'faces': mesh.faces.tolist(),
            'face_colors': colors.tolist(),
            'overhang_indices': overhang_faces
        }
    
    def _get_suggested_settings(self, support_type: str) -> Dict:
        """Get printer-specific suggested settings based on support type"""
        settings = {
            'tree': {
                'support_structure': 'tree',
                'support_angle': 45,
                'support_density': 15,
                'support_z_distance': 0.2,
                'support_xy_distance': 0.7
            },
            'grid': {
                'support_structure': 'grid',
                'support_angle': 60,
                'support_density': 20,
                'support_z_distance': 0.2,
                'support_xy_distance': 0.5
            },
            'line': {
                'support_structure': 'line',
                'support_angle': 50,
                'support_density': 10,
                'support_z_distance': 0.3,
                'support_xy_distance': 0.8
            },
            'none': {}
        }
        
        return settings.get(support_type, settings['tree'])
    
    def generate_support_geometry(self, part: Part, 
                                   recommendation: SupportRecommendation) -> Optional[Part]:
        """
        Generate actual support geometry as build123d Part
        (Advanced feature - would implement actual support generation)
        """
        if not recommendation.needs_supports:
            return None
        
        # This would generate actual support structures using build123d
        # Complex implementation - would create lattice/tree structures
        # based on the support type and geometry analysis
        
        # Placeholder
        return None
```

### 4. Main Orchestrator

```python
# orchestrator.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import uuid4
import asyncio
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
app = FastAPI(title="AI Prompt to STL Pipeline", version="1.0.0")
llm_manager = LLMManager()
security_validator = SecurityValidator(use_docker=True)
geometry_processor = GeometryProcessor()
support_analyzer = SupportStructureAnalyzer(geometry_processor)

# Job storage (in production, use database)
jobs = {}

class GenerateRequest(BaseModel):
    """Request model for STL generation"""
    prompt: str = Field(..., description="Natural language description of 3D model")
    llm_provider: Optional[str] = Field("openai", description="LLM provider to use")
    llm_model: Optional[str] = Field(None, description="Specific model name")
    api_key: Optional[str] = Field(None, description="API key for the LLM provider")
    temperature: float = Field(0.3, ge=0, le=1, description="Creativity of generation")
    analyze_supports: bool = Field(True, description="Whether to analyze support needs")
    auto_repair: bool = Field(True, description="Auto-repair mesh issues")
    include_visualization: bool = Field(True, description="Include support visualization")

class GenerateResponse(BaseModel):
    """Response model for generation request"""
    job_id: str
    status: str
    estimated_time: int  # seconds
    message: str

class JobStatus(BaseModel):
    """Job status response"""
    job_id: str
    status: str  # pending, processing, completed, failed
    created_at: datetime
    completed_at: Optional[datetime]
    stl_url: Optional[str]
    support_recommendation: Optional[Dict]
    error_message: Optional[str]
    metadata: Optional[Dict]

@app.post("/generate", response_model=GenerateResponse)
async def generate_stl(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Submit a prompt for STL generation
    """
    job_id = str(uuid4())
    
    jobs[job_id] = {
        "id": job_id,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "request": request.dict(),
        "result": None
    }
    
    # Process in background
    background_tasks.add_task(
        process_generation_job,
        job_id,
        request
    )
    
    return GenerateResponse(
        job_id=job_id,
        status="pending",
        estimated_time=30,  # seconds
        message="Job submitted successfully"
    )

@app.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Check the status of a generation job
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        created_at=job["created_at"],
        completed_at=job.get("completed_at"),
        stl_url=job.get("stl_url"),
        support_recommendation=job.get("support_recommendation"),
        error_message=job.get("error_message"),
        metadata=job.get("metadata")
    )

@app.get("/download/{job_id}")
async def download_stl(job_id: str):
    """
    Download the generated STL file
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    stl_path = job.get("stl_path")
    if not stl_path or not Path(stl_path).exists():
        raise HTTPException(status_code=404, detail="STL file not found")
    
    return FileResponse(
        stl_path,
        media_type="model/stl",
        filename=f"{job_id}.stl"
    )

async def process_generation_job(job_id: str, request: GenerateRequest):
    """
    Background task to process STL generation
    """
    try:
        logger.info(f"Starting job {job_id}")
        jobs[job_id]["status"] = "processing"
        
        # Step 1: Generate code using LLM
        logger.info(f"Generating code for prompt: {request.prompt[:100]}")
        generation_result = await llm_manager.generate_code(
            prompt=request.prompt,
            provider=request.llm_provider,
            api_key=request.api_key,
            model=request.llm_model,
            temperature=request.temperature
        )
        
        generated_code = generation_result["code"]
        
        # Step 2: Security validation
        logger.info("Validating generated code")
        is_safe, violations = security_validator.validate_code(generated_code)
        
        if not is_safe:
            raise ValueError(f"Security violations: {', '.join(violations)}")
        
        # Step 3: Execute in sandbox
        logger.info("Executing code in sandbox")
        success, stdout, stderr = security_validator.execute_sandboxed(generated_code)
        
        if not success:
            raise RuntimeError(f"Execution failed: {stderr.decode()}")
        
        # Step 4: Generate geometry
        logger.info("Creating geometry")
        part = geometry_processor.execute_generated_code(generated_code)
        
        # Step 5: Export to temporary STL
        temp_stl_path = f"/tmp/{job_id}_raw.stl"
        geometry_processor.export_to_stl(part, temp_stl_path)
        
        # Step 6: Repair if requested
        if request.auto_repair:
            logger.info("Repairing mesh")
            final_stl_path = geometry_processor.repair_mesh(temp_stl_path)
        else:
            final_stl_path = temp_stl_path
        
        # Step 7: Analyze support structures
        support_recommendation = None
        if request.analyze_supports:
            logger.info("Analyzing support needs")
            support_recommendation = support_analyzer.analyze_support_needs(part)
            support_recommendation = support_recommendation.__dict__
        
        # Step 8: Store results
        jobs[job_id].update({
            "status": "completed",
            "completed_at": datetime.utcnow(),
            "stl_path": final_stl_path,
            "stl_url": f"/download/{job_id}",
            "support_recommendation": support_recommendation,
            "metadata": {
                "model_used": generation_result["model_used"],
                "tokens_used": generation_result["tokens_used"],
                "cost": generation_result["cost"]
            }
        })
        
        logger.info(f"Job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}")
        jobs[job_id].update({
            "status": "failed",
            "completed_at": datetime.utcnow(),
            "error_message": str(e)
        })
```

---

## API Design

### REST API Endpoints

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/generate` | Submit new generation job | `GenerateRequest` | `GenerateResponse` |
| GET | `/status/{job_id}` | Check job status | - | `JobStatus` |
| GET | `/download/{job_id}` | Download STL file | - | STL binary |
| GET | `/health` | Health check | - | `{"status": "ok"}` |
| GET | `/metrics` | Prometheus metrics | - | Metrics text |
| POST | `/preview` | Generate preview without saving | `GenerateRequest` | `PreviewResponse` |
| GET | `/providers` | List supported LLM providers | - | `ProviderList` |

### WebSocket API (Optional)

```python
# For real-time updates
@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await websocket.accept()
    
    while jobs[job_id]["status"] not in ["completed", "failed"]:
        await websocket.send_json({
            "status": jobs[job_id]["status"],
            "progress": get_progress(job_id)
        })
        await asyncio.sleep(1)
    
    await websocket.close()
```

---

## Data Models

### Database Schema (PostgreSQL)

```sql
-- Jobs table
CREATE TABLE jobs (
    id UUID PRIMARY KEY,
    user_id UUID,
    prompt TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    llm_provider VARCHAR(50),
    llm_model VARCHAR(100),
    tokens_used INTEGER,
    cost DECIMAL(10, 6),
    stl_size_bytes INTEGER,
    support_type VARCHAR(20),
    error_message TEXT
);

-- Generated files metadata
CREATE TABLE files (
    id UUID PRIMARY KEY,
    job_id UUID REFERENCES jobs(id),
    file_type VARCHAR(20), -- 'stl', 'preview', '3mf'
    file_path VARCHAR(500),
    file_size INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Support analysis results
CREATE TABLE support_analysis (
    id UUID PRIMARY KEY,
    job_id UUID REFERENCES jobs(id),
    needs_supports BOOLEAN,
    overhang_area DECIMAL(10, 2),
    support_volume DECIMAL(10, 2),
    recommended_type VARCHAR(20),
    complexity VARCHAR(10),
    analysis_data JSONB
);

-- User API keys (encrypted)
CREATE TABLE user_api_keys (
    id UUID PRIMARY KEY,
    user_id UUID,
    provider VARCHAR(50),
    encrypted_key TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used TIMESTAMP
);

-- Indexes
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_files_job_id ON files(job_id);
```

---

## Error Handling

### Error Types and Recovery Strategies

| Error Type | Detection | Recovery Strategy | User Message |
|------------|-----------|-------------------|--------------|
| **Syntax Error** | AST parsing fails | Auto-retry with LLM (provide error feedback) | "Generated code had syntax issues, retrying..." |
| **Security Violation** | Import of dangerous module | Reject immediately, log attempt | "Code rejected due to security policy" |
| **Execution Timeout** | Sandbox timeout (30s) | Retry with simplified prompt | "Generation timed out, trying simpler approach" |
| **Memory Exceeded** | Docker memory limit | Fail with suggestion | "Model too complex, try simplifying description" |
| **Non-manifold Mesh** | trimesh validation | Auto-repair or fail gracefully | "Fixed mesh issues automatically" |
| **LLM API Error** | Rate limit/timeout | Exponential backoff (3 retries) | "LLM service temporarily unavailable, retrying..." |
| **Invalid build123d** | Import error in execution | Feed error back to LLM for correction | "Correcting CAD logic and retrying" |

### Retry Logic Implementation

```python
# retry_handler.py
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class RetryHandler:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIError, TimeoutError, RateLimitError))
    )
    async def generate_with_retry(self, prompt: str, llm_manager, error_feedback=None):
        """Retry LLM generation with exponential backoff"""
        
        if error_feedback:
            prompt = f"""
            Previous attempt failed with error:
            {error_feedback}
            
            Please fix the code and try again.
            
            Original request: {prompt}
            """
        
        return await llm_manager.generate_code(prompt)
```

---

## Deployment Architecture

### Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  # API Service
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/aistl
      - REDIS_URL=redis://redis:6379
      - MINIO_ENDPOINT=minio:9000
    depends_on:
      - postgres
      - redis
      - minio
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock  # For Docker-in-Docker sandbox

  # Worker for background jobs
  worker:
    build: .
    command: celery -A orchestrator worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/aistl
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock

  # Database
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=aistl
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          memory: 1G

  # Redis for caching and message broker
  redis:
    image: redis:7-alpine
    deploy:
      resources:
        limits:
          memory: 512M

  # MinIO for STL storage
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"

  # Prometheus for monitoring
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"

  # Grafana for visualization
  grafana:
    image: grafana/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus

volumes:
  postgres_data:
  minio_data:
  prometheus_data:
  grafana_data:
```

### Kubernetes Deployment (Production)

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aistl-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aistl-api
  template:
    metadata:
      labels:
        app: aistl-api
    spec:
      containers:
      - name: api
        image: aistl/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        volumeMounts:
        - name: docker-socket
          mountPath: /var/run/docker.sock
      volumes:
      - name: docker-socket
        hostPath:
          path: /var/run/docker.sock
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: aistl-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: aistl-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Performance Optimization

### Caching Strategy

```python
# cache.py
from functools import lru_cache
import hashlib
import redis

class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
        self.ttl = 3600  # 1 hour cache
    
    def get_cache_key(self, prompt: str, provider: str, model: str) -> str:
        """Generate cache key from prompt and parameters"""
        content = f"{prompt}|{provider}|{model}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def get_cached_stl(self, prompt: str, provider: str, model: str):
        """Retrieve cached STL if available"""
        key = self.get_cache_key(prompt, provider, model)
        cached_path = self.redis_client.get(key)
        
        if cached_path and Path(cached_path).exists():
            return cached_path
        return None
    
    async def cache_stl(self, prompt: str, provider: str, model: str, stl_path: str):
        """Cache generated STL"""
        key = self.get_cache_key(prompt, provider, model)
        self.redis_client.setex(key, self.ttl, stl_path)
```

### Batch Processing

```python
# batch_processor.py
class BatchProcessor:
    """Process multiple generation requests efficiently"""
    
    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size
        self.queue = asyncio.Queue()
    
    async def add_to_batch(self, request: GenerateRequest):
        """Add request to batch queue"""
        await self.queue.put(request)
        
        if self.queue.qsize() >= self.batch_size:
            await self.process_batch()
    
    async def process_batch(self):
        """Process a batch of similar requests together"""
        batch = []
        
        for _ in range(min(self.batch_size, self.queue.qsize())):
            batch.append(await self.queue.get())
        
        # Group by similar parameters
        grouped = self._group_by_similarity(batch)
        
        # Process each group with optimized LLM calls
        for group in grouped:
            await self._process_group(group)
```

### Async Optimization

```python
# async_optimizer.py
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncOptimizer:
    """Optimize async operations for better throughput"""
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def parallel_analyze(self, parts: List[Part]):
        """Analyze multiple parts in parallel"""
        tasks = [
            asyncio.get_event_loop().run_in_executor(
                self.executor, 
                support_analyzer.analyze_support_needs, 
                part
            )
            for part in parts
        ]
        
        return await asyncio.gather(*tasks)
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_security.py
import pytest
from security import SecurityValidator

def test_dangerous_import_detection():
    validator = SecurityValidator(use_docker=False)
    
    dangerous_code = """
    import os
    from build123d import *
    
    def create_model():
        os.system('rm -rf /')
        return Box(10, 10, 10)
    """
    
    is_safe, violations = validator.validate_code(dangerous_code)
    
    assert not is_safe
    assert any("Dangerous import: os" in v for v in violations)

def test_safe_code_passes():
    validator = SecurityValidator(use_docker=False)
    
    safe_code = """
    from build123d import *
    
    def create_model():
        with BuildPart() as context:
            Box(10, 10, 10)
            return context.part
    """
    
    is_safe, violations = validator.validate_code(safe_code)
    
    assert is_safe
    assert len(violations) == 0
```

### Integration Tests

```python
# tests/test_integration.py
import pytest
from fastapi.testclient import TestClient
from orchestrator import app

client = TestClient(app)

def test_full_pipeline():
    """Test the complete generation pipeline"""
    
    response = client.post("/generate", json={
        "prompt": "Create a 20mm cube",
        "llm_provider": "openai",
        "analyze_supports": True
    })
    
    assert response.status_code == 200
    job_id = response.json()["job_id"]
    
    # Poll until complete
    import time
    while True:
        status_response = client.get(f"/status/{job_id}")
        status = status_response.json()["status"]
        
        if status in ["completed", "failed"]:
            break
        
        time.sleep(1)
    
    assert status_response.json()["status"] == "completed"
    assert "stl_url" in status_response.json()
```

### Load Testing

```python
# tests/load_test.py
import asyncio
import aiohttp
import time

async def test_concurrent_requests(num_requests: int = 100):
    """Test system under load"""
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        for i in range(num_requests):
            task = session.post(
                "http://localhost:8000/generate",
                json={"prompt": f"Test cube {i}"}
            )
            tasks.append(task)
        
        start = time.time()
        responses = await asyncio.gather(*tasks)
        elapsed = time.time() - start
        
        print(f"Processed {num_requests} requests in {elapsed:.2f} seconds")
        print(f"Throughput: {num_requests/elapsed:.2f} req/sec")
        
        return responses
```

---

## Monitoring & Observability

### Metrics to Track

```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
requests_total = Counter('stl_requests_total', 'Total generation requests', ['provider', 'status'])
generation_duration = Histogram('stl_generation_duration_seconds', 'Generation time', buckets=[5, 10, 30, 60, 120])

# Resource metrics
active_jobs = Gauge('stl_active_jobs', 'Currently processing jobs')
sandbox_memory_usage = Gauge('stl_sandbox_memory_bytes', 'Sandbox memory usage')

# Quality metrics
support_success_rate = Counter('stl_support_success_total', 'Support analysis success rate')
mesh_repair_rate = Counter('stl_mesh_repair_total', 'Mesh repair operations')

# LLM metrics
llm_tokens_total = Counter('stl_llm_tokens_total', 'Total tokens used', ['provider'])
llm_cost_total = Counter('stl_llm_cost_total', 'Total API costs', ['provider'])
```

### Logging Configuration

```python
# logging_config.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "message": record.getMessage(),
            "job_id": getattr(record, 'job_id', None),
            "user_id": getattr(record, 'user_id', None)
        }
        
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

# Configure logging
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

---

## Future Enhancements

### Phase 2 Features

1. **Interactive Mode**
   - Chat interface for iterative design refinement
   - Real-time preview with Three.js
   - Voice-to-prompt conversion

2. **Advanced Support Generation**
   - Automatic support structure generation as separate STL
   - Breakaway vs dissolvable support recommendations
   - Support optimization for specific printer models

3. **Multi-Material Support**
   - Generate separate STLs for multi-material printing
   - Automatic material assignment based on geometry

4. **Print Time Estimation**
   - Integrate with CuraEngine for accurate time estimates
   - Cost calculation based on material usage

5. **Model Marketplace**
   - Upload and share successful generations
   - Community ratings and improvements

### Phase 3 Features

1. **Fine-tuning Pipeline**
   - User-specific fine-tuning of LLM for their design style
   - Domain-specific fine-tuning (mechanical, artistic, architectural)

2. **3D Model Understanding**
   - Upload reference images for image-to-3D generation
   - 3D scan to editable parametric model

3. **Collaborative Design**
   - Real-time collaboration on generated models
   - Version control for design iterations

4. **Print Farm Integration**
   - Direct integration with OctoPrint and similar systems
   - Queue management for multiple printers

---

## Appendix

### A. Environment Variables

```bash
# .env file
# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...
TOGETHER_API_KEY=...

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/aistl

# Redis
REDIS_URL=redis://localhost:6379

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Security
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=32-byte-key-for-api-keys

# Performance
MAX_WORKERS=4
CACHE_TTL=3600
DOCKER_TIMEOUT=30
MAX_MEMORY_MB=512
```

### B. Installation Instructions

```bash
# Clone repository
git clone https://github.com/yourusername/aistl-pipeline.git
cd aistl-pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Docker (required for sandbox)
# Follow instructions at https://docs.docker.com/get-docker/

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Initialize database
alembic upgrade head

# Run the application
uvicorn orchestrator:app --reload --port 8000

# Run tests
pytest tests/ -v

# Run with Docker Compose (production)
docker-compose up -d
```

### C. Requirements File

```txt
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
litellm==1.0.0
build123d==0.6.0
cadquery==2.4.0
trimesh==3.23.0
numpy==1.24.3
docker==6.1.3
celery==5.3.4
redis==5.0.1
asyncpg==0.29.0
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.5.0
python-multipart==0.0.6
prometheus-client==0.19.0
tenacity==8.2.3
aiohttp==3.9.0
minio==7.2.0
cryptography==41.0.7
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1
python-dotenv==1.0.0
```

---

## Conclusion

This architecture provides a complete, production-ready solution for converting AI prompts to STL files with automatic support structure analysis. The key innovations are:

1. **Multi-layer security** ensuring safe code execution
2. **Intelligent support detection** as a core feature
3. **Modular design** allowing easy extension
4. **Production-ready deployment** with monitoring and scaling

The system is ready for implementation, with clear paths for future enhancements and optimizations.

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Maintainer**: Architecture Team  
**License**: MIT