
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import uuid

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb+srv://umatiyaaziz2004_db_user:lkCvLsRTypDho7Wx@siramik.k3vxnao.mongodb.net/')
db = client['invoice_db']
invoices_collection = db['invoices']

# Helper function to format date
def format_date(date_str):
    if not date_str:
        return ''
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%d %B, %Y')
    except:
        return date_str

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    invoices = list(invoices_collection.find())
    for inv in invoices:
        inv['_id'] = str(inv['_id'])
        inv['date'] = format_date(inv.get('date', ''))
        inv['nameDate'] = format_date(inv.get('nameDate', ''))
        inv['total'] = float(inv['total']) if 'total' in inv else 0
        inv['amountPaid'] = float(inv.get('amountPaid', 0))
        inv['payments'] = inv.get('payments', [])
    return jsonify(invoices)

@app.route('/api/invoices', methods=['POST'])
def save_invoice():
    data = request.json
    invoice = {
        '_id': str(uuid.uuid4()),
        'number': data['number'],
        'date': data['date'],
        'name': data['name'],
        'address': data['address'],
        'city': data['city'],
        'nameNumber': data.get('nameNumber', ''),
        'nameDate': data.get('nameDate', ''),
        'npn': data.get('npn', ''),
        'items': data['items'],
        'total': float(data['total']),
        'amountPaid': float(data.get('amountPaid', 0)),
        'payments': data.get('payments', []),
        'amountInWords': data.get('amountInWords', ''),
        'numberValue': data.get('numberValue', ''),
        'createdAt': datetime.utcnow().isoformat()
    }
    invoices_collection.insert_one(invoice)
    return jsonify({'message': 'Invoice saved successfully', 'id': invoice['_id']})

@app.route('/api/invoices/<id>', methods=['GET'])
def get_invoice(id):
    invoice = invoices_collection.find_one({'_id': id})
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404
    invoice['_id'] = str(invoice['_id'])
    invoice['date'] = format_date(invoice.get('date', ''))
    invoice['nameDate'] = format_date(invoice.get('nameDate', ''))
    invoice['total'] = float(invoice['total'])
    invoice['amountPaid'] = float(invoice.get('amountPaid', 0))
    return jsonify(invoice)

@app.route('/api/invoices/<id>', methods=['PUT'])
def update_invoice(id):
    data = request.json
    invoice = {
        'number': data['number'],
        'date': data['date'],
        'name': data['name'],
        'address': data['address'],
        'city': data['city'],
        'nameNumber': data.get('nameNumber', ''),
        'nameDate': data.get('nameDate', ''),
        'npn': data.get('npn', ''),
        'items': data['items'],
        'total': float(data['total']),
        'amountPaid': float(data.get('amountPaid', 0)),
        'payments': data.get('payments', []),
        'amountInWords': data.get('amountInWords', ''),
        'numberValue': data.get('numberValue', ''),
        'updatedAt': datetime.utcnow().isoformat()
    }
    result = invoices_collection.update_one({'_id': id}, {'$set': invoice})
    if result.matched_count == 0:
        return jsonify({'error': 'Invoice not found'}), 404
    return jsonify({'message': 'Invoice updated successfully'})

@app.route('/api/invoices/<id>', methods=['DELETE'])
def delete_invoice(id):
    result = invoices_collection.delete_one({'_id': id})
    if result.deleted_count == 0:
        return jsonify({'error': 'Invoice not found'}), 404
    return jsonify({'message': 'Invoice deleted successfully'})

@app.route('/api/invoices/search', methods=['GET'])
def search_invoices():
    name = request.args.get('name', '').lower()
    address = request.args.get('address', '').lower()
    query = {}
    if name:
        query['name'] = {'$regex': name, '$options': 'i'}
    if address:
        query['address'] = {'$regex': address, '$options': 'i'}
    invoices = list(invoices_collection.find(query))
    for inv in invoices:
        inv['_id'] = str(inv['_id'])
        inv['date'] = format_date(inv.get('date', ''))
        inv['nameDate'] = format_date(inv.get('nameDate', ''))
        inv['total'] = float(inv['total'])
        inv['amountPaid'] = float(inv.get('amountPaid', 0))
    return jsonify(invoices)

@app.route('/api/invoice-number', methods=['GET'])
def get_invoice_number():
    last_invoice = invoices_collection.find_one(sort=[('createdAt', -1)])
    counter = int(last_invoice['number'].replace('G2FEE', '')) + 1 if last_invoice else 1
    return jsonify({'number': f'G2FEE{counter:03d}'})

if __name__ == '__main__':
    app.run(debug=True)