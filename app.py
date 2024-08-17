from flask import Flask,request,render_template,redirect,session,url_for,flash,jsonify
from forms import RegistrationForm, LoginForm
from models import db,User,CourseTaken,CourseCompleted,Rating,Path,pathFromCsv,coursesFromCsv,ratingFromCsv
from sqlalchemy.exc import OperationalError
import pickle
from recommendation import load,recommend
import pandas as pd
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, instance_path=os.path.join(base_dir, 'instance'))

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(app.instance_path, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if not os.path.exists(app.instance_path):
    os.makedirs(app.instance_path)

app.secret_key='secret_key'

db.init_app(app)

with app.app_context():
    db.create_all()

    course_csv_path = os.path.join(base_dir,'Dataset', 'Courses.csv')
    path_csv_path = os.path.join(base_dir,'Dataset', 'Path.csv')
    rating_csv_path = os.path.join(base_dir,'Dataset', 'Rating.csv')

    coursesFromCsv(course_csv_path)
    pathFromCsv(path_csv_path)
    ratingFromCsv(rating_csv_path)
    load()
    file_path=os.path.join(base_dir,'templates','popular.pkl')
    popular_df=pickle.load(open(file_path,'rb'))
    

def get_current_user():
    if 'email' in session:
        return User.query.filter_by(email=session['email']).first()
    return None

@app.route('/')
def index():
    return 'Hello World'

@app.route('/register',methods=['GET','POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        
        new_user = User(name=name,email=email,password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['email']=user.email
            return redirect('/dashboard')
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html',form=form)

@app.route('/dashboard')
def dashboard():
    user=get_current_user()
    if user:
        try:
            courses_taken = CourseTaken.query.filter_by(umail=user.email).all()
        except OperationalError:
            courses_taken = None
        try:
            courses_completed = CourseCompleted.query.filter_by(umail=user.email).all()
        except OperationalError:
            courses_completed = None
            
        message=request.args.get('message')
        
        return render_template('dashboard.html',user=user,courses_taken=courses_taken,courses_completed=courses_completed,message=message)
    return redirect('/login')

@app.route('/skills')
def skills():
    user = get_current_user()
    if user:
        skills_list = Path.query.with_entities(Path.skill).all()
        skills_list = [row[0] for row in skills_list]
        return render_template('skills.html',user=user,skills_list=skills_list)
    return redirect('/login')

@app.route('/path')
def path():
    user = get_current_user()
    if user:
        skill=request.args.get('skill')
        session['selected_skill']=skill
        path_row = Path.query.filter_by(skill=skill).first()
        if path_row:
            return render_template('path.html', user=user, path_row=path_row)
    return redirect('/login')

@app.route('/courses')
def courses():
    user = get_current_user()
    if user:
        step=request.args.get('step')
        return render_template('courses.html',step=step,
                           course_name=list(popular_df['Course_Title'].values),
                           course_by=list(popular_df['Course_by'].values),
                           img_link=list(popular_df['Image_link'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_ratings'].values),
                           link=list(popular_df['Link'].values),
                           subject=list(popular_df['Subject'].values)
                           )
    return redirect('/login')
    
@app.route('/add',methods=['GET','POST'])
def add():
    if request.method=='POST':
        data = request.json
        umail = data.get('umail')
        cname = data.get('cname')
        cby = data.get('cby')
        image = data.get('img')
        link = data.get('link')
        new_course = CourseTaken(umail=umail,cname=cname,cby=cby,img=image,link=link)
        db.session.add(new_course)
        db.session.commit()
        
        return jsonify({'message': 'Course added successfully'})
    else:
        user = get_current_user()
        if user:
            url = request.args.get('url')
            img = request.args.get('img')
            name = request.args.get('name')
            by = request.args.get('by')
            step = request.args.get('step')
            if CourseTaken.query.filter_by(umail=user.email , cname=name).first():
                return render_template('done.html',status='taken')
            elif CourseCompleted.query.filter_by(umail=user.email , cname=name).first():
                return render_template('done.html',status='completed')
            else:
                return render_template('add.html',user=user,url=url,img=img,name=name,by=by,step=step)
    
        return redirect('/login')
    
@app.route('/rating', methods=['GET', 'POST'])
def rating():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            user_id = data.get('user_id')
            cid = data.get('cid')
            rated_index = data.get('ratedIndex')
            
            if user_id is None or cid is None or rated_index is None:
                return jsonify({'error': 'Missing data in request'}), 400
                
            new_rating = Rating(user_id=user_id, cid=cid, rating=rated_index)
            db.session.add(new_rating)
            db.session.commit()
            
            course_name = popular_df[popular_df['cid'] == cid]['Course_Title'].iloc[0]
            course_entry=CourseTaken.query.filter_by(cname=course_name).first()
            if course_entry:
                new_completed_entry=CourseCompleted(umail=course_entry.umail,cname=course_entry.cname,cby=course_entry.cby,img=course_entry.img,link=course_entry.link)
                db.session.add(new_completed_entry)
                db.session.commit()
            CourseTaken.query.filter_by(cname=course_name).delete()
            db.session.commit()

            return jsonify({'message': 'Rating saved successfully'}), 200
    user = get_current_user()
    if user:
        cname = request.args.get('cname')
        course = popular_df[popular_df['Course_Title'] == cname]
        return render_template('rating.html',user=user,course=course)
    else:
        return redirect('/login')
        
@app.route('/recommendation')
def recommendation():
    user=get_current_user()
    if user:
        cid = int(request.args.get('cid'))
        course = popular_df[popular_df['cid']==cid]
        subject=session.get('selected_skill')
        rec = recommend(subject, course.Course_Title)
        
        if isinstance(rec, tuple):
            return redirect(url_for('dashboard', message=rec[1]))
        
        rec_df = pd.DataFrame({'Course_Title': rec})
        filtered_df = pd.merge(rec_df, popular_df, on='Course_Title', how='left')
        return render_template('recommendation.html',
                               course_name=list(filtered_df['Course_Title'].values),
                               course_by=list(filtered_df['Course_by'].values),
                               link=list(filtered_df['Link'].values),
                               img_link=list(filtered_df['Image_link'].values))

@app.route('/logout')
def logout():
    session.pop('email',None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True,use_reloader=False)
