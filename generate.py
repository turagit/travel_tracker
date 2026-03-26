#!/usr/bin/env python3
"""Convenience entry point: python generate.py [output_dir]"""
import sys
from src.shortcut_generator.generator import generate_shortcuts

def main():
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    files = generate_shortcuts(output_dir)
    print(f"Generated {len(files)} shortcut files in '{output_dir}/':")
    for f in files:
        print(f"  {f}")
    print()
    print("To install on your iPhone:")
    print("  1. AirDrop the .shortcut files to your phone, OR")
    print("  2. Upload to iCloud Drive and tap to open on your phone")
    print()
    print("Run 'Travel Tracker Setup' first, then set up Bluetooth automations.")

if __name__ == "__main__":
    main()
