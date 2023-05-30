from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, BooleanField
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
    har01 = BooleanField('Самодостаточность')
    har02 = BooleanField('Честность')
    har03 = BooleanField('Бесстрашие')
    har04 = BooleanField('Доверие')
    har05 = BooleanField('Заинтересованность')
    har06 = BooleanField('Дружелюбие')
    har07 = BooleanField('Чувствительность')
    har08 = BooleanField('Поддержка')
    har09 = BooleanField('Верность')
    har10 = BooleanField('Чувство юмора')
    har11 = BooleanField('Оптимизм')
    har12 = BooleanField('Терпение')
    har13 = BooleanField('Доброта')
    submit = SubmitField('Сохранить')

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

