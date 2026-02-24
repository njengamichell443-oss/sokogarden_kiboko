from flask import *
import pymysql
import pymysql.cursors
from flask_cors import CORS
import os
#Flask application
app=Flask(__name__)  
CORS(app) #allows requests from external origins
#configure our upload folder
app.config['UPLOAD_FOLDER']='static/images'
#App route
@app.route('/api/signup',methods =['POST'])
def signup():
    #Extract values posted in the request and store them in variables
    username= request.form['username']
    email=request.form['email']
    password= request.form['password']
    phone=request.form['phone']
    #connect to our database
    connection = pymysql.connect(host='localhost',user='root',password='',database='dailyyoghurt_kiboko')
       #initialize the connection
    cursor = connection.cursor()
    #do the sql query to insert the data of the four columns
    sql= 'insert into users(username,email,password,phone) values(%s,%s,%s,%s)'
    # create data to replace the placeholders
    data = (username,email,password,phone)
    #execute the sql and data together using our cursor
    cursor.execute(sql,data)
    #we need to commit/savechanges
    connection.commit()
    return jsonify({'success':'Thankyou for joining'})
#Signinroute
@app.route('/api/signin',methods =['POST'])
def signin():
    username= request.form['username']
    password= request.form['password']
    #Connect to our database
    connection = pymysql.connect(host='localhost',user='root',password='',database='dailyyoghurt_kiboko')
    #initiatize the connection
    cursor=connection.cursor(pymysql.cursors.DictCursor)
    #do the sql query to insert the data of the two columns
    sql='select*from users where username = %s and password = %s'
    #create data to replace the place holders
    data=(username,password)
    #execute thedatabase and python togther
    cursor.execute (sql,data)
    #count
    count=cursor.rowcount
    if count==0:
        return jsonify({'message':'Login failed'})
    else:
        user=cursor.fetchone()
        #remove the password key
        user.pop('password',None)
        return jsonify({'message':'Login successful','user':user})
#Add products
@app.route('/api/add_product',methods=['POST'])
def add_product():
    product_name=request.form['product_name']
    product_description=request.form['product_description']
    product_cost=request.form['product_cost']
    #extract image data
    product_photo=request.files['product_photo']
    #Get the image file name
    filename=product_photo.filename
    #specify where the image will be saved
    photo_path=os.path.join(app.config['UPLOAD_FOLDER'],filename)
    #save the above path
    product_photo.save(photo_path)
    #connection to our data base
    connection=pymysql.connect(host='localhost',user='root',password='',database='dailyyoghurt_kiboko')
    #initialize the conection
    cursor=connection.cursor()
    #do an sql query to insert data into the database
    sql='insert into product_details(product_name,product_description,product_cost,product_photo) values(%s,%s,%s,%s)'
    #create data to replace the placeholders
    data=(product_name,product_description,product_cost,filename)
    #execute our python together with our database 
    cursor.execute(sql,data)
    #save changes
    connection.commit()
    return jsonify({'success':'Product successfuly added'})
#get products
@app.route('/api/get_product_details')
def getproducts():
    #connection to our database
    connection=pymysql.connect(host='localhost',user='root',password='',database='dailyyoghurt_kiboko')
    #creating a cursor object
    cursor=connection.cursor(pymysql.cursors.DictCursor)
    #sql query
    sql='select* from product_details'
    #execute the sql 
    cursor.execute(sql)
    #get products in form of a dictionary
    product_details=cursor.fetchall()
    #return products
    return jsonify(product_details)
#mpesa payments
# Mpesa Payment Route 
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
         if request.method == 'POST':
            # Extract POST Values sent
            amount = request.form['amount']
            phone = request.form['phone']

            # Provide consumer_key and consumer_secret provided by safaricom
            consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
            consumer_secret = "amFbAoUByPV2rM5A"

           # Authenticate Yourself using above credentials to Safaricom Services, and Bearer Token this is used by safaricom for security identification purposes - Your are given Access
            api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
            # Provide your consumer_key and consumer_secret 
            response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
            # Get response as Dictionary
            data = response.json()
            # Retrieve the Provide Token
            # Token allows you to proceed with the transaction                                                                              
            access_token = "Bearer" + ' ' + data['access_token']

            #  GETTING THE PASSWORD
            timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')  # Current Time
            passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  # Passkey(Safaricom Provided)
            business_short_code = "174379"  # Test Paybile (Safaricom Provided)
            # Combine above 3 Strings to get data variable
            data = business_short_code + passkey + timestamp
            # Encode to Base64
            encoded = base64.b64encode(data.encode())
            password = encoded.decode()

            # BODY OR PAYLOAD
            payload = {
                "BusinessShortCode": "174379",
                "Password":password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": "1",  # use 1 when testing
                "PartyA": phone,  # change to your number
                "PartyB": "174379",
                "PhoneNumber": phone,
                "CallBackURL": "https://coding.co.ke/api/confirm.php",
                "AccountReference": "SokoGarden Online",
                "TransactionDesc": "Payments for Products"
            }

            # POPULAING THE HTTP HEADER, PROVIDE THE TOKEN ISSUED EARLIER
            headers = {
                "Authorization": access_token,
                "Content-Type": "application/json"
            }

            # Specify STK Push  Trigger URL
            url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  
            # Create a POST Request to above url, providing headers, payload 
            # Below triggers an STK Push to the phone number indicated in the payload and the amount.
            response = requests.post(url, json=payload, headers=headers)
            print(response.text) # 
            # Give a Response
            return jsonify({"message": "An MPESA Prompt has been sent to Your Phone, Please Check & Complete Payment"})

#makes sure that the file runs when executed directly
if __name__=='__main__':
    app.run(debug=True)