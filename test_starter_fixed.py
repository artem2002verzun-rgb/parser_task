"""Тесты для recommend_price.

Запуск (из папки test_task_parser):
    python -m unittest -v test_starter_fixed
"""

import asyncio
import unittest
from decimal import Decimal

from starter_fixed import recommend_price, sample_fetch_offers


def make_source(offers, status="success"):
    """Фейковый источник: async-функция без аргументов, как fetch_offers."""
    async def fetch():
        return {"status": status, "offers": offers}
    return fetch


class RecommendPriceTest(unittest.IsolatedAsyncioTestCase):

    async def test_sample_from_task(self):
        """Обычный расчёт: пример из задания."""
        result = await recommend_price(
            sample_fetch_offers, Decimal("4900.00"), Decimal("4500.00"))
        self.assertEqual(result["price"], Decimal("4728.00"))
        self.assertEqual(result["decision"], "APPLY")

    async def test_timeout_holds_current_price(self):
        """Сбой: источник не ответил вовремя — цену не меняем."""
        async def slow_source():
            await asyncio.sleep(1)
        result = await recommend_price(
            slow_source, Decimal("4900.00"), Decimal("4500.00"), timeout_s=0.05)
        self.assertEqual(result["price"], Decimal("4900.00"))
        self.assertEqual(result["decision"], "HOLD")

    async def test_exactly_30_percent_is_applied(self):
        """Граница: ровно 30% допускается."""
        # 1319.80 * 0.985 = 1300.003 -> вниз до 1300.00, ровно +30% от 1000
        offers = [{"seller": "PARTS", "price": Decimal("1319.80"), "delivery_days": 3}]
        result = await recommend_price(
            make_source(offers), Decimal("1000.00"), Decimal("1.00"))
        self.assertEqual(result["price"], Decimal("1300.00"))
        self.assertEqual(result["decision"], "APPLY")


if __name__ == "__main__":
    unittest.main()
