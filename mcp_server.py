#!/usr/bin/env python3
"""
MCP Server for Report Access
Provides access to the war-on-art report data through Model Context Protocol
"""

import json
import sys
from pathlib import Path


def load_report():
    """Load the report data from report.json"""
    report_path = Path(__file__).parent / "report.json"
    try:
        with open(report_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": "Report file not found"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in report file"}


def get_report_summary():
    """Get a summary of the report"""
    report = load_report()
    if "error" in report:
        return report
    
    return {
        "title": report.get("title", "N/A"),
        "date": report.get("date", "N/A"),
        "summary": report.get("summary", "N/A"),
        "author": report.get("metadata", {}).get("author", "N/A")
    }


def get_report_section(section_id):
    """Get a specific section of the report"""
    report = load_report()
    if "error" in report:
        return report
    
    sections = report.get("sections", [])
    for section in sections:
        if section.get("id") == section_id:
            return section
    
    return {"error": f"Section {section_id} not found"}


def get_full_report():
    """Get the full report"""
    return load_report()


def handle_request(request):
    """Handle incoming MCP requests"""
    action = request.get("action", "summary")
    
    if action == "summary":
        return get_report_summary()
    elif action == "full":
        return get_full_report()
    elif action == "section":
        section_id = request.get("section_id", 1)
        return get_report_section(section_id)
    else:
        return {"error": f"Unknown action: {action}"}


def main():
    """Main MCP server loop"""
    print("MCP Report Server started", file=sys.stderr)
    print("Available actions: summary, full, section", file=sys.stderr)
    
    # Simple stdio-based MCP server
    # Reads JSON requests from stdin and writes JSON responses to stdout
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            
            try:
                request = json.loads(line)
                response = handle_request(request)
                print(json.dumps(response))
                sys.stdout.flush()
            except json.JSONDecodeError:
                error_response = {"error": "Invalid JSON request"}
                print(json.dumps(error_response))
                sys.stdout.flush()
    except KeyboardInterrupt:
        print("MCP Report Server stopped", file=sys.stderr)


if __name__ == "__main__":
    main()
