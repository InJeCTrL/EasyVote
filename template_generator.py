import json

Questions = []
Topic = ""

i_Q = 0
Topic = input("Input Topic of the Vote:")
while True:
    tQuestion = input("Input Question(string):")
    if not tQuestion:
        break
    Questions.append({"Question": tQuestion, "Answers": []})
    while True:
        tAnswer = input("Input Answer(string):")
        if not tAnswer:
            break
        tScore = float(input("Input Score of this Answer(digit):"))
        tScore = int(tScore) if tScore == int(tScore) else tScore
        Questions[i_Q]["Answers"].append({"Answer": tAnswer, "Score": tScore})
    i_Q += 1

with open("template.txt", "w", encoding='utf-8') as f:
    f.write(json.dumps({"Topic": Topic, "Questions": Questions}))
