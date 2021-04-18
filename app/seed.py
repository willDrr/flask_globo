import random
from sqlalchemy.exc import IntegrityError
from faker import Faker
from app import db
from app.models import User, Gig, Role

def seed_db(num_of_employers=20, num_of_gigs=30, num_of_musicians=20):
    num_of_users = User.query.count()

    fake = Faker()
    i = 0
    print("Creating employers...")
    print("Created: 0", end="\r")
    while i < num_of_employers:
        e = User(
                username=fake.company(),
                email=fake.email(),
                password='password123',
                location=fake.city(),
                description="We sometimes put up gig offers. Here are some random words: " + fake.paragraph(3, True),
                role_id=Role.EMPLOYER
            )
        e.activated = True
        db.session.add(e)
        try:
            db.session.commit()
            i += 1
            print("Created: " + str(i), end="\r")
        except IntegrityError:
            db.session.rollback()
    print("Finished creating " + str(num_of_employers) + " employers...")
    print("\n")

    i = 0
    print("Creating gigs...")
    print("Created: 0", end="\r")
    employer_ids = db.session.query(User.id).filter_by(role_id=3).all()
    while i < num_of_gigs:
        random_title = random_gig_title()
        g = Gig(
                title=random_title,
                description=random_gig_description(random_title),
                payment=round(random.uniform(100, 2000),2),
                location=fake.city(),
                employer_id=random.choice(employer_ids)[0]
            )
        db.session.add(g)
        db.session.commit()
        i += 1
        print("Created: " + str(i), end="\r")
    print("Finished creating " + str(num_of_gigs) + " gigs...")
    print("\n")

    i = 0
    print("Creating musicians...")
    print("Created: 0", end="\r")
    while i < num_of_musicians:
        m = User(
                username=fake.user_name(),
                email=fake.email(),
                password='password123',
                location=fake.city(),
                description="I am ready to make some music! Please hire me. Here are some random words: " + fake.paragraph(3, True),
                role_id=Role.MUSICIAN
            )
        m.activated = True
        db.session.add(m)
        try:
            db.session.commit()
            i += 1
            print("Created: " + str(i), end="\r")
        except IntegrityError:
            db.session.rollback()
    print("Finished creating " + str(num_of_musicians) + " musicians...")
    print("\n")

    i = 0
    print("Applying musicians to gigs...")
    num_of_applications = int(num_of_musicians/2)
    print("Will create " + str(num_of_applications*num_of_gigs) + " applications.")
    musician_ids = db.session.query(User.id).filter_by(role_id=2).all()
    while i < num_of_gigs:
        g = Gig.query.get(i+1)
        j = 0
        while j < num_of_applications:
            m = User.query.get(random.choice(musician_ids)[0])
            try:
                m.apply(g)
                db.session.commit()
                j += 1
            except IntegrityError:
                db.session.rollback()
        i += 1

    print("\n")
    print("Creating admin user...")
    print("\n")
    print("Login info for admin:")
    print("Email: admin@mail.com")
    print("Password: pass")
    print("\n")
    admin = User("admin", "admin@mail.com", "password123", "Nowhere", "I am admin", Role.ADMIN)
    db.session.add(admin)
    db.session.commit()
    print("Database is ready!")

instruments = [
    "Handpan",
    "Marimba",
    "Tambourine",
    "Vibraphone",
    "Bongo drums",
    "Accordion",
    "Bagpipe",
    "Clarinet",
    "English horn",
    "Harmonica",
    "Oboe",
    "Pan flute",
    "Pipe organ",
    "Saxophone",
    "Trombon",
    "Banjo",
    "Cello",
    "Acoustic guitar",
    "Classic guitar",
    "Electric guitar",
    "Bass guitar",
    "Koto",
    "Lyre",
    "Mandolin",
    "Sitar",
    "Ukulele",
    "Viola",
    "Violin",
    "Drums",
    "Piano",
    "Harp",
    "Electronic keyboard"
]

titles = [
    "We need",
    "Need",
    "In need of",
    "Wanted:",
    "Urgent! We need",
    "Looking for",
    "Apply for"
]

gig_types = [
    "company picnic",
    "company celebration",
    "team building",
    "a bar",
    "a tavern",
    "a concert",
    "a party",
    "a small gathering",
    "a wedding",
    "a theatre",
    "a coffe place",
    "a restaurant"
]

description = [
    "Hello! We are a small company in need of music.",
    "Hi there. If you think you can do this, please apply.",
    "This is a big deal for us. Please only serious musicians.",
    "A 5 years of experience is a must.",
    "If you have a band, even better. Please apply or contact us.",
    "It is not a big deal, just few people will be attending.",
    "Everything is ready, we only need music. Apply if interested.",
    "Apply if you are interested. See you soon!",
    "Maybe you are the right match for us. Apply and we will see.",
    "You first need to pass an audition. Only serious musicians please.",
    "We require at least the 10 years of experience with this instrument.",
    "Apply. Payment can be negotiated.",
    "Hello there, hi. We need your services ASAP.",
    "We are in a rush!! The first one gets the cake.",
    "Please hurry, we need someone quick.",
    "We require a professional.",
    "We will be satisfied with the amateur player.",
    "Play music and get free drinks too! Apply!",
    "Hi there. This is the first time we need music at an event. We will have an audition.",
    "Apply! Please send us a video of you playing too!",
    "Hello, we need someone ASAP."
]

def random_gig_title():
    return random.choice(titles) + " " + random.choice(instruments) + " player for " + random.choice(gig_types)

def random_gig_description(title):
    return random.choice(description) + " " + title
