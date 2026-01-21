from flask import Flask, render_template, request, redirect, jsonify
import json, os

app = Flask(__name__)

FILE = "students.json"

students = []
if os.path.exists(FILE):
    try:
        with open(FILE, "r") as f:
            students = json.load(f)
    except json.JSONDecodeError:
        students = []


def save():
    with open(FILE, "w") as f:
        json.dump(students, f, indent=4)


# ---------- GRADE FUNCTION ----------
def grade_from_mark(mark):
    if mark >= 90:
        return "A"
    elif mark >= 75:
        return "B"
    elif mark >= 60:
        return "C"
    elif mark >= 50:
        return "D"
    else:
        return "F"


# ---------- AVERAGE (SAFE) ----------
def average(student):
    g = student["grades"]

    def get_mark(sub):
        if isinstance(g[sub], dict):
            return g[sub]["mark"]
        return g[sub]

    return (get_mark("math") + get_mark("science") + get_mark("english")) / 3


# ---------- ADD STUDENT ----------
@app.route("/", methods=["GET", "POST"])
def add_student():
    message = None

    if request.method == "POST":
        student = {
            "id": len(students) + 1,
            "rollno": request.form["rollno"],
            "name": request.form["name"],
            "age": int(request.form["age"]),
            "class_name": request.form["class_name"],
            "gender": request.form["gender"],
            "grades": {
                "math": {
                    "mark": int(request.form["math"]),
                    "grade": grade_from_mark(int(request.form["math"]))
                },
                "science": {
                    "mark": int(request.form["science"]),
                    "grade": grade_from_mark(int(request.form["science"]))
                },
                "english": {
                    "mark": int(request.form["english"]),
                    "grade": grade_from_mark(int(request.form["english"]))
                }
            }
        }
        students.append(student)
        save()
        message = "Student added successfully"

    return render_template("add_student.html", message=message)


# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    ranked_students = sorted(students, key=average, reverse=True)
    return render_template("dashboard.html", students=ranked_students)


# ---------- SEARCH ----------
@app.route("/search")
def search():
    name = request.args.get("name", "").lower()
    result = [s for s in students if name in s["name"].lower()]
    return jsonify(result)


# ---------- UPDATE FULL DETAILS ----------
@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    for s in students:
        if s["id"] == id:
            s["rollno"] = request.form["rollno"]
            s["name"] = request.form["name"]
            s["age"] = int(request.form["age"])

            for sub in ["math", "science", "english"]:
                mark = int(request.form[sub])
                s["grades"][sub] = {
                    "mark": mark,
                    "grade": grade_from_mark(mark)
                }

            save()
            break
    return redirect("/dashboard")


# ---------- STATISTICS (ALL RANKED) ----------
@app.route("/stats")
def stats():
    ranked = sorted(students, key=average, reverse=True)

    output = []
    for s in ranked:
        output.append({
            "rollno": s["rollno"],
            "name": s["name"],
            "average": round(average(s), 2)
        })

    return jsonify(output)


if __name__ == "__main__":
    app.run(debug=True)

