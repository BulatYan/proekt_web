from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class Create_GroupForm(FlaskForm):
    group = StringField('Название группы', validators=[DataRequired()])
    description = StringField('Описание группы')
    submit = SubmitField('Создать группу')



