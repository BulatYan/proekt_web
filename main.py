from flask import Flask, render_template, redirect, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user


from data import db_session
from data.users import User
from data.groups import Group, GroupMember
from form.user import RegisterForm, LoginForm, MemberForm, ProfileForm
from form.group import Create_GroupForm
from data.description import Description

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ps_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#Создаем ссылку на главную страницу
@app.route('/')
#Создаем ссылку на сайт index
@app.route('/index')
#Создаем функцию index
def index():
    return render_template('index.html', title='Начальная страница')

#Создаем ссылку на сайт логин
@app.route('/login', methods=['GET', 'POST'])
#Создаем функцию логина
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user:
            true_pass = user.check_password(form.password.data)
            if true_pass:
                login_user(user, remember=form.remember_me.data)
                return redirect('/')
            return render_template('login.html', message='Неправильный пароль',
                                   form=form)
        return render_template('login.html', message='Неправильный логин',
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


#Создаем ссылку на сайт register
@app.route('/register', methods=['GET', 'POST'])
#Создаем функцию register
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            group=form.group.data,
            login=form.login.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


#Создаем ссылку на сайт members
@app.route('/members/<group>', methods=['GET'])
#Cоздаем функцию members
def members(group):
    db_sess = db_session.create_session()
    group_members = db_sess.query(User).filter(User.group == group, User.id != current_user.id).all()
    return render_template('members.html', members=group_members)


#Создаем ссылку на сайт member
@app.route('/member/<member_id>', methods=['GET', 'POST'])
#Cоздаем функцию member
def member(member_id):
    db_sess = db_session.create_session()
    group_member = db_sess.query(User).get(member_id)
    if member_id == current_user.id:
        group = group_member.group
        return redirect(f"/member/{group}")
    else:
        form = MemberForm()
        descr = db_sess.query(Description).filter(Description.member_id == member_id,
                                                  Description.author_id == current_user.id).first()
        add_new = False
        if descr is None:
            descr = Description()
            add_new = True
        if form.validate_on_submit():
            descr.member_id = group_member.id
            descr.author_id = current_user.id
            descr.har01 = form.har01.data
            descr.har02 = form.har02.data
            descr.har03 = form.har03.data
            descr.har04 = form.har04.data
            descr.har05 = form.har05.data
            descr.har06 = form.har06.data
            descr.har07 = form.har07.data
            descr.har08 = form.har08.data
            descr.har09 = form.har09.data
            descr.har10 = form.har10.data
            descr.har11 = form.har11.data
            descr.har12 = form.har12.data
            descr.har13 = form.har13.data
            if add_new:
                db_sess.add(descr)
            db_sess.commit()
            return redirect('/')
        else:
            form.har01.data = descr.har01
            form.har02.data = descr.har02
            form.har03.data = descr.har03
            form.har04.data = descr.har04
            form.har05.data = descr.har05
            form.har06.data = descr.har06
            form.har07.data = descr.har07
            form.har08.data = descr.har08
            form.har09.data = descr.har09
            form.har10.data = descr.har10
            form.har11.data = descr.har11
            form.har12.data = descr.har12
            form.har13.data = descr.har13
        return render_template('member.html', member=group_member, form=form)


#Создаем ссылку на сайт profile
@app.route("/profile", methods=['GET', 'POST'])
@login_required
#Создаем функцию profile
def profile():
    form = ProfileForm()
    db_sess = db_session.create_session()
    member_profile = db_sess.query(User).get(current_user.id)
    if form.validate_on_submit():
        if form.cancel.data:
            return redirect('/')
        if form.password.data != form.password_again.data:
            return render_template('profile.html', title='Изменение данных',
                                   form=form,
                                   message="Пароли не совпадают")
        member_profile.login = form.login.data
        member_profile.email = form.email.data
        member_profile.group = form.group.data
        if form.password.data:
            member_profile.set_password(form.password.data)
        db_sess.commit()
        return redirect('/')
    else:
        form.login.data = member_profile.login
        form.email.data = member_profile.email
        form.group.data = member_profile.group
    return render_template('profile.html', title='Изменение данных',
                           form=form)


#Создаем ссылку на сайт aboutme
@app.route('/aboutme', methods=['GET'])
@login_required
#Cоздаем функцию aboutme
def aboutme():
    db_sess = db_session.create_session()
    descr_list = []
    descr_base = {"har01":"Самодостаточность",
                    "har02":"Честность",
                    "har03":"Бесстрашие",
                    "har04":"Доверие",
                    "har05":"Заинтересованность",
                    "har06":"Дружелюбие",
                    "har07":"Чувствительность",
                    "har08":"Поддержка",
                    "har09":"Верность",
                    "har10":"Чувство юмора",
                    "har11":"Оптимизм",
                    "har12":"Терпение",
                    "har13":"Доброта"}
    for row in db_sess.query(Description).filter(Description.member_id == current_user.id).all():
        row_list = []
        if row.har01:
            row_list.append(descr_base['har01'])
        if row.har02:
            row_list.append(descr_base['har02'])
        if row.har03:
            row_list.append(descr_base['har03'])
        if row.har04:
            row_list.append(descr_base['har04'])
        if row.har05:
            row_list.append(descr_base['har05'])
        if row.har06:
            row_list.append(descr_base['har06'])
        if row.har07:
            row_list.append(descr_base['har07'])
        if row.har08:
            row_list.append(descr_base['har08'])
        if row.har09:
            row_list.append(descr_base['har09'])
        if row.har10:
            row_list.append(descr_base['har10'])
        if row.har11:
            row_list.append(descr_base['har11'])
        if row.har12:
            row_list.append(descr_base['har12'])
        if row.har13:
            row_list.append(descr_base['har13'])
        if row_list:
            descr_list.append(', '.join(row_list).capitalize())
    return render_template('aboutme.html', descr_list=descr_list)


@app.route("/create_group", methods=['GET', 'POST'])
def ctreate_group():
    form = Create_GroupForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        admin = db_sess.query(User).filter(User.id == current_user.id).first()
        if admin:
            group = Group(
                group_admin=admin.id,
                group_name=form.group.data,
                description=form.description.data
            )
            group_member = GroupMember(
                members_group=form.group.data,
                member=admin.id
            )
            db_sess.add(group)
            db_sess.add(group_member)
            db_sess.commit()
            return redirect('/')

    return render_template('create_group.html', title='Создание группы', form=form)


@app.route("/my_groups", methods=['GET', 'POST'])
def my_groups():
    db_sess = db_session.create_session()
    group_list = []
    for row in db_sess.query(GroupMember).all():
        group_list.append(row.members_group)
    return render_template('my_groups.html', group_list=group_list)


@app.route("/invite", methods=['GET', 'POST'])
def invite():
    pass

def main():
    db_session.global_init("db/db.db")
    app.run()


if __name__ == '__main__':
    main()
