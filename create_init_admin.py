"""Create Initial Admin User"""


from datetime import datetime

time = "%Y-%m-%dT%H:%M:%S"


def create_admin(db, User, Role, Person):
    """Create an admin user."""

    # create initial roles
    # admin
    try:
        admin_role = Role.query.filter_by(name="admin").first()
        if admin_role:
            pass
        else:
            admin_role = Role(name="admin", description="Administrator")
            db.session.add(admin_role)
            db.session.commit()
    except Exception as e:
        print(f"Failed to create admin role: {e}")
        return None

    # provider
    try:
        provider_role = Role.query.filter_by(name="provider").first()
        if provider_role:
            pass
        else:
            provider_role = Role(name="provider", description="Provider")
            db.session.add(provider_role)
            db.session.commit()
    except Exception as e:
        print(f"Failed to create provider role: {e}")
        return None

    # patient
    try:
        patient_role = Role.query.filter_by(name="patient").first()
        if patient_role:
            pass
        else:
            patient_role = Role(name="patient", description="Patient")
            db.session.add(patient_role)
            db.session.commit()
    except Exception as e:
        print(f"Failed to create patient role: {e}")
        return None

    # create initial admin user
    try:
        admin = User.query.filter_by(phone_no="+254700000000").first()
        if admin:
            return admin
        admin = User(
            first_name="Root Admin",
            surname="Admin",
            phone_no="+254700000000",
            middle_name="Admin",
            password_hash=Person.generate_hash("1Admin234"),
            sex="root",
            birth_date=datetime.now().strftime(time),
            facility_id="1",
        )
        admin.roles.append(admin_role)
        db.session.add(admin)
        db.session.commit()
        return admin
    except Exception as e:
        print(f"Failed to create admin user: {e}")
        return None
