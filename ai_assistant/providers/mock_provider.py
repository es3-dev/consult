from .base import AIProvider


class MockProvider(AIProvider):
    name = "mock"

    def generate(self, prompt: str) -> str:
        lower = prompt.lower()
        if "categorias_top" in lower:
            return "Segun tus datos agregados, revisa tus categorias con mayor gasto y reduce consumos variables esta semana."
        return "Con la informacion disponible, mantén tus gastos por debajo de tus ingresos y prioriza presupuestos cercanos al limite."
