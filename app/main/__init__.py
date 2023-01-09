from flask import Blueprint
from app import models

bp = Blueprint('main', __name__)

from app.main import routes
