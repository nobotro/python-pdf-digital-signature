import requests
import datetime
import time
resp=None
d=open('sample.pdf','rb')
data=d.read()
d.close()
print('send pdf to signature server')

try:
    resp=requests.get('http://127.0.0.1:1327',data=data).content
except:
    pass


if resp:

    f=open('result_'+str(datetime.datetime.now().strftime("%m_%d_%Y %H_%M_%S"))+'.pdf','wb')
    f.write(resp)
    f.close()
    print('saving signed pdf')
else:
    print ('error ')


time.sleep(5)
