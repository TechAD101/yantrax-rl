
import sys
import os
import json
from datetime import datetime

# Add backend to path
sys.path.append(os.path.abspath('backend'))

from ai_firm.report_generation import InstitutionalReportGenerator

def verify_report():
    print("🚀 Starting Institutional Report Verification...")
    
    # We mock the dependencies or use the real ones if they don't require external keys
    # For verification, we'll try to generate a report for AAPL
    try:
        generator = InstitutionalReportGenerator()
        report = generator.generate_full_report("AAPL")
        
        print(f"✅ Report Generated Successfully!")
        print(f"Trust Score: {report['trust_score']}")
        print(f"Confidence Band: {report['confidence_band']}")
        print(f"Audit ID: {report['audit_id']}")
        
        # Verify 13 sections exist
        sections_found = report['markdown'].count('### ')
        print(f"📊 Sections Found: {sections_found}/14") # 0-13 = 14 headers
        
        if sections_found >= 13:
            print("✨ Section count verified.")
        else:
            print("⚠️ Missing sections detected.")
            
        print("\n--- REPORT PREVIEW ---")
        print(report['markdown'][:500] + "...")
        print("--- END PREVIEW ---\n")
        
        return True
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_report()
    sys.exit(0 if success else 1)
