from flask import Flask, request, Response
from pymysql import cursors
import json

def javaHashMapStrToJson(data):
    data = data.replace(',', '}, {')
    data = data.replace('=',',')
    data = data.replace("'",'"')
    data = '['+data+']'
    data = eval(data)
    data = sorted(data,key = lambda i:i['id'])
    return data

def mod(n):
    if n < 0:
        return -n
    return n

def answers(connection):
    with connection.cursor() as cursor:
        fbid = request.form.get("firebase_id")
        cursor.execute("SELECT firebase_id FROM profile WHERE firebase_id = '{}'".format(fbid))
        if cursor.rowcount == 0:
            return Response(json.dumps({"status": "failure", "Reason":"Firebase ID doesnot exist", "status_code": "200"}), mimetype="application/json", status=200)
        data = request.form.get("answers")
        try:
            data = javaHashMapStrToJson(data)
        except:
            return Response(json.dumps({"status":"failure", "Reason":"Cant parse answers", "status_code":"200"}),mimetype="application/json",status = 200)
        score = 0
        id = 0
        query = "select * from quiz where id = ".format(data[id]["id"])
        for i in range(len(data)):
            query += " {} or id = ".format(data[id]["id"])
            id+=1
        id = 0
        query = query[:-9]
        cursor.execute(query)
        if cursor.rowcount==0:
            return Response(json.dumps({"status": "failure", "status_code": "200"}), mimetype="application/json", status=200)
        ans = cursor.fetchall()
        for i in range(len(data)):
            qid = ans[id]["id"]
            if(int(ans[id]["ans"])==int(data[id]["ans"])):
                score+=1
            id+=1
        cursor.execute("SELECT quiz_rating FROM profile WHERE firebase_id = '{}'".format(fbid))
        rating = cursor.fetchone()
        rating = rating["quiz_rating"]
        newRating = rating+score
        cursor.execute("UPDATE profile SET quiz_rating = '{}', points = points + {} WHERE firebase_id = '{}'".format(newRating,score,fbid))
        # connection.commit()
    return Response(json.dumps({"status": "success", "status_code": "200", "score": score}),mimetype = "application/json",status = 200)
