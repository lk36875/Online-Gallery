from modules.models import GalleryModel
from flask import Blueprint, render_template, request, redirect, url_for, send_file, session, flash
from .api_operations import Gallery, PictureObject, FileTransfer
from threading import Thread
from . import db

routes = Blueprint('routes', __name__)


@routes.route('/')
def home():
    """ Redirects to welcome function """
    return redirect(url_for('routes.welcome'))


@routes.route('/welcome')
def welcome():
    """ Renders welcome template """
    return render_template('welcome.html')


@routes.route('/about')
def about():
    """ Renders about template """
    return render_template('about.html')


@routes.route('/gallery', methods=['POST', 'GET'])
def gallery():
    """
    Redirects to gallery if requested by post method.
    Otherwise renders gallery, with images if one was already created.

    """

    if request.method == 'POST':
        search = request.form['search']
        number_of_images = request.form['search-number']
        return redirect(f'/generate-gallery/{search}/{number_of_images}')

    elif session.get('gallery_id'):
        try:
            unpickled_gallery = FileTransfer.unpickle_gallery()
            return render_template('gallery.html', images=unpickled_gallery.get_picture_objects())
        except:
            return render_template('gallery.html')

    else:
        return render_template('gallery.html')


@routes.route('/generate-gallery/<search>/<int:number_of_images>', methods=['GET'])
def generate_gallery(search, number_of_images):
    """
    Generates gallery using threads in order to reduce time user has to wait for requests.
    Adds gallery id to session variable in order to know which gallery belong to user.

    """

    if request.method == 'GET':
        search.replace('%20', ' ')
        gallery = Gallery([])

        def get_picture(number_of_picture):
            image = PictureObject(number_of_picture, search)
            gallery.add_picture(image)

        threads = []
        for i in range(number_of_images):
            threads.append(Thread(target=get_picture, args=(i,)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        clear_db()
        session['gallery_id'] = FileTransfer.make_gallery_model_object(gallery)
        unpickled_gallery = FileTransfer.unpickle_gallery()

        return render_template('gallery.html', images=unpickled_gallery.get_picture_objects(), number_of_images=number_of_images)


@routes.route('/apply-changes', methods=['POST'])
def apply_changes():
    """
    Applies changes requested by user. Picture index variable makes sure to keep track with
    images id, that changes when picture is deleted.

    """
    if request.method == 'POST':
        gallery = FileTransfer.unpickle_gallery()
        pictures = gallery.get_picture_objects()

        picture_index = -1
        for i in range(len(pictures)):
            picture_index += 1  # this index makes sure delete function does not distrub this loop
            form_number = i + 1  # images on website are indexed 1 number higher
            blur = request.form[f"blur{form_number}"]
            brightness = request.form[f"brightness{form_number}"]
            transpose = request.form.get(f"transpose{form_number}")
            delete = request.form.get(f"delete{form_number}")
            if blur != '':
                pictures[picture_index].change_blur(int(blur))
            if brightness != '':
                pictures[picture_index].change_brightness(
                    float(brightness.replace(',', '.')))
            if transpose is not None:
                pictures[picture_index].transpose()
            if delete is not None:
                gallery.delete_picture(picture_index)
                picture_index -= 1

        clear_db()
        session['gallery_id'] = FileTransfer.make_gallery_model_object(gallery)
        return render_template('gallery.html', images=gallery.get_picture_objects())


@routes.route('/download-gallery', methods=['POST'])
def download_gallery():
    """ Downloads gallery using zipfile and io libraries. """

    if request.method == 'POST':
        try:
            gallery = FileTransfer.unpickle_gallery()
            if gallery.get_picture_objects() == []:
                raise Exception()
            zip_file_bytes_io = gallery.save_gallery()
            return send_file(zip_file_bytes_io, mimetype='application/zip', as_attachment=True, download_name='gallery.zip')
        except:
            flash('There was problem downloading your gallery')
            return redirect('/gallery')


@routes.route('/display-image/<int:id>')
def display_image(id):
    """ Displays larger image in new tab. """
    gallery = FileTransfer.unpickle_gallery()
    image = gallery.get_picture_objects()[id-1].get_bytes_picture()
    return render_template('display_image.html', image=image)


@routes.route('/collage/<int:collage_style_number>', methods=['POST'])
def collage(collage_style_number):
    """ Renders collage from picked images """

    collage_length = {1: 6,
                      2: 9,
                      3: 5,
                      }

    if request.method == 'POST':
        try:
            gallery = FileTransfer.unpickle_gallery()
            pictures = gallery.get_picture_objects()
            acceptable_indexes = [str(index)
                                  for index, image in enumerate(pictures, 1)]
            index_list = request.form[f"collage{collage_style_number}"].split()

            for index in index_list:
                if index not in acceptable_indexes:
                    flash('Indexes of images are not in range!')
                    return render_template('gallery.html', images=gallery.get_picture_objects(), number_of_images=len(pictures))

            if len(index_list) != collage_length[collage_style_number]:
                flash('Wrong number of images!')
                return render_template('gallery.html', images=gallery.get_picture_objects(), number_of_images=len(pictures))

            collage_gallery = Gallery([pictures[int(i)-1] for i in index_list])
            session[f'collage{collage_style_number}_id'] = FileTransfer.make_gallery_model_object(
                collage_gallery)
            return render_template('collage.html', images=collage_gallery.get_picture_objects(), collage_style_number=collage_style_number)

        except:
            flash('There was problem with collage. Make sure to generate gallery first!')
            return redirect('/gallery')


def clear_db():
    """
    Deletes latest model, it is not covering all cases in order to allow multiple users to use application,
    but reduces frequency of clearing database
    """
    if session.get('gallery_id'):
        try:
            GalleryModel.query.filter(
                GalleryModel.id == session['gallery_id']).delete()
            db.session.commit()
        except:
            print('Model does not exist')
