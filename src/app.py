from distutils.log import error
from flask import Flask, redirect
from flask import render_template,request,redirect
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,LoginManager,login_user,login_required,logout_user,current_user
import datetime
import pandas as pd
from  check import Check

#自動更新するwebdriver
from webdriver_manager.chrome import ChromeDriverManager


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///fitness.db'
app.config['SECRET_KEY']='aiueo'
db=SQLAlchemy(app)

login_manager=LoginManager()
login_manager.init_app(app)

#==============================
#table定義
#==============================
#ユーザー情報
class User(UserMixin,db.Model):
    id=db.Column(db.String(12),primary_key=True)
    pw=db.Column(db.String(12),nullable=False)
    age=db.Column(db.Integer)
    height=db.Column(db.Float)
    weight=db.Column(db.Float)
    bmr=db.Column(db.Float)
    tdee=db.Column(db.Float)
    protein=db.Column(db.Integer)
#摂取タンパク質
class Protein(db.Model):
    id=db.Column(db.String(12),primary_key=True)
    protein=db.Column(db.Integer)
    date=db.Column(db.Date,primary_key=True)
#胸トレーニングボリューム
class TrainingChest(db.Model):
    id=db.Column(db.String(12),primary_key=True)
    date=db.Column(db.Date,primary_key=True)
    chest_press=db.Column(db.Integer)
    fly=db.Column(db.Integer)
    modified_front_raise=db.Column(db.Integer)
    crunch=db.Column(db.Integer)
    twist=db.Column(db.Integer)
#背中トレーニングボリューム   
class TrainingBack(db.Model):
    id=db.Column(db.String(12),primary_key=True)
    date=db.Column(db.Date,primary_key=True)
    lat_pulldown=db.Column(db.Integer)
    seated_row=db.Column(db.Integer)
    dumbbell_curl=db.Column(db.Integer)
    hammer_curl=db.Column(db.Integer)
    twist=db.Column(db.Integer)
#肩トレーニングボリューム   
class TrainingShoulder(db.Model):
    id=db.Column(db.String(12),primary_key=True)
    date=db.Column(db.Date,primary_key=True)
    front_raise=db.Column(db.Integer)
    Shoulder_Press=db.Column(db.Integer)
    Side_Raise=db.Column(db.Integer)
    Rear_Raise=db.Column(db.Integer)
    Upright_Row=db.Column(db.Integer)
#トレーニング重量
class TrainingWeight(db.Model):
    id=db.Column(db.String(12),primary_key=True)
    chest_press=db.Column(db.Integer)
    fly=db.Column(db.Integer)
    modified_front_raise=db.Column(db.Integer)
    crunch=db.Column(db.Integer)
    twist=db.Column(db.Integer)
    lat_pulldown=db.Column(db.Integer)
    seated_row=db.Column(db.Integer)
    dumbbell_curl=db.Column(db.Integer)
    hammer_curl=db.Column(db.Integer)
    twist=db.Column(db.Integer)
    front_raise=db.Column(db.Integer)
    Shoulder_Press=db.Column(db.Integer)
    Side_Raise=db.Column(db.Integer)
    Rear_Raise=db.Column(db.Integer)
    Upright_Row=db.Column(db.Integer)

    
#login_user判断方法
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

#新規登録
@app.route('/',methods=['GET','POST'])
def hello_world():
    if request.method=='GET':
        return render_template('signup.html')
    else:
        #form情報取得
        id=request.form.get('id')
        pw=request.form.get('pw')
        age=request.form.get('age')
        height=request.form.get('height')
        weight=request.form.get('weight')
        active=request.form.get('active')

        msg=Check.check(id=id,pw=pw,age=age,height=height,weight=weight)
        if msg is not None:
            return render_template('signup.html',msg=msg)
        
        #ブラウザ起動
        browser = webdriver.Chrome(ChromeDriverManager().install())

        url='https://keisan.casio.jp/exec/system/1567491116'
        browser.get(url)

        #ブラウザにform情報送信
        b_age=browser.find_element_by_id("var_a")
        b_age.send_keys(age)
        
        b_height=browser.find_element_by_id("var_h")
        b_height.send_keys(height)
        b_weight=browser.find_element_by_id("var_w")
        b_weight.send_keys(weight)
        
        b_active=browser.find_element_by_id("var_lebel")
        b_active=Select(b_active)
        b_active.select_by_value(active)
        #計算ボタンクリック
        btn=browser.find_element_by_id('executebtn')
        btn.click()

        bmr=browser.find_element_by_id('ans0')
        tdee=browser.find_element_by_id('ans1')
        bmr=bmr.text
        tdee=tdee.text
        #DB代入前の型変換
        bmr=bmr.replace(',','') 
        tdee=tdee.replace(',','')
        age=int(age)
        protein=round(int(weight)*2)
        
        #入力データをDBへ
        user=User(id=id,pw=pw,age=age,height=height,weight=weight,bmr=bmr,tdee=tdee,protein=protein)

        db.session.add(user)
        db.session.commit()
        db.session.close()
        return redirect('/login')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    if request.method=='POST':
        id=request.form.get('id')
        pw=request.form.get('pw')

        user_id=User.query.filter_by(id=id).first()
        user_id_pw=User.query.filter_by(id=id,pw=pw).first()
        error_msg_id='ID is not found'
        error_msg_pw='PW is not found'
        if (user_id is not None ) and  (user_id_pw is None):
            return render_template('login.html',error_msg_pw=error_msg_pw)
        elif (user_id is None) and (user_id_pw is None):
            return render_template('login.html',error_msg_id=error_msg_id,error_msg_pw=error_msg_pw)
        else :
            login_user(user_id_pw)
            return redirect('/home')       



@app.route('/home',methods=['GET'])
@login_required
def home():

    today=datetime.date.today()
    user=current_user
    created_check=Protein.query.filter_by(id=current_user.id,date=today).first()
    if created_check is None:
        #今日のcurrent_userのProteinデータがあるか確認し、なければ作成
        today_protein=Protein(id=current_user.id,protein=0,date=today)
        db.session.add(today_protein)
        db.session.commit() 
    #現在loginしているUser情報を渡す
    today_protein=Protein.query.filter_by(id=current_user.id,date=today).first()
    return render_template('home.html',user=user,today_protein=today_protein)

@app.route('/<int:figure>/<string:del_or_add>/cal',methods=['GET'])
@login_required
def delete(figure,del_or_add):
    #今日のデータを取得
    today=datetime.date.today()
    new_protein=Protein.query.filter_by(id=current_user.id,date=today).first()
    #現在の値取得し、delかaddか判定し、計算
    now=new_protein.protein
    if del_or_add=='delete':
        new_protein.protein=now-figure
    elif del_or_add=='add':
        new_protein.protein=now+figure
    #0以下にならない処理
    if new_protein.protein<0:
        new_protein.protein=0

    db.session.commit()
    return redirect('/home')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/kanri')
def test():
    users=User.query.all()
    proteins=Protein.query.all()
    return render_template('kanri.html',users=users,proteins=proteins)


# 実行コマンド
# set FLASK_APP=app.py
# set FLASK_ENV=development
# python -m flask run