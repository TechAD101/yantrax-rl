with open('backend/models.py', 'r') as f:
    content = f.read()

# Replace the incorrect relationship
old_rel = "positions = relationship('PortfolioPosition', backref='memecoin')"
new_rel = "positions = relationship('PortfolioPosition', backref='memecoin', primaryjoin='Memecoin.symbol == foreign(PortfolioPosition.symbol)')"

if old_rel in content:
    content = content.replace(old_rel, new_rel)
    with open('backend/models.py', 'w') as f:
        f.write(content)
    print("Fixed Memecoin.positions relationship.")
else:
    print("Relationship not found.")
