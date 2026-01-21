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


def average(student):
    g = student["grades"]
    return (g["math"]["mark"] + g["science"]["mark"] + g["english"]["mark"]) / 3


# ---------- ADD STUDENT ----------
@app.route("/", methods=["GET", "POST"])
def add_student():
    message = None

    if request.method == "POST":
        student = {
            "id": len(students) + 1,
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


# ---------- DASHBOARD (SORTED TOP → LOW) ----------
@app.route("/dashboard")
def dashboard():
    sorted_students = sorted(students, key=average, reverse=True)
    return render_template("dashboard.html", students=sorted_students)


# ---------- SEARCH ----------
@app.route("/search")
def search():
    name = request.args.get("name", "").lower()
    result = [s for s in students if name in s["name"].lower()]
    return jsonify(result)


# ---------- UPDATE MARKS ----------
@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    for s in students:
        if s["id"] == id:
            s["grades"]["math"]["mark"] = int(request.form["math"])
            s["grades"]["science"]["mark"] = int(request.form["science"])
            s["grades"]["english"]["mark"] = int(request.form["english"])

            s["grades"]["math"]["grade"] = grade_from_mark(s["grades"]["math"]["mark"])
            s["grades"]["science"]["grade"] = grade_from_mark(s["grades"]["science"]["mark"])
            s["grades"]["english"]["grade"] = grade_from_mark(s["grades"]["english"]["mark"])

            save()
            break
    return redirect("/dashboard")


# ---------- STATISTICS ----------
@app.route("/stats")
def stats():
    if not students:
        return jsonify({"class_avg": 0, "top": "N/A"})

    sorted_students = sorted(students, key=average, reverse=True)
    class_avg = sum(average(s) for s in students) / len(students)

    return jsonify({
        "class_avg": round(class_avg, 2),
        "top": sorted_students[0]["name"]
    })


if __name__ == "__main__":
    app.run(debug=True)
