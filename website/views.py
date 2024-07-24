from flask import Blueprint, render_template,request, flash,redirect,url_for, jsonify, abort, send_file
from flask_login import login_required, current_user
import datetime
import markdown2
from . import db
from .models import BlogPost
from .models import Images
import uuid
import io 

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html",user = current_user)

@views.route('/create',methods=['GET','POST'])
@login_required
def blogPost():
    if request.method=='POST':
        title=request.form['title']
        author=request.form['author']
        thumbnail=request.form['thumbnail']
        md_content=request.form['content']
        date_created=datetime.datetime.now()
        html_content = markdown2.markdown(md_content)
        blog_post = BlogPost(title=title,
                        content_md=md_content,
                        content_html=html_content,
                        thumbnail=thumbnail,
                        author=author,
                        date_created=date_created)
        db.session.add(blog_post)
        db.session.commit()
        flash("Blog Post Created!",category='success')
        return redirect(url_for('views.home'))

    return render_template("create.html",user=current_user)

@views.route('/blog/<int:id>', methods=['GET'])
def get_blog(id):
    try:
        blog_post = BlogPost.query.get(id)
        if not blog_post:
            abort(404, description="Blog post not found")
        
        response = {
            'id': blog_post.id,
            'title': blog_post.title,
            'author': blog_post.author,
            'thumbnail': blog_post.thumbnail,
            'content': blog_post.content_html,
            'date_created': blog_post.date_created
        }
        return jsonify(response), 200
    except Exception as e:
        print(f"Error retrieving blog post: {e}")
        abort(500, description="Internal server error")

@views.route('/manage',methods=['GET'])
@login_required
def manage():
    posts = BlogPost.query.order_by(BlogPost.id.desc()).all()
    return render_template("manage.html",user=current_user,posts=posts)


@views.route('view/<int:id>',methods=['GET'])
@login_required
def view_post(id):
    try:
        blog_post = BlogPost.query.get(id)
        if not blog_post:
            abort(404, description="Blog post not found")
        
        response = {
            'id': blog_post.id,
            'title': blog_post.title,
            'author': blog_post.author,
            'thumbnail': blog_post.thumbnail,
            'content': blog_post.content_html,
            'date_created': blog_post.date_created
        }
        return render_template("blog.html",user=current_user,res=response)
    except Exception as e:
        print(f"Error retrieving blog post: {e}")
        abort(500, description="Internal server error")


@views.route('/delete/<int:id>',methods=['GET'])
@login_required
def delete(id):
    post = BlogPost.query.get(id)
    db.session.delete(post)
    db.session.commit()
    flash("Blog Post Deleted!",category='success')
    return redirect(url_for('views.manage'))

@views.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def updateBlog(id):
    blog_post = BlogPost.query.get_or_404(id)
    if request.method == 'POST':
        blog_post.title = request.form['title']
        blog_post.author = request.form['author']
        blog_post.thumbnail = request.form['thumbnail']
        blog_post.content_md = request.form['content']
        blog_post.content_html = markdown2.markdown(blog_post.content_md)
        blog_post.date_created = datetime.datetime.now()

        db.session.commit()
        flash("Blog Post Updated!", category='success')
        return redirect(url_for('views.manage'))

    return render_template("update.html", blog_post=blog_post, user=current_user)

@views.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = file.filename
        image_data = file.read()
        image_uuid = str(uuid.uuid4())
        image_url = url_for('views.get_image', image_uuid=image_uuid, _external=True)
        new_image = Images(image_name=filename, image_data=image_data, url=image_url)
        db.session.add(new_image)
        db.session.commit()
        return jsonify({'url': image_url}), 201

@views.route('/image/<image_uuid>', methods=['GET'])
def get_image(image_uuid):
    image = Images.query.filter_by(url=url_for('views.get_image', image_uuid=image_uuid, _external=True)).first_or_404()

    return send_file(
        io.BytesIO(image.image_data),
        mimetype='image/jpeg', 
        as_attachment=False,
    )

@views.route('/asset-manager', methods=['GET'])
def asset_manager():
    images = Images.query.order_by(Images.id.desc()).all()
    return render_template('assets.html', images=images, user=current_user)

@views.route('/delete-image/<int:id>', methods=['GET'])
def delete_image(id):
    image = Images.query.get(id)
    db.session.delete(image)
    db.session.commit()
    flash("Image deleted!", category='success')
    return redirect(url_for('views.asset_manager'))