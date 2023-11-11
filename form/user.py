from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, BooleanField, TextAreaField
from wtforms.validators import DataRequired


#Создаем класс RegisterForm
class RegisterForm(FlaskForm):
    group = StringField('Название группы', validators=[DataRequired()])
    login = StringField('Имя пользователя', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторить пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


#Создаем класс LoginForm
class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


#Создаем класс MemberForm
class MemberForm(FlaskForm):
    login = StringField('Имя пользователя', render_kw={'readonly': True}, validators=[DataRequired()])
    email = EmailField('Почта', render_kw={'readonly': True}, validators=[DataRequired()])
    is_admin = BooleanField('Является администратором')


#Создаем класс ProfileForm
class ProfileForm(FlaskForm):
    group = StringField('Название группы', validators=[DataRequired()])
    login = StringField('Имя пользователя', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль')
    password_again = PasswordField('Повторить пароль')
    submit = SubmitField('Изменить')
    cancel = SubmitField('Отменить')


class InviteForm(FlaskForm):
    group = StringField('Название группы', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    submit = SubmitField('Создать')
    cancel = SubmitField('Отменить')

class MessageForm(FlaskForm):
    message = StringField('Сообщение')
    message_head = StringField('Сообщение')


class TaskForm(FlaskForm):
    login = StringField('Имя пользователя',render_kw={'readonly': True}, validators=[DataRequired()])
    short_task = StringField('Краткое описание', validators=[DataRequired()])
    detail_task = TextAreaField('Детальное описание', validators=[DataRequired()])
    completed = BooleanField('Задача завершена')
    submit = SubmitField('Создать')
