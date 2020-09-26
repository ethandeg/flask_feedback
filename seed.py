from models import User, db, Feedback
from app import app

# Create all tables
db.drop_all()
db.create_all()

# If table isn't empty, empty it
User.query.delete()


root = User.register(username='root', pwd='root', email='root@gmail.com',
                     first_name='root', last_name='root')
cody = User.register(username='cody_playful_paws', pwd='cody',
                     email='cody@gmail.com', first_name='Cody', last_name='Playful Paws')
ethan = User.register(username='ethandeg', pwd='admin', email='admin@gmail.com',
                      first_name='Ethan', last_name='Degenhardt')


f1 = Feedback(title='This site sucks',
              content='Do you plan on releasing any features?', username='ethandeg')
f2 = Feedback(title='This site rocks', content='I like the features',
              username='cody_playful_paws')
f3 = Feedback(title='What is the purpose of this site?',
              content='Seriously? This site has no other functionality than talking about its features', username='ethandeg')
f4 = Feedback(title='initializing', content='Initializing', username='root')


db.session.add_all([root, cody, ethan])
db.session.commit()
db.session.add_all([f1, f2, f3, f4])
db.session.commit()
