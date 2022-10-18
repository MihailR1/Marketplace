from webapp.marketplace.models import UserFavoriteProduct

def is_user_add_product_to_favorite(current_user, product):
    return UserFavoriteProduct.query.filter(
        UserFavoriteProduct.user_id == current_user.id, 
        UserFavoriteProduct.product_id == product.id
    ).count() > 0


