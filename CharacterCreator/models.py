from django.db import models
#from django.core.validators import MinValueValidator, MaxValueValidator

class Dice(models.Model):
    string = models.CharField(max_length=50, null=True)
    quantity = models.IntegerField(default=1)
    sides = models.IntegerField(default=2)
    offset = models.IntegerField(default=0)

    def __str__(self):
        if self.offset < 0:
            return str(self.quantity) + 'd' + str(self.sides) + ' - ' + str((-1)*self.offset)
        elif self.offset == 0:
            return str(self.quantity) + 'd' + str(self.sides)
        elif self.offset > 0:
            return str(self.quantity) + 'd' + str(self.sides) + ' + ' + str(self.offset)


class Event(models.Model):
    name = models.CharField(max_length=50)
    dice = models.ForeignKey(Dice, null=True, on_delete=models.CASCADE)
    rerollevent = models.ForeignKey('self', null=True, on_delete=models.CASCADE, related_name='RerollEvent')
    nextevent = models.ForeignKey('self', null=True, on_delete=models.CASCADE, related_name='NextEvent')

    def __str__(self):
        return self.name


class EventRoll(models.Model):
    roll = models.IntegerField(null=True)
    outcome = models.CharField(max_length=300, null=True)
    npc = models.CharField(max_length=50, null=True)
    rerollcount = models.IntegerField(default=1)
    mainevent = models.ForeignKey(Event, null=True, on_delete=models.CASCADE, related_name='MainEvent')
    rollevent = models.ForeignKey(Event, null=True, on_delete=models.CASCADE, related_name='RollEvent')

    def __str__(self):
        if self.outcome:
            return self.mainevent.name + ' (' + str(self.roll) + '): ' + self.outcome
        elif self.rollevent:
            return self.mainevent.name + ' (' + str(self.roll) + ') -> ' + self.rollevent.name
        else:
            return self.mainevent.name + ' (' + str(self.roll) + ')'

class NPCEvent(models.Model):
    current = models.ForeignKey(Event, null=True, on_delete=models.CASCADE, related_name='CurrentNPCEvent')
    next = models.ForeignKey(Event, null=True, on_delete=models.CASCADE, related_name='NextNPCEvent')

    def __str__(self):
        return self.current.name + ' -> ' + self.next.name


class Statistic(models.Model):
    name = models.CharField(max_length=50, unique=True)
    minimum = models.IntegerField(null=True)
    maximum = models.IntegerField(null=True)

    def __str__(self):
        return self.name + ' (' + str(self.minimum) + '->' + str(self.maximum) + ')'


class Skill(models.Model):
    name = models.CharField(max_length=50)
    minimum = models.IntegerField()
    maximum = models.IntegerField()
    statistic = models.ForeignKey(Statistic, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return '[' + self.statistic.name + '] ' + self.name + ' (' + str(self.minimum) + '->' + str(self.maximum) + ')'


class Role(models.Model):
    name = models.CharField(max_length=50)
    special_skills = models.ManyToManyField(Skill, related_name='SpecialSkill')
    common_skills = models.ManyToManyField(Skill, related_name='CommonSkill')

    def __str__(self):
        return self.name


class Character(models.Model):
    name = models.CharField(default='', unique=True, max_length=50)
    role = models.ForeignKey(Role, null=True, on_delete=models.CASCADE)
    stat_points = models.IntegerField(default=0)
    role_points = models.IntegerField(default=0)
    other_points = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class CharacterEventRoll(models.Model):
    character = models.ForeignKey(Character, null=True, on_delete=models.CASCADE)
    eventroll = models.ForeignKey(EventRoll, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.eventroll)


class NPCEventRoll(models.Model):
    npc = models.ForeignKey(Character, null=True, on_delete=models.CASCADE, related_name='NPC')
    character = models.ForeignKey(Character, null=True, on_delete=models.CASCADE, related_name='PlayerCharacter')
    eventroll = models.ForeignKey(EventRoll, null=True, on_delete=models.CASCADE)

    def __str__(self):
        # return str(self.npc) + ': ' + str(self.eventroll)
        return str(self.eventroll)


class CharacterStatistic(models.Model):
    character = models.ForeignKey(Character, null=True, on_delete=models.CASCADE)
    statistic = models.ForeignKey(Statistic, null=True, on_delete=models.CASCADE)
    current = models.IntegerField(blank=True)

    def __str__(self):
        return self.statistic.name + ': ' + str(self.current)


class CharacterSkill(models.Model):
    character = models.ForeignKey(Character, null=True, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, null=True, on_delete=models.CASCADE)
    current = models.IntegerField(blank=True)

    def __str__(self):
        return '[' + self.skill.statistic.name + '] ' + self.skill.name + ': ' + str(self.current)

