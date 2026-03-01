with open('backend/order_manager.py', 'r') as f:
    content = f.read()

# Need to set portfolio_id. Find default portfolio or create it if not exists.
new_code = """        # simulate execution (paper)
        exec_res = simulate_trade(symbol, usd)
        price = exec_res.get('price')
        quantity = exec_res.get('quantity')

        from models import Portfolio
        portfolio = session.query(Portfolio).first()
        if not portfolio:
            portfolio = Portfolio(name="Default Paper Portfolio", initial_capital=100000.0, current_value=100000.0)
            session.add(portfolio)
            session.flush()

        o = Order(portfolio_id=portfolio.id, symbol=symbol.upper(), usd=usd, quantity=quantity, price=price, status='filled', executed_at=datetime.utcnow(), meta={'simulated': True})"""

content = content.replace("""        # simulate execution (paper)
        exec_res = simulate_trade(symbol, usd)
        price = exec_res.get('price')
        quantity = exec_res.get('quantity')

        o = Order(symbol=symbol.upper(), usd=usd, quantity=quantity, price=price, status='filled', executed_at=datetime.utcnow(), meta={'simulated': True})""", new_code)

with open('backend/order_manager.py', 'w') as f:
    f.write(content)
print("Updated backend/order_manager.py")
