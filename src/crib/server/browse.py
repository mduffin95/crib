"""
Browser for properties
"""
from flask import Blueprint, render_template

from crib.server.auth import login_required

bp = Blueprint("browse", __name__)


@bp.route("/", methods=("GET",))
@login_required
def view():
    return render_template("browse/view.html")
