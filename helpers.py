from flask import make_response, jsonify

def json_response(status, message, status_code):
    return make_response(jsonify({
        "status": status,
        "message": message
    }), status_code)


def return_complex_json(ret_data, ids2post, message, status_code = 200, status = "success"):


    data = {}
    # ret_data_c = []
    # for elem  in ret_data:
    #     # el_id = elem["_id"]
    #     # print(el_id)
    #     elem["_id"] = str(elem["_id"])
    #     print(elem)
    #     ret_data_c.append(elem)
    # if len(ret_data_c) == 1:
    #     ret_data_c = ret_data_c[0]
    #
    # for k, v in ids2post.items():
    #     for elem in v:
    #         elem["_id"] = str(elem["_id"])
    data["places"] = ret_data
    data["posts"] = ids2post

    return make_response(jsonify({
        "status": status,
        "message": message,
        "data": data
    }), status_code)
