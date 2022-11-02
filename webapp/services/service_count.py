from flask_login import current_user

from webapp.marketplace.models import UserFavoriteProduct


def count_favorite_products_current_user():
    if current_user.is_authenticated:
        count_favorite = UserFavoriteProduct.query.filter(UserFavoriteProduct.user_id == current_user.id).count()
        return count_favorite
    else:
        count_favorite = 0
        return count_favorite
