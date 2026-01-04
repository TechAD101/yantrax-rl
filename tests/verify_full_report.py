import sys
import os
from pprint import pprint

# Add project root and backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from backend.ai_firm.report_generation import InstitutionalReportGenerator

def verify_full_report():
    print("📉 Generating Full Institutional Report...\n")
    
    # Initialize Generator
    generator = InstitutionalReportGenerator()
    
    # Generate Report for AAPL
    report_data = generator.generate_full_report("AAPL")
    
    # Extract Markdown
    full_md = report_data['markdown']
    sections = full_md.split('\n\n---\n\n')
    
    print(f"📄 Total Sections Found: {len(sections)}")
    for i, s in enumerate(sections):
        header = s.strip().split('\n')[0]
        print(f"  [{i}] {header}")
    
    section_map = {
        '5': "5. CAPITAL FLOWS",
        '6': "6. DERIVATIVES",
        '7': "7. QUANT"
    }
    
    for key, name in section_map.items():
        found = next((s for s in sections if f"{key}. {name}" in s or f"{key}. {name}" in s.upper()), None)
        if found:
            print(f"✅ Section {key} Found:\n")
            print(found)
            print("-" * 50 + "\n")
        else:
            print(f"❌ Section {key} ({name}) NOT Found.")
            
    print(f"\n📊 Trust Score: {report_data['trust_score']}")
    print(f"🎯 Band: {report_data['confidence_band']}")

if __name__ == "__main__":
    verify_full_report()
