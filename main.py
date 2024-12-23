import sqlite3
from bottle import Bottle, run, template, request, redirect

# Initialize the Bottle app
app = Bottle()

# Initialize the SQLite database and create a table for products if it doesn't exist
def init_db():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()

    # Create a table for products if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL
                )''')

    # Create a table for orders if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )''')

    # Insert some sample products if table is empty
    c.execute('SELECT COUNT(*) FROM products')
    if c.fetchone()[0] == 0:
        sample_products = [
            ('Laptop', 1000.00),
            ('Smartphone', 700.00),
            ('Tablet', 300.00),
            ('Smartwatch', 150.00)
        ]
        c.executemany('INSERT INTO products (name, price) VALUES (?, ?)', sample_products)
    
    conn.commit()
    conn.close()

# Route to display the form and product list
@app.route('/')
def product_form():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()

    # Fetch the list of products from the database
    c.execute('SELECT * FROM products')
    products = c.fetchall()

    conn.close()

    # Render the form with the list of products
    return template('''
        <h1>Place Your Order</h1>
        <form action="/submit_order" method="POST">
            <label for="product">Select Product:</label>
            <select name="product_id" id="product">
                % for product in products:
                    <option value="{{product[0]}}">{{product[1]}} (Price: ${{product[2]}})</option>
                % end
            </select><br><br>

            <label for="quantity">Quantity:</label>
            <input type="number" name="quantity" id="quantity" min="1" required><br><br>

            <input type="submit" value="Submit Order">
        </form>

        <h2>Available Products:</h2>
        <ul>
            % for product in products:
                <li>{{product[1]}} - ${{product[2]}}</li>
            % end
        </ul>
    ''', products=products)

# Route to handle form submission and insert order into the database
@app.route('/submit_order', method='POST')
def submit_order():
    product_id = request.forms.get('product_id')
    quantity = request.forms.get('quantity')

    conn = sqlite3.connect('products.db')
    c = conn.cursor()

    # Insert the order into the database
    c.execute('INSERT INTO orders (product_id, quantity) VALUES (?, ?)', (product_id, quantity))
    conn.commit()
    conn.close()

    # Redirect to the home page after order submission
    redirect('/')

# Run the app
if __name__ == '__main__':
    # Initialize the database and sample data
    init_db()

    # Run the Bottle app on localhost and port 8080
    run(app, host='localhost', port=8080, debug=True)
