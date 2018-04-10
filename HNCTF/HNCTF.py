#encoding: utf-8

from flask import Flask, render_template, request, redirect, url_for, session, g, flash
from exts import db
import config
import os
from models import Teacher, Team, School, Member
from datetime import timedelta


app = Flask(__name__)
app.config.from_object(config)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=20)
db.init_app(app)



@app.route('/')
def Index():
    return render_template('Index.html')

@app.route('/Base/')
def Base():
    teams = g.teacher.teacher_teams
    return render_template('Base.html',teams=teams)

@app.route('/Add/MyPage/',methods=['GET','POST'])
def MyPage():
    if g.teacher_id:
        if request.method=='GET':
            school = g.teacher.Teacher_school
            teams = g.teacher.teacher_teams
            return render_template('form.html',school=school,teams = teams)
        else:
            createteam = request.form.get('createteam')
            team =Team.query.filter(Team.teamname==createteam).first()
            if team:
                print('qingchong..')
                return '已有学校注册此队伍名称'
            else:
                team = Team(teamname=createteam,teacher_team_id = g.teacher_id,school_team_id = g.teacher.Teacher_school.id)
                db.session.add(team)
                db.session.commit()
                return redirect(url_for('MyPage'))
    else:
        return redirect(url_for('Login'))


@app.route('/del/team/',methods=['GET','POST'])
def delteam():
    if request.method=='POST':
        delteam = request.form.get('delteam')
        print(delteam)
        team = Team.query.filter(Team.teamname==delteam).first()
        db.session.delete(team)
        db.session.commit()
        return redirect(url_for('MyPage'))
    else:
        print('qq')
        return redirect(url_for('MyPage'))


@app.route('/AllMessage/')                #所有信息显示
def AllMessage():
    if g.teacher_id:
        teams = g.teacher.teacher_teams
        return render_template('AllMessage.html',teams=teams)
    else:
        return redirect(url_for('Login'))#
#设置信息
@app.route('/Setting/Basic/')              # 基础模版
def Basic():
    if g.teacher_id:
        teams = g.teacher.teacher_teams
        return render_template('Basic.html',teams=teams)
    else:
        return redirect(url_for('Login'))#
@app.route('/Delete/Team',methods=['GET'])





@app.route('/Setting/Profile/',methods=['GET','POST'])       #个人信息展示
def Profile():
    if g.teacher_id:
        if request.method == 'GET':
            school = g.teacher.Teacher_school
            teams = g.teacher.teacher_teams
            return render_template('Profile.html', school=school,teams=teams)
        else:
            teachersex = request.form.get('teachersex')
            teacherdepartment = request.form.get('teacherdepartment')
            teacherjob = request.form.get('teacherjob')
            teacheremail = request.form.get('teacheremail')
            teacherroom = request.form.get('teacherroom')
            teacher = Teacher.query.filter(Teacher.id == g.teacher_id).first()
            teacher.teachersex = teachersex
            teacher.teacherdepartment = teacherdepartment
            teacher.teacherjob = teacherjob
            teacher.teacheremail = teacheremail
            teacher.teacherroom = teacherroom
            db.session.commit()
            return redirect(url_for('Profile'))
    else:
        return redirect(url_for('Login'))#


@app.route('/Setting/CreateTeam/')
def CreateTeam():
    if g.teacher_id:
        return render_template('CreateTeam.html')
    else:
        return redirect(url_for('Login'))#


@app.route('/Setting/FirstTeam/',methods=['GET','POST'])            #  第一支队伍的展示
def FirstTeam():
    if g.teacher_id:
        if request.method=='GET':
            school = g.teacher.Teacher_school
            teams = g.teacher.teacher_teams
            teamss = g.teacher.teacher_teams
            members = teams[0].team_members  #第一支队伍下面的全部的成员
            try:
                return render_template('FirstTeam.html',school=school,teamss=teamss[0],teams=teams,members=members)
            except IndexError as e:
                return '404'

        else:
            member = Member(school_member_id=g.teacher.Teacher_school.id, teacher_member_id=g.teacher_id, team_member_id=g.teacher.teacher_teams[0].id, membername='')
            db.session.add(member)
            db.session.commit()
            return redirect(url_for('FirstTeam'))
    else:
        return redirect(url_for('Login'))#

