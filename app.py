from flask import Flask, render_template, request, redirect, session
from database import Base, engine, SessionLocal
import models
import PyPDF2
import docx
import json
from ai import analyze_resume

app = Flask(__name__)
app.secret_key = "secret916"

Base.metadata.create_all(bind = engine)

# HOME
@app.route("/")
def home() :
   if "user" in session:
      return redirect("/dashboard")
   return redirect("/login")


# SIGNUP
@app.route("/signup", methods = ["GET","POST"] )
def signup():
   db = SessionLocal()
   if request.method == "POST":
      email = request.form.get("email")
      password = request.form.get("password")

      existing_user = db.query(models.User).filter_by(email=email).first()
      if existing_user:
         return "User already exists"

      user = models.User(email=email, password=password)
      db.add(user)
      db.commit()

      return redirect("/login")

   return render_template("/signup.html")

# LOGIN

@app.route("/login", methods = ["GET", "POST"])

def login():
   db = SessionLocal()
   if request.method == "POST":
      email = request.form.get("email")
      password = request.form.get("password")
      user = db.query(models.User).filter_by(email=email, password=password).first()

      if user:
         session["user"] = user.email
         return redirect("/dashboard")
      else:
         return "Invalid credentials"
   return render_template("login.html")
   
# DASHBOARD

@app.route("/dashboard", methods = ["GET", "POST"])
def dashboard():
   if "user" not in session:
      return redirect("/login")

   result = None

   if request.method == "POST":
      user_goal = request.form.get("role")
      resume = request.form.get("resume")

      resume_text = resume
      file = request.files.get("file")

      # File Handling
      if file and file.filename != "":
            if file.filename.endswith(".pdf"):
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""
                    resume_text = text
                except Exception as e:
                    result = {"error": f"PDF error {str(e)}"}
            elif file.filename.endswith(".docx"):
                try:
                    doc = docx.Document(file)
                    text = ""
                    for para in doc.paragraphs:
                        text += para.text + "\n"
                    resume_text = text
                except Exception as e:
                    result = {"error": f"Docx error {str(e)}"}

        # CRUCIAL CHANGE: Only request Gemini if no file parsing error occurred
      if result is None and resume_text and user_goal:
            try:
                ai_response = analyze_resume(resume_text, user_goal)
                result = ai_response
                
                # Safe Database Block (Nest it here so it ONLY logs when AI succeeds!)
                try:
                    db = SessionLocal()
                    user = db.query(models.User).filter_by(email=session["user"]).first()
                    if user:
                        report = models.Report(
                            user_id=user.id,
                            resume_text=resume_text,
                            result=json.dumps(ai_response)
                        )
                        db.add(report)
                        db.commit()
                except Exception as db_err:
                    print(f"Database logging skipped: {str(db_err)}")

            except Exception as ai_err:
                result = {"error": f"AI error: {str(ai_err)}"}

   return render_template("dashboard.html", user=session["user"], result=result)
           
# HISTORY

@app.route("/history")
def history():
   if "user" not in session:
      return redirect("/login")

   db = SessionLocal()
   user = db.query(models.User).filter_by(email=session["user"]).first()

   reports = db.query(models.Report).filter_by(user_id=user.id).all()

   # Convert JSON string to Dict
   parsed_reports = []
   for r in reports:
      try:
         parsed_result = json.loads(r.result)
      except Exception:
         parsed_result = []

      parsed_reports.append({
         "resume": r.resume_text,
         "result": parsed_result
      })
   return render_template("history.html", reports=parsed_reports)

# Logout

@app.route("/logout")
def logout():
   session.pop("user", None)
   return redirect("/login")
       

if __name__ == "__main__" :
   app.run(debug=True)