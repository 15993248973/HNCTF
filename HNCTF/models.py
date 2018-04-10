#encoding: utf-8

from exts import db
from werkzeug.security import generate_password_hash, check_password_hash

class School(db.Model):
    __tablename__ = 'school'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school = db.Column(db.String(100), nullable=True)

class Teacher(db.Model):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) # 老师id
    teachername = db.Column(db.String(100), nullable=False) # 老师名字
    teamname = db.Column(db.String(100), nullable=True)     # 队伍名字
    teacherphone = db.Column(db.String(11), nullable=False)     # 老师手机
    password = db.Column(db.String(100), nullable=False)     # 老师密码
    teachersex = db.Column(db.String(100), nullable=True)     # 老师性别
    teacherdepartment = db.Column(db.String(100), nullable=True)     # 老师部门
    teacherjob = db.Column(db.String(100), nullable=True)     # 老师职位
    teacheremail = db.Column(db.String(100), nullable=True)     # 老师邮箱
    teacherroom = db.Column(db.String(100), nullable=True)     # 老师备注房间
    school_teacher_id = db.Column(db.Integer, db.ForeignKey('school.id'))

    Teacher_school = db.relationship('School',backref= db.backref('school_teachers'))


    #拦截用户数据
    def __init__(self,*args, **kwargs):
        school = kwargs.get('school')
        teachername = kwargs.get('teachername')
        teacherphone = kwargs.get('teacherphone')
        password = kwargs.get('password')

        self.school = school
        self.teachername = teachername
        self.teacherphone = teacherphone
        self.password = generate_password_hash(password)

    def check_password(self, raw_password):
        result = check_password_hash(self.password, raw_password)
        return result

class Team(db.Model):
    __talename__ = 'team'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)     #团队id
    teamname = db.Column(db.String(100), nullable=True)     # 队伍名
    school_team_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    teacher_team_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))

    Team_school = db.relationship('School', backref=db.backref('school_teams'))  # 学校下面所有的团队
    Team_teacher = db.relationship('Teacher', backref=db.backref('teacher_teams')) #老师下面的所有团队


class Member(db.Model):
    __talename__ = 'member'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)     # 学生id
    membername = db.Column(db.String(100), nullable=True)     # 成员姓名
    membersex = db.Column(db.String(100), nullable=True)     # 成员性别
    membergrade = db.Column(db.String(100), nullable=True)     # 成员专业年级
    memberskill = db.Column(db.String(100), nullable=True)     # 成员技能
    membersize = db.Column(db.String(100), nullable=True)     # 成员尺寸
    memberphone = db.Column(db.String(11), nullable=True)     # 成员手机
    memberemail = db.Column(db.String(100), nullable=True)     # 成员邮件
    school_member_id = db.Column(db.Integer,db.ForeignKey('school.id'))
    teacher_member_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    team_member_id = db.Column(db.Integer, db.ForeignKey('team.id'))

    Member_school = db.relationship('School',backref = db.backref('school_members'))  #学校下面所有的人

    Member_teacher = db.relationship('Teacher', backref=db.backref('teacher_members'))   #老师下面所有的人

                          #在team中查找某个学生             在老师中查找某个老师
                          #。zteacher就是老师对象             。teams就是全部学生对象然后for循环出所有的对象
    Member_team = db.relationship('Team', backref=db.backref('team_members'))     # 团队下面所有的人



