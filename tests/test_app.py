import pytest
from flask_testing import TestCase
import os
import sys
topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)
from modules import app, db
from modules.api_operations import Gallery, FileTransfer


class BaseTestCase(TestCase):
    """A base test case."""

    def create_app(self):
        app.config.from_object('config.TestConfig')
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class FlaskTestCase(BaseTestCase):

    def test_base(self):
        response = self.client.get('/', content_type='html/text')
        assert response.status_code == 302

    def test_route_base(self):
        response = self.client.get('/', follow_redirects=True)
        assert b'Welcome' in response.data

    def test_route_welcome(self):
        response = self.client.get('/welcome', content_type='html/text')
        assert response.status_code == 200
        assert b'Welcome' in response.data

    def test_route_about(self):
        response = self.client.get('/about', content_type='html/text')
        assert response.status_code == 200
        assert b'Gallery' in response.data

    def test_route_gallery(self):
        response = self.client.get('/gallery', content_type='html/text')
        assert response.status_code == 200
        assert b'There will be your gallery' in response.data

    def test_route_gallery_download_empty(self):
        response = self.client.get('/gallery', content_type='html/text')
        assert response.status_code == 200
        assert b'There will be your gallery' in response.data
        response2 = self.client.post('/download-gallery')
        assert response2.status_code == 302

    def test_route_generate_gallery(self):
        response = self.client.get('/gallery', content_type='html/text')
        assert response.status_code == 200
        assert b'There will be your gallery' in response.data
        response2 = self.client.post(
            '/gallery',
            data={'search': 'dogs', 'search-number': 2},
            follow_redirects=True
        )
        assert response2.status_code == 200
        assert b'Apply' in response2.data
        assert b'You can type more than one thing' in response2.data


    def test_route_generate_gallery_and_display_image(self):
        response = self.client.get('/gallery', content_type='html/text')
        assert response.status_code == 200
        assert b'There will be your gallery' in response.data
        response2 = self.client.post(
            '/gallery',
            data={'search': 'dogs', 'search-number': 2},
            follow_redirects=True
        )
        assert response2.status_code == 200
        assert b'Apply' in response2.data
        assert b'You can type more than one thing' in response2.data

        response3 = self.client.get(
            '/display-image/1', content_type='html/text')
        assert response3.status_code == 200

    def test_route_gallery_download(self):
        response = self.client.get('/gallery', content_type='html/text')
        assert response.status_code == 200
        assert b'There will be your gallery' in response.data
        response2 = self.client.get('/generate-gallery/dogs/4', )
        assert response2.status_code == 200
        assert b'There will be your gallery' not in response2.data
        response3 = self.client.post('/download-gallery')
        assert response3.status_code == 200

    def test_collage_input_wrong_number_of_images(self):
        response = self.client.get('/gallery', content_type='html/text')
        response2 = self.client.get('/generate-gallery/dogs/4', )
        response3 = self.client.post(
            '/collage/1',
            data={'collage1': '1'},
            follow_redirects=True
        )
        assert b'Wrong number of images' in response3.data
        response4 = self.client.post(
            '/collage/1',
            data={'collage1': '111'},
            follow_redirects=True
        )
        assert b'Indexes of images are not in range' in response4.data

    def test_collage_input_wrong_range(self):
        response = self.client.get('/gallery', content_type='html/text')
        response2 = self.client.get('/generate-gallery/dogs/4', )
        response3 = self.client.post(
            '/collage/1',
            data={'collage1': '111'},
            follow_redirects=True
        )
        assert b'Indexes of images are not in range' in response3.data

    def test_collage_input_too_much_images(self):
        response = self.client.get('/gallery', content_type='html/text')
        response2 = self.client.get('/generate-gallery/dogs/4', )
        response3 = self.client.post(
            '/collage/1',
            data={'collage1': '1 1 1 1 1  1 1 1 1 1 1 1  1 1 1 '},
            follow_redirects=True
        )
        assert b'Wrong number of images' in response3.data

    def test_collage1_proper_input(self):
        response = self.client.get('/gallery', content_type='html/text')
        response2 = self.client.get('/generate-gallery/dogs/7', )
        response3 = self.client.post(
            '/collage/1',
            data={'collage1': '1 2 3 4 5 6'},
            follow_redirects=True
        )
        assert response.status_code == 200
    
    def test_collage1_proper_input_no_images(self):
        response = self.client.get('/gallery', content_type='html/text')
        response2 = self.client.get('/generate-gallery/dogs/3', )
        response3 = self.client.post(
            '/collage/1',
            data={'collage1': '1 2 3 4 5 6'},
            follow_redirects=True
        )
        assert b'Indexes of images are not in range' in response3.data
    
    def test_collage2_proper_input(self):
        response = self.client.get('/gallery', content_type='html/text')
        response2 = self.client.get('/generate-gallery/dogs/10', )
        response3 = self.client.post(
            '/collage/2',
            data={'collage2': '1 2 3 4 5 6 7 8 9'},
            follow_redirects=True
        )
        assert response.status_code == 200
    
    def test_collage3_proper_input(self):
        response = self.client.get('/gallery', content_type='html/text')
        response2 = self.client.get('/generate-gallery/dogs/5', )
        response3 = self.client.post(
            '/collage/3',
            data={'collage3': '1 2 3 4 5'},
            follow_redirects=True
        )
        assert response.status_code == 200


    def test_apply_changes(self):
        response = self.client.get('/gallery', content_type='html/text')
        response2 = self.client.get('/generate-gallery/dogs/2')
        response3 = self.client.post(
            '/apply-changes',
            data={'blur1': '3', 'brightness1': '1.5', 'transpose1': 'on', 'delete1': '',
                  'blur2': '', 'brightness2': '', 'transpose2': '', 'delete2': 'on',
                  },
            follow_redirects=True
        )
        assert response3.status_code == 200
    
    def test_apply_changes_delete_all(self):
        response = self.client.get('/gallery', content_type='html/text')
        response2 = self.client.get('/generate-gallery/dogs/2')
        response3 = self.client.post(
            '/apply-changes',
            data={'blur1': '3', 'brightness1': '1.5', 'transpose1': 'on', 'delete1': 'on',
                  'blur2': '', 'brightness2': '', 'transpose2': '', 'delete2': 'on',
                  },
            follow_redirects=True
        )
        assert response3.status_code == 200
        response4 = self.client.post('/download-gallery')
        assert response4.status_code == 302


if __name__ == '__main__':
    pytest.main()
