from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ExerciseForm(FlaskForm):
    id = IntegerField('Exercise ID')
    name = StringField('Exercise Name', validators=[DataRequired()])
    reps = IntegerField('Number of Repetitions', validators=[DataRequired(), NumberRange(min=1)])
    weight = IntegerField('Weight (kg)', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Exercise')

class WorkoutPlanForm(FlaskForm):
    plan_name = StringField('Workout Plan Name', validators=[DataRequired()])
    save_submit = SubmitField('Save Workout Plan')
    load_submit = SubmitField('Load Workout Plan')
    new_submit = SubmitField('Create')
    reset_submit = SubmitField('Reset Workout Plan')
    analyse_submit = SubmitField('Analyze Workout Plan')
