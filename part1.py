from flask import Flask, jsonify, request

app=Flask(__name__)

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.json
   
    #Creating Required fields
     required-[‘name’, ‘sku’, ‘price’, ‘warehouse_id’, ‘initial_quantity’]
     for field in required:
	if field not in data or data[field] is None:
		return{“error”: f“Missing {field}”},400
 

    # Checking if SKU exists
     if Product.query.filter_by(sku=data[‘sku]).first():
	return {“error”: “SKU already exists”} , 409

    try:
     #Saving both together
      product = Product(
		name=data['name'],
        	sku=data['sku'],
        	price=float(data['price']))
    db.session.add(product)
    db.session.flush()

     inventory=Inventory(
Product_id=product.id, 
warehouse_id=data['warehouse_id'], 
            quantity=data[‘initial_quantity’]
    )
    
    db.session.add( inventory)
    db.session.commit()    
             return {"message": "Product created", "product_id": product.id}
     except Exception as e:
	db.session.rollback()
	return{“error” : str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)
