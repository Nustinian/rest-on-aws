from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_claims, jwt_optional, get_jwt_identity, fresh_jwt_required
from models.item import ItemModel

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price', type=float, required=True, help="'price' field cannot be left blank")
    parser.add_argument('store_id', type=int, required=True, help="'store_id' field cannot be left blank") 

    @jwt_required
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {"message": "Item not found."}, 404

    @fresh_jwt_required
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {"message": "Item already exists."}, 400
        data = Item.parser.parse_args()
        item = ItemModel(name, **data)
        try:
            item.save_to_db()
        except:
            return {"message": "Something went wrong on our end. Sorry about that."}, 500
        return {"message": "Successfully added item.", "item": item.json()}, 201

    def put(self, name):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(name)
        try:
            if item:
                item.price = data['price']
                item.store_id = data['store_id']
            else:
                item = ItemModel(name, **data)
            item.save_to_db()
        except:
            return {"message": "Something went wrong internally. Sorry about that."}, 500
        return {"message": "Successfully updated item.", "item": item.json()}, 201

    @jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        return claims
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401
        item = ItemModel.find_by_name(name)
        if ItemModel.find_by_name(name):
            item.delete_from_db()
            return {'message': 'Item deleted.'}
        return {'message': 'Item not found.'}


class ItemList(Resource):
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]
        if user_id:
            return {"items": items}
        return {"items": [item['name'] for item in items], "message": "More data available if you log in."}