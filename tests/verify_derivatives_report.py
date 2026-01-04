import sys
import os
from pprint import pprint

# Add project root and backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from backend.ai_firm.report_generation import InstitutionalReportGenerator

# Mock services to avoid full dependency chain if needed, 
# but the real ones likely work fine if they have simulate modes.
# We'll try using the real ones first.

def verify_derivatives_section():
    print("📉 Generating Institutional Report with Derivatives Analytics...\n")
    
    # Initialize Generator
    generator = InstitutionalReportGenerator()
    
    # Generate Report for AAPL
    # This triggers the simulated Option Chain generation and metrics calc
    report_data = generator.generate_full_report("AAPL")
    
    # Extract Section 6 Markdown
    full_md = report_data['markdown']
    sections = full_md.split('\n\n---\n\n')
    
    # Find Section 6
    derivatives_section = next((s for s in sections if "6. DERIVATIVES POSITIONING" in s), None)
    
    if derivatives_section:
        print("✅ Section 6 Found:\n")
        print(derivatives_section)
    else:
        print("❌ Section 6 NOT Found in Markdown output.")
        
    print("\n\n📊 Raw Trust Score:", report_data['trust_score'])
    print("🎯 Confidence Band:", report_data['confidence_band'])

if __name__ == "__main__":
    verify_derivatives_section()
