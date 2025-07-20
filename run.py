#!/usr/bin/env python3
"""
Simple script to run the Flask application
"""
import subprocess
import sys

if __name__ == "__main__":
    # Run the main Flask application
    subprocess.run([sys.executable, "main.py"])