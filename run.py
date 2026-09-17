"""Runner script for RevScan AI.
Starts FastAPI backend, Streamlit dashboard, or both.
"""
import sys
import subprocess
import time
import argparse


def run_api():
    """Run FastAPI backend server."""
    print("🚀 Starting RevScan AI FastAPI Backend on http://localhost:8000 ...")
    subprocess.run([sys.executable, "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])


def run_dashboard():
    """Run Streamlit dashboard frontend."""
    print("📊 Starting RevScan AI Streamlit Dashboard on http://localhost:8501 ...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard/app.py", "--server.port", "8501"])


def run_all():
    """Run both API backend and Streamlit dashboard concurrently."""
    print("🚀 Launching RevScan AI (Backend + Frontend)...")
    p_api = subprocess.Popen([sys.executable, "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"])
    time.sleep(2)
    p_dash = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "dashboard/app.py", "--server.port", "8501"])

    try:
        p_api.wait()
        p_dash.wait()
    except KeyboardInterrupt:
        print("\nStopping RevScan AI services...")
        p_dash.terminate()
        p_api.terminate()


def main():
    parser = argparse.ArgumentParser(description="RevScan AI Service Runner")
    parser.add_argument(
        "service",
        nargs="?",
        default="all",
        choices=["api", "dashboard", "all"],
        help="Service to run: 'api', 'dashboard', or 'all' (default)"
    )
    args = parser.parse_args()

    if args.service == "api":
        run_api()
    elif args.service == "dashboard":
        run_dashboard()
    else:
        run_all()


if __name__ == "__main__":
    main()
