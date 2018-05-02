#encoding: utf-8

from flask import Flask, render_template, request, redirect, url_for, session, g, flash, send_from_directory,make_response
from exts import db
import config
import os
from werkzeug.security import generate_password_hash, check_password_hash
from models import Teacher, Team, School, Member
from datetime import timedelta
from export_excel import Toexcel

app = Flask(__name__)
app.config.from_object(config)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=20)
db.init_app(app)
admin = u'1'
Toexcel = Toexcel()

@app.route('/')
def Index():
    return render_template('Index.html')

@app.route('/Base/')
def Base():
    teams = g.teacher.teacher_teams
    return render_template('Base.html',teams=teams)


@app.route('/Download')
def Download():
    return render_template('Download.html')


@app.route('/Download/<filename>')
def DownloadFilename(filename):
    dir = '/static/home/download/'
    print(filename)
    response = make_response(send_from_directory(dir,filename,as_attachment=True))
    print(response)
    response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
    return response


@app.route('/Add/MyPage/',methods=['GET','POST'])     # 注册队伍
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
                flash (u'警告：已有学校注册 "%s" 队伍名称,请更换名称重新注册！！！'% createteam)
                return redirect(url_for('MyPage'))
            else:
                team = Team(teamname=createteam,teacher_team_id = g.teacher_id,school_team_id = g.teacher.Teacher_school.id)
                db.session.add(team)
                db.session.commit()
                return redirect(url_for('MyPage'))
    else:
        return redirect(url_for('Login'))


@app.route('/del/team/',methods=['GET','POST'])    #删除队伍
def delteam():
    if request.method=='POST':
        delteamid = request.form.get('delteamid')
        team = Team.query.filter(Team.id==delteamid).first()
        db.session.query(Member).filter(Member.team_member_id == team.id).delete()
        db.session.delete(team)
        db.session.commit()
        return redirect(url_for('MyPage'))
    else:
        return redirect(url_for('MyPage'))

'''
所有信息的展示
'''
@app.route('/AllMessage/<schoolid>')                #所有信息显示
def AllMessage(schoolid):
    if g.teacher_id:
        teacherflag = Teacher.query.filter(Teacher.teacherflag == '1', Teacher.id == g.teacher_id).first()
        school = School.query.filter(School.id == schoolid).first()
        if teacherflag:
            members = Member.query.filter(Member.school_member_id==schoolid).order_by('team_member_id').all()
            teams = []
            for member in members:
                if member.team_member_id not in teams:
                    teams.append(member.team_member_id)
            Toexcel.examine_excel(schoolid, school.school, g.teacher.teachername)
            print('我有权限')
            return render_template('AllMessage.html', members=members, teamlist=teams,school=school)
        else:
            teams = Team.query.filter(Team.teacher_team_id == g.teacher_id).all()
            members = Member.query.filter(Member.school_member_id == schoolid , Member.teacher_member_id==g.teacher_id).order_by('team_member_id').all()
            Toexcel.unexamine_excel(schoolid, g.teacher_id, school.school, g.teacher.teachername)
            print('我没权限')
            return render_template('AllMessage.html', members=members, teamlist=teams, school=school)
    else:
        return redirect(url_for('Login'))#

@app.route('/Admin/ManageTeacher/',methods=['POST','GET']) #审核功能，审核成功
def admin_manage_teacher():
    if g.teacher_id:
        teacher = Teacher.query.filter(Teacher.id == g.teacher_id).first()
        if teacher.teacheradmin == admin:
            if request.method=='GET':
                manageteacher = Teacher.query.order_by('id').all()
                return render_template('AdminManageTeacher.html',manageteacher=manageteacher)
            else:
                teacherid = request.form.get('teacherid')
                teacher = Teacher.query.filter(Teacher.id ==teacherid).first()
                teacher.teacherflag = 1
                db.session.commit()
                return redirect( url_for('admin_manage_teacher'))
        else:
            return redirect(url_for('Index'))  #
    else:
        return redirect(url_for('Login'))#

@app.route('/Admin/ManageTeacherFlag/',methods=['POST'])    #未审核
def admin_manage_teacher_flag():
    if g.teacher_id:
        teacher = Teacher.query.filter(Teacher.id == g.teacher_id).first()
        if teacher.teacheradmin == admin:
            if request.method=='POST':
                teacherid = request.form.get('teacherid')
                teacher = Teacher.query.filter(Teacher.id == teacherid).first()
                teacher.teacherflag = 0
                db.session.commit()
                return redirect(url_for('admin_manage_teacher'))
            else:return redirect(url_for('Index'))  #

        else:
            return redirect(url_for('Index'))  #
    else:
        return redirect(url_for('Login'))  #

