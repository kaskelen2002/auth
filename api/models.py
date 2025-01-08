import passlib.hash as _hash
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = "userdata"
    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]

    def verify_password(self, password: str):
        return _hash.bcrypt.verify(password, self.hashed_password)
