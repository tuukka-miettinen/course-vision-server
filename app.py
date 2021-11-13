from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3

from dotenv import dotenv_values
config = dotenv_values(".env") 

app = Flask(__name__)
CORS(app)

@app.route("/similar", methods = ['GET'])
def get_similar():
    course_id = request.args.get('course_id')
    client = boto3.resource('dynamodb',
        region_name="eu-central-1",
        aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"])
    table = client.Table('course_similarities')
    resp = table.get_item(Key={"course_id": course_id})
    return jsonify(
        isError=False,
        message= "Success",
        statusCode= 200,
        data=resp['Item']), 200

if __name__ == "__main__":
    app.run(debug=True)
    #app.run(host="0.0.0.0", port=80)