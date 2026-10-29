from flask import Flask, request, jsonify,session, make_response,redirect
app = Flask(__name__)
app.secret_key= "moulya@12345"
data = {
    1:{'name':"moulya",'class':5},
    2:{'name':"swathi",'class':6},
    3:{'name':"sowmya",'class':5},
    4:{'name':"shannu",'class':8},
    5:{'name':"ram",'class':7}
}
@app.route('/')
def home():
    return {"msg":"This is student application"}

@app.route('/login')
def login():
    response=make_response("Here data can store in cookie format")
    response.set_cookie("username","moulya")
    # response.set_cookie("id","5")
    session['id']=5
    return response

#get data from cookies:
@app.route("/readcookie")
def read_cookie():
    if "id" not in session:
        return redirect ('/')

    username=request.cookies.get('username')
    return f"This browser using user is :{username},id:{session['id']}"


@app.route('/students', methods = ['GET'])
def Get_all_students():
    class_no = int(request.args.get('class'))
    res={}
    if class_no:
        for id in data:
            if data[id]['class'] == class_no:
                res[id]=data[id]
    return jsonify(res if res else data)

#get students data as per id-{dynamic path parameter)
@app.route('/students/<int:id>', methods = ['GET'])
def get_student_data_by_id(id):
    if id in data:
        return jsonify({"msg":"success", "data":data[id]})
    return jsonify({'status': "error", "msg":"Student id not found"}),404

#register a student
@app.route('/students', methods=['POST'])
def register():
    new_student=request.get_json()
    if 'name' not  in new_student or 'class' not in new_student:
        return jsonify({"status":"error","msg":f"Reguest data format incorrect"}),400

    id=len(data)+1
    data[id] = new_student
    return jsonify({"status":"success","msg":f"Registered Successfully and  your id is {id}"}),201

# Update a student
@app.route('/students/<int:id>', methods=['PUT'])
def update(id):
    new_student = request.get_json()
    if id not in data:
        return jsonify({"status": "error","msg": "Student not found"}), 404

    data[id] = new_student

    return jsonify({ "status": "success","msg": f"Updated Successfully and your id is {id}"}), 200

#delete students
# Delete a student
@app.route('/students/<int:id>', methods=['DELETE'])
def delete(id):

    if id not in data:
        return jsonify({"status": "error","msg": "Student not found"}), 404

    del data[id]

    return jsonify({"status": "success","msg": f"Student deleted successfully. ID: {id}"}), 200

#main
if __name__ == "__main__":
    app.run(debug=True)