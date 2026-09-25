#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import socket
import subprocess

import shutil
import time

def ensure_postgres_running(host='localhost', port=5432):
    """Ensure local PostgreSQL server is running and fully ready before executing Django commands."""
    try:
        import psycopg2
        conn = psycopg2.connect('host=127.0.0.1 port=5432 dbname=postgres user=postgres password=postgres connect_timeout=1')
        conn.close()
        return True
    except Exception:
        pass

    print("\n[INFO] PostgreSQL service is not active on port 5432. Starting PostgreSQL server...")
    
    data_dir = r"C:\my_install\pgsql\data"
    postgres_bin = r"C:\my_install\pgsql\bin\postgres.exe"
    pg_ctl_bin = r"C:\my_install\pgsql\bin\pg_ctl.exe"

    if not os.path.exists(data_dir):
        print("[WARNING] PostgreSQL data directory not found.\n")
        return False

    pid_file = os.path.join(data_dir, 'postmaster.pid')
    status_res = subprocess.run([pg_ctl_bin, 'status', '-D', data_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if status_res.returncode != 0 and os.path.exists(pid_file):
        try:
            os.remove(pid_file)
            print("[INFO] Removed stale postmaster.pid file.")
        except Exception:
            pass

    if os.path.exists(postgres_bin):
        try:
            subprocess.Popen([postgres_bin, "-D", data_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            for _ in range(25):
                try:
                    import psycopg2
                    conn = psycopg2.connect('host=127.0.0.1 port=5432 dbname=postgres user=postgres password=postgres connect_timeout=1')
                    conn.close()
                    print("[SUCCESS] PostgreSQL server started and ready.\n")
                    return True
                except Exception:
                    time.sleep(0.3)
        except Exception:
            pass

    print("[WARNING] Could not start PostgreSQL automatically.\n")
    return False

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    # Auto-start Postgres if running backend server or database commands
    if len(sys.argv) > 1 and sys.argv[1] in ['runserver', 'migrate', 'makemigrations', 'shell', 'dbshell']:
        ensure_postgres_running()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

