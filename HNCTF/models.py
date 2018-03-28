#encoding: utf-8

from exts import db
from werkzeug.security import generate_password_hash, check_password_hash


class Teacher(db.Model):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school = db.Column(db.String(100), nullable=False)
    teachername = db.Column(db.String(100), nullable=False)
    teacherphone = db.Column(db.String(11), nullable=False)
    password = db.Column(db.String(100), nullable=False)

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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school = db.Column(db.String(100), nullable=False)
    teamname = db.Column(db.String(100), nullable=False)
    teacher = db.Column(db.String(100), nullable=False)
    teacherphone = db.Column(db.String(11), nullable=False)

    member1 = db.Column(db.String(100), nullable=False)
    member1phone = db.Column(db.String(11), nullable=False)

    member2 = db.Column(db.String(100), nullable=False)
    member2phone = db.Column(db.String(11), nullable=False)

    member3 = db.Column(db.String(100), nullable=False)
    member3phone = db.Column(db.String(11), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))

    user = db.relationship('Teacher', backref=db.backref('teams'))



