from flask import Flask
app=Flask(__name__)
#wsgi application
@app.route('/')    #decorator here URL is given
def welcome():
    return "welcome to my page and goood morning !!"

@app.route('/members')    #decorator here URL is given
def members():
    return " goood morning !!"

@app.route('/name')    #decorator here URL is given
def name():
    return "my nmae is suresh."


if __name__=='__main__':
    app.run(debug=True)