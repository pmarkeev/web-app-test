# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 18:20:52 2022

@author: MarkeevP
"""

import xml.etree.ElementTree as ET
from flask import Flask
from flask_restful import reqparse, Api
import yak_modules
from flask_sqlalchemy import SQLAlchemy
from os.path import exists
from sqlalchemy.sql import func

# Create an instance of Flask
app = Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.sqlite3'
# Create the API
api = Api(app)

def read_herd_xml(file_name):        
    tree = ET.parse(file_name)
    root = tree.getroot()
    herd_temp = yak_modules.Herd()     
    for yak_tag in root.findall('labyak'):
        name = yak_tag.get('name')
        age = float(yak_tag.get('age'))
        sex = yak_tag.get('sex')
        herd_temp.add_yak(yak_modules.Yak(name, age, sex))
    return herd_temp

herd = read_herd_xml('Herd.xml')

db = SQLAlchemy(app)

class Orders(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    milk = db.Column(db.Float(100))  
    skins = db.Column(db.Integer)

    def __init__(self, name, milk, skins):
        self.name = name
        self.milk = milk
        self.skins = skins
    
    def set_milk(self, milk):
        self.milk = milk
        
    def set_skins(self, skins):
        self.skins = skins   

db.create_all()

@app.route('/yak-shop/stock/<int:days>', methods = ['GET'])
def stock_resource(days):
    return {"milk": round(herd.stock_milk(days), 2), "skins": herd.stock_hides(days)}, 200

@app.route('/yak-shop/herd/<int:days>', methods = ['GET'])
def herd_info(days):
    return {"herd" : herd.identify(days)}, 200

@app.route('/yak-shop/order/<int:days>', methods = ['POST'])
def order_page(days):
    parser = reqparse.RequestParser()

    parser.add_argument('name', type=str, required=True)
    parser.add_argument('milk', type=float, required=True)
    parser.add_argument('skins', type=float, required=True)
    
    args = parser.parse_args()

    already_ordered_milk = db.session.query(func.sum(Orders.milk).label('sum_milk')).scalar() 
    already_ordered_skins = db.session.query(func.sum(Orders.skins).label('sum_skins')).scalar()

    already_ordered_milk = 0 if already_ordered_milk is None else already_ordered_milk
    already_ordered_skins = 0 if already_ordered_skins is None else already_ordered_skins

    available_milk = herd.stock_milk(days)  - already_ordered_milk
    available_skins = herd.stock_hides(days) - already_ordered_skins
    
    if (available_milk < args['milk'] and available_skins < args['skins']):
        return 'Not in stock', 404
    
    order = Orders(name=args['name'], milk=0 , skins=0)
    response = {}
    
    milk_ordered, skins_ordered = False, False
        
    if available_milk >= args['milk']:
    	order.set_milk(args['milk'])
    	response["milk"] = args['milk']
    	milk_ordered = True
    
    if (available_skins >= args['skins']):
    	order.set_skins(args['skins'])
    	response["skins"]=args['skins']
    	skins_ordered = True
    
    db.session.add(order)
    db.session.commit()
    
    status = 200 if milk_ordered & skins_ordered else 206
    
    return response, status

@app.route('/yak-shop/view-orders', methods = ['GET'])
def see_all_orders():
    query_all = Orders.query.all()
    query_all_list = []
    
    for order in query_all:
        query_all_list.append({order:[order.name, order.milk, order.skins]})
    
    return str(query_all_list), 201

@app.route('/shepherd/clear-orders/', methods = ['DELETE'])
def delete():
        query = Orders.query.all()
        
        for i in query:
            db.session.delete(i)
            db.session.commit()
        
        return '', 204

@app.route('/shepherd/add-yak', methods = ['POST'])
def add_yak():
    parser = reqparse.RequestParser()

    parser.add_argument('name', type=str, required=True)
    parser.add_argument('age', type=float, required=True)
    parser.add_argument('sex', type=str, required=True)
    
    args = parser.parse_args()
    
    herd.add_yak(yak_modules.Yak(args['name'], args['age'], args['sex']))
    
    if exists('Herd_udated.xml'):
        tree = ET.parse('Herd_udated.xml')
    else: 
        tree = ET.parse('Herd.xml')
    root = tree.getroot()
    string_to_add = '<labyak sex="' + args['sex'] + '" age="' + str(args['age']) + '" name="' + args['name'] + '"/>' 
    root.append(ET.fromstring(string_to_add))
    tree.write("Herd_updated.xml")
    
    return 'Herd was updated', 200

app.run()