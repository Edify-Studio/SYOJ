import sys
import importlib
importlib.reload(sys)
import time

from flask import request, render_template
from urllib import parse
from syzoj import oj,db
from syzoj.models import User, Notice
from syzoj.controller import Tools, Paginate
from .session import sign_up, login
from .problem import problem, problem_set
from .judge import submit_code, judge_state
from .user import user, edit_user
from .discussion import edit_article, article, discussion
from .contest import contest_list
from syzoj.models import User, Problem, File, FileParser
from sqlalchemy import or_
from syzoj.controller import Paginate, Tools
from .common import need_login, not_have_permission, show_error
from flask import jsonify, redirect, url_for, abort, request, render_template


@oj.route("/")
def index():
    query = Problem.query.order_by(Problem.time_limit)
    problem_title = request.args.get("problem_title")
    notice = Notice.query.all()
    if request.args.get("problem_title"):
        query = query.filter(
            or_(Problem.title.like((u"%" + problem_title + u"%")), Problem.tags.like((u"%" + problem_title + u"%")),
                Problem.id.like((u"%" + problem_title + u"%"))))
    else:
        problem_title = ''

    def make_url(page, other):
        other["page"] = page
        return url_for("problem_set") + "?" + parse.urlencode(other)

    return render_template("index.html", tool=Tools, tab="home", problems=query, notice=notice)


@oj.route("/info")
def info():
    query = User.query.order_by(db.desc(User.ac_num))
    notice = Notice.query.all()
    ranker = Paginate(query, cur_page=1,  per_page=10)
    return render_template("info.html", tool=Tools, tab="info", notice=notice, ranker=ranker)


@oj.route("/error")
def error():
    info = request.args.get("info")
    next = request.args.get("next")
    # TODO:rewrite error page for beautiful
    return render_template("error_info.html", tool=Tools, info=info, next=next)


@oj.route("/info/<int:notice_id>/edit", methods=["GET", "POST"])
def edit_notice(notice_id):
    user = User.get_cur_user()
    if not user:
        return need_login()
    notice = Notice.query.filter_by(id=notice_id).first()
    try:
        if notice and not notice.is_allowed_edit(user):
            return not_have_permission()
        elif not (user.have_privilege(4) or user.have_privilege(
        )):
            return not_have_permission()
        else:
            return not_have_permission()
    except:
        return not_have_permission()
    
    if request.method == "POST":
        if request.form.get("title") == "" or request.form.get("content") == "":
            return show_error("Please input title and content",
                              url_for("edit_notice", anotice_id=notice_id))
        if not notice:
            notice = Notice(title=request.form.get("title"), content=request.form.get("content"), user=user)

        notice.title = request.form.get("title")
        notice.content = request.form.get("content")
        notice.tags = request.form.get("tags")
        notice.update_time = time.time()
        notice.sort_time = time.time()
        notice.save()
        return redirect(url_for("info"))
    else:
        return render_template("edit_notice.html", tool=Tools, notice=notice, tab="notice")


@oj.route("/notice/<int:notice_id>")
def notice(notice_id):
    notice = Notice.query.filter_by(id=notice_id).first()
    if not notice:
        return show_error("找不到公告", url_for('index'))

    def make_url(page, other):
        return url_for("notice", notice_id=notice_id) + "?" + parse.urlencode({"page": page})

    return render_template("notice.html", tool=Tools, notice=notice, tab="info")


@oj.route("/notice/<int:notice_id>/delete")
def delete_notice(notice_id):
    user = User.get_cur_user()
    if not user:
        return need_login()
    notice = Notice.query.filter_by(id=notice_id).first()
    if notice and notice.is_allowed_edit(user) is False:
        return not_have_permission()
    notice.delete()
    return redirect(url_for("info"))