@app.route('/Admin/ManageTeacherDelete/', methods=['POST'])   #移除老师用户
def admin_manage_teacher_delete():
    if g.teacher_id:
        teacher = Teacher.query.filter(Teacher.id == g.teacher_id).first()
        if teacher.teacheradmin == admin:
            if request.method == 'POST':
                teacherid = request.form.get('teacherid')
                teacher = Teacher.query.filter(Teacher.id == teacherid).first()
                db.session.query(Member).filter(Member.teacher_member_id == teacherid).delete()
                db.session.query(Team).filter(Team.teacher_team_id==teacherid).delete()
                db.session.delete(teacher)
                db.session.commit()
                return redirect(url_for('admin_manage_teacher'))
            else:
                return redirect(url_for('Index'))  #

        else:
            return redirect(url_for('Index'))  #
    else:
        return redirect(url_for('Login'))

@app.route('/Admin/ManageTeacherAdmin/',methods=['POST'])   #提升为管理员和降级为普通用户
def admin_manage_teacher_admin():
    if g.teacher_id:
        teacher = Teacher.query.filter(Teacher.id == g.teacher_id).first()
        if teacher.teacheradmin == admin:
            if request.method=='POST':
                teacherid = request.form.get('teacherid')
                teacher = Teacher.query.filter(Teacher.id == teacherid).first()
                teacher.teacheradmin = 1
                db.session.commit()
                return redirect(url_for('admin_manage_teacher'))
            else:return redirect(url_for('Login'))  #

        else:
            return redirect(url_for('Index'))  #
    else:
        return redirect(url_for('Login'))  #

@app.route('/Admin/ManageTeacherUser/', methods=['POST'])
def admin_manage_teacher_user():
    if g.teacher_id:
        teacher = Teacher.query.filter(Teacher.id == g.teacher_id).first()
        if teacher.teacheradmin == admin:
            if request.method=='POST':
                teacherid = request.form.get('teacherid')
                teacher = Teacher.query.filter(Teacher.id == teacherid).first()
                teacher.teacheradmin = 0
                db.session.commit()
                return redirect(url_for('admin_manage_teacher'))
            else:return redirect(url_for('Login'))  #

        else:
            return redirect(url_for('Login'))  #
    else:
        return redirect(url_for('Login'))  #

@app.route('/Admin/Allmessage/')                 #管理员信息
def admin_allmessage():
    if g.teacher_id:
        teacher = Teacher.query.filter(Teacher.id == g.teacher_id).first()
        if teacher.teacheradmin == admin:
            members = Member.query.order_by('team_member_id').all()
            teamslist=[]     #统计成员
            teacherlist = []  # 统计老师
            schoollist = []  # 统计学校
            for member in members:
                if member.team_member_id not in teamslist:
                    teamslist.append(member.team_member_id)
                else:pass
                if member.teacher_member_id  not in teacherlist:
                    teacherlist.append(member.teacher_member_id)
                else:pass
                if member.school_member_id not in schoollist:
                    schoollist.append(member.school_member_id)
                else:pass
            Toexcel.all_school_excel()    #审核过后的人员提交队伍信息
            return render_template('AdminAllMessage.html',members=members, teamslist=teamslist,teacherlist=teacherlist,schoollist=schoollist)
        else:
            return redirect(url_for('Login'))#
    else:
        return redirect(url_for('Login'))#

@app.route('/Setting/Profile/',methods=['GET','POST'])       #个人信息展示
def Profile():
    if g.teacher_id:
        if request.method == 'GET':
            school = g.teacher.Teacher_school
            teams = g.teacher.teacher_teams
            return render_template('Profile.html', school=school,team=teams)
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


@app.route('/Setting/Team/<id>',methods=['GET']) #队伍的展示
def team(id):
    if g.teacher_id:
        if request.method == 'GET':
            team = Team.query.filter(Team.id ==id).first()
            teams = g.teacher.teacher_teams
            return render_template('FirstTeam.html',team=team,teams=teams)
    else:
        return redirect(url_for('Login'))#


    '''
    创建队伍
    '''
@app.route('/Setting/AddTeam/',methods=['POST'])
def AddTeam():
    if g.teacher_id:
        if request.method =='POST':
            teamid = request.form.get('teamid')
            member = Member(school_member_id=g.teacher.Teacher_school.id, teacher_member_id=g.teacher_id,
                            team_member_id=teamid, membername='', membersex=''
                            , membergrade='', memberskill='', membersize='', memberphone='', memberemail='')
            db.session.add(member)
            db.session.commit()
            return redirect(url_for('team',id=teamid))

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
        return redirect(url_for('Login'))#

#更新队员信息
@app.route('/Setting/Team/Updata/',methods=['POST'])
def Updata():
    if g.teacher_id:
        if request.method=='POST':
            teamid = request.form.get('team_id')
            memberid = request.form.get('memberid')
            membername = request.form.get('membername')
            membersex = request.form.get('membersex')
            membergrade= request.form.get('membergrade')
            membersize = request.form.get('membersize')
            memberskill = request.form.get('memberskill')
            memberphone = request.form.get('memberphone')
            memberemail = request.form.get('memberemail')
            memberroom = request.form.get('memberroom')
            member = Member.query.filter(Member.id == memberid).first()
            member.membername = membername
            member.membersex = membersex
            member.membergrade=membergrade
            member.membersize=membersize
            member.memberskill=memberskill
            member.memberphone=memberphone
            member.memberemail=memberemail
            member.memberroom = memberroom
            db.session.commit()
            return redirect(url_for('team',id=teamid))
    else:
        return redirect(url_for('Login'))#

