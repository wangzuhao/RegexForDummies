# This module run test cases and generate feedbacks for a session

import re
import json
import signal
import io
from collections import OrderedDict

def run_test_case_session(solution):
    """
    run test cases here
    :param solution: user submit solution
    :return: a tuple of (result, is_solved)
    """
    resultList = []
    solved = True
    
    # Answer
    # answer_q1 = r"EditPad (Lite|Pro)"
    # answer_q2_search = r"\b(\w+)\s+\1\b"
    # answer_q2_replace = r"\1"
    
    lines = solution.split("\n")
    
    '''
    solved = False
    resultList = [{
        'case_objective': solution.replace("\n", " @n "),
        'expected': str(lines),
        'received': "No Answer Received for Question 1 and 2",
        'correct': False
    }]
    return resultList, solved
    '''
    answer_q1 = ""
    answer_q2_search = ""
    answer_q2_replace = ""
    
    if len(lines) >= 2:
        answer_q1 = lines[1].strip()
    if len(lines) < 2 or answer_q1 == "":
        solved = False
        resultList = [{
            'case_objective': "No Answer Received for Question 1",
            'expected': "No Answer Received for Question 1",
            'received': "No Answer Received for Question 1",
            'correct': False
        }]
        return resultList, solved
        
    if len(lines) >= 4:
        answer_q2_search = lines[3].strip()
    if len(lines) < 4 or answer_q2_search == "":
        solved = False
        resultList = [{
            'case_objective': "No Answer Received for Question 2",
            'expected': "No Answer Received for Question 2",
            'received': "No Answer Received for Question 2",
            'correct': False
        }]
        return resultList, solved
        
    if len(lines) >= 6:
        answer_q2_replace = lines[5].strip()
    if len(lines) < 6 or answer_q2_replace == "":
        solved = False
        resultList = [{
            'case_objective': "No Answer Received for Question 2 - String for Replacement",
            'expected': "No Answer Received for Question 2 - String for Replacement",
            'received': "No Answer Received for Question 2 - String for Replacement",
            'correct': False
        }]
        return resultList, solved
    
    def check_q1(test_case, expected):
        correct = True
        answer = ""
        try:
            answer = re.sub(answer_q1, r'\1 version', test_case)
        except:
            answer = "None"
        
        if answer == expected:
            correct = True
        else:
            correct = False
        
        resultDict = {
            'case_objective': "Question 1 Test Case: " + test_case,
            'expected': expected,
            'received': answer,
            'correct': correct
        }
        return resultDict
    
    def check_q2(test_case, expected):
        correct = True
        answer = ""
        try:
            answer = re.sub(answer_q2_search, answer_q2_replace, test_case)
        except:
            answer = "None"
        
        if answer == expected:
            correct = True
        else:
            correct = False
        
        resultDict = {
            'case_objective': "Question 2 Test Case: " + test_case,
            'expected': expected,
            'received': answer,
            'correct': correct
        }
        return resultDict
    
    resultDict_q1_1 = check_q1('EditPad Lite', "Lite version")
    resultList.append(resultDict_q1_1)
    if resultDict_q1_1['correct'] == False:
        solved = False
    resultDict_q1_2 = check_q1('Not Replace Lite', "Not Replace Lite")
    resultList.append(resultDict_q1_2)
    if resultDict_q1_2['correct'] == False:
        solved = False
    resultDict_q1_3 = check_q1('EditPad Pro', "Pro version")
    resultList.append(resultDict_q1_3)
    if resultDict_q1_3['correct'] == False:
        solved = False
    resultDict_q1_4 = check_q1('Not Replace Pro', "Not Replace Pro")
    resultList.append(resultDict_q1_4)
    if resultDict_q1_4['correct'] == False:
        solved = False
    
    resultDict_q2_1 = check_q2('This is a a test', "This is a test")
    resultList.append(resultDict_q2_1)
    if resultDict_q2_1['correct'] == False:
        solved = False
    resultDict_q2_2 = check_q2('This is a test', "This is a test")
    resultList.append(resultDict_q2_2)
    if resultDict_q2_2['correct'] == False:
        solved = False

    return resultList, solved



