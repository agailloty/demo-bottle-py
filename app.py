import sqlite3
from bottle import Bottle, run, template, request, redirect, static_file

# Initialize the Bottle app
app = Bottle()

# Initialize the SQLite database and create tables if they don't exist
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

    conn.commit()
    conn.close()

# Serve Tailwind CSS from CDN (you could also host it locally)
@app.route('/static/<filename>')
def serve_static(filename):
    return static_file(filename, root='./static')

# Route to display the order form and product list
@app.route('/')
def product_form():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()

    # Fetch the list of products from the database
    c.execute('SELECT * FROM products')
    products = c.fetchall()

    conn.close()

    # Render the form with the list of products using Tailwind CSS for styling
    return template('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Order Products</title>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.0.2/dist/tailwind.min.css" rel="stylesheet">
        </head>
        <body class="bg-gray-100 text-gray-800">
            <div class="container mx-auto p-4">
                <h1 class="text-3xl font-bold mb-4 text-center">Order Tech Products</h1>

                <!-- Order Form Section -->
                <div class="bg-white p-6 rounded-lg shadow-md mb-6">
                    <h2 class="text-xl font-semibold mb-4">Place Your Order</h2>
                    <form action="/submit_order" method="POST" class="space-y-4">
                        <div>
                            <label for="product" class="block font-medium">Select Product:</label>
                            <select name="product_id" id="product" class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500">
                                % for product in products:
                                    <option value="{{product[0]}}">{{product[1]}} (Price: ${{product[2]}})</option>
                                % end
                            </select>
                        </div>

                        <div>
                            <label for="quantity" class="block font-medium">Quantity:</label>
                            <input type="number" name="quantity" id="quantity" min="1" required class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500">
                        </div>

                        <button type="submit" class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700">Submit Order</button>
                    </form>
                </div>

                <!-- Add Product Form Section -->
                <div class="bg-white p-6 rounded-lg shadow-md">
                    <h2 class="text-xl font-semibold mb-4">Add New Product</h2>
                    <form action="/add_product" method="POST" class="space-y-4">
                        <div>
                            <label for="name" class="block font-medium">Product Name:</label>
                            <input type="text" name="name" id="name" required class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500">
                        </div>

                        <div>
                            <label for="price" class="block font-medium">Price:</label>
                            <input type="number" step="0.01" name="price" id="price" required class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500">
                        </div>

                        <button type="submit" class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700">Add Product</button>
                    </form>
                </div>
            </div>
        </body>
        </html>
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

# Route to handle adding new products
@app.route('/add_product', method='POST')
def add_product():
    name = request.forms.get('name')
    price = request.forms.get('price')

    conn = sqlite3.connect('products.db')
    c = conn.cursor()

    # Insert the new product into the database
    c.execute('INSERT INTO products (name, price) VALUES (?, ?)', (name, price))
    conn.commit()
    conn.close()

    # Redirect to the home page after adding the product
    redirect('/')

# Run the app
if __name__ == '__main__':
    # Initialize the database
    init_db()

    # Run the Bottle app on localhost and port 8080
    run(app, host='localhost', port=8080, debug=True)
