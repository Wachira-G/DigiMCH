"""Define a block list model."""

from datetime import datetime
from flask_jwt_extended import decode_token
from app import db
from sqlalchemy.sql import func

class TokenBlockList(db.Model):
    """Define a block list model."""

    __tablename__ = "block_list"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jti = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __init__(self, jti):
        """Initialize a block list model."""
        self.jti = jti

    def __repr__(self):
        """Represent a block list model by its id."""
        return f"<BlockList {self.id}>"

    def save(self):
        """Save a block list model."""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def is_jti_blocklisted(jti):
        """Check if a token is blocklisted."""
        query = TokenBlockList.query.filter_by(jti=jti).first()
        return bool(query)
    
    @staticmethod
    def clean_block_list():
        """Delete all block list entries."""
        now = datetime.now()
        blocklisted_tokens = TokenBlockList.query.all()
        for token in blocklisted_tokens:
            metadata = decode_token(token.jti)
            if metadata['exp'] < now:
                db.session.delete(token)
        db.session.commit()
