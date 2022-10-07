from webapp.marketplace.views import blueprint
from webapp.marketplace.models import Category, db
from webapp import cache


@blueprint.context_processor
def utility_processor():
    def dropdown_categories():
        categories = Category.query.filter(Category.parent_id.is_(None)).all()
        result = [sub_categories for category in categories for sub_categories in category.drilldown_tree()]
        return result

    return dict(dropdown_categories=dropdown_categories)
