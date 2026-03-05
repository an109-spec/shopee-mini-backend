from sqlalchemy import func
from app.extensions.db import db
from app.models.order import Order


class AnalyticsService:

    @staticmethod
    def revenue_by_month():

        result = db.session.execute("""

        SELECT
            DATE_TRUNC('month', created_at) AS month,
            SUM(total_price) AS revenue

        FROM orders
        WHERE status='COMPLETED'

        GROUP BY month
        ORDER BY month

        """)

        return [dict(row._mapping) for row in result]