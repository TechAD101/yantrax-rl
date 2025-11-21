import re

# Read main.py
with open('main.py', 'r') as f:
    content = f.read()

# Check if already integrated
if 'market_data_service_v2' in content:
    print("✅ Already integrated! No changes needed.")
    exit(0)

# Find the imports section and add our new import
import_pattern = r'(from fix_market_data import MarketDataManager)'
if re.search(import_pattern, content):
    # Replace the old import with the new one
    content = re.sub(
        import_pattern,
        'from services.market_data_service_v2 import MarketDataService',
        content
    )
    print("✅ Updated import statement")
else:
    # Add import after other imports
    import_location = content.find('from fastapi.middleware.cors')
    if import_location != -1:
        end_of_line = content.find('\n', import_location)
        content = content[:end_of_line+1] + 'from services.market_data_service_v2 import MarketDataService\n' + content[end_of_line+1:]
        print("✅ Added new import")

# Replace MarketDataManager() with MarketDataService()
content = re.sub(
    r'market_data\s*=\s*MarketDataManager\(\)',
    'market_data = MarketDataService()',
    content
)
print("✅ Replaced MarketDataManager instantiation")

# Update method calls if needed
# get_stock_price -> get_price
content = re.sub(
    r'\.get_stock_price\(',
    '.get_price(',
    content
)
print("✅ Updated method calls")

# Write back
with open('main.py', 'w') as f:
    f.write(content)

print("\n�� Integration complete! main.py now uses MarketDataService v2")
