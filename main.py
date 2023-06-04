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
    group = db_sess.query(Group).filter(Group.id == current_user.group).first()
    admin = db_sess.query(User).get(group.group_admin)
    is_admin = False
    if current_user.id == admin.id:
        is_admin = True
    group_members = db_sess.query(GroupMember).filter(GroupMember.members_group == current_user.group,
                                                      GroupMember.member != current_user.id).all()
    group_members_new = []
    for row in group_members:
        group_members_new.append(db_sess.query(User).get(row.member))

    return render_template('members.html', members=group_members_new, is_admin=is_admin)




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
    groups = db_sess.query(GroupMember).filter(GroupMember.member == current_user.id).all()
    for row in groups:
        group = db_sess.query(Group).filter(Group.id == row.members_group).first()
        admin = db_sess.query(User).get(group.group_admin).login
        if not group.description:
            group.description = 'None'
        cor = (group.group_name, admin, group.description)
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


@app.route('/create_task/<email>', methods=['GET', 'POST'])
@login_required
def create_task(email):
    form = TaskForm()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == email).first()
    group = db_sess.query(Group).filter(Group.id == current_user.group).first()
    admin = db_sess.query(User).get(group.group_admin)
    is_admin = False
    if current_user.id == admin.id:
        is_admin = True
    form.login.data = user.login

    if form.validate_on_submit():
        task = Task(
            author_id=admin.id,
            user_id=user.id,
            group_id=group.id,
            short_task=form.short_task.data,
            detail_task=form.detail_task.data,
            completed=form.completed.data
        )
        db_sess.add(task)
        db_sess.commit()

        return redirect(f'/member/{user.id}')
    return render_template('task.html', title='Постановка задачи', form=form, is_admin=is_admin)


@app.route('/my_tasks', methods=['GET', 'POST'])
@login_required
def my_tasks():
    db_sess = db_session.create_session()
    task_list = []
    tasks = db_sess.query(Task).filter(Task.user_id == current_user.id).all()
    if tasks:
        for row in tasks:
            group = db_sess.query(Group).get(row.group_id).group_name
            author = db_sess.query(User).get(row.author_id).login
            short_task = row.short_task
            detail_task = row.detail_task
            completed = row.completed
            if completed:
                completed = 'Задача выполнена'
            else:
                completed = 'Задача не выполнена'
            cor = (group, author, short_task, detail_task, completed)
            task_list.append(cor)
        return render_template('my_tasks.html', tasks=task_list)
    return render_template('my_tasks.html', message='У вас нет задач')


