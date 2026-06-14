import re

file_path = 'backend/main.py'

with open(file_path, 'r') as f:
    content = f.read()

# Replace import numpy as np globally just in case or wrap it
# actually numpy is in requirements.txt.
# let's just make it optional in main.py
replacement = """
try:
    import numpy as np
except ImportError:
    pass
"""

content = content.replace("import numpy as np", replacement)

with open(file_path, 'w') as f:
    f.write(content)

print("Patched numpy!")
