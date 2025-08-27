from django.db import models
from datetime import datetime
from django.contrib.auth.models import User


class TypeBoost(models.Model):
    """Типы бустов (без этой дополнительнй модели не получалось)."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    """Модель игрока."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)
    created_player = models.DateTimeField(default=datetime.now)
    everyday_login = models.DateField(null=True, blank=True)
    boosts = models.ManyToManyField(
        'Boost',
        through='PlayerBoost',
        through_fields=('player', 'boost'),
        related_name='players'
    )

    def add_daily_score(self, points=100):
        """Для добавления ежедневных баллов."""

        date_today = datetime.now().date()
        if self.everyday_login != date_today:
            self.total_score += points
            self.everyday_login = date_today
            self.save()
            return True
        return False

    def __str__(self):
        return self.user.username


class Boost(models.Model):
    """Модель буста."""

    type_boost = models.ForeignKey(TypeBoost, on_delete=models.CASCADE)
    create_boost = models.DateTimeField(default=datetime.now)
    finish_boost = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def is_expired(self):
        if self.finish_boost:
            return datetime.now() > self.finish_boost
        return False

    def __str__(self):
        return self.type_boost.name


class PlayerBoost(models.Model):
    """Промежуточная модель для связи игроков и бустов."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    boost = models.ForeignKey(Boost, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.now)
    choice_adder = models.CharField(
        max_length=20,
        choices=[('level', 'За прохождение уровня'), ('manual', 'Вручную')],
        default='manual'
    )

    class Meta:
        unique_together = ['player', 'boost']

    def __str__(self):
        return f"{self.player} - {self.boost}"
