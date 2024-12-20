import logging, uuid, os
from flask import Flask, flash, render_template, request, redirect, url_for, send_file
from dbutils import get_cursor, db_setup

logging.basicConfig(level=logging.INFO)

app = Flask(__name__, )
app.secret_key = 'your_secret_key'

@app.route('/favicon.ico')
def favicon():
    return send_file("static/images/favicon.ico", mimetype='image/vnd.microsoft.icon')

@app.route("/admin/item_list", methods=["GET"])
def admin_item_list():
    with get_cursor() as cursor:
        cursor.execute('SELECT id, title, price, quantity FROM items')
        items = cursor.fetchall()
    return render_template("admin_item_list.html", items=items)


@app.route('/admin/item_details/<int:item_id>', methods=["GET"])
def admin_details_item(item_id):
    with get_cursor() as cursor:
        item = cursor.execute('SELECT id, title, price, quantity, description FROM items WHERE id = ?', (item_id,)).fetchone()
        images = cursor.execute('SELECT image_name FROM images WHERE item_id = ?', (item_id,)).fetchall()
    
    return render_template("admin_item.html", item=item, images=images)


@app.route('/admin/item_update/<int:item_id>', methods=["POST"])
def admin_update_item(item_id):

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

    with get_cursor() as cursor:
        cursor.execute('''UPDATE items SET title = ?, price = ?, quantity = ?, description = ? WHERE id = ?''', (title, price, quantity, description, item_id))

        for file_key in request.files:
            image_file = request.files[file_key]
            if image_file:
                original_name = cursor.execute('SELECT image_name FROM images WHERE slot = ? AND item_id = ?', (file_key, item_id,)).fetchone()[0]
                
                #TODO (func): resize the image to a predefined standard, and convert to VP9 codec
                image_file.save(f'static/images/{original_name}')  # Save the file
    
    flash('Item updated successfully!', 'success')

    return redirect(url_for('admin_details_item', item_id=item_id))

@app.route('/admin/item_add', methods=['POST', 'GET'])
def admin_add_item():
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        quantity = request.form['quantity']
        description = request.form['description']

        if not title or not price or not quantity:
            flash('Title, price, and quantity are required.', 'error')
            return redirect(url_for('admin_add_item'))

        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            flash('Invalid price or quantity.', 'error')
            return redirect(url_for('admin_add_item'))

        with get_cursor() as cursor:
            cursor.execute('''
                INSERT INTO items (title, price, quantity, description) VALUES (?, ?, ?, ?)
            ''', (title, price, quantity, description))


            item_id = cursor.execute('SELECT last_insert_rowid()').fetchone()[0]
            for file_key in request.files:
                image_file = request.files[file_key]
                if image_file:
                    image_name = f"{str(uuid.uuid4())}.png"

                    cursor.execute('''
                        INSERT INTO images (item_id, image_name, slot) VALUES (?, ?, ?)
                    ''', (item_id, image_name, file_key))

                    #TODO (func): resize the image to a predefined standard, and convert to VP9 codec
                    image_file.save(f'static/images/{image_name}')  # Save the file

        flash('New item added successfully!', 'success')
        return redirect(url_for('admin_item_list'))

    return render_template('admin_add_item.html')

@app.route('/admin/item_update/<int:item_id>', methods=["GET"])
def admin_delete_item(item_id):
    logging.info(f"Deleting item with id: {item_id}")

    with get_cursor() as cursor:
        images = cursor.execute('SELECT image_name FROM images WHERE item_id = ?', (item_id,)).fetchall()
        for image in images:
            os.remove(f'static/images/{image[0]}')

        cursor.execute('DELETE FROM items WHERE id = ?', (item_id,))

    flash('Item deleted successfully!', 'success')
    return redirect(url_for('admin_item_list'))

@app.route('/admin/image_delete/<int:item_id>/<int:slot>', methods=['GET'])
def admin_delete_image(item_id, slot):
    logging.info(f"Deleting image with ids: {item_id} {slot}")

    with get_cursor() as cursor:
        image_name = cursor.execute('SELECT image_name FROM images WHERE item_id = ? AND slot = ?', (item_id, slot)).fetchone()[0]
        os.remove(f'static/images/{image_name}')
        cursor.execute('DELETE FROM images WHERE item_id = ? AND slot = ?', (item_id, slot))
    
    flash('Image deleted successfully!', 'success')
    return redirect(url_for('admin_details_item', item_id=item_id))

if __name__ == "__main__":
    db_setup()
    app.run(debug=True, host="0.0.0.0", port=3000)