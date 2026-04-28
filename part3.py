@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def low_stock_alerts(company_id):
    THRESHOLDS = {'standard': 20, 'perishable': 10}  # Rule 1: Threshold by type
    
    try:
        # EDGE CASE 1
        warehouses = db.session.query(Warehouse).filter_by(company_id=company_id).all()
        if not warehouses:
            return jsonify({'alerts': [], 'total_alerts': 0}), 200
        
        alerts = []
        
        for warehouse in warehouses:
           
            low_items = db.session.query(Inventory).outerjoin(Product).filter(
                Inventory.warehouse_id == warehouse.id,
                Inventory.quantity < THRESHOLDS.get(Product.type, 20)  # Default 20
            ).all()
            
            for inv in low_items:
                product = inv.product
                
                # EDGE CASE 2
                recent_sales = db.session.query(func.sum(Sale.quantity)).filter(
                    Sale.product_id == product.id,
                    Sale.created_at >= datetime.now() - timedelta(days=30)
                ).scalar() or 0
                
                if recent_sales == 0:
                    continue  # Rule 2: Only recent activity
                
                # EDGE CASE 3
                avg_daily = recent_sales / 30.0
                days_out = 999 if avg_daily == 0 else int(inv.quantity / avg_daily)
                
                # EDGE CASE 4
                supplier = db.session.query(Supplier).join(ProductSupplier).filter(
                    ProductSupplier.product_id == product.id
                ).first()
                
                alert = {
                    'product_id': product.id,
                    'product_name': product.name,
                    'sku': product.sku,
                    'warehouse_id': warehouse.id,
                    'warehouse_name': warehouse.name,
                    'current_stock': inv.quantity,
                    'threshold': THRESHOLDS.get(product.type, 20),
                    'days_until_stockout': days_out,
                    'supplier': {
                        'id': supplier.id if supplier else None,
                        'name': supplier.name if supplier else 'No supplier assigned',
                        'contact_email': supplier.email if supplier else None
                    }
                }
                alerts.append(alert)
        
        # Sort by urgency (bonus!)
        alerts.sort(key=lambda x: x['days_until_stockout'])
        
        return jsonify({
            'alerts': alerts,
            'total_alerts': len(alerts)
        }), 200
        
    except Exception as e:
        # EDGE CASE 5:
        return jsonify({'error': 'Service unavailable', 'details': str(e)}), 500
