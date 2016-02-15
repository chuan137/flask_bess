from flask import Flask
from modules.sites.bess.app import bess

app = Flask(__name__)

@app.route("/")
def index():
    return "try: /bess"

app.register_blueprint(bess)

if __name__ == "__main__":
    app.run(debug=False)