def init_db():
    db_sess = db_session.create_session()
    if db_sess.query(User).count() == 0:
        # 1 Группа
        group = Group(
            group_name="Цветоводы",
            description="Начальная инициализация"
        )
        db_sess.add(group)
        db_sess.commit()
        user = User(
            login="Володя",
            group=group.id,
            email="vlad@mail.ru"
        )
        user.set_password("1")
        db_sess.add(user)
        db_sess.commit()
        group.group_admin = user.id
        grop_member = GroupMember(
            member=user.id,
            members_group=group.id
        )
        db_sess.add(grop_member)
        db_sess.commit()
        user = User(
            login="Петя",
            group=group.id,
            email="peter@mail.ru"
        )
        user.set_password("1")
        db_sess.add(user)
        db_sess.commit()
        grop_member = GroupMember(
            member=user.id,
            members_group=group.id
        )
        db_sess.add(grop_member)
        db_sess.commit()
        user = User(
            login="Антон",
            group=group.id,
            email="anton@mail.ru"
        )
        user.set_password("1")
        db_sess.add(user)
        db_sess.commit()
        grop_member = GroupMember(
            member=user.id,
            members_group=group.id
        )
        db_sess.add(grop_member)
        db_sess.commit()

        # 2 Группа
        group = Group(
            group_name="Строители",
            description="Начальная инициализация"
        )
        db_sess.add(group)
        db_sess.commit()
        user = User(
            login="Влад",
            group=group.id,
            email="vlad1@mail.ru"
            )
        user.set_password("1")
        db_sess.add(user)
        db_sess.commit()
        group.group_admin = user.id
        grop_member = GroupMember(
            member=user.id,
            members_group=group.id
        )
        db_sess.add(grop_member)
        db_sess.commit()
        user = User(
            login="Евгений",
            group=group.id,
            email="evgeh@mail.ru"
        )
        user.set_password("1")
        db_sess.add(user)
        db_sess.commit()
        grop_member = GroupMember(
            member=user.id,
            members_group=group.id
        )
        db_sess.add(grop_member)
        db_sess.commit()

        # 3 Группа
        group = Group(
            group_name="Водители",
            description="Начальная инициализация"
        )
        db_sess.add(group)
        db_sess.commit()
        user = User(
            login="Андрей",
            group=group.id,
            email="andrey@mail.ru"
        )
        user.set_password("1")
        db_sess.add(user)
        db_sess.commit()
        group.group_admin = user.id
        grop_member = GroupMember(
            member=user.id,
            members_group=group.id
        )
        db_sess.add(grop_member)
        db_sess.commit()
        user = User(
            login="Иван",
            group=group.id,
            email="ivan@mail.ru"
        )
        user.set_password("1")
        db_sess.add(user)
        db_sess.commit()
        grop_member = GroupMember(
            member=user.id,
            members_group=group.id
        )
        db_sess.add(grop_member)
        db_sess.commit()
        user = User(
            login="Саша",
            group=group.id,
            email="alex@mail.ru"
        )
        user.set_password("1")
        db_sess.add(user)
        db_sess.commit()
        grop_member = GroupMember(
            member=user.id,
            members_group=group.id
        )
        db_sess.add(grop_member)
        db_sess.commit()

        a = [('Петро', 'peter11@mail.ru', '1'), ('Андрюха', 'andrey1@mail.ru', '1'), ('Илья', 'm0nesy@mail.ru', '1'),
             ('Ян', 'yan@mail.ru', '1'), ('Solo', 'solo@mail.ru', '1'), ('Pugh', 'pugh@mail.ru', '1'),
             ('Понтий', 'pon@mail.ru', '2'), ('Евграфий', 'evgf@mail.ru', '2'), ('Ростик', 'rost@mail.ru', '2'),
             ('Анатолий', 'art@mail.ru', '2'), ('Арут', 'money@mail.ru', '2'), ('Вова', 'world@mail.ru', '2'),
             ('Олег', 'oleg@mail.ru', '3'), ('Владлен', 'inst@mail.ru', '3'), ('Ярик', 'omg@mail.ru', '3'),
             ('Дима', 'medved@mail.ru', '3'), ('Артём', 'artem@mail.ru', '3'), ('Саня', 'karto@mail.ru', '3')]
        for i in a:
            user = User(
                login=i[0],
                group=i[2],
                email=i[1]
            )
            user.set_password("1")
            db_sess.add(user)
            db_sess.commit()
            for j in range(1, 4):
                grop_member = GroupMember(
                    member=user.id,
                    members_group=j
                )
                db_sess.add(grop_member)
                db_sess.commit()
        task_list = [(2, 1, 1, 'Посадить розу'), (3, 1, 1, 'Посадить одуванчик'), (9, 1, 1, 'Посадить фиалку'),
                     (10, 1, 1, 'Посадить арбуз'), (11, 1, 1, 'Посадить кактус'), (12, 1, 1, 'Посадить пальму'),
                     (5, 4, 2, 'Посадить розу'), (15, 4, 2, 'Посадить одуванчик'), (16, 4, 1, 'Посадить фиалку'),
                     (17, 4, 2, 'Посадить арбуз'), (18, 4, 2, 'Посадить кактус'), (19, 4, 2, 'Посадить пальму'),
                     (5, 4, 2, 'Построить дом'), (15, 4, 2, 'Построить сарай'), (16, 4, 2, 'Построить ферму'),
                     (17, 4, 2, 'Построить башню'), (18, 4, 2, 'Построить замок'), (19, 4, 2, 'Построить мост'),
                     (7, 6, 3, 'Построить дом'), (8, 6, 3, 'Построить сарай'), (21, 6, 3, 'Построить ферму'),
                     (22, 6, 3, 'Построить башню'), (23, 6, 3, 'Построить замок'), (9, 1, 1, 'Построить мост'),
                     (2, 1, 1, 'Поехать домой'), (3, 1, 1, 'Поехать на Невский проспект'),
                     (21, 6, 3, 'Поехать в больницу'), (10, 1, 1, 'Поехать в гостиницу'),
                     (11, 1, 1, 'Поехать в магазин'), (12, 1, 1, 'Поехать в синагогу'),
                     (7, 6, 3, 'Поехать домой'), (8, 6, 3, 'Поехать на Невский проспект'), (21, 6, 3,
                                                                                            'Поехать в больницу'),
                     (22, 6, 3, 'Поехать в гостиницу'), (23, 6, 3, 'Поехать в магазин'), (24, 6, 3,
                                                                                          'Поехать в синагогу')]
        for i in task_list:
            task = Task(
                user_id=i[0],
                author_id=i[1],
                group_id=i[2],
                short_task=i[3],
                detail_task=i[3]
            )
            db_sess.add(task)
            db_sess.commit()
def main():
    db_session.global_init("db/db.db")
    init_db()
    app.run()

if __name__ == '__main__':
    main()