'''
队伍的删除
'''
@app.route('/Setting/Team/Dele/',methods=['POST'])
def dele():
    if g.teacher_id:
        if request.method=='POST':
            memberid = request.form.get('memberid')
            teamid = request.form.get('teamid')
            print(memberid)
            member = Member.query.filter(Member.id == memberid).first()
            db.session.delete(member)
            db.session.commit()
            return redirect(url_for('team',id=member.team_member_id))
    return redirect(url_for('Index'))


#添加学校模块，查询学校是否被添加到school表中

@app.route('/Admin/Add/School/' ,methods=['GET','POST'])
def AddSchool():
    if g.teacher_id:
        teacher = Teacher.query.filter(Teacher.id == g.teacher_id).first()
        if teacher.teacheradmin == admin:
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
        else:
            print(teacher.teachername)
            return redirect(url_for('Index'))
    else:

        return redirect(url_for('Index'))
'''
完成登录模块
'''
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
            session.permanent = True
            return redirect(url_for('Index'))
        else:
            flash(u'账号或密码输入错误，请确认后重新输入!!！')
            return redirect(url_for('Login'))



#测试页面
@app.route('/test/',methods=['GET','POST'])
def test():
    if request.method=='GET':
        return render_template('test.html')
    else:
        name=request.form.get('name')
        return redirect(url_for('test'))
''''
注册页面
'''
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
        teacher_phone = Teacher.query.filter(Teacher.teacherphone == teacherphone).first()
        if teacher_phone:
            flash(u'该手机号已被注册!')
            return redirect(url_for('Regist'))
        else:
            if password != repassword:
                flash(u'两次输入的密码不相同，请重新输入！')
                return redirect(url_for('Regist'))
            else:
                school_id = School.query.filter(School.school == school).first()
                newteacher = Teacher(teachername=teachername, teacherphone=teacherphone, password=password)
                #数据添加到数据库中
                newteacher.teachersex=''
                newteacher.teacherdepartment=''
                newteacher.teacheremail=''
                newteacher.teacherjob=''
                newteacher.teacherroom=''
                newteacher.school_teacher_id=school_id.id
                db.session.add(newteacher)
                db.session.commit()
                #注册完成 就跳转到登陆页面db.session.commit()
                return render_template('RegisterSuccess.html')


#修改密码
@app.route('/ModifyPassword/',methods=['GET','POST'])
def ModifyPassword():
    if g.teacher_id:
        if request.method=='GET':
            school = g.teacher.Teacher_school
            teams = g.teacher.teacher_teams
            return render_template('ModifyPassword.html',school=school,teams=teams)
        else:
            oldpassword = request.form.get('oldpassword')
            newpassword = request.form.get('newpassword')
            teacher = Teacher.query.filter(Teacher.id == g.teacher_id).first()
            if teacher.check_password(oldpassword):
                teacher.password = generate_password_hash(newpassword)
                db.session.commit()
                flash(u'密码修改成功')
                return redirect(url_for('ModifyPassword'))
            else:
                flash(u'原密码不正确，请输入正确密码')
                return redirect(url_for('ModifyPassword'))
    else:
        return redirect(url_for('Login'))

#重置密码
@app.route('/asd',methods=['POST'])
def password():
    if g.teacher_id:
        teacher = Teacher.query.filter(Teacher.id == g.teacher_id).first()
        if teacher.teacheradmin == admin:
            if request.method=='POST':
                teacherid = request.form.get('teacherid')
                teacher = Teacher.query.filter(Teacher.id==teacherid).first()
                teacher.password = generate_password_hash('dropsec2018')
                db.session.commit()
                flash(u'密码重置成功')
                return redirect( url_for('admin_manage_teacher'))
            else:
                flash(u'密码重置失败请重试')
                return redirect( url_for('admin_manage_teacher'))
        else:
            return redirect(url_for('Index'))  #
    else:
        return redirect(url_for('Login'))  #


@app.errorhandler(404)              #页面不存在
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)              #服务器不能响应
def internal_server_error(e):
    return render_template('500.html'), 500

'''
在请求之前完成的函数
'''
@app.before_request
def my_before_request():
    teacher_id = session.get('teacher_id')
    g.teacher_id = teacher_id                 # 全局化teacher的id 在session中取得
    if teacher_id:
        teacher = Teacher.query.filter(Teacher.id == teacher_id).first()
        if teacher:
            g.teacher = teacher     #全局下的变量teacher对象
        else:pass
    else:pass




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
