import sys
import importlib
importlib.reload(sys)

from urllib import parse

from flask import jsonify, redirect, url_for, abort, request, render_template

from sqlalchemy import or_
from syzoj import oj, controller
from syzoj.models import User, Problem, File, FileParser, Notice
from syzoj.controller import Paginate, Tools
from .common import need_login, not_have_permission, show_error


@oj.route("/problem")
def problem_set():
    query = Problem.query
    problem_title = request.args.get("problem_title")
    
    if request.args.get("problem_title"):
        query = query.filter(or_(Problem.title.like((u"%" + problem_title + u"%")), Problem.tags.like((u"%" + problem_title + u"%")), Problem.id.like((u"%" + problem_title + u"%"))))
    else:
        problem_title = ''

    def make_url(page, other):
        other["page"] = page
        return url_for("problem_set") + "?" + parse.urlencode(other)
        
    sorter = Paginate(query, make_url=make_url, other={"problem_title": problem_title},
            cur_page=request.args.get("page"), edge_display_num=50, per_page=50)
    return render_template("problem_set.html", tool=Tools, tab="problem_set", sorter=sorter, problems=sorter.get(), problem_title=problem_title)


@oj.route("/problem/<int:problem_id>")
def problem(problem_id):
    user = User.get_cur_user()

    problem = Problem.query.filter_by(id=problem_id).first()
    if not problem:
        abort(404)

    if problem.is_allowed_use(user) is False:
        return not_have_permission()

    return render_template("problem.html", tool=Tools, tab="problem_set", problem=problem)


@oj.route("/problem/<int:problem_id>/edit", methods=["GET", "POST"])
def edit_problem(problem_id):
    user = User.get_cur_user()
    if not user:
        return need_login()

    problem = Problem.query.filter_by(id=problem_id).first()
    if problem and problem.is_allowed_edit(user) == False:
        return not_have_permission()

    if request.method == "POST":
        if not problem:
            problem_id = controller.create_problem(user=user, title=request.form.get("title"))
            problem = Problem.query.filter_by(id=problem_id).first()
        problem.update(title=request.form.get("title"),
                       description=request.form.get("description"),
                       input_format=request.form.get("input_format"),
                       output_format=request.form.get("output_format"),
                       example=request.form.get("example"),
                       tags=request.form.get("tags") ,
                       limit_and_hint=request.form.get("limit_and_hint"))

        problem.save()

        return redirect(url_for("problem", problem_id=problem.id))
    else:
        return render_template("edit_problem.html", tool=Tools, problem=problem)


@oj.route("/problem/<int:problem_id>/star")
def star_problem(problem_id):
    user = User.get_cur_user()
    problem = Problem.query.filter_by(id=problem_id).first()
    if not problem:
        abort(404)
    problem.stared.append(user)
    problem.save()
    return redirect(url_for("problem", problem_id=problem_id))


@oj.route("/problem/<int:problem_id>/unstar")
def unstar_problem(problem_id):
    user = User.get_cur_user()
    problem = Problem.query.filter_by(id=problem_id).first()
    if not problem:
        abort(404)
    problem.stared.remove(user)
    problem.save()
    return redirect(url_for("problem", problem_id=problem_id))


@oj.route("/problem/<int:problem_id>/upload", methods=["GET", "POST"])
def upload_testdata(problem_id):
    user = User.get_cur_user()
    if not user:
        return need_login()

    problem = Problem.query.filter_by(id=problem_id).first()
    if not problem:
        abort(404)
    if problem.is_allowed_edit(user) is False:
        return not_have_permission()
    if request.method == "POST":
        file = request.files.get("testdata")
        if file:
            problem.update_testdata(file)
        if request.form.get("time_limit"):
            problem.time_limit = int(request.form.get("time_limit"))
        if request.form.get("memory_limit"):
            problem.memory_limit = int(request.form.get("memory_limit"))
        problem.save()
        return redirect(url_for("upload_testdata", problem_id=problem_id))
    else:
        return render_template("upload_testdata.html", tool=Tools, problem=problem, parse=FileParser.parse_as_testdata)


# TODO:Maybe need add the metho of toggle is_public attr to Problem
@oj.route("/api/problem/<int:problem_id>/public", methods=["POST", "DELETE"])
def change_public_attr(problem_id):
    session_id = request.args.get('session_id')
    user = User.get_cur_user(session_id=session_id)
    problem = Problem.query.filter_by(id=problem_id).first()
    if problem and user and user.have_privilege(2):
        if request.method == "POST":
            problem.is_public = True
        elif request.method == "DELETE":
            problem.is_public = False
        problem.save()
    else:
        abort(404)
    return jsonify({"status": 0})
