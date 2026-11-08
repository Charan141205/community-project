#!/usr/bin/env python3
"""
Convenience entry point to run the flood-ews sensor nodes simulation from root.
"""
import os
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.scripts.simulate_nodes import run_simulation, parser

if __name__ == "__main__":
    args = parser.parse_args()
    run_simulation(args.broker, args.port, args.scenario, args.duration, args.interval)
