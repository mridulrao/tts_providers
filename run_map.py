#!/usr/bin/env python3
"""
Run frontend (python http.server) and backend (uvicorn FastAPI) together.

Env vars (optional):
  FRONTEND_PORT=5500
  BACKEND_PORT=8000
  NO_OPEN=1      # don't auto-open the browser
"""
import os, sys, signal, time, webbrowser, subprocess, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "5500"))
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
AUTO_OPEN = os.getenv("NO_OPEN", "0") != "1"

def spawn(cmd, name):
    # Start each in its own process group for clean shutdown on POSIX
    kwargs = dict(cwd=str(ROOT))
    if os.name == "posix":
        kwargs["preexec_fn"] = os.setsid
    print(f"→ starting {name}: {' '.join(cmd)}")
    return subprocess.Popen(cmd, **kwargs)

def main():
    # Sanity checks
    if not (ROOT / "index.html").exists():
        print("⚠️  index.html not found next to run_dev.py", file=sys.stderr)
    if not shutil.which("uvicorn"):
        print("❌ uvicorn not found. Install with: pip install uvicorn fastapi", file=sys.stderr)
        sys.exit(1)

    backend_cmd = [sys.executable, "-m", "uvicorn", "app:app",
                   "--port", str(BACKEND_PORT), "--reload"]
    frontend_cmd = [sys.executable, "-m", "http.server", str(FRONTEND_PORT)]

    procs = {
        "backend": spawn(backend_cmd, "backend"),
        "frontend": spawn(frontend_cmd, "frontend"),
    }

    print(f"\nBackend:  http://localhost:{BACKEND_PORT}")
    print(f"Frontend: http://localhost:{FRONTEND_PORT}\n")

    if AUTO_OPEN:
        try:
            webbrowser.open(f"http://localhost:{FRONTEND_PORT}")
        except Exception:
            pass

    def cleanup(*_):
        print("\n🛑 Shutting down...")
        for name, p in procs.items():
            if p.poll() is None:
                try:
                    if os.name == "posix":
                        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                    else:
                        p.terminate()
                except Exception:
                    pass
        # Give them a moment
        time.sleep(0.5)
        for p in procs.values():
            try:
                if p.poll() is None:
                    p.kill()
            except Exception:
                pass
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    # If either process exits, shut everything down
    try:
        while True:
            if any(p.poll() is not None for p in procs.values()):
                break
            time.sleep(0.4)
    finally:
        cleanup()

if __name__ == "__main__":
    main()
