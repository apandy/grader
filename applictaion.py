from flask import Flask, request, session
from flask_restful import Resource, Api, reqparse
from sqlalchemy import create_engine
from json import dumps
from flask_jsonpify import jsonify
from flask import render_template
import time
import uuid
import sys
import os

app = Flask(__name__)

@app.route('/')
def main_screen():
    return render_template('index.html')

submissions = []
app.secret_key = 'any random string'

parser = reqparse.RequestParser()
parser.add_argument('source_code')

api = Api(app)

class Submissions(Resource):
    def __init__(self):
        self.test_cases = [
            {
                "description": "Negative Test",
                "test_array": [1,2,3],
                "expected_result" : False
            },
            {
                "description": "Positive Test (Even Cardinality)",
                "test_array": [1,2,3,3],
                "expected_result" : True
            },
            {
                "description": "Positive Test (Odd Cardinality)",
                "test_array": [1,1,4,1,1],
                "expected_result" : True
            },
            {
                "description": "Lower Boundary Test",
                "test_array": [2,0,0,0],
                "expected_result" : True
            },
            {
                "description": "Upper Boundary Test",
                "test_array": [0,0,0,2],
                "expected_result" : True
            }
            
        ]
    def post(self):
        if 'uuid' not in session:
            session['uuid'] = uuid.uuid4()

        test_case_results = []
        
        args = parser.parse_args()
        new_sub = {'source_code':args['source_code'], 'timestamp':time.time(), 'session_id': session['uuid']}
        module_name = "userCode"+str(int(new_sub['timestamp'])) 
        file = open(module_name+".py","w") 
        #file = open("usercode.py","w")
        file.write(new_sub['source_code']) 
        file.close()
        #module_name = "usercode"
        success = False
        try:
        
            __import__(module_name)
            mymodule = sys.modules[module_name]
            
            for test_case in self.test_cases:
                received_output = mymodule.balancedSums(test_case["test_array"])
                test_case_results.append({
                    "descirption" : test_case["description"],
                    "received_output" : received_output,
                    "passed": received_output == test_case["expected_result"] })
           
            
            if (all(item["passed"] for item in test_case_results )):
                resultText= "All test cases passed. Nice work!"
                success = True
            elif (all([item["received_output"] == True for item in test_case_results])):
                resultText=  "All test outputs were True. Plaese rewiew the places where you set return value"
            elif (all(item["received_output"] == False for item in test_case_results )):
                resultText="All test outputs were False. Plaese rewiew the places where you set return value"
            elif (test_case_results[0]["passed"] and test_case_results[1]["passed"] and test_case_results[2]["passed"]
                     and ( not test_case_results[3]["passed"] or not test_case_results[4]["passed"])):
                resultText = "Please remember, that the sum of all elements to the left is zero if the selected element is the first one, and vice versa."
            else:
                resultText = "Please review your code."
        except:
            resultText = "Code execution failed. Please review your code."

        
        if os.path.exists(module_name+".py"):
            os.remove(module_name+".py") 
        
        result = {"text_message":   resultText, "test_case_results" : test_case_results, "success": success}
        
        new_sub['result'] = result
        submissions.append(new_sub)
        return jsonify(result)
    def get(self):
        return jsonify(submissions)

api.add_resource(Submissions, '/submissions') 

if __name__ == '__main__':
     app.run(port='5002')
