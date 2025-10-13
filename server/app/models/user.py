import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_bcrypt import Bcrypt
from app import db

bcrypt = Bcrypt()

class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    
    username: so.Mapped[str] = so.mapped_column(sa.String(50), unique=True)
    password: so.Mapped[str] = so.mapped_column(sa.String(128))

    files: so.Mapped[list['File']] = so.relationship(back_populates='owner', cascade="all, delete-orphan") # type: ignore


    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

