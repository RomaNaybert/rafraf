from flask import Flask, request, send_file
import os
from shap_e import item_generate

app = Flask(__name__)

@app.route("/", methods=["POST","GET"])
def main():
    try:
        if request.method == 'POST':
            image = request.files['image']
            print(image)
            filename = os.path.join('test', image.filename)
            print(filename)
            image.save(filename)

            obj_filename = item_generate(filename)

            return send_file(obj_filename, as_attachment=True)
        else:
            return {"error":"select you wave file"}
    except Exception as e:
        return {"error":str(e)}

if __name__=="__main__":
    app.run("0.0.0.0", port=8000 ,debug=True)