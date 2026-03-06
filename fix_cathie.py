with open('backend/ai_agents/personas/cathie.py', 'r') as f:
    content = f.read()

# _analyze_innovation is missing from the file but called. It might have been replaced or renamed or just incomplete.
# I'll add the missing methods if they don't exist. Let's see what's actually missing.

new_methods = """
    def _analyze_innovation(self, context: Dict[str, Any]) -> float:
        company_data = context.get('company_data', {})
        rd_ratio = company_data.get('rd_revenue_ratio', 0)
        return min(1.0, rd_ratio / self.innovation_criteria['rd_spending_threshold'])

    def _assess_growth_potential(self, context: Dict[str, Any]) -> float:
        company_data = context.get('company_data', {})
        growth = company_data.get('revenue_growth', 0)
        return min(1.0, max(0.0, growth / self.innovation_criteria['min_revenue_growth']))

    def _evaluate_disruption(self, context: Dict[str, Any]) -> float:
        res = self._analyze_disruption_potential(context)
        return res.get('score', 0.5)

    def _generate_innovation_recommendation(self, innovation_score: float, growth_score: float, disruption_score: float, sector_timing: Dict[str, Any]) -> Dict[str, Any]:
        return self._generate_recommendation(innovation_score, {'score': growth_score}, {'score': disruption_score}, sector_timing)
"""

if "def _analyze_innovation" not in content:
    content = content.replace("    # ============ PersonaAgent Interface Implementation ============", new_methods + "\n    # ============ PersonaAgent Interface Implementation ============")
    with open('backend/ai_agents/personas/cathie.py', 'w') as f:
        f.write(content)
    print("Added missing methods to CathieAgent.")
else:
    print("Methods already exist.")
