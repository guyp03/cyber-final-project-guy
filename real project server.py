from  flask import Flask,redirect,url_for,render_template,request,session,flash
from flask_sqlalchemy import SQLAlchemy
from scrapeConcerts import *
app=Flask(__name__)
app.secret_key="hey"
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///users.sql3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)
months_dictionary={1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
states_list=["United States","United Kindom","Germany","Spain","France","Italy"]
saved=db.Table('saved',
               db.Column('user_id',db.Integer,db.ForeignKey('users.user_id')),
               db.Column('concert_id',db.Integer,db.ForeignKey('concerts.concert_id'))
               )
class users(db.Model):
    user_id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    password=db.Column(db.String(100))
    saved_events=db.relationship('concerts',secondary=saved,backref=db.backref('registered',lazy='dynamic'))
    def __init__(self,name,password):
        self.password=password
        self.name=name
class concerts(db.Model):
    concert_id = db.Column(db.Integer, primary_key=True)
    state=db.Column(db.String(100))
    day=db.Column(db.Integer)
    month=db.Column(db.String(20))
    year=db.Column(db.Integer)
    event=db.Column(db.String(200))
    artists=db.Column(db.String(100))
    venue=db.Column(db.String(100))
    address=db.Column(db.String(100))
    def __init__(self,state,day,month,year,event,artists,venue,address):
        self.state=state
        self.day=day
        self.month = month
        self.year=year
        self.event=event
        self.artists = artists
        self.venue = venue
        self.address = address

def create_concerts():
    if concerts.query.all()==[]:
        index=0
        scraper=scraper_concerts()
        states_list,days_list,months_list,years_list,events_list,artists_list,venues_list,addresses_list=scraper.ret_events()
        while index < len(states_list):
            con=concerts(states_list[index],days_list[index],months_list[index],years_list[index],events_list[index],artists_list[index],venues_list[index],addresses_list[index])
            db.session.add(con)
            index=index+1
        db.session.commit()


@app.route("/home",methods=["POST","GET"])
def home():
    if request.method=="POST":
        sign_type=request.form["in or up"]
        if sign_type=="sign in":
            return redirect(url_for("sign_in"))
        else:
            return redirect(url_for("sign_up"))
    else:
        if "my_user_name" in session:
            flash("you've already signed in","info")
            return redirect(url_for("user_page"))
        else:
            return render_template("home_page.html")
@app.route("/signin",methods=["POST","GET"])
def sign_in():
    final_user_name = ""
    if request.method=="POST":
        done=False
        while True:
            user_name=request.form["un"]
            password=request.form["p"]
            found_user = users.query.filter_by(name=user_name).first()
            if found_user:
                if found_user.password==password:
                    session["my_user_name"]=user_name
                    break
            flash("user name or password is'nt correct.please try again.","info")
            return render_template("sign_in.html")

        return redirect(url_for("user_page"))
    else :
        return render_template("sign_in.html")
@app.route("/signup",methods=["POST","GET"])
def sign_up():
    if request.method=="POST":
        while True:
            erorr_m=""
            user_name = request.form["un"]
            password = request.form["p"]
            verify_password=request.form["vp"]
            found_user = users.query.filter_by(name=user_name).first()
            if found_user:
                erorr_m = "the name is occupied.please enter a different one."
            else:
                if password==verify_password:
                    usr=users(user_name, password)
                    db.session.add(usr)
                    session["my_user_name"]=user_name
                    db.session.commit()
                    break
                else:
                    erorr_m="please enter the exact same password you enterd above."
            flash(erorr_m,"info")
            return render_template("sign_up.html")
        return redirect(url_for("user_page"))
    else:
        return render_template("sign_up.html")
@app.route("/user",methods=["POST","GET"])
def user_page():
    if request.method=="POST":
        my_user = users.query.filter_by(name=session["my_user_name"]).first()
        session["date"]=request.form["d"]
        print(session["date"])
        session["country"]=request.form["c"]
        date_componantes=session["date"].split("-")
        year=date_componantes[0]
        number_month=int(date_componantes[1])
        month=months_dictionary[number_month]
        day=date_componantes[2]
        print(day)
        print(month)
        print(year)
        print(session["country"])
        found_concert=concerts.query.filter_by(state=session["country"],day=day,year=year,month=month)
        check=found_concert.first()
        print(found_concert)
        if check:
            None
        else:
            print("in")
            flash("concerts have not been found.","info")
        return render_template("user_main_page.html", user=my_user,concerts=found_concert,states=states_list,date=session["date"],country=session["country"])
    else:
        if "date" in session:
            my_user = users.query.filter_by(name=session["my_user_name"]).first()
            date_componantes = session["date"].split("-")
            year = date_componantes[0]
            number_month = int(date_componantes[1])
            month = months_dictionary[number_month]
            day = date_componantes[2]
            found_concert = concerts.query.filter_by(state=session["country"], day=day, year=year, month=month)
            return render_template("user_main_page.html", user=my_user,concerts=found_concert,states=states_list,date=session["date"],country=session["country"])
        else:
            if "my_user_name" in session:
                my_user = users.query.filter_by(name=session["my_user_name"]).first()
                return render_template("user_main_page.html",user=my_user,states=states_list)
            else:
                flash("you've got to sign in first of all.","info")
                return redirect(url_for("home"))

@app.route("/logout",methods=["POST","GET"])
def logout():
    flash("you logged out seccessfully!", "info")
    session.pop("my_user_name", None)
    if "date" in session:
        session.pop("date",None)
        session.pop("country",None)
    return redirect(url_for("home"))
@app.route("/add",methods=["POST","GET"])
def add_event():
    if request.method=="POST":
        my_user = users.query.filter_by(name=session["my_user_name"]).first()
        my_id=request.form["add"]
        selected_event=concerts.query.filter_by(concert_id=int(my_id)).first()
        selected_event.registered.append(my_user)
        db.session.commit()
    else:
        None
    return redirect(url_for("user_page"))

@app.route("/user events",methods=["POST","GET"])
def my_events():
    if "my_user_name" in session:
        my_user = users.query.filter_by(name=session["my_user_name"]).first()
        found_concerts=my_user.saved_events
        return render_template("events page.html",concerts=found_concerts)
    else:
        flash("you've got to sign in first of all.","info")
        return redirect(url_for("home"))

@app.route("/remove",methods=["POST","GET"])
def remove():
    if request.method=="POST":
        my_user = users.query.filter_by(name=session["my_user_name"]).first()
        id_to_remove = request.form["remove"]
        concert_to_remove=concerts.query.filter_by(concert_id=int(id_to_remove)).first()
        my_user.saved_events.remove(concert_to_remove)
        db.session.commit()
    else:
        None
    return redirect(url_for("my_events"))


if __name__ == '__main__':
    db.create_all()
    create_concerts()
    app.run(debug=True)