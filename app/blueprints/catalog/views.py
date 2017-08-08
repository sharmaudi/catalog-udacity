from flask import Blueprint, render_template
from config.settings import ITEMS_PER_PAGE

from app.blueprints.catalog.models import Category, Item

catalog = Blueprint('catalog', __name__, template_folder='templates')


@catalog.route('/')
@catalog.route('/catalog/items')
@catalog.route('/catalog/items/<int:page>')
@catalog.route('/catalog/<string:category>/items', methods=['GET', 'POST'])
@catalog.route('/catalog/<string:category>/items/<int:page>', methods=['GET', 'POST'])
def home(category=None, page=1):
    selected_category = None
    categories = Category.query.all()
    if not category:
        items = Item.query.order_by(Item.created_on.desc()).paginate(page, ITEMS_PER_PAGE, True)
    else:
        selected_category = Category.category_details(category)
        items = selected_category.get_items().order_by(Item.created_on.desc()).paginate(page, ITEMS_PER_PAGE, True)

    return render_template('catalog/home.html',
                           categories=categories,
                           items=items,
                           selected_category=selected_category)


@catalog.route('/catalog/<string:category>/items/<string:item>')
def item_in_category(category, item):
    selected_item = Item.get_item(category, item)
    return render_template('catalog/item_details.html', item=selected_item)
