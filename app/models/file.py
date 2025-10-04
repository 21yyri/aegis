from app import db
import sqlalchemy as sa
import sqlalchemy.orm as so
from datetime import datetime

class File(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    owner_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'))
    owner: so.Mapped['User'] = so.relationship(back_populates='files') # type: ignore

    name: so.Mapped[str] = so.mapped_column(sa.String(200), unique=True)
    date: so.Mapped[datetime] = so.mapped_column(sa.DateTime(), default=datetime.now)
