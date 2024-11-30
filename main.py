import logging
from flask import Flask, flash, render_template, request, redirect, url_for
from dbutils import get_cursor, db_setup

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route("/admin/item_list", methods=["GET"])
def admin_item_list():
    cursor = get_cursor()
    cursor.execute('SELECT id, title, price, quantity FROM items')
    
    items = cursor.fetchall()
    return render_template("admin_item_list.html", items=items)


@app.route('/admin/item_details/<int:item_id>', methods=["GET"])
def admin_details_item(item_id):
    cursor = get_cursor()

    item = cursor.execute('SELECT id, title, price, quantity, description FROM items WHERE id = ?', (item_id,)).fetchone()

    return render_template("admin_item.html", item=item)


@app.route('/api/item_update/<int:item_id>', methods=["POST"])
def admin_update_item(item_id):
    cursor = get_cursor()

    title = request.form.get('title', '').strip()
    price = request.form.get('price', '').strip()
    quantity = request.form.get('quantity', '').strip()
    description = request.form.get('description', '').strip()

    if not title or not price or not quantity:
        flash('Title, price, and quantity are required.', 'error')
        return redirect(url_for('admin_item_details', item_id=item_id))
        
    try:
        price = float(price)
        quantity = int(quantity)
    except ValueError:
        flash('Invalid price or quantity.', 'error')
        return redirect(url_for('admin_item_details', item_id=item_id))


    cursor.execute('''UPDATE items SET title = ?, price = ?, quantity = ?, description = ? WHERE id = ?''', (title, price, quantity, description, item_id))
    cursor.connection.commit()

    flash('Item updated successfully!', 'success')

    return redirect(url_for('admin_item_list'))

if __name__ == "__main__":
    db_setup()
    app.run(debug=True, host="0.0.0.0", port=3000)