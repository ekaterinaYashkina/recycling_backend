from flask import Flask, render_template, request, make_response, jsonify
# from geopy.geocoders import Nominatim
# import pymongo
from helpers import json_response, return_complex_json
import db
from bson.objectid import ObjectId
# import base64

app = Flask(__name__)
@app.route('/')
def flask_mongodb_atlas():
    return "flask mongodb atlas!"

@app.route("/test")
def test():
    res = db.place_collection.find()
    print(res.count())
    db.place_collection.insert_one({"name": "John"})
    return "Connected to the data base!"


@app.route('/gar_col_place', methods=('POST',))
def gar_col_place():


    if not (request.is_json
            and 'address' in request.json
            and 'coordinates' in request.json
            and 'type' in request.json
            and 'garbage_type' in request.json):
        return json_response(
            "fail",
            "Request contains no JSON body or required field",
            400
        )

    place_item = {

        "address": request.json["address"],
        "coordinates": {"lat": request.json["coordinates"]["lat"], "lon": request.json["coordinates"]["lon"]},
         "type": request.json["type"],
        "garbage_type": request.json["garbage_type"],
        "feedback_ids": []
                        }

    if "additional_info" in request.json:
        material_info = request.json["additional_info"].get("material_info", None)
        contacts = request.json["additional_info"].get("contacts", None)
        pics = request.json["additional_info"].get("pictures", None)
        text = request.json["additional_info"].get("text", None)
        place_item["additional_info"] = {"material_info": material_info,
                                         "contacts": contacts,
                                         "pictures": pics,
                                         "text": text}

    else:
        place_item["additional_info"] = None

    try:
        db.place_collection.insert_one(place_item)
        return json_response(
            "success",
            "Place is added",
            200
        )

    except:
        return json_response(
            "fail",
            "Database error",
            500
        )


@app.route('/get_places', methods=('GET',))
def get_all_places():


    try:
        res_1 = []
        res = db.place_collection.find()
        ids2posts = {}
        for elem in res:
            elem["_id"] = str(elem["_id"])
            res_1.append(elem)
            cur_id = elem["_id"]
            post_res = db.post_collection.find({ "place_id": cur_id } )
            ids2posts[cur_id] = []
            for post in post_res:
                post["_id"] = str(post["_id"])
                if cur_id in ids2posts:

                    ids2posts[cur_id].append(post)

                else:
                    ids2posts[cur_id] = [post]
    except:
        return json_response(
            "fail",
            "Database error",
            500
        )

    # print(ids2posts)
    # print(res_1)
    return return_complex_json(res_1, ids2posts, message='Retrieved all places info')

@app.route('/get_place_by_id', methods=('GET',))
def get_place_by_id():

    # print(request.form)
    if not (request.is_json and 'place_id' in request.json):
        return json_response(
            "fail",
            "Request contains no JSON body or required field",
            400
        )


    try:
        res = db.place_collection.find_one({'_id': ObjectId(request.json["place_id"])})
        ids2posts = {}

        res["_id"] = str(res["_id"])
        cur_id = res["_id"]
        post_res = db.post_collection.find({"place_id": cur_id})
        ids2posts[cur_id] = []
        for post in post_res:
            post["_id"] = str(post["_id"])
            ids2posts[cur_id].append(post)
    except:
        return json_response(
            "fail",
            "Database error",
            500
        )

    res = [res]
    return return_complex_json(res, ids2posts, message='Retrieved all places info')


"""
Posts requests processing

"""


