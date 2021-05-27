import time
from flask import Flask
from flask import jsonify
from flask import request
from transformers.pipelines import pipeline
from db import create_tables
from db import get_db

global modelList
modelList = [
    {
        'name': "distilled-bert",
        'tokenizer': "distilbert-base-uncased-distilled-squad",
        'model': "distilbert-base-uncased-distilled-squad"
    }
]

# Create my flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


# Define a handler for the / path, which
# returns "Hello World"
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


# Define a handler for the /answer path, which
# processes a JSON payload with a question and
# context and returns an answer using a Hugging
# Face model.
@app.route("/answer", methods=['POST'])
def answer():
    # Get the request body data
    data = request.json

    # Import model
    hg_comp = pipeline('question-answering', model=modelList[0]['model'],
                       tokenizer=modelList[0]['tokenizer'])

    # Answer the answer
    answer = hg_comp({'question': data['question'], 'context': data['context']})['answer']

    # Create the response body.
    out = {
        "question": data['question'],
        "context": data['context'],
        "answer": answer
    }

    return jsonify(out)





def insert_db(timestamp, model, answer,question,context):
    db = get_db()
    cursor = db.cursor()
    statement = "INSERT INTO prodscale(timestamp, model, answer,question,context) VALUES (?, ?, ?, ?, ?)"
    cursor.execute(statement, [timestamp, model, answer,question,context])
    db.commit()



@app.route("/answers", methods=['POST','GET'])
def answers():
    if request.method == 'POST':
        # Get the request body data
        model = request.args.get('model')
        data = request.json

        if (model == None):
            model = default_model['name']
            hg_comp = pipeline('question-answering', model=default_model['model'],
                               tokenizer=default_model['tokenizer'])
            # Answer the answer
            answer = hg_comp({'question': data['question'], 'context': data['context']})['answer']

            timestamp = int(time.time())

            # Create the response body.
            out = {
                "timestamp": timestamp,
                "model": model,
                "answer": answer,
                "question": data['question'],
                "context": data['context']

            }

            insert_db(timestamp,model,answer,data['question'],data['context'])

            return jsonify(out)

        else:
            model_name = ""
            tokenizer = ""

            for i in range(len(modelList)):
                if modelList[i]['name'] == model:
                    model_name = modelList[i]['model']
                    tokenizer = modelList[i]['tokenizer']
                    break

            hg_comp = pipeline('question-answering', model=model_name,
                               tokenizer=tokenizer)
            # Answer the answer
            answer = hg_comp({'question': data['question'], 'context': data['context']})['answer']

            timestamp = int(time.time())

            # Create the response body.
            out = {
                "timestamp": timestamp,
                "model": model,
                "answer": answer,
                "question": data['question'],
                "context": data['context']

            }

            insert_db(timestamp, model, answer, data['question'], data['context'])

            return jsonify(out)
    else:

        model = request.args.get('model')
        start = request.args.get('start')
        end = request.args.get('end')

        if (model == None):
            query = "SELECT timestamp, model, answer, question,context FROM prodscale WHERE timestamp BETWEEN ? AND ?"
            #query = "SELECT timestamp, model, answer, question,context FROM prodscale"
            db = get_db()
            cursor = db.cursor()
            cursor.execute(query,[start,end])
            result = cursor.fetchall()
            return jsonify(result)
        else:
            query = "SELECT timestamp, model, answer, question,context FROM prodscale WHERE timestamp BETWEEN ? AND ? AND model=?"
            db = get_db()
            cursor = db.cursor()
            cursor.execute(query,[start,end,model])
            result = cursor.fetchall()
            return jsonify(result)



@app.route("/model", methods=['GET','PUT','DELETE'])
def getModels(modelList=modelList):
    if request.method == 'PUT':
        data = request.json
        modelList.append({
            'name': data['name'],
            'tokenizer': data['tokenizer'],
            'model': data['model']
        })
        seen = set()
        new_l = []
        for d in modelList:
            t = tuple(d.items())
            if t not in seen:
                seen.add(t)
                new_l.append(d)

        modelList = new_l
        return jsonify(modelList)

    elif request.method == 'DELETE':
        model = request.args.get('model')
        for i in range(len(modelList)):
            if modelList[i]['name'] == model:
                del modelList[i]
                break
        return jsonify(modelList)

    else:
        return jsonify(modelList)


# Run if running "python answer.py"
if __name__ == '__main__':
    # Run our Flask app and start listening for requests!
    create_tables()
    default_model = modelList[0]

    app.run(host='0.0.0.0', port=8000, threaded=True)
