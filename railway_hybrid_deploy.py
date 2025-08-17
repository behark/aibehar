#!/usr/bin/env python3
"""
Railway Hybrid deployment script that serves Open WebUI frontend through FastAPI
Optimized for Railway deployment with nixpacks
"""
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Open WebUI + Enhanced Model Loader", version="2.0.0")

# Check if webui build exists
webui_build_path = Path("webui/build")
webui_available = webui_build_path.exists() and webui_build_path.is_dir()

print(f"🔍 WebUI build directory available: {webui_available}")
if webui_available:
    print(f"📁 WebUI build path: {webui_build_path.absolute()}")
    
    # Mount Open WebUI assets correctly
    app.mount("/assets", StaticFiles(directory=str(webui_build_path / "assets")), name="assets")
    app.mount("/static", StaticFiles(directory=str(webui_build_path / "static")), name="static")
    app.mount("/audio", StaticFiles(directory=str(webui_build_path / "audio")), name="audio")
    app.mount("/pyodide", StaticFiles(directory=str(webui_build_path / "pyodide")), name="pyodide")
    app.mount("/wasm", StaticFiles(directory=str(webui_build_path / "wasm")), name="wasm")
    app.mount("/themes", StaticFiles(directory=str(webui_build_path / "themes")), name="themes")
    
    print("✅ Open WebUI assets mounted: /assets, /static, /audio, /pyodide, /wasm, /themes")

@app.get("/health")
def health():
    return {
        "status": "healthy", 
        "service": "Open WebUI + Enhanced Model Loader", 
        "version": "2.0.0",
        "webui_available": webui_available,
        "environment": "railway-hybrid"
    }

@app.get("/", response_class=HTMLResponse)
def root():
    if webui_available:
        # Try to serve the Open WebUI index.html
        index_path = webui_build_path / "index.html"
        if index_path.exists():
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return HTMLResponse(content=content)
            except Exception as e:
                print(f"❌ Error serving index.html: {e}")
    
    # Fallback to status page
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html><head><title>Open WebUI + Enhanced Model Loader</title>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
           background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
           color: white; margin: 0; padding: 20px; min-height: 100vh; }}
    .container {{ max-width: 800px; margin: 0 auto; text-align: center; padding: 40px; }}
    .title {{ font-size: 3em; margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
    .subtitle {{ font-size: 1.3em; margin-bottom: 40px; opacity: 0.9; }}
    .status {{ background: #4CAF50; padding: 10px; border-radius: 20px; display: inline-block; margin: 20px; }}
    .info {{ background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 20px 0; }}
    </style>
    </head><body><div class="container">
    <h1 class="title">🎯 Open WebUI + Enhanced Model Loader</h1>
    <p class="subtitle">Hybrid Deployment Ready</p>
    <div class="status">✅ LIVE & OPERATIONAL</div>
    
    <div class="info">
        <h3>🔍 System Status</h3>
        <p><strong>WebUI Available:</strong> {webui_available}</p>
        <p><strong>Build Path:</strong> {webui_build_path.absolute() if webui_available else 'Not found'}</p>
        <p><strong>Static Files:</strong> {'Mounted at /static' if webui_available else 'Not available'}</p>
    </div>
    
    <div class="info">
        <h3>🔗 Available Endpoints</h3>
        <p><a href="/health" style="color: white;">Health Check</a></p>
        {'<p><a href="/static/" style="color: white;">WebUI Static Files</a></p>' if webui_available else ''}
    </div>
    </div></body></html>
    """)

@app.get("/api/config")
def get_config():
    """Open WebUI config endpoint"""
    return {
        "name": "Open WebUI + Enhanced Model Loader",
        "version": "2.0.0",
        "auth": False,
        "default_models": [],
        "features": {
            "model_loading": True,
            "enhanced_registry": True,
            "webui_frontend": webui_available
        }
    }

@app.get("/{file_path:path}")
def serve_webui_files(file_path: str):
    """Serve any missing files from Open WebUI build directory"""
    if not webui_available:
        raise HTTPException(status_code=404, detail="WebUI not available")
    
    # Try to serve the requested file from webui/build
    requested_file = webui_build_path / file_path
    if requested_file.exists() and requested_file.is_file():
        return FileResponse(str(requested_file))
    
    # If file not found, serve the main index.html for SPA routing
    index_path = webui_build_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    
    raise HTTPException(status_code=404, detail="File not found")

# Try to import and mount Open WebUI routes if available
try:
    # Check if Open WebUI backend exists
    webui_backend_path = Path("webui/backend")
    if webui_backend_path.exists():
        import sys
        sys.path.insert(0, str(webui_backend_path.absolute()))
        
        # Try to import Open WebUI main app
        from open_webui.main import app as webui_app

        # Mount Open WebUI routes
        app.mount("/api", webui_app)
        print("✅ Open WebUI API routes mounted at /api")
    else:
        print("ℹ️  No Open WebUI backend found - frontend-only deployment")
        
except ImportError as e:
    print(f"ℹ️  Open WebUI backend not available: {e}")
    print("📦 Running with static file serving only")
except Exception as e:
    print(f"⚠️  Unexpected error with Open WebUI backend: {e}")
    print("📦 Continuing with static file serving")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting hybrid Open WebUI server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
