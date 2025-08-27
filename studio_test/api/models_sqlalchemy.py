from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, ForeignKey, Text
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class TypeBoost(Base):
    """Типы бустов."""
    __tablename__ = 'type_boosts'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(Text)
    boosts = relationship("Boost", back_populates="type_boost")

    def __repr__(self):
        return f"<TypeBoost(name='{self.name}')>"


class Player(Base):
    """Модель игрока."""

    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    total_score = Column(Integer, default=0)
    created_player = Column(DateTime, default=datetime.now)
    everyday_login = Column(DateTime, nullable=True)
    boost_relationship = relationship(
        "PlayerBoostTable", 
        back_populates="player"
    )

    def add_daily_score(self, session, points=100):
        """Для добавления ежедневных баллов."""

        date_today = datetime.now().date()
        if self.everyday_login != date_today:
            self.total_score += points
            self.everyday_login = date_today
            session.commit()
            return True
        return False

    def add_boost(self, session, boost, choice_adder='manual'):
        """Добавить буст игроку."""

        boost_obj = PlayerBoostTable(
            player=self,
            boost=boost,
            choice_adder=choice_adder
        )
        session.add(boost_obj)
        session.commit()
        return boost_obj

    def __repr__(self):
        return f"<Player(user_id={self.user_id}, score={self.total_score})>"


class Boost(Base):
    """Модель буста."""

    __tablename__ = 'boosts'

    id = Column(Integer, primary_key=True)
    type_boost_id = Column(Integer, ForeignKey('type_boosts.id'))
    create_boost = Column(DateTime, default=datetime.now)
    finish_boost = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    type_boost = relationship("TypeBoost", back_populates="boosts")
    player_relationship = relationship(
        "PlayerBoostTable",
        back_populates="boost"
    )

    def __repr__(self):
        return f"<Boost(type='{self.type_boost.name}', active={self.is_active})>"


class PlayerBoostTable(Base):
    """Промежуточная модель для связи игроков и бустов."""

    __tablename__ = 'player_boost_table'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'))
    boost_id = Column(Integer, ForeignKey('boosts.id'))
    created_at = Column(DateTime, default=datetime.now)
    choice_adder = Column(
        String(20),
        default='manual'
    )

    # Связи многие-к-одному с Player и Boost
    player = relationship("Player", back_populates="boost_relationship")
    boost = relationship("Boost", back_populates="player_relationship")

    def __repr__(self):
        return f"<PlayerBoostTable(player={self.player_id}, boost={self.boost_id})>"
