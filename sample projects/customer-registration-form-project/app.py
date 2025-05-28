from flask import Flask, request
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS if your HTML is hosted separately (e.g., S3)

# ✅ Replace these with your actual RDS config
db_config = {
    'host': 'your-rds-endpoint.rds.amazonaws.com',
    'user': 'admin',
    'password': 'YourSecurePassword123',
    'database': 'cloud_form'
}

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Get data from the form
        name = request.form.get('fullname')
        email = request.form.get('email')
        address = request.form.get('address')
        phone = request.form.get('phone')

        # Validate inputs (optional)
        if not all([name, email, address, phone]):
            return "❌ Missing required fields", 400

        # Connect to RDS and insert data
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = """
            INSERT INTO personal_details (fullname, email, address, phone)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (name, email, address, phone))
        conn.commit()
        cursor.close()
        conn.close()

        return "✅ Data stored in RDS successfully!"

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return f"❌ Error storing data: {str(e)}", 500

@app.route('/', methods=['GET'])
def health_check():
    return "✅ Flask app is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
