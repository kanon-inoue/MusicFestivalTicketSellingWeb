from flask import Blueprint
from flask import render_template, request, redirect, send_from_directory

bp = Blueprint('main', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@bp.route('/eventCreation', methods=['GET', 'POST'])
def index():
    return render_template('eventCreation.html')

@bp.route('/eventDetail', methods=['GET', 'POST'])
def index():
    return render_template('eventDetail.html')
