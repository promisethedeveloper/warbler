"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user1 = User.signup("test1", "test1@test.com", "testpassword", None)
        user2 = User.signup("test2", "test2@test.com", "testpassword", None)

        self.user1 = user1
        self.user2 = user2

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)


    def test_user_follows(self):
        """Test user follows"""

        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertEqual(len(self.user1.following), 1)
        self.assertEqual(self.user1.following[0].id, self.user2.id)
        self.assertEqual(len(self.user2.followers), 1)
        self.assertEqual(self.user2.followers[0].id, self.user1.id)

    
    def test_is_following(self):
        """Test is_following method"""

        self.assertFalse(self.user1.is_following(self.user2))
        self.user1.following.append(self.user2)
        db.session.commit()
        self.assertTrue(self.user1.is_following(self.user2))

    
    def test_is_followed_by(self):
        """Test is_followed_by method"""

        self.assertFalse(self.user2.is_followed_by(self.user1))
        self.user1.following.append(self.user2)
        db.session.commit()
        self.assertTrue(self.user2.is_followed_by(self.user1))

    
    def test_user_signup(self):
        """Test User.signup method"""

        new_user = User.signup('test3', 'test3@test.com', 'password', None)
        db.session.commit()

        self.assertTrue(new_user.username == 'test3')
        self.assertTrue(new_user.email == 'test3@test.com')
        self.assertTrue(new_user.password.startswith('$2b$'))

        error_user = User.signup(None, 'error@test.com', 'password', None)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    
    def test_auth(self):
        """Test User.authenticate method"""

        # new_user = User.signup('test4', 'test4@test.com', 'password', None)
        # db.session.commit()

        user_from_auth = User.authenticate('test1', 'testpassword')

        error_auth1 = User.authenticate('test11111', 'testpassword')
        error_auth2 = User.authenticate('test1', 'wrongpassword')

        self.assertTrue(user_from_auth.id == self.user1.id)
        self.assertTrue(error_auth1 == False)
        self.assertTrue(error_auth2 == False)