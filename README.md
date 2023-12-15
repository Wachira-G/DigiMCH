# DigiMCH

This project is a Flask-based app for managing mother and child health care data during antenatal and postnatal periods. It is highly influenced by the 'Mother Child Health Handbook'. It uses SQLAlchemy for database management and Marshmallow for data serialization and validation. It used Flash_JWT_Extended to manage user authentication and authorization.


## Models 

The main models in this project are:

- `Patient`: This model represents the patient. It would store personal information about the patient. When a new patient visits, a new instance of this model would be created if they are not already registered in the system.

- `Visit`: This model represents a visit by a patient to the health facility. When a patient visits, a new instance of this model would be created and linked to the corresponding Patient instance.

- `Encounter`: This model represents an interaction between the patient and the health facility during a visit. It could be a consultation, lab test, pharmacy visit, etc. When a patient has an encounter during a visit, a new instance of this model would be created and linked to the corresponding Visit instance. The Encounter model also has a foreign key to the Patient model, directly linking an encounter to a patient.

- `User`: This model represents a user in the system, which could be a health worker or an admin. The Encounter model has a foreign key to the User model, indicating which user was involved in the encounter.

- `MaternalProfile`, `PresentPregnancy`, `AntenatalProfile`, `ClinicalNote`, etc.: These models represent various health records related to the patient. They would be linked to the Patient model via foreign keys. When a patient visits and new health data is collected, new instances of these models would be created or existing ones would be updated.

- `Appointment`, `Role`, `Location`, etc.: These models represent other aspects of the system, such as appointments made by the patient, roles of users in the system, and locations of health facilities. They would interact with the patient visit flow as necessary.

## Setup

To set up this project:

1. Clone the repository.
2. Create a python environment. You can create one with `python3 -m venv <environment_name>`.
3. If you created the environment, activate it on linux with `source <environment_name>/bin/activate`.
4. Install the dependencies with `pip install -r requirements.txt`.
5. Run the server in development mode with `FLASK_ENV=development flask run`.
