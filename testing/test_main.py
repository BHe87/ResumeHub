import unittest

class TestStringMethods(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(dict(
            SECRET_KEY='GROUP18_RESUMEHUB',
            USERNAME='admin',
            PASSWORD='greatpassword',
            SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'resumehub.db'),
            SQLALCHEMY_TRACK_MODIFICATIONS = False
        ))
        self.db.init_app(app)

    def test_organization(self):
        # Test with a user, should return the html template for the organization
        g.user = User.query.get(session['user_id'])
        self.assertEqual(app.organization(), 'org.html')

        # Test with no user, redirects to the login page
        g.user = NULL
        self.assertEqual(app.organization(), redirect(url_for('login'))

    def test_download_resume(self):
        # Test with a student that has a resume
        # Should download the resume
        # Mocking a returned resume in function
        self.Student.query.get(session['user_id']).resume = MagicMock(return_value= "tempResume.pdf")
        self.assertEqual(app.download_resume(self.filename), send_file(io.BytesIO(res),
                     mimetype='application/octet-stream')

        # Test without a resume in the database
        # Should redirect to profile
        # Mocking a null resume
        self.Student.query.get(session['user_id']).resume = MagicMock(return_value= NULL)
        self.assertEqual(app.download_resume(self.filename), redirect(url_for('profile')))
        
        

    def test_save_resume(self):
        # Test with signed in user and proper resume
        # Should add resume to the database and redirect to profile
        g.user = User.query.get(session['user_id'])
        # Mock student
        self.Student.query.get(session['user_id']) = MagicMock(tempStudent)
        student = Student.query.get(session['user_id'])
        self.assertEqual(app.save_resume(), redirect(url_for('profile')))
        # check to see if resume is in database
        self.assertTrue(student.resume != NULL)


        # Test with signed out user and proper resume
        # Should redirect to login
        g.user = NULL
        self.assertEqual(app.save_resume(), redirect(url_for('login')))


        # Test with signed in user and resume is not the correct file type
        g.user = User.query.get(session['user_id'])
        # Mock student
        self.Student.query.get(session['user_id']) = MagicMock(tempStudent)
        student = Student.query.get(session['user_id'])
        self.assertEqual(app.save_resume(), redirect(url_for('profile')))
        # check to see if resume is in database --> it should not be
        self.assertTrue(student.resume == NULL)

    def test_add_organization(self):
        # Test with Null user, should redirect to login
        g.user = NULL
        self.assertEqual(app.add_organization(), redirect(url_for('login')))

        # Test with user, for student trying to join an organization twice
        # should redirect to profile
        g.user = User.query.get(session['user_id'])
        self.Organization.query.filter_by(username=request.form['organization']).first() = MagicMock(return_value=tempOrganziation)
        self.Student.query.get(session['user_id']) = MagicMock(return_value=tempStudent)
        current_student = Student.query.get(session['user_id'])
        self.assertEqual(app.add_organization, redirect(url_for('profile')))

        # Test with user, join a new organization 
        # should render student_submission template
        # Should add organization to the organization list
        g.user = User.query.get(session['user_id'])
        self.Organization.query.filter_by(username=request.form['organization']).first() = MagicMock(return_value=tempOrganziation)
        self.Student.query.get(session['user_id']) = MagicMock(return_value=tempStudent)
        current_student = Student.query.get(session['user_id'])
        self.assertEqual(app.add_organization, 'student_submission.html')
        self.assertTrue(current_student.organization.contains(tempOrganization))

    def test_student_submission(self):
        # Test without user, should redirect to login
        g.user = NULL
        self.assertEqual(app.student_submission(), redirect(url_for('login')))

        # Test with user, should render student_submission template
        g.user = User.query.get(session['user_id'])
        self.assertEqual(app.student_submission(), 'student_submission')

    def test_save_profile(self):

    def test_profile(self):

    def test_register(self):

    def test_logout(self):

    def test_login(self):

    def test_root(self):

    def test_before_request(self):

if __name__ == '__main__':
    unittest.main()