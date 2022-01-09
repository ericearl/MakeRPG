from django.db import models
from django.core.validators import MinLengthValidator
import random

INC = 'I'
DEC = 'D'
DIRECTION_CHOICES = (
    (INC, 'increasing'),
    (DEC, 'decreasing'),
)

IND = 'I'
DEP = 'D'
TYPE_CHOICES = (
    (IND, 'independent'),
    (DEP, 'dependent'),
)

TIER_CHOICES = (
    (0, 'add'),
    (1, 'multiply'),
    (2, 'double'),
    (3, 'triple'),
    (4, 'quadruple'),
    (5, 'quintuple'),
    (6, 'sextuple'),
    (7, 'septuple'),
    (8, 'octuple'),
    (9, 'nonuple'),
    (10, 'decuple'),
)

class Dice(models.Model):
    string = models.CharField(max_length=500, null=True, validators=[MinLengthValidator(1)])
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
    
    def roll(self):
        total = 0
        for die in range(self.quantity):
            total += random.choice(range(self.sides)) + 1

        return total + self.offset


class Event(models.Model):
    name = models.CharField(default='0', unique=True, max_length=500, validators=[MinLengthValidator(1)])
    dice = models.ForeignKey(Dice, null=True, on_delete=models.CASCADE)
    rerollevent = models.ForeignKey('self', null=True, on_delete=models.CASCADE, related_name='RerollEvent')
    nextevent = models.ForeignKey('self', null=True, on_delete=models.CASCADE, related_name='NextEvent')

    def __str__(self):
        return self.name


class EventRoll(models.Model):
    roll = models.IntegerField(null=True)
    outcome = models.CharField(max_length=500, null=True, validators=[MinLengthValidator(1)])
    npc = models.CharField(max_length=500, null=True, validators=[MinLengthValidator(1)])
    rerollcount = models.IntegerField(default=1)
    selection = models.BooleanField(default=False)
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


class Pointpool(models.Model):
    name = models.CharField(default='0', unique=True, max_length=500, validators=[MinLengthValidator(1)])

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(default='0', unique=True, max_length=500, validators=[MinLengthValidator(1)])

    def __str__(self):
        return self.name


class Archetype(models.Model):
    name = models.CharField(default='0', unique=True, max_length=500, validators=[MinLengthValidator(1)])

    def __str__(self):
        return self.name


class TraitCategory(models.Model):
    name = models.CharField(default='0', unique=True, max_length=500, validators=[MinLengthValidator(1)])

    def __str__(self):
        return self.name


class Statistic(models.Model):
    name = models.CharField(default='0', unique=True, max_length=500, validators=[MinLengthValidator(1)])
    direction = models.CharField(max_length=100, choices=DIRECTION_CHOICES, default=INC)
    cost = models.IntegerField(default=0)
    tier = models.IntegerField(choices=TIER_CHOICES, default=0)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES, default=IND)
    # purchase = models.ForeignKey(Dice, null=True, on_delete=models.CASCADE)
    purchase = models.IntegerField(default=0)
    role = models.ForeignKey(Role, null=True, on_delete=models.CASCADE)
    archetype = models.ForeignKey(Archetype, null=True, on_delete=models.CASCADE)
    pointpool = models.ForeignKey(Pointpool, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(default='0', max_length=500, validators=[MinLengthValidator(1)])
    direction = models.CharField(max_length=100, choices=DIRECTION_CHOICES, default=INC)
    cost = models.IntegerField(default=0)
    tier = models.IntegerField(choices=TIER_CHOICES, default=0)
    # purchase = models.ForeignKey(Dice, null=True, on_delete=models.CASCADE)
    purchase = models.IntegerField(default=0)
    role = models.ForeignKey(Role, null=True, on_delete=models.CASCADE)
    archetype = models.ForeignKey(Archetype, null=True, on_delete=models.CASCADE)
    pointpool = models.ForeignKey(Pointpool, null=True, on_delete=models.CASCADE)
    statistic = models.ForeignKey(Statistic, null=True, on_delete=models.CASCADE)

    def __str__(self):
        if self.statistic and self.statistic.name != 'none':
            return '[' + self.statistic.name + '] ' + self.name
        elif self.role and self.role.name != 'none':
            return '[' + self.role.name + '] ' + self.name
        else:
            return self.name


class Trait(models.Model):
    name = models.CharField(default='0', unique=True, max_length=500, validators=[MinLengthValidator(1)])
    direction = models.CharField(max_length=100, choices=DIRECTION_CHOICES, default=INC)
    cost = models.IntegerField(default=0)
    tier = models.IntegerField(choices=TIER_CHOICES, default=0)
    category = models.ForeignKey(TraitCategory, null=True, on_delete=models.CASCADE)
    # purchase = models.ForeignKey(Dice, null=True, on_delete=models.CASCADE)
    purchase = models.IntegerField(default=0)
    role = models.ForeignKey(Role, null=True, on_delete=models.CASCADE)
    archetype = models.ForeignKey(Archetype, null=True, on_delete=models.CASCADE)
    pointpool = models.ForeignKey(Pointpool, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Character(models.Model):
    name = models.CharField(default='0', unique=True, max_length=500, validators=[MinLengthValidator(1)])
    role = models.ForeignKey(Role, null=True, on_delete=models.CASCADE)
    archetype = models.ForeignKey(Archetype, null=True, on_delete=models.CASCADE)

    def __str__(self):
        if self.archetype and self.archetype.name != 'none' and self.role and self.role.name != 'none':
            return '[' + self.archetype.name + ' ' + self.role.name + '] ' + self.name
        elif self.role and self.role.name != 'none':
            return '[' + self.role.name + '] ' + self.name
        elif self.archetype and self.archetype.name != 'none':
            return '[' + self.archetype.name + '] ' + self.name
        else:
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


class CharacterPointpool(models.Model):
    character = models.ForeignKey(Character, null=True, on_delete=models.CASCADE)
    pointpool = models.ForeignKey(Pointpool, null=True, on_delete=models.CASCADE)
    current = models.IntegerField(default=0)
    total = models.IntegerField(default=0)

    def __str__(self):
        return self.pointpool.name + ': ' + str(self.current) + '/' + str(self.total)


class CharacterStatistic(models.Model):
    character = models.ForeignKey(Character, null=True, on_delete=models.CASCADE)
    statistic = models.ForeignKey(Statistic, null=True, on_delete=models.CASCADE)
    current = models.IntegerField(default=0)
    minimum = models.IntegerField(null=True)
    maximum = models.IntegerField(null=True)

    def __str__(self):
        return self.statistic.name + ' (' + str(self.statistic.cost) + '): ' + str(self.current)


class CharacterSkill(models.Model):
    character = models.ForeignKey(Character, null=True, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, null=True, on_delete=models.CASCADE)
    current = models.IntegerField(default=0)
    minimum = models.IntegerField(null=True)
    maximum = models.IntegerField(null=True)

    def __str__(self):
        if self.skill.statistic:
            return '[' + self.skill.statistic.name + '] ' + self.skill.name + ' (' + str(self.skill.cost) + '): ' + str(self.current)
        elif self.skill.role:
            return '[' + self.skill.role.name + '] ' + self.skill.name + ' (' + str(self.skill.cost) + '): ' + str(self.current)
        else:
            return self.skill.name + ' (' + str(self.skill.cost) + '): ' + str(self.current)


class CharacterTrait(models.Model):
    character = models.ForeignKey(Character, null=True, on_delete=models.CASCADE)
    trait = models.ForeignKey(Trait, null=True, on_delete=models.CASCADE)
    current = models.IntegerField(default=0)
    minimum = models.IntegerField(null=True)
    maximum = models.IntegerField(null=True)

    def __str__(self):
        if self.trait.category:
            return '[' + self.trait.category.name + '] ' + self.trait.name + ' (' + str(self.trait.cost) + '): ' + str(self.current)
        else:
            return self.trait.name + ' (' + str(self.trait.cost) + '): ' + str(self.current)

