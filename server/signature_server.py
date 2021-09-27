import time

from flask import Flask, Response,request

import multiprocessing
import threading
from flask import Flask
import signature_capture
app = Flask(__name__)


def sig_worker(data,res):

    sm = signature_capture.Signature_Manager()
    pdfb = sm.sign_pdf(data)
    res.append(pdfb)

@app.route("/")
def hello():


    manager = multiprocessing.Manager()
    result = manager.list()

    p1=multiprocessing.Process(target=sig_worker,args=(request.data,result))
    p1.start()
    p1.join()

    # app.run(ssl_context='adhoc')
    data='error'
    if result:
        data=result[0]


    return Response(data, mimetype='application/pdf')




if __name__ == "__main__":
    multiprocessing.freeze_support()


    # t1=threading.Thread(target=sgsg,args=())

    # app.run(ssl_context='adhoc')
    app.run(host='127.0.0.1',port=1327,threaded=True)
    # main()
