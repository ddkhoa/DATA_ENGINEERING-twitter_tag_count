from flask import Flask, jsonify, request
from flask import render_template
import ast

app = Flask(__name__)
labels = []
values = []


@app.route("/")
def get_chart_page():

    # render the chart page with current data
    global labels, values

    return render_template('chart.html', values=values, labels=labels)


@app.route("/refreshData")
def refresh_graph_data():

    # return the current data to client
    global labels, values
    print("labels now: " + str(labels))
    print("data now: " + str(values))

    return jsonify(sLabels=labels, sData=values)


@app.route("/updateData", methods=["POST"])
def update_data():

    # update the in memory data (labels & values)
    global labels, values

    # verify the input
    if not request.form or "data" not in request.form:
        return "error", 400

    # input ok, update data
    labels = ast.literal_eval(request.form["label"])
    values = ast.literal_eval(request.form["data"])

    print("labels received: " + str(labels))
    print("data received: " + str(values))

    return "success", 201


if __name__ == "__main__":
    app.run(host="localhost", port=5001)
