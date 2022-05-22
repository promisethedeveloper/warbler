
import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app
db.create_all()

class MessageModelTestCase(TestCase):
    """Tests for Message model"""
    def setUp(self):
        """Create test client and add some sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user = User.signup("test1", "test1@test.com", "testpassword", None)
        db.session.commit()

        self.user = user

      
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Does basic model work?"""
        
        message = Message(
            text="hello",
            user_id=self.user.id
        )

        db.session.add(message)
        db.session.commit()

        self.assertEqual(len(self.user.messages), 1)
        self.assertEqual(self.user.messages[0].text, "hello")

    def test_message_likes(self):
        message = Message(
            text="text",
            user_id=self.user.id, 
            timestamp = None
        )

        db.session.add(message)
        db.session.commit()

        self.user.likes.append(message)

        db.session.commit()

        liked_messages = Likes.query.filter(Likes.user_id == self.user.id).all()
        msg_text = Message.query.get(liked_messages[0].message_id).text
        
        self.assertEqual(len(liked_messages), 1)
        self.assertEqual(msg_text, 'text')

        self.assertEqual(liked_messages[0].user_id, self.user.id)
        self.assertEqual(liked_messages[0].message_id, message.id)