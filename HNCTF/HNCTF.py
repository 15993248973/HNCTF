#encoding: utf-8

from flask import Flask, render_template, request, redirect, url_for, session, g, flash
from exts import db
import config
import os
from models import Teacher, Team
from datetime import timedelta


app = Flask(__name__)
app.config.from_object(config)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
db.init_app(app)



@app.route('/')
def Index():
    return render_template('Index.html')

@app.route('/Base/')
def Base():
    return render_template('Base.html')

@app.route('/MyPage/')
def MyPage():
    if g.teacher_id:
        return render_template('MyPage.html')
    else:
        return redirect(url_for('Login'))


@app.route('/MyTeam/')
def MyTeam():
    if g.teacher_id:
        result = g.teacher.teams
        return render_template('MyTeam.html', result=result)
    else:
        return redirect(url_for('Login'))


@app.route('/ModifyTeam/', methods=['GET', 'POST'])
def ModifyTeam():
    if g.teacher_id:
        if request.method == 'GET':
            return render_template('ModifyTeam.html')
        else:
            school = request.form.get('school')
            teamname = request.form.get('teamname')
            teacher = request.form.get('teacher')
            teacherphone = request.form.get('teacherphone')
            member1 = request.form.get('member1')
            member1phone = request.form.get('member1phone')
            member2 = request.form.get('member2')
            member2phone = request.form.get('member2phone')
            member3 = request.form.get('member3')
            member3phone = request.form.get('member3phone')

            teamnameGet = request.args.get("teamname")
            team = Team.query.filter(Team.teamname == teamnameGet).first()
            team.school = school
            team.teamname = teamname
            team.teacher = teacher
            team.teacherphone = teacherphone
            team.member1 = member1
            team.member1phone = member1phone
            team.member2 = member2
            team.member2phone = member2phone
            team.member3 = member3
            team.member3phone = member3phone
            db.session.commit()
            return '修改成功'
    else:
        return redirect(url_for('Login'))




@app.route('/Login/', methods=['GET', 'POST'])
def Login():
    if request.method == 'GET':
        return render_template('Login.html')
    else:
        teacherphone = request.form.get('teacherphone')
        password = request.form.get('password')
        #判断，把手机号跟密码拿去数据库表中进行对比
        teacher = Teacher.query.filter(Teacher.teacherphone == teacherphone).first()
        #当前用户输入正确，设置cookie给用户，当登陆成功后把用户相关信息保存在cookie里面，
        # 这样他访问该网页其他东西就不用再次验证信息
        if teacher and teacher.check_password(password):
            session['teacher_id'] = teacher.id
            # 如果想在31天内都不需要登陆
            session.permanent = True

            return redirect(url_for('Index'))
        else:
            flash(u'账号或密码输入错误，请确认后重新输入！')
            return redirect(url_for('Login'))




@app.route('/Register/', methods=['GET', 'POST'])
def Regist():
    if request.method == 'GET':
        return render_template('Register.html')
    else:
        school = request.form.get('school')
        teachername = request.form.get('teachername')
        teacherphone = request.form.get('teacherphone')
        password = request.form.get('password')
        repassword = request.form.get('repassword')

        #号码验证，注册过得不能再次注册
        teacher = Teacher.query.filter(Teacher.teacherphone == teacherphone).first()
        if teacher:
            return '该s手机号已被注册!'
        else:
            # password1要跟password2相等才行
            if password != repassword:
                flash('两次输入的密码不相同，请重新输入！')
                return redirect(url_for('Regist'))
            else:
                teacher = Teacher(school=school, teachername=teachername, teacherphone=teacherphone, password=password)
                #数据添加到数据库中
                db.session.add(teacher)
                db.session.commit()

                #注册完成 就跳转到登陆页面db.session.commit()
                return redirect(url_for('Login'))


@app.route('/RegisterTeam/', methods=['GET', 'POST'])
def RegisterTeam():
    if g.teacher_id:
        if request.method == 'GET':
            return render_template('RegisterTeam.html')
        else:
            school = request.form.get('school')
            teamname = request.form.get('teamname')
            teacher = request.form.get('teacher')
            teacherphone = request.form.get('teacherphone')
            member1 = request.form.get('member1')
            member1phone = request.form.get('member1phone')
            member2 = request.form.get('member2')
            member2phone = request.form.get('member2phone')
            member3 = request.form.get('member3')
            member3phone = request.form.get('member3phone')

            team = Team.query.filter(Team.teamname == teamname).first()
            if team:
                return '该队名已注册'
            else:
                team = Team(school=school, teamname=teamname, teacher=teacher, teacherphone=teacherphone,
                            member1=member1, member1phone=member1phone, member2=member2, member2phone=member2phone,
                            member3=member3, member3phone=member3phone, user_id=g.teacher.id)
                db.session.add(team)
                db.session.commit()
                return '注册成功'
    else:
        return redirect(url_for('Login'))



@app.before_request
def my_before_request():
    teacher_id = session.get('teacher_id')
    g.teacher_id = teacher_id
    if teacher_id:
        teacher = Teacher.query.filter(Teacher.id == teacher_id).first()
        if teacher:
            g.teacher = teacher


@app.route('/Logout/')
def Logout():
    #session.pop('user_id')
    #del session['user_id']
    session.clear()
    return redirect(url_for('Login'))


@app.context_processor
def my_context_processor():
    if hasattr(g, 'teacher'):
            return {'teacher': g.teacher}
    return {}


if __name__ == '__main__':
    app.run()
