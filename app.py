
from read_data import*
from flask import Flask,redirect,url_for,render_template,request
from PIL import Image
import requests
from io import BytesIO
from flask import Flask,redirect,url_for,render_template,request
import base64
import re
app=Flask(__name__)

row=df.shape[0]

@app.route("/")
def pop():
    return render_template('index.html')

def localize_objects_uri(uri):
    """Localize objects in the image on Google Cloud Storage

    Args:
    uri: The path to the file in Google Cloud Storage (gs://...)
    """
    from google.cloud import vision

    client = vision.ImageAnnotatorClient()

    image = vision.Image()
    image.source.image_uri = uri

    objects = client.object_localization(image=image).localized_object_annotations
    obj=[]
    for object_ in objects:
       obj.append(object_.name) 
    return obj
       
def detect_labels(path):
    """Detects labels in the file."""
    from google.cloud import vision
    from google.cloud.vision_v1 import types
    client = vision.ImageAnnotatorClient()

    
    if(path.startswith("https:")==True):
        client = vision.ImageAnnotatorClient()
        image = vision.Image()
        image.source.image_uri = path

        response = client.label_detection(image=image)
        labels = response.label_annotations
        print("Labels:")

        for label in labels:
            print(label.description)
        
    else:
        with open(path, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.label_detection(image=image)

        labels = response.label_annotations
        print("Labels:")
        desc=[]
        for label in labels:
           print(label.description,end=" ")
        return desc
    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )
# obj=localize_objects_uri('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR7J_bn4kLNxhp935XB69TIW8Oo_ghIyNn7ag&s')

@app.route('/display/<string:product>/<path:url>')
def display(product,url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img_str = base64.b64encode(BytesIO(response.content).read()).decode('utf-8')
   
    return render_template('Product_detail.html',product=product,image=img_str)


@app.route("/Error")
def Data_not_found():
    return render_template('Error.html')

@app.route('/submit',methods=["POST","GET"])
def submit():
    if request.method=="POST":
        img_URl=request.form["URL"]
        print(img_URl)
        obj=localize_objects_uri(img_URl)
        # desc=detect_labels(img_URl)
        # print(desc)
        print(obj)
        links=[]
        desc=[]
    for i in range(1,row):
        if df.Product_label[i]==obj[0]:
            product=df.Product_label[i]
            url=(df.Image[i])
            links.append(url)
            desc.append(df.Description[i])
    if not links:
        return redirect(url_for("Data_not_found"))
    
    
    # if links:
    #     for link in links:
    
    # return redirect(url_for('display',product=product,url=links))
    data=[{'link':link,"Description":desc_item} for link,desc_item in zip(links,desc)]
    # parsed_desc = [eval(desc_str) for desc_str in desc]
    return render_template("Product_detail.html",data=data,product=product)
            
@app.route("/search",methods=["POST","GET"])
def Search_By_Name():
    if request.method=="POST":
            name=request.form["Product_Name"]
            links=[]
            desc=[]
            pattern = re.compile(format(re.escape(name)), re.IGNORECASE)
    for i in range(1,row):
        match = re.findall(pattern,df.Product_label[i] )
        if match:
            product=df.Product_label[i]
            url=(df.Image[i])
            links.append(url)
            desc.append(df.Description[i])
    if not links:
        return redirect(url_for("Data_not_found"))
    
    data=[{'link':link,"Description":desc_item} for link,desc_item in zip(links,desc)]
    return render_template("Product_detail.html",data=data,product=product)


            
    
    
if __name__=='__main__':
    app.run(debug=True)