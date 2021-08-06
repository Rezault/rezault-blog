from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Post, User, Comment
from . import db
from .lists import admins, developers
import requests

views = Blueprint("views", __name__)

@views.route("/")
@views.route("/home")
@login_required
def home():
    if current_user.username in admins:
        if current_user.admin == False:
            current_user.admin = True
            db.session.commit()

    if current_user.username in developers:
        if current_user.developer == False:
            current_user.developer = True
            db.session.commit()

    posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)

@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get("text")

        if not text:
            flash("Post cannot be empty.", category="error")
        else:
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash("Post created!", category="success")
            return redirect(url_for("views.home"))

    return render_template("create_post.html", user=current_user)

@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category="error")
    elif developers[current_user.id]:
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted", category="success")
    elif current_user.id != post.user.id:
        flash("You do not have permission to delete this post.", category="error")
    else:
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted.", category="success")

    return redirect(url_for("views.home"))

@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash("Comment does not exist.", category="error")
    elif developers[current_user.id]:
        db.session.delete(comment)
        db.session.commit()
        flash("Comment deleted.", category="success")
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash("You do not have permission to delete this comment.", category="error")
    else:
        db.session.delete(comment)
        db.session.commit()
        flash("Comment deleted.", category="success")

    return redirect(url_for("views.home"))

@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash("User does not exist.", category="error")
        return redirect(url_for("views.home"))

    posts = user.posts
    return render_template("posts.html", user=user, posts=posts, username=username)

@views.route("/create-comment/<post_id>", methods=["POST"])
@login_required
def create_comment(post_id):
    text = request.form.get("text")

    if not text:
        flash("Comment cannot be empty.", category="error")
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash("Post doesn't exist.", category="error")

    return redirect(url_for("views.home"))

@views.route("/profiles/<id>")
@login_required
def user_profile(id):
    user = User.query.filter_by(id=id).first()

    if not user:
        flash("User does not exist.", category="error")
        return redirect(url_for("views.home"))

    return render_template("profiles.html", current_user=current_user, user=user, posts=posts)

@views.route("/edit-profile")
@login_required
def edit_profile():
    return render_template("edit-profile.html", user=current_user)

@views.route("/change-profile-picture", methods=['GET', 'POST'])
@login_required
def change_profile_picture():
    if request.method == "POST":
        url = request.form["url"]

        if not url:
            flash("URL cannot be empty.", category="error")
        else:
            image_formats = ("image/png", "image/jpeg", "image/jpg")
            r = requests.head(url)
            if r.headers["content-type"] in image_formats:
                flash("Profile Picture successfuly changed!", category="success")
                current_user.profile_picture = url
                db.session.commit()
            else:
                flash("Picture URL not valid.", category="error")

    return render_template("edit-profile.html", user=current_user)

@views.route("/users")
@login_required
def users():
    users = User.query.all()
    return render_template("users.html", user=current_user, users=users)

@views.route("/admin-panel")
@login_required
def admin_panel():
    if current_user.admin == False or current_user.developer == False:
        flash("You do not have permission to do that.", category="error")
        redirect(url_for(views.home))
    
    return render_template("admin-panel.html", user=current_user)
