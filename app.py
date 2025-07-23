from flask import Flask, render_template
from ai_routes import ai_routes

app = Flask(__name__)
app.register_blueprint(ai_routes)

@app.route("/")
def index():
    return render_template("index.html", project_name="BizBot")

if __name__ == "__main__":
    app.run(debug=True)