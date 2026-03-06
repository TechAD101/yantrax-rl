with open('tests/test_order_manager.py', 'r') as f:
    content = f.read()

# Add a default portfolio creation before creating an order
setup_code = """    # Create a default portfolio first to satisfy foreign key constraint
    client.post('/api/portfolio', json={'name': 'Default Paper Portfolio', 'initial_capital': 100000})

    # create order"""
content = content.replace("    # create order", setup_code)

with open('tests/test_order_manager.py', 'w') as f:
    f.write(content)
print("Updated tests/test_order_manager.py")
