import os
import time

import bleach
from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app, send_from_directory, \
    jsonify
from flask_breadcrumbs import register_breadcrumb, default_breadcrumb_root
from flask_login import login_required, current_user
from markupsafe import Markup
from werkzeug.utils import secure_filename

from app.blueprints.catalog.forms import ItemForm, UploadForm
from app.blueprints.catalog.models import Category, Item
from app.extensions import csrf
from app.mixins.util_wtforms import choices_from_dict
from config.settings import ITEMS_PER_PAGE

catalog = Blueprint('catalog', __name__, template_folder='templates')
default_breadcrumb_root(catalog, '.')


# noinspection PyUnusedLocal
def view_catalog_dlc(*args, **kwargs):
    if 'category' in request.view_args:
        category = request.view_args['category']
        return [{'text': 'Catalog', 'url': url_for('catalog.home')},
                {'text': category, 'url': url_for('catalog.home', category=category)}]
    else:
        return [{'text': 'Catalog', 'url': url_for('catalog.home')}]


# noinspection PyUnusedLocal
def view_item_dlc(*args, **kwargs):
    category = request.view_args['category']
    item = request.view_args['item']
    return [{'text': item, 'url': url_for('catalog.item_in_category', category=category, item=item)}]


# noinspection PyUnusedLocal
def edit_item_dlc(*args, **kwargs):
    category = request.view_args['category']
    item = request.view_args['item']
    return [{'text': f"Edit", 'url': url_for('catalog.edit_item', category=category, item=item)}]


# noinspection PyUnusedLocal
def upload_item_dlc(*args, **kwargs):
    category = request.view_args['category']
    item = request.view_args['item']
    return [{'text': f"Upload", 'url': url_for('catalog.upload_image', category=category, item=item)}]


# noinspection PyUnusedLocal
def delete_item_dlc(*args, **kwargs):
    category = request.view_args['category']
    item = request.view_args['item']
    return [{'text': f"Delete", 'url': url_for('catalog.item_in_category', category=category, item=item)}]


@catalog.route('/')
@catalog.route('/catalog/items')
@catalog.route('/catalog/items/<int:page>')
@catalog.route('/catalog/<string:category>/items', methods=['GET', 'POST'])
@catalog.route('/catalog/<string:category>/items/<int:page>', methods=['GET', 'POST'])
@register_breadcrumb(catalog, '.', 'Home', dynamic_list_constructor=view_catalog_dlc)
def home(category=None, page=1):
    selected_category = None
    categories = Category.query.all()
    if not category:
        items = Item.query.order_by(Item.updated_on.desc()).paginate(page, ITEMS_PER_PAGE, True)
    else:
        selected_category = Category.category_details(category)
        items = selected_category.get_items().order_by(Item.created_on.desc()).paginate(page, ITEMS_PER_PAGE, True)

    return render_template('catalog/home.html',
                           categories=categories,
                           items=items,
                           selected_category=selected_category)


@catalog.route('/catalog/<string:category>/items/<string:item>')
@register_breadcrumb(catalog, '.item', '', dynamic_list_constructor=view_item_dlc)
def item_in_category(category, item):
    selected_item = Item.get_item(category, item)
    return render_template('catalog/item_details.html', item=selected_item)


@catalog.route('/catalog/items/add', methods=['GET', 'POST'])
@register_breadcrumb(catalog, '.add', 'Add Item')
@login_required
def add_item():
    form = ItemForm()
    upload_form = UploadForm()
    form.category_id.choices = choices_from_dict(Category.get_categories_as_dict())

    if form.validate_on_submit():
        item = Item()
        # Not sure whether this is required as flask-wtf should already be sanitizing the data
        form.description = bleach.clean(form.description)
        form.name = bleach.clean(form.name)
        form.populate_obj(item)
        item.created_by = current_user.username
        print(f"Creating item ${item}")
        item.save()
        flash("Item Created Successfully", "success")
        return redirect(url_for('catalog.edit_item', category=item.category.name, item=item.name))

    return render_template('catalog/item_create_or_update.html', form=form, upload_form=upload_form)


