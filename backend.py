from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Simulated user progress data
user_progress = {
    "quizzes_completed": 0,
    "documents_studied": 0,
    "average_score": 0,
    "quiz_scores": []
}

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/features")
def features():
    return render_template("features.html")

@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

@app.route("/assessments")
def assessments():
    return render_template("assessments.html")

@app.route("/progress")
def progress():
    return render_template("progress.html")

@app.route("/recommendations")
def recommendations():
    return render_template("recommendations.html")

# ---------------- FILE UPLOAD ---------------- #

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    # For demo: just read plain text (works for .txt)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        content = "Uploaded file saved but preview not available."

    user_progress["documents_studied"] += 1

    return jsonify({"filename": file.filename, "content": content})

# ---------------- QUIZ SUBMISSION ---------------- #

@app.route("/submit-quiz", methods=["POST"])
def submit_quiz():
    data = request.get_json()
    score = data.get("score", 0)

    user_progress["quizzes_completed"] += 1
    user_progress["quiz_scores"].append(score)

    # Update average
    user_progress["average_score"] = round(
        sum(user_progress["quiz_scores"]) / len(user_progress["quiz_scores"]), 2
    )

    return jsonify({"message": "Quiz recorded", "progress": user_progress})

# ---------------- PROGRESS API ---------------- #

@app.route("/get-progress")
def get_progress():
    return jsonify(user_progress)

# ---------------- RECOMMENDATIONS API ---------------- #

@app.route("/get-recommendations")
def get_recommendations():
    tips = []
    avg = user_progress["average_score"]

    if avg < 50:
        tips.append("📖 Revise your weak areas daily.")
        tips.append("📝 Take smaller quizzes more often.")
    elif avg < 80:
        tips.append("💡 Focus on practice problems in tricky topics.")
        tips.append("⏱️ Use Pomodoro sessions to stay consistent.")
    else:
        tips.append("🔥 Great job! Start exploring advanced topics.")
        tips.append("✅ Teach others to reinforce your learning.")

    tips.append("📊 You have studied {} documents so far.".format(user_progress["documents_studied"]))

    return jsonify({"recommendations": tips})

# ---------------- MAIN ---------------- #
if __name__ == "__main__":
    app.run(debug=True)
