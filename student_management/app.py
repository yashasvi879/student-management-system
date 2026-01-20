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


# ---------- HOME / ADD STUDENT ----------
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
                "math": int(request.form["math"]),
                "science": int(request.form["science"]),
                "english": int(request.form["english"])
            }
        }
        students.append(student)
        save()
        message = "Student added successfully"

    return render_template("add_student.html", message=message)


# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", students=students)


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
            s["grades"]["math"] = int(request.form["math"])
            s["grades"]["science"] = int(request.form["science"])
            s["grades"]["english"] = int(request.form["english"])
            save()
            break
    return redirect("/dashboard")


# ---------- STATISTICS ----------
@app.route("/stats")
def stats():
    if not students:
        return jsonify({"class_avg": 0, "top": "N/A"})

    total = 0
    top_name = ""
    highest = 0

    for s in students:
        g = s["grades"]
        avg = (g["math"] + g["science"] + g["english"]) / 3
        total += avg
        if avg > highest:
            highest = avg
            top_name = s["name"]

    return jsonify({
        "class_avg": round(total / len(students), 2),
        "top": top_name
    })


if __name__ == "__main__":
    app.run(debug=True)
