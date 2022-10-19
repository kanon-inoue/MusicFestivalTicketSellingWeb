from flask import Blueprint
from flask import render_template, request, redirect, send_from_directory

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return render_template('index.html')
    ##render_template
