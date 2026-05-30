##jinga templete engine
'''
{%......%} for statement(condition, for loop)
{{   }} expression to print output
{#......#}  THIS IS FOR COMMENT
'''

from flask import Flask,url_for,redirect,render_template,request
app=Flask(__name__)

@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/passed/<int:score>')
def passed(score):
    if score>=50:
        res="PASS"
    else:
        res="FAIL"
    exp={"score":score,"result":res}
    return render_template('result_01.html',result=exp)

@app.route('/submit',methods=['POST','GET'])
def submit():
    total_score=0
    if request.method=='POST':
        science=float(request.form['science'])
        maths=float(request.form['maths'])
        c=float(request.form['c'])
        data_science=float(request.form['data_science'])
        total_score=(maths+science+data_science+c)/4

        return redirect(url_for('passed',score=total_score))
        


if __name__=='__main__':
    app.run(debug=True)