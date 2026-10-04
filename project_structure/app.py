from flask import Flask,render_template,request,redirect


app = Flask(__name__)

data ={
    "1":{'name':'moulya','class':5,'Marks':80},
    "2":{'name':'siri','class':6,'Marks':50},
    "3":{'name':'charan','class':5,'Marks':75},
    "4":{'name':'harika','class':7,'Marks':35},
    "5":{'name':'sai','class':8,'Marks':70}
}
# @app.route('/path')
# def func():
      # block statements
      # return statments
# home route
@app.route('/')
def home():
    return render_template('home.html',name="moulya",module="Flask",Batch = 60,time = "2-4 PM")

@app.route('/students')
def students():
  return render_template('students.html',students = data)


# register
@app.route('/register',methods = ['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        name = request.form.get('username')
        Class_no = request.form.get('Class')
        Marks = int(request.form.get('Marks'))
        print(name,Class_no,Marks)
        id = len(data) + 1
        student_data = {'name':name,'class':Class_no,'Marks':Marks}
        data[id] = student_data
        return redirect('/students')



#@app.route('/classdata',method = 'POST')
#def classdata():

#@app.route('/students/1')
#def student1():
#    return data["1"]

#@app.route('/students/2')
#def student1():
#    return data["2"]


#Dynamic path parameters
#@app.route("/students/<id>")
#def get_student_data(id):
 #   print(type(id))
 #   if id in data:
 #       return data[id]
  #  return "student id not found"
# Dynamic path parameter data
@app.route('/class-data',methods = ['GET','POST'])
def get_class_data():
    if request.method =='GET':
        return render_template('class_data.html')
    if request.method =='POST':
        # get form data
        # filter data as per the class
        # show data in browser
        class_number = int(request.form.get('class'))
        res = {}
        for id in data:
            if data[id]['class'] == class_number:
                res[id] = data[id]
        return render_template('class_data.html', students = res)
# Get student by search student name
@app.route("/students/<name>")
def get_student_data(name):
    students = []
    for student in data.values():
        if name in student["name"]:
            students.append(student)
    if students:
        return students
    return "Student not found"

# contact route
@app.route('/contact')
def contact():
    return "This is contact page"

# main
if __name__=="__main__":
    app.run(debug = True) #changes browser lo reflect avutaye debug = true ani pedete