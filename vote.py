from flask import Flask, jsonify, send_file, request, render_template
import argparse
import threading
import uuid
import json

argParser = argparse.ArgumentParser()
argParser.description = 'For learning use only, DO NOT use it for illegal purposes. -- InJeCTrL'
argParser.add_argument("-i", "--input", help = "Input questions file.", required=True)
argParser.add_argument("-n", "--nvoters", help = "Count of voters.", required=True)
argParser.add_argument("-p", "--port", help = "Port of server.", required=True)
args = argParser.parse_args()

n_Voters = int(args.nvoters)
manual_port = int(args.port)
file_input = args.input

GUIDs = {}
Questions_Scored = []
Questions = []
Total = 0
Full = 0
Topic = ""
n_Voted = 0
n_Abstain = 0
m_vote = threading.Lock()

# Generate and export GUID list
with open("VoteGUID.txt", "w", encoding='utf-8') as f:
    for i in range(n_Voters):
        tg = str(uuid.uuid1())
        GUIDs[tg] = False
        f.write(tg + "\n")

app = Flask(__name__)

@app.route("/api/result", methods = ["GET"])
def getResult():
    return jsonify({"total_score": Total, "full_score": Full, "rest_score": Full - Total,
                    "total_vcount": n_Voters, "voted_vcount": n_Voted, "abstain_vcount": n_Abstain,
                    "topic": Topic, "question_count": len(Questions) ,"data": Questions_Scored})

@app.route("/api/question", methods = ["GET"])
def getQuestionList():
    return jsonify({"topic": Topic, "question_count": len(Questions) ,"data": Questions})

@app.route("/api/vote", methods = ["POST"])
def postVote():
    global Questions_Scored
    global Total
    global Full
    global GUIDs
    global n_Voted
    var_request = {}
    try:
        v_guid = request.values.get("guid")
        v_answers = json.loads(request.values.get("data"))
        if len(v_answers) != len(Questions_Scored):
            return jsonify({"success": 1, "data": "Illegal Vote!"})
        else:
            if not GUIDs.__contains__(v_guid):
                return jsonify({"success": 1, "data": "Illegal GUID!"})
            elif GUIDs[v_guid] == True:
                return jsonify({"success": 1, "data": "No duplicate votes!"})
            for i_question in range(len(Questions_Scored)):
                if int(v_answers[i_question]) in list(range(len(Questions_Scored[i_question]["Answers"]))):
                    var_request[i_question] = int(v_answers[i_question])
                else:
                    return jsonify({"success": 1, "data": "Illegal Vote!"})
    except:
        return jsonify({"success": 1, "data": "Illegal Vote!"})
    with m_vote:
        for index, question in enumerate(Questions_Scored):
            Full += Questions_Scored[index]["Full"]
            Total += Questions_Scored[index]["Answers"][var_request[index]]["Score"]
            Questions_Scored[index]["Answers"][var_request[index]]["Count"] += 1
        GUIDs[v_guid] = True
        n_Voted += 1
        return jsonify({"success":0, "data":"Vote successfully!"})

@app.route("/api/abstain", methods = ["POST"])
def postAbstain():
    global GUIDs
    global n_Abstain
    try:
        v_guid = request.values.get("guid")
        if not GUIDs.__contains__(v_guid):
            return jsonify({"success": 1, "data": "Illegal GUID!"})
        elif GUIDs[v_guid] == True:
            return jsonify({"success": 1, "data": "No duplicate votes!"})
    except:
        return jsonify({"success": 1, "data": "Illegal Vote!"})
    with m_vote:
        GUIDs[v_guid] = True
        n_Abstain += 1
        return jsonify({"success":0, "data":"Abstained successfully!"})

@app.route("/", methods = ["GET"])
@app.route("/vote.html", methods = ["GET"])
def index():
    v_guid = request.args.get("guid")
    with m_vote:
        if GUIDs.__contains__(v_guid) and GUIDs[v_guid] == False:
            return render_template("./vote.html", GUID = v_guid)
        else:
            return send_file("./index.html")

def inputParser(path):
    global Questions
    global Questions_Scored
    global Topic
    with open(path, "r") as f:
        content = f.read()
        data_parsed = json.loads(content)
        Topic = data_parsed["Topic"]
        Questions = data_parsed["Questions"].copy()
        Questions_Scored = Questions.copy()
        for question in Questions_Scored:
            question["Full"] = 0
            for answer in question["Answers"]:
                answer["Count"] = 0
                question["Full"] = max(question["Full"], answer["Score"])

inputParser(file_input)
app.run(host='0.0.0.0', port=manual_port)
