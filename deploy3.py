from flask import Flask,request,jsonify
import os
from sklearn.externals import joblib
from PIL import Image
import pickle
import string
import base64
import json
import requests
import base64
import json

from io import BytesIO

app = Flask(__name__)
@app.route("/hello",methods=['POST'])

def hello():
		    # load the model
		print("Loading model")
		content=request.get_json()
		im=Image.open(BytesIO(base64.b64decode(content["image"])))
		im.save("image.jpg")
		IMAGE_PATH = './image.jpg'
		SECRET_KEY = 'sk_f6ac2b4be10b0ccedbe6ed61'

		with open(IMAGE_PATH, 'rb') as image_file:
			img_base64 = base64.b64encode(image_file.read())

    
		url = 'https://api.openalpr.com/v2/recognize_bytes?recognize_vehicle=1&country=in&secret_key=%s' % (SECRET_KEY)
		r = requests.post(url, data = img_base64)

		res=json.dumps(r.json(), indent=2)
		print(res)
		my_dict=json.loads(res)
		res2=my_dict["results"]
		#print(res2)
		for res3 in res2[:1]:
			res4=res3['plate']

		print(res4)

		return res4	
		 


if __name__ == '__main__':
    app.run(host='0.0.0.0')