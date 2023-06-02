from flask import Flask, render_template, redirect, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user


from data import db_session
from data.users import User, Task
from data.groups import Group, GroupMember, Ticket
from form.user import RegisterForm, LoginForm, MemberForm, ProfileForm, InviteForm, TaskForm
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

        # Есть ли приглашение

        group_exists = False
        group = db_sess.query(Group).filter(Group.group_name == form.group.data).first()
        if group:
            group_exists = True
            if db_sess.query(Ticket).filter(Ticket.email == form.email.data).first():
                if db_sess.query(Ticket).filter(Ticket.members_group != form.group.data).first():
                    return render_template('register.html', title='Регистрация',
                                           form=form,
                                           message=f"У вас нет приглашения в {form.group.data} \
                                           или вы неправильно написали группу.")
            else:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="У вас нет приглашений в никакие группы")
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if not group_exists:
            group = Group(
                group_name=form.group.data,
                description='Создан при регистрации'
            )
            db_sess.add(group)
            db_sess.commit()
        user = User(
            group=group.id,
            login=form.login.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        if not group_exists:
            group.group_admin = user.id
        group_member = GroupMember(
                member=user.id,
                members_group=group.id,
            )
        db_sess.add(group_member)
        db_sess.commit()
        # TODO удалить тикет
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


#Создаем ссылку на сайт members
@app.route('/members/<group>', methods=['GET'])
#Cоздаем функцию members
def members(group):
    db_sess = db_session.create_session()
    group_members = db_sess.query(GroupMember).filter(GroupMember.members_group == current_user.group,
                                                      GroupMember.member != current_user.id).all()
    group_members_new = []
    for row in group_members:
        group_members_new.append(db_sess.query(User).get(row.member))

    return render_template('members.html', members=group_members_new)




#Создаем ссылку на сайт member
@app.route('/member/<member_id>', methods=['GET', 'POST'])
#Cоздаем функцию member
def member(member_id):
    db_sess = db_session.create_session()
    form = MemberForm()
    user_group = db_sess.query(Group).filter(Group.id == current_user.group).first()
    admin = db_sess.query(User).filter(User.id == user_group.group_admin).first()
    group_member = db_sess.query(User).get(member_id)
    form.login.data = group_member.login
    form.email.data = group_member.email
    form.is_admin.data = True
    if admin != current_user:
        form.is_admin.data = False
    return render_template('member.html', form=form)


#Создаем ссылку на сайт profile
@app.route("/profile", methods=['GET', 'POST'])
@login_required
#Создаем функцию profile
def profile():
    form = ProfileForm()
    db_sess = db_session.create_session()
    user_profile = db_sess.query(User).get(current_user.id)
    user_group = db_sess.query(Group).get(current_user.group)
    if form.validate_on_submit():
        if form.cancel.data:
            return redirect('/')
        if form.password.data != form.password_again.data:
            return render_template('profile.html', title='Изменение данных',
                                   form=form,
                                   message="Пароли не совпадают")
        user_profile.login = form.login.data
        user_profile.email = form.email.data
        user_group = db_sess.query(Group).filter(Group.group_name == form.group.data).first()
        if not user_group:
            return render_template('profile.html', title='Изменение данных',
                                   form=form,
                                   message=f"Группа: '{form.group.data}' не существует.")
        group_member = db_sess.query(GroupMember).filter(GroupMember.members_group == user_group.id,
                                                          GroupMember.member == user_profile.id).first()
        if not group_member:
            return render_template('profile.html', title='Изменение данных',
                                   form=form,
                                   message=f"Вы не являетесь членом группы '{form.group.data}'.")
        user_profile.group = user_group.id
        if form.password.data:
            user_profile.set_password(form.password.data)
        db_sess.commit()
        return redirect('/')
    else:
        form.login.data = user_profile.login
        form.email.data = user_profile.email
        form.group.data = user_group.group_name
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
@login_required
def create_group():
    form = Create_GroupForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        admin = db_sess.query(User).filter(User.id == current_user.id).first()
        group = db_sess.query(Group).filter(Group.group_name == form.group.data).first()
        if not group:
            group = Group(
                group_admin=admin.id,
                group_name=form.group.data,
                description=form.description.data
            )
            db_sess.add(group)
            db_sess.commit()
            group_member = GroupMember(
                members_group=group.id,
                member=admin.id
            )
            db_sess.add(group_member)
            db_sess.commit()
            return "<h3>Создание группы</h3>" \
                   f"<p class='my-3 my-md-4'> Группа '{group.group_name}' создана.</p>" \
                   "<a href='/profile'>Возврат</a>"
        else:
            return render_template('create_group.html', title='Создание группы', form=form,
                                   message=f"Такая группа '{group.group_name}' уже есть.")
    return render_template('create_group.html', title='Создание группы', form=form)


@app.route("/my_groups", methods=['GET', 'POST'])
def my_groups():
    db_sess = db_session.create_session()
    group_list = []
    groups = db_sess.query(Group).filter(Group.group_admin == current_user.id).all()
    for row in groups:
        if not row.description:
            row.description = 'None'
        cor = (row.group_name, row.description)
        group_list.append(cor)

    return render_template('my_groups.html', group_list=group_list)


@app.route("/invite", methods=['GET', 'POST'])
def invite():
    form = InviteForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        ticket = db_sess.query(Ticket).filter(Ticket.email == form.email.data,
                                              Ticket.members_group == form.group.data).first()

        if ticket:
            return render_template('invite.html', title='Приглашение в группу', form=form,
                                   message=f"Приглашение в группу для {form.email.data} уже есть")
        else:
            ticket = Ticket(
                members_group=form.group.data,
                email=form.email.data
            )
            db_sess.add(ticket)
            db_sess.commit()
            # return render_template('message.html', title='Приглашение в группу',
            #                        message=f"Пользователь {form.email.data} включен в группу")
            return "<h3>Приглашение в группу</h3>"\
                "<p class='my-3 my-md-4'> Отправте по email приглашение.</p>"\
                f"<div>Пользователь {form.email.data} включен в группу</div>"\
                "<a href='/'>Возврат</a>"
    return render_template('invite.html', title='Приглашение в группу', form=form)


@app.route('/task/<email>', methods=['GET', 'POST'])
@login_required
def task(email):
    form = TaskForm()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == email).first()
    group = db_sess.query(Group).filter(Group.id == current_user.group).first()
    admin = db_sess.query(User).get(group.group_admin)
    is_admin = False
    if user.id == admin.id:
        is_admin = True
    form.login.data = user.login

    if form.validate_on_submit():
        task = Task(
            login=user.login,
            short_task=form.short_task.data,
            detail_task=form.detail_task.data,
            completed=form.completed.data
        )

        group = db_sess.query(Group).filter(Group.group_name == form.group.data).first()
        if group:
            group_exists = True
            if db_sess.query(Ticket).filter(Ticket.email == form.email.data).first():
                if db_sess.query(Ticket).filter(Ticket.members_group != form.group.data).first():
                    return render_template('register.html', title='Регистрация',
                                           form=form,
                                           message=f"У вас нет приглашения в {form.group.data} \
                                           или вы неправильно написали группу.")
            else:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="У вас нет приглашений в никакие группы")
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if not group_exists:
            group = Group(
                group_name=form.group.data,
                description='Создан при регистрации'
            )
            db_sess.add(group)
            db_sess.commit()
        user = User(
            group=group.id,
            login=form.login.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        if not group_exists:
            group.group_admin = user.id
        group_member = GroupMember(
                member=user.id,
                members_group=group.id,
            )
        db_sess.add(group_member)
        db_sess.commit()
        # TODO удалить тикет
        return redirect('/')
    return render_template('task.html', title='Постановка задачи', form=form)



def main():
    db_session.global_init("db/db.db")
    app.run()


if __name__ == '__main__':
    main()
