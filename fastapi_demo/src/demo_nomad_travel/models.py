from sentry_sdk.session import Session
from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    Text, create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Regions(Base):
    __tablename__ = 'regions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False) # Mapped makes convert our datatype to our DB's type (like VarChar 50)

    tourist_points: Mapped[list['TouristPoints']] = relationship(
        'TouristPoints',
        back_populates='region',
        cascade='all, delete-orphan',
    )


class TouristPoints(Base):
    __tablename__ = 'tourist_points'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    short_description: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    long_description: Mapped[str] = mapped_column(Text, nullable=False)

    region_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('regions.id'),
    )
    region: Mapped['Regions'] = relationship(
        'Regions',
        back_populates='tourist_points',
    )

# Responsible for our DB connection
engine = create_engine('sqlite:///sample_nomad_travel.db')

# Generates schemas and all tables
Base.metadata.create_all(engine)

# Creation session that's binded to our engine db connection ( OLD Way)
# Session = sessionmaker(bind=engine)
# session = Session()

# New SQLAclhemy 2 way
with Session(engine) as session:
    almaty = Regions(name='Almaty')
    kyzylorda = Regions(name='Kyzylorda')
    session.add_all([almaty, kyzylorda])
    session.commit() # Saving our added cities, if you don't commit - you won't save changes
    cities = session.query(Regions).all()
    for city in cities:
        print(city.name)