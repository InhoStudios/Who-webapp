from flask import Flask, render_template


app = Flask(__name__)

@app.route("/")
def home():
    username = "inho"
    return render_template("index.html", username=username)

if __name__ == "__main__":
    app.run(port=3000, debug=True)