#更新队员信息
@app.route('/Setting/FirstTeam/Updata/',methods=['POST'])
def Updata():
    if g.teacher_id:
        if request.method=='POST':
            membername = request.form.get('membername')
            membersex = request.form.get('membersex')
            membergrade= request.form.get('membergrade')
            membersize = request.form.get('membersize')
            memberskill = request.form.get('memberskill')
            memberphone = request.form.get('memberphone')
            memberemail = request.form.get('memberemail')
            memberroom = request.form.get('memberroom')
            member = Member.query.filter(Member.teacher_member_id==g.teacher_id).first()
            member.membername = membername
            member.membersex=membersex
            member.membergrade=membergrade
            member.membersize=membersize
            member.memberskill=memberskill
            member.memberphone=memberphone
            member.memberemail=memberemail
            member.memberroom = memberroom
            db.session.commit()
            return redirect(url_for('FirstTeam'))
    else:
        return redirect(url_for('Login'))#

@app.route('/Setting/FirstTeam/Dele/',methods=['POST'])
def dele():
    if g.teacher_id:
        if request.method=='POST':
            membername = request.form.get('membername')
            print(membername)
            member = Member.query.filter(Member.membername=='').first()
            print(member)
            db.session.delete(member)
            db.session.commit()
            return redirect(url_for('FirstTeam'))
        else:

            return redirect(url_for('FirstTeam'))
    return redirect(url_for('Index'))


@app.route('/Setting/SecondTeam/')
def SecondTeam():
    if g.teacher_id:
        return render_template('SecondTeam.html')
    else:
        return redirect(url_for('Login'))#
@app.route('/Setting/ThirdTeam/')
def ThirdTeam():
    if g.teacher_id:
        return render_template('ThirdTeam.html')
    else:
        return redirect(url_for('Login'))#


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

#添加学校模块，查询学校是否被添加到school表中

@app.route('/admin/add/school/' ,methods=['GET','POST'])
def AddSchool():
    if request.method=='GET':
        Schools = {
            'schools': School.query.order_by('id').all()
        }
        return render_template('Admin.html',**Schools)
    else:
        school = request.form.get('addschool')

        addschool = School.query.filter(School.school==school).first()
        if addschool:
            return '学校已经添加'
        else:
            school = School(school = school)
            db.session.add(school)
            db.session.commit()
            return redirect(url_for('AddSchool'))



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


# 删除学校

@app.route('/Register/', methods=['GET', 'POST'])
def Regist():
    if request.method == 'GET':
        Schools = {
            'schools': School.query.order_by('id').all()
        }
        return render_template('Register.html',**Schools)
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
                print(school)
                school_id = School.query.filter(School.school == school).first()

                print('school',school_id.school)
                print(teachername)
                print (teachername,teacherphone,password,repassword)
                teacher = Teacher(teachername=teachername, teacherphone=teacherphone, password=password)
                #数据添加到数据库中
                teacher.school_teacher_id=school_id.id
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
    g.teacher_id = teacher_id                 # 全局化teacher的id 在session中取得
    if teacher_id:
        teacher = Teacher.query.filter(Teacher.id == teacher_id).first()
        if teacher:
            g.teacher = teacher                          #全局下的变量teacher对象


@app.route('/Logout/')
def Logout():
    session.clear()
    return redirect(url_for('Login'))


@app.context_processor
def my_context_processor():
    if hasattr(g, 'teacher'):
            return {'teacher': g.teacher}
    return {}


if __name__ == '__main__':
    app.run(debug=True,port=5000)
