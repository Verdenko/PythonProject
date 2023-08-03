# coding: utf-8
from sqlalchemy import BigInteger, CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# Автоматически выгруженные структуры бд на PostgreSQL с помощью sqlacodegen
Base = declarative_base()
metadata = Base.metadata


class IrenderDryertype(Base):
    __tablename__ = 'irender_dryertype'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=False)


class IrenderTimeperiod(Base):
    __tablename__ = 'irender_timeperiod'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=False)


class IrenderWoodtype(Base):
    __tablename__ = 'irender_woodtype'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=False)


class IrenderWoodcatalog(Base):
    __tablename__ = 'irender_woodcatalog'
    __table_args__ = (
        CheckConstraint('density >= 0'),
    )

    id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=False)
    density = Column(Integer, nullable=False)
    wood_type_id = Column(ForeignKey('irender_woodtype.id', deferrable=True, initially='DEFERRED'), nullable=False,
                          index=True)

    wood_type = relationship('IrenderWoodtype')


class IrenderWoodparameter(Base):
    __tablename__ = 'irender_woodparameters'

    id = Column(BigInteger, primary_key=True)
    temp_dif = Column(Integer, nullable=False)
    heat_value = Column(Integer, nullable=False)
    dryer_id = Column(ForeignKey('irender_dryertype.id', deferrable=True, initially='DEFERRED'), nullable=False,
                      index=True)
    period_id = Column(ForeignKey('irender_timeperiod.id', deferrable=True, initially='DEFERRED'), nullable=False,
                       index=True)
    wood_type_id = Column(ForeignKey('irender_woodtype.id', deferrable=True, initially='DEFERRED'), nullable=False,
                          index=True)

    dryer = relationship('IrenderDryertype')
    period = relationship('IrenderTimeperiod')
    wood_type = relationship('IrenderWoodtype')