@app.route('/give_feedback', methods=('POST',))
def give_feedback():


    if not (request.is_json
            and 'place_id' in request.json
            and 'place_info_rating' in request.json):
        return json_response(
            "fail",
            "Request contains no JSON body or required field",
            400
        )

    post_item = {

        "place_id": request.json["place_id"],
        "place_info_rating": request.json["place_info_rating"]
                        }
    if "all_correct" in request.json:
        all_correct = request.json.get("all_correct", None)
        post_item["all_correct"]= all_correct
    else:
        post_item["all_correct"] = None

    if "feedback" in request.json:
        wrong = request.json["feedback"].get("wrong", None)
        correct = request.json["feedback"].get("correct", None)
        additional = request.json["feedback"].get("additional_info", None)
        post_item["feedback"] = {
                                         "wrong": wrong,
                                         "correct": correct,
                                            "additional_info": additional}

    else:
        post_item["feedback"] = None
    #
    try:
        id = db.post_collection.insert_one(post_item)
        res = db.place_collection.find_one({'_id': ObjectId(request.json["place_id"])})
        existing = res["feedback_ids"]
        if existing is None or len(existing) == 0:
            existing = [str(id.inserted_id)]
        else:
            existing.append(str(id.inserted_id))
        print(existing)

        db.place_collection.update_one({
              '_id': res['_id']
            },{
              '$set': {
                'feedback_ids': existing
              }
            }, upsert=False)

        return json_response(
            "success",
            "Post is added",
            200
        )

    except Exception as e:
        print(e)
        return json_response(
            "fail",
            "Database error",
            500
        )


@app.route('/gar_col_place_feedback', methods=('POST',))
def gar_col_place_feedback():


    if not (request.is_json
            and 'address' in request.json
            and 'coordinates' in request.json
            and 'type' in request.json
            and 'garbage_type' in request.json
            and 'feedback' in request.json):
        return json_response(
            "fail",
            "Request contains no JSON body or required field",
            400
        )

    if not('place_info_rating' in request.json["feedback"]):
        return json_response(
            "fail",
            "Request contains no JSON body or required field",
            400
        )

    place_item = {

        "address": request.json["address"],
        "coordinates": {"lat": request.json["coordinates"]["lat"], "lon": request.json["coordinates"]["lon"]},
         "type": request.json["type"],
        "garbage_type": request.json["garbage_type"],
        "feedback_ids": []
                        }

    if "additional_info" in request.json:
        material_info = request.json["additional_info"].get("material_info", None)
        contacts = request.json["additional_info"].get("contacts", None)
        pics = request.json["additional_info"].get("pictures", None)
        text = request.json["additional_info"].get("text", None)
        place_item["additional_info"] = {"material_info": material_info,
                                         "contacts": contacts,
                                         "pictures": pics,
                                         "text": text}

    post_item = {
        "place_id": None,
        "place_info_rating": request.json["feedback"]["place_info_rating"]
    }
    if "all_correct" in request.json["feedback"]:
        all_correct = request.json["feedback"].get("all_correct", None)
        post_item["all_correct"]= all_correct
    else:
        post_item["all_correct"] = None

    if "feedback" in request.json["feedback"]:
        wrong = request.json["feedback"]["feedback"].get("wrong", None)
        correct = request.json["feedback"]["feedback"].get("correct", None)
        additional_info = request.json["feedback"]["feedback"].get("additional_info", None)
        post_item["feedback"] = {
                                         "wrong": wrong,
                                        "correct": correct,
                                         "additional_info": additional_info}
    else:
        post_item["feedback"] = None

    # try:

    id = db.place_collection.insert_one(place_item)
    post_item["place_id"] = str(id.inserted_id)

    id1 = db.post_collection.insert_one(post_item)
    res = db.place_collection.find_one({'_id': ObjectId(id.inserted_id)})
    existing = res["feedback_ids"]
    if existing is None or len(existing) == 0:
        existing = [str(id1.inserted_id)]
    else:
        existing.append(str(id1.inserted_id))
    print(existing)

    db.place_collection.update_one({
        '_id': res['_id']
    }, {
        '$set': {
            'feedback_ids': existing
        }
    }, upsert=False)

    return json_response(
        "success",
        "Post is added",
        200
    )

    # except Exception as e:
    #     print("Exception", e)
    #     return json_response(
    #         "fail",
    #         "Database error",
    #         500
    #     )

# @app.route('/file-upload', methods=['POST'])
# def upload_file():
#
#     image = request.json["image"]
#     text = request.json["text"]
#     print(text)
#     print(image)
#     img = base64.b64decode(image)
#
#
#     # print(request.form["data"].is_json)
#     # imgs = request.form["image"]
#     # data = request.form["data"]
#     #
#     # print(data)
#
#     return json_response(
#         "success",
#         "Added",
#         200
#     )

if __name__ == '__main__':
    # app.run(port=8000)
    app.run(host='0.0.0.0', port = 8000)
# class mongo_connection:
#     conn = None
#
#     def connect(self):
#         myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#         mydb = myclient["flask_tutorial"]
#         self.conn = mydb["restaurants"]
#
#     def query(self, sql):
#         cursor = self.conn.find(sql)
#         return cursor
#
#
# db = mongo_connection()
# db.connect()
#
# app = Flask(__name__)
#
#
# # @app.route('/')
# # def index():
# #     return render_template("index.html")
#
#


#
#
# @app.route('/give_feedback', methods=('POST',))
# def give_feedback():
#
#
#     if not (request.is_json
#             and 'place_id' in request.json
#             and 'place_info_rating' in request.json):
#         return json_response(
#             "fail",
#             "Request contains no JSON body or required field",
#             400
#         )
#
#     pass
#
#
# @app.route('/gar_col_place_feedback', methods=('POST',))
# def gar_col_place_feedback():
#
#
#     if not (request.is_json
#             and 'address' in request.json
#             and 'coordinates' in request.json
#             and 'type' in request.json
#             and 'garbage_type' in request.json
#             and 'place_id' in request.json
#             and 'place_info_rating' in request.json):
#         return json_response(
#             "fail",
#             "Request contains no JSON body or required field",
#             400
#         )
#
#     pass
#
#
#
# @app.route('/get_by_id', methods=['GET'])
# def get_by_id():
#
#     if not (request.is_json
#             and 'place_id' in request.json):
#
#         return json_response(
#             "fail",
#             "Request contains no JSON body or required field",
#             400
#         )
#
#     cur_id = request.args["place_id"]
#
#
#     pass
#
#
# ## Example from the Internet
# @app.route('/get_all_data', methods=['GET'])
# def get_all_data():
#     restname = request.args.get('restaurant')
#     city = request.args.get('city')
#     state = request.args.get('state')
#     zipcode = request.args.get('zipcode')
#     rad = request.args.get('radius')
#     print(rad)
#     print(type(rad))
#
#     print(restname, city, state, zipcode)
#
#     zip_or_addr = city + ' ' + state + ' ' + zipcode
#
#     print(f'zip_or_addr: {zip_or_addr}')
#
#     geolocator = Nominatim(user_agent='myapplication')
#     location = geolocator.geocode(zip_or_addr)
#     lat = float(location.raw['lat'])
#     lon = float(location.raw['lon'])
#     nearby_restaurants = [{'orig_lat': lat, 'orig_lon': lon}]
#
#     print(lat, lon)
#
#     METERS_PER_MILE = 1609.34
#
#     filters = {'location': {'$nearSphere': {'$geometry': {'type': "Point",
#                                                           'coordinates': [lon, lat]},
#                                             '$maxDistance': int(rad) * METERS_PER_MILE}},
#                'name': {'$regex': restname, "$options": "i"}}
#
#     cursor = db.query(filters)
#
#     for cur in cursor:
#         nearby_restaurants.append({
#             'restaurant_name': cur['name'],
#             'lat': cur['location']['coordinates'][1],
#             'lon': cur['location']['coordinates'][0]
#         })
#
#     return jsonify(nearby_restaurants)
#
#
# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=9763, debug=True)