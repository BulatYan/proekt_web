from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class Create_GroupForm(FlaskForm):
    group = StringField('Название группы', validators=[DataRequired()])
    description = StringField('Описание группы')
    submit = SubmitField('Создать группу')
    cancel = SubmitField('Отменить')


class Leave_Group(FlaskForm):
    group_old = StringField('Название старой группы', validators=[DataRequired()])
    group_new =  SelectField('Название новой группы', choices=[], coerce=int, validate_choice=False)
    submit = SubmitField('Покинуть группу')
    cancel = SubmitField('Отменить')



