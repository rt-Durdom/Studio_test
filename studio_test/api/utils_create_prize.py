#### __________________Дано по условию _______________####
from django.db import models


class Player(models.Model):
    player_id = models.CharField(max_length=100)
    
    
class Level(models.Model):
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    
    
    
class Prize(models.Model):
    title = models.CharField()
    
    
class PlayerLevel(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed = models.DateField()
    is_completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)
    
    
class LevelPrize(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    received = models.DateField()
     
####_____________Решение_____________________####
    
from datetime import datetime


class PlayerPrize(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    receiving_prize = models.DateField(default=datetime.now)

    class Meta:
        unique_together = ('player', 'prize', 'level')


def check_prize(player: Player, level: Level, prize: Prize):
    """Приз за прохождение уровня."""
    # Проверяем факт прохождения уровня
    try:
        player_level = PlayerLevel.objects.get(player=player, level=level)
    except PlayerLevel.DoesNotExist:
        raise ValueError("Игрок ещё не играл этот уровень")

    if not player_level.is_completed:
        return None

    player_prize = PlayerPrize.objects.get_or_create(
        player=player,
        level=level,
        prize=prize,
        defaults={"receiving_prize": datetime.now().date()}
    )[0]
    return player_prize



#  Загрузка в CSV __________________________________________________________
import csv

# Вариант 1 - когда память не важна - метод "В тупую"
def export_prizes_direct_csv(filepath="player_prizes.csv"):
    queryset = PlayerPrize.objects.select_related("player", "level", "prize").all()

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["player_id", "level", "prize", "received"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for obj in queryset:
            writer.writerow({
                "player_id": obj.player.player_id,
                "level": obj.level.title,
                "prize": obj.prize.title,
                "received": obj.receiving_prize.isoformat() if obj.receiving_prize else ""
            })


# Вариант 2 - Загрузка частями
def export_prizes_chunked_csv(
        filepath="player_prizes_chunked.csv",
        str_size=5000):
    queryset = PlayerPrize.objects.select_related("player", "level", "prize").all()

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["player_id", "level", "prize", "received"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for obj in queryset.iterator(chunk_size=str_size):
            writer.writerow({
                "player_id": obj.player.player_id,
                "level": obj.level.title,
                "prize": obj.prize.title,
                "received": obj.receiving_prize.isoformat() if obj.receiving_prize else ""
            })
