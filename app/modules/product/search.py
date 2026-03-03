from sqlalchemy import or_

from .models import Product


def search_products(query, keyword: str | None):
    if not keyword:
        return query
    keyword = keyword.strip()
    if not keyword:
        return query

    like_keyword = f"%{keyword}%"
    return query.filter(
        or_(
            Product.name.ilike(like_keyword),
            Product.slug.ilike(like_keyword),
            Product.description.ilike(like_keyword),
        )
    )


def full_text_query(query, keyword: str | None):
    # Fallback LIKE để tương thích SQLite và PostgreSQL.
    # Có thể mở rộng full-text theo engine trong tương lai.
    return search_products(query, keyword)