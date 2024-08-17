from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exists,and_
import csv
import bcrypt

db=SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(100),unique=False)
    password = db.Column(db.String(100))
    
    def __init__(self,email,password,name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')
        
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))
    
class CourseTaken(db.Model):
    __tablename__='CourseTaken'
    id = db.Column(db.Integer,primary_key=True)
    umail = db.Column(db.String(100))
    cname = db.Column(db.String(100))
    cby = db.Column(db.String(100))
    img = db.Column(db.String(100))
    link = db.Column(db.String(100))
    
    def __init__(self,umail,cname,cby,img,link):
        self.umail = umail
        self.cname = cname
        self.cby = cby
        self.img = img
        self.link = link
    
class CourseCompleted(db.Model):
    __tablename__='CourseCompleted'
    id = db.Column(db.Integer,primary_key=True)
    umail = db.Column(db.String(100))
    cname = db.Column(db.String(100))
    cby = db.Column(db.String(100))
    img = db.Column(db.String(100))
    link = db.Column(db.String(100))
    
    def __init__(self,umail,cname,cby,img,link):
        self.umail = umail
        self.cname = cname
        self.cby = cby
        self.img = img
        self.link = link
        
class Rating(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer)
    cid=db.Column(db.Integer)
    rating=db.Column(db.Integer)
    
    def __init__(self,user_id,cid,rating):
        self.user_id=user_id
        self.cid=cid
        self.rating=rating
        
def ratingFromCsv(csv_file):
    if db.session.query(Rating).count() == 0:
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                existing_path = db.session.query(exists().where(and_(Rating.user_id == row[0],Rating.cid == row[1]))).scalar()
                if not existing_path:
                    new_rating = Rating(
                        user_id=row[0],
                        cid=row[1],
                        rating=row[2]
                    )
                    db.session.add(new_rating)
        db.session.commit()

class Course(db.Model):
    cid=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String)
    by=db.Column(db.String)
    subject=db.Column(db.String)
    link=db.Column(db.String)
    img_link=db.Column(db.String)
    
    def __init__(self,cid,title,by,subject,link,img_link):
        self.cid=cid
        self.title=title
        self.by=by
        self.subject=subject
        self.link=link
        self.img_link=img_link
    
def coursesFromCsv(csv_file):
    if db.session.query(Course).count() == 0:
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                existing_path = db.session.query(exists().where(Course.cid == row[0])).scalar()
                if not existing_path:
                    new_course = Course(
                        cid=row[0],
                        title=row[1],
                        by=row[2],
                        subject=row[3],
                        link=row[4],
                        img_link=row[5]
                    )
                    db.session.add(new_course)
        db.session.commit()

class Path(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    skill=db.Column(db.String)
    step1=db.Column(db.String)
    step2=db.Column(db.String)
    step3=db.Column(db.String)
    step4=db.Column(db.String)
    
    def __init__(self,skill,step1,step2,step3,step4):
        self.skill=skill
        self.step1=step1
        self.step2=step2
        self.step3=step3
        self.step4=step4
        
def pathFromCsv(csv_file):
    if db.session.query(Path).count() == 0:
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                existing_path = db.session.query(exists().where(Path.skill == row[0])).scalar()
                if not existing_path:
                    new_path = Path(
                        skill=row[0],
                        step1=row[1],
                        step2=row[2],
                        step3=row[3],
                        step4=row[4]
                    )
                    db.session.add(new_path)
        db.session.commit()