def generate_feedback(solution):
    """
    take in user submit solution and run test cases to generate feedback
    :param solution: user submit solution
    :return: a dict of feedback
    """
    output = io.StringIO()

    timeout = False

    # handler function that tell the signal module to execute
    # our own function when SIGALRM signal received.
    def timeout_handler(num, stack):
        print("Received SIGALRM")
        raise Exception("processTooLong")

    # register this with the SIGALRM signal
    signal.signal(signal.SIGALRM, timeout_handler)

    # signal.alarm(10) tells the OS to send a SIGALRM after 10 seconds from this point onwards.
    signal.alarm(10)

    # After setting the alarm clock we invoke the long running function.
    try:
        result, solved = run_test_case_session(solution)
        printed = output.getvalue()
        responseDict = {"solved": solved, "results": result, "printed": printed}
    except Exception as ex:
        if "processTooLong" in ex:
            timeout = True
            print("processTooLong triggered")
    # set the alarm to 0 seconds after all is done
    finally:
        signal.alarm(0)

    jsonResponseData = responseDict

    textResults = tableContents = ""
    overallResults = """<span class="md-subheading">All tests passed: {0}</span><br/>""".format(
        str(jsonResponseData.get("solved")))
    resultContent = jsonResponseData.get('results')

    if resultContent:
        for i in range(len(resultContent)):
            expectedText = resultContent[i]["expected"]
            receivedText = resultContent[i]["received"]
            correct = resultContent[i]["correct"]
            objective = resultContent[i]["case_objective"]
            if correct:
                textResults = textResults + "\nHurray! You have passed this test case {}.\n".format(expectedText)
                textBackgroundColor = "#b2d8b2"
            else:
                if expectedText == 'skip':
                    textResults = textResults + "\nYou should skip this case: {}".format(expectedText)
                textResults = textResults + "\nThe test case eludes your code so far but try again! You should match {} but received {}.\n".format(
                    expectedText, receivedText)
                textBackgroundColor = "#ff9999"
            tableContents = tableContents + """
                    <tr bgcolor={4}>
                        <td>{0}</td>
                        <td>{1}</td>
                        <td>{2}</td>
                        <td>{3}</td>
                    </tr>
                    """.format(objective, expectedText, receivedText, str(correct), textBackgroundColor)
    solvedStatusText = str(jsonResponseData.get("solved")) or "error"
    textResults = """All tests passed: {0}\n""".format(solvedStatusText) + textResults
    if not resultContent:
        textResults = "Your test is passing but something is incorrect..."

    if timeout or jsonResponseData.get("errors"):
        textResults = "An error - probably related to code syntax - has occured. Do look through the JSON results to understand the cause."
        tableContents = """
                    <tr>
                        <td></td>
                        <td></td>
                        <td>error</td>
                        <td></td>
                    </tr>
                    """
    htmlResults = """
                <html>
                    <head>
                        <meta charset="utf-8">
                        <meta content="width=device-width,initial-scale=1,minimal-ui" name="viewport">
                    </head>
                    <body>
                        <div>
                            {0}
                            <span class="md-subheading tableTitle">Tests</span>
                            <table>
                                 <thead>
                                    <tr>
                                        <th>Objective</th>
                                        <th>Case</th>
                                        <th>Received</th>
                                        <th>Correct</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {1}
                                </tbody>
                            </table>
                        </div>
                    </body>
                    <style>
                    br {{
                        display:block;
                        content:"";
                        margin:1rem
                    }}
                    table{{
                        text-align:center
                    }}
                    .tableTitle{{
                        text-decoration:underline
                    }}
                    </style>
                </html>
                """.format(overallResults, tableContents)
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps({
            "isComplete": jsonResponseData.get("solved"),
            "jsonFeedback": jsonResponseData,
            "htmlFeedback": htmlResults,
            "textFeedback": textResults
        })
    }


def main():
    print(generate_feedback_session_1('y{2,4}[es]{1,5}'))


if __name__ == '__main__':
    main()