@catalog.route('/catalog/<string:category>/items/<string:item>/edit', methods=['GET', 'POST'])
@register_breadcrumb(catalog, '.item.edit', '', dynamic_list_constructor=edit_item_dlc)
@login_required
def edit_item(category, item):
    selected_item = Item.get_item(category, item)
    authorized = check_authorization(selected_item)
    if not authorized:
        flash("You are not authorized to do that operation.", "error")
        return redirect(url_for('catalog.item_in_category', category=category, item=item))

    form = ItemForm(obj=selected_item)
    form.category_id.choices = choices_from_dict(Category.get_categories_as_dict())
    if form.validate_on_submit():
        print(f"Item current state ${selected_item}")
        selected_item.description = bleach.clean(form.description.data)
        selected_item.name = bleach.clean(form.name.data)
        selected_item.category_id = form.category_id.data
        selected_item.save()
        print(f"Updated item state ${selected_item}")
        flash("Item Updated Successfully", "success")
        return redirect(url_for('catalog.edit_item', category=selected_item.category.name, item=selected_item.name))

    return render_template('catalog/item_create_or_update.html',
                           item=selected_item,
                           form=form,
                           oper="edit")


@catalog.route('/catalog/<string:category>/items/<string:item>/edit/upload', methods=['GET', 'POST'])
@register_breadcrumb(catalog, '.item.upload', '', dynamic_list_constructor=upload_item_dlc)
@csrf.exempt
@login_required
def upload_image(category, item):
    print("In upload image")
    selected_item = Item.get_item(category, item)

    authorized = check_authorization(selected_item)
    if not authorized:
        flash("You are not authorized to do that operation.", "error")
        return redirect(url_for('catalog.item_in_category', category=category, item=item))

    form = UploadForm()
    print(form.image.data)

    if request.method == "POST":
        f = form.image.data
        ext = os.path.splitext(secure_filename(f.filename))[1]
        filename = secure_filename(f"{category}_{selected_item.id}_{time.time()}{ext}")
        print(f"Filename is {filename}")
        path = os.path.join(
            current_app.instance_path, 'uploads', filename
        )
        print(f"Saving file to {path}")
        f.save(os.path.join(
            current_app.instance_path, 'uploads', filename
        ))
        selected_item.image = f'/uploads/{filename}'
        selected_item.save()
        flash("File Uploaded", "success")
        return redirect(url_for('catalog.upload_image', category=category, item=item))
    return render_template('catalog/upload_image.html',
                           category=category,
                           item=selected_item,
                           form=form)


@catalog.route('/catalog/<string:category>/items/<string:item>/delete', methods=['GET'])
@register_breadcrumb(catalog, '.item.delete', '', dynamic_list_constructor=delete_item_dlc)
@login_required
def delete_item(category, item):
    selected_item = Item.get_item(category, item)

    authorized = check_authorization(selected_item)
    if not authorized:
        flash("You are not authorized to do that operation.", "error")
        return redirect(url_for('catalog.item_in_category', category=category, item=item))

    confirm_flag = request.args.get('confirm')

    markup = "Please confirm that you " \
             "want to delete Item " \
             "{}? <a href='{}?confirm=true'>" \
             "Confirm</a>"

    if confirm_flag and "true".lower() == confirm_flag.lower():
        selected_item.delete()
        flash("Item has been deleted.")
        return redirect(url_for('catalog.home', category=category))
    else:
        flash_message = markup.format(selected_item.name,
                                      url_for('catalog.delete_item',
                                              category=category,
                                              item=item))
        confirm_msg = Markup(flash_message)
        flash(confirm_msg, "info")
        return render_template('catalog/item_details.html', item=selected_item)


@catalog.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(f'{current_app.instance_path}/uploads',
                               filename)


@catalog.route('/api/v1/catalog')
def catalog_as_json():
    categories = Category.query.all()
    result = {
        "Categories": [category.serialize for category in categories]
    }
    return jsonify(result)


def check_authorization(item):
    logged_in_user = current_user.username
    if item.created_by == logged_in_user:
        return True
    return False

