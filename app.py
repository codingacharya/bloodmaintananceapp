from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/blood_bank"
mongo = PyMongo(app)

default_blood_units = {"A+": 0, "A-": 0, "B+": 0, "B-": 0, "O+": 0, "O-": 0, "AB+": 0, "AB-": 0}

@app.route('/')
def index():
    inventory = list(mongo.db.blood_inventory.find())
    return render_template('index.html', inventory=inventory)

@app.route('/add_donor', methods=['POST'])
def add_donor():
    donor = {
        "name": request.form['name'],
        "blood_type": request.form['blood_type'],
        "contact": request.form['contact']
    }
    mongo.db.donors.insert_one(donor)
    return redirect(url_for('index'))

@app.route('/add_inventory', methods=['POST'])
def add_inventory():
    blood_type = request.form['blood_type']
    units = int(request.form['units'])
    mongo.db.blood_inventory.update_one({"blood_type": blood_type}, {"$inc": {"units": units}}, upsert=True)
    return redirect(url_for('index'))

@app.route('/request_blood', methods=['POST'])
def request_blood():
    requester_name = request.form['requester_name']
    blood_type = request.form['blood_type']
    units_needed = int(request.form['units_needed'])
    inventory = mongo.db.blood_inventory.find_one({"blood_type": blood_type})
    
    if inventory and inventory.get("units", 0) >= units_needed:
        mongo.db.blood_inventory.update_one({"blood_type": blood_type}, {"$inc": {"units": -units_needed}})
        new_request = {
            "requester_name": requester_name,
            "blood_type": blood_type,
            "units_needed": units_needed
        }
        mongo.db.blood_requests.insert_one(new_request)
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    for blood_type in default_blood_units:
        if not mongo.db.blood_inventory.find_one({"blood_type": blood_type}):
            mongo.db.blood_inventory.insert_one({"blood_type": blood_type, "units": 0})
    app.run(debug=True)
