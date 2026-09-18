"""Runner script for RevScan AI.
Starts FastAPI backend, Streamlit dashboard, or both.
"""
import sys
import subprocess
import time
import argparse

# Enable UTF-8 encoding on Windows console where supported
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def run_api():
    """Run FastAPI backend server."""
    print("[RevScan AI] Starting FastAPI Backend on http://localhost:8000 ...")
    subprocess.run([sys.executable, "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])


def run_dashboard():
    """Run Streamlit dashboard frontend."""
    print("[RevScan AI] Starting Streamlit Dashboard on http://localhost:8501 ...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard/app.py", "--server.port", "8501"])


def run_all():
    """Run both API backend and Streamlit dashboard concurrently."""
    print("[RevScan AI] Launching full stack (FastAPI Backend + Streamlit Dashboard)...")
    p_api = subprocess.Popen([sys.executable, "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"])
    time.sleep(2)
    p_dash = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "dashboard/app.py", "--server.port", "8501"])

    try:
        p_api.wait()
        p_dash.wait()
    except KeyboardInterrupt:
        print("\n[RevScan AI] Stopping services...")
        p_dash.terminate()
        p_api.terminate()


def run_agent(package_name: str = "com.example.demo"):
    """Run autonomous AI Agent exploration directly via CLI."""
    from src.core.orchestrator import orchestrator
    from src.knowledge.knowledge_pack import knowledge_generator
    
    print(f"[RevScan AI] Starting Autonomous Agent for target: '{package_name}'...")
    orchestrator.start_scan(package_name)
    
    while orchestrator.is_running:
        status = orchestrator.get_status()
        print(f"  -> [Step {status.step}] Screens found: {status.screens_found} | Actions executed: {status.actions_executed}")
        time.sleep(1.5)
        
    final_status = orchestrator.get_status()
    print(f"\n[RevScan AI] Exploration Completed! Final Status: {final_status.status}")
    print(f"\n================ App Knowledge Pack Summary ================\n")
    print(knowledge_generator.export_ai_summary())
    print(f"\n============================================================")



def main():
    parser = argparse.ArgumentParser(description="RevScan AI Service Runner")
    parser.add_argument(
        "service",
        nargs="?",
        default="all",
        choices=["api", "dashboard", "scan", "all"],
        help="Service to run: 'api', 'dashboard', 'scan' (AI agent CLI), or 'all' (default)"
    )
    parser.add_argument(
        "--package",
        "-p",
        default="com.example.demo",
        help="Target Android package name for scan mode (default: 'com.example.demo')"
    )
    args = parser.parse_args()

    if args.service == "api":
        run_api()
    elif args.service == "dashboard":
        run_dashboard()
    elif args.service == "scan":
        run_agent(args.package)
    else:
        run_all()



if __name__ == "__main__":
    main()
