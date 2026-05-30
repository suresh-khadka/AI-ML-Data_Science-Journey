from flask import Flask,url_for,redirect
app=Flask(__name__)

@app.route('/')
def welcome():
    return 'welcome to my course '

@app.route('/passed/<int:score>')
def passed(score):
    return f'you are pass and the score is {score}'

@app.route('/failed/<int:score>')
def failed(score):
    return f'you are fail and the score is {score}'

#result chaker
@app.route('/result/<int:marks>')
def result(marks):
    if marks<40:
        result='failed'
    else:
        result="passed"

    return redirect(url_for(result,score=marks))
    

if __name__=='__main__':
    app.run(debug=True)