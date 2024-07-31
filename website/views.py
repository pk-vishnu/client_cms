from flask import Blueprint, render_template,request, flash,redirect,url_for, jsonify, abort, send_file,session
from flask_login import login_required, current_user
import datetime
import markdown2
from . import db
from .models import Product, ProductImage, Description
from .models import Images
from .descriptionBot import generate_marketing_content
import uuid
import io 
from .models import Blogger
from .models import VerifiedBlog
from bleach import clean

views = Blueprint('views', __name__)
import time 
@views.route('/')
def home():
    return render_template("home.html",user = current_user)

@views.route('/create', methods=['GET', 'POST'])
@login_required
def blogPost():
    if request.method == 'POST':
        prompt = request.form['prompt']
        blogger_entry = Blogger.query.filter_by(prompt=prompt).first()
        
        if blogger_entry:
            response = blogger_entry.response_list
            time.sleep(3)  # Simulate processing time
            return render_template("blog.html", user=current_user, res=response)
        else:
            flash("No responses found for the given prompt.", category='error')
            return redirect(url_for('views.blogPost'))
    return render_template("create.html", user=current_user)

@views.route('/loading')
@login_required
def loading_screen():
    response = session.pop('response', None)
    return render_template("blog.html", user=current_user, res=response)


@views.route('/verify', methods=['POST'])
def verify_content():
    content = request.json.get('content')
    if content:
        new_blog = VerifiedBlog(content=content)
        db.session.add(new_blog)
        db.session.commit()
        flash("Blog post verified!", category='success')
        return redirect(url_for('views.blogPost'))
    return jsonify({"message": "No content provided"}), 400


@views.route('/blogs', methods=['GET'])
def list_blogs():
    blogs = VerifiedBlog.query.all()
    sanitized_blogs = [clean(blog.content, tags=['p', 'a', 'b', 'i', 'u'], attributes={'a': ['href']}) for blog in blogs]
    return render_template('preview_blogs.html',blogs=blogs)

@views.route('/blog/<int:blog_id>', methods=['GET'])
def view_blog(blog_id):
    blog = VerifiedBlog.query.get_or_404(blog_id)
    return render_template('view_blog.html', blog=blog)



# @views.route('/create',methods=['GET','POST'])
# def blogPost():
#     if request.method=='POST':
#         title=request.form['title']
#         author=request.form['author']
#         thumbnail=request.form['thumbnail']
#         md_content=request.form['content']
#         date_created=datetime.datetime.now()
#         html_content = markdown2.markdown(md_content)
#         blog_post = BlogPost(title=title,
#                         content_md=md_content,
#                         content_html=html_content,
#                         thumbnail=thumbnail,
#                         author=author,
#                         date_created=date_created)
#         db.session.add(blog_post)
#         db.session.commit()
#         flash("Blog Post Created!",category='success')
#         return redirect(url_for('views.home'))

    return render_template("create.html", user=current_user, response=response)

#     return render_template("create.html",user=current_user)

# @views.route('/blog/<int:id>', methods=['GET'])
# def get_blog(id):
#     try:
#         blog_post = BlogPost.query.get(id)
#         if not blog_post:
#             abort(404, description="Blog post not found")
        
#         response = {
#             'id': blog_post.id,
#             'title': blog_post.title,
#             'author': blog_post.author,
#             'thumbnail': blog_post.thumbnail,
#             'content': blog_post.content_html,
#             'date_created': blog_post.date_created
#         }
#         return jsonify(response), 200
#     except Exception as e:
#         print(f"Error retrieving blog post: {e}")
#         abort(500, description="Internal server error")

# @views.route('/manage',methods=['GET'])
# @login_required
# def manage():
#     posts = BlogPost.query.order_by(BlogPost.id.desc()).all()
#     return render_template("manage.html",user=current_user,posts=posts)


# @views.route('view/<int:id>',methods=['GET'])
# @login_required
# def view_post(id):
#     try:
#         blog_post = BlogPost.query.get(id)
#         if not blog_post:
#             abort(404, description="Blog post not found")
        
#         response = {
#             'id': blog_post.id,
#             'title': blog_post.title,
#             'author': blog_post.author,
#             'thumbnail': blog_post.thumbnail,
#             'content': blog_post.content_html,
#             'date_created': blog_post.date_created
#         }
#         return render_template("blog.html",user=current_user,res=response)
#     except Exception as e:
#         print(f"Error retrieving blog post: {e}")
#         abort(500, description="Internal server error")


# @views.route('/delete/<int:id>',methods=['GET'])
# @login_required
# def delete(id):
#     post = BlogPost.query.get(id)
#     db.session.delete(post)
#     db.session.commit()
#     flash("Blog Post Deleted!",category='success')
#     return redirect(url_for('views.manage'))

# @views.route('/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
# def updateBlog(id):
#     blog_post = BlogPost.query.get_or_404(id)
#     if request.method == 'POST':
#         blog_post.title = request.form['title']
#         blog_post.author = request.form['author']
#         blog_post.thumbnail = request.form['thumbnail']
#         blog_post.content_md = request.form['content']
#         blog_post.content_html = markdown2.markdown(blog_post.content_md)
#         blog_post.date_created = datetime.datetime.now()

#         db.session.commit()
#         flash("Blog Post Updated!", category='success')
#         return redirect(url_for('views.manage'))

#     return render_template("update.html", blog_post=blog_post, user=current_user)

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

# @views.route('/image/<image_uuid>', methods=['GET'])
# def get_image(image_uuid):
#     image = Images.query.filter_by(url=url_for('views.get_image', image_uuid=image_uuid, _external=True)).first_or_404()

#     return send_file(
#         io.BytesIO(image.image_data),
#         mimetype='image/jpeg', 
#         as_attachment=False,
#     )

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


@views.route('/create-product', methods=['GET', 'POST'])
def create_product():
    md_content = ''
    if request.method == 'POST':
        try:
            print("Form Submitted")  
            title = request.form.get('title')
            md_content = request.form.get('content')
            print(f"Received data - Title: {title}, Content: {md_content}")  
            date_created = datetime.datetime.now()

            product = Product(
                title=title,
                content_md=md_content,
                date_created=date_created
            )

            db.session.add(product)
            db.session.commit()

            image_files = request.files.getlist('images')
            for image_file in image_files:
                image_data = image_file.read()
                image_uuid = str(uuid.uuid4())
                image_url = url_for('views.get_image', image_uuid=image_uuid, _external=True)
                product_image = ProductImage(
                    product_id=product.id,
                    image_name=image_file.filename,
                    image_data=image_data,
                    url=image_url
                )
                db.session.add(product_image)

            db.session.commit()
            flash("Product Created!", category='success')
            return redirect(url_for('views.home'))

        except KeyError as e:
            flash(f"Missing form field: {e.args[0]}", category='error')
            return redirect(url_for('views.create_product'))
        except Exception as e:
            print(f"Error: {e}")  # Debugging statement
            flash(f"An error occurred: {e}", category='error')
            return redirect(url_for('views.create_product'))

    return render_template("create_product.html", user=current_user, md_content= md_content, generate_marketing_content = generate_marketing_content )

@views.route('/image/<image_uuid>', methods=['GET'])
def get_image(image_uuid):
    image = ProductImage.query.filter_by(url=url_for('views.get_image', image_uuid=image_uuid, _external=True)).first_or_404()
    return send_file(
        io.BytesIO(image.image_data),
        mimetype='image/jpeg',
        as_attachment=False,
    )

@views.route('/product/<int:id>', methods=['GET'])
def view_product(id):
    product = Product.query.get_or_404(id)
    images = ProductImage.query.filter_by(product_id=product.id).all()
    return render_template("product.html", product=product, images=images, user=current_user)
# @views.route('/product/<int:id>', methods=['GET'])
# def view_product(id):
#     product = Product.query.get_or_404(id)
#     images = ProductImage.query.filter_by(product_id=id).all()
#     response = {
#         'id': product.id,
#         'title': product.title,
#         'author': product.author,
#         'content': product.content_html,
#         'date_created': product.date_created,
#         'images': [{'id': img.id, 'url': img.url} for img in images]
#     }
#     return render_template("product.html", user=current_user, product=response)

@views.route('/generateDescription',methods=['GET','POST'])
def generateDescription():
    description= ''
    content = ''
    if request.method=='POST':
        content=request.form['content']
        desc = generate_marketing_content(content)
        desc_content = desc.split("!!!!!")
        description = desc_content[1]
        session['content'] = content
        session['description'] = description
    return render_template("create.html",user=current_user, description = description, content = content)

@views.route('/createDesc',methods=['GET','POST'])
def createDesc():
    prompt = session.get('content')
    desc = session.get('description')
    newDesc = Description(content = prompt,description = desc)
    db.session.add(newDesc)
    db.session.commit()
    return redirect(url_for('views.generateDescription'))

@views.route('/generate-marketing-content', methods=['POST'])
def generate_marketing_content_route():
    try:
        content = request.json.get('content')
        if not content:
            return jsonify({"error": "Content is required"}), 400
        
        generated_content = generate_marketing_content(content)
        desc = generated_content.split('!!!!!')
        final_content = desc[1]
        return jsonify({"generatedContent": final_content}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@views.route('/product')
@login_required
def product():
    return render_template("product.html",user=current_user)

@views.route('/preview_site')
@login_required
def preview_site():
    return render_template("preview_home.html",user=current_user)

@views.route('/preview_products')
@login_required
def preview_products():
    return render_template("preview_products.html",user=current_user)


