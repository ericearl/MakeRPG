# MakeRPG

MakeRPG is intended to be a system that allows anyone who can edit YAML files to make automatic characters from game systems.

To see example outputs of a Character Index, Character Sheet, and NPC Sheet look in the `Examples/cyberpunk_2020/` folder.

# Dependencies

MakeRPG runs using Python 3.7 and Django 2.1.  You can install those however you like, but here is an easy way.

## Windows, Mac, or Linux

1. [Install Anaconda](https://docs.anaconda.com/anaconda/install/)
1. Open your new [Anaconda Navigator](https://docs.anaconda.com/anaconda/navigator/) and go to the Environments
1. On the right, choose "Not installed" from the drop-down menu
1. Type "django" into the "Search Packages" field
1. Click the checkbox to the left of "django" in the table
1. Click Apply in the bottom-right of the panel and it will install Django

# Getting Set Up

Getting set up can be easy too.  It involves configuring your admin and starting the server.

## Configuring your admin

1. Clone this repository
2. Open your Anaconda prompt by clicking the "Play" button next to your "base (root)" environment where you installed Django in the Anaconda Navigator
3. Select the "Open Terminal" option
4. Change directory with `cd` on the terminal into the path on your computer where you cloned this repository
5. Type the following three lines in sequence (type the line and then hit Enter):

```
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

6. You will be prompted for your Django server admin username, email address, and password

## Starting the server

Type the following any time you need to start the server.

```
python manage.py runserver
```

# Using CharacterCreator

Now you are ready for the extra cool part, automatic character generation.  It is currently achieved with two Python scripts called `setup.py` and `makecharacter.py`.  You'll need to edit a few numbers in the `makecharacter.py` script to be ready for the character generation portion, described in detail below.

Make sure you already started your server.  If you just did your setup you are fine, but if you have restarted your computer or shut down your server you will need to run the following command again.  In a terminal navigated to the same folder from the "Getting Set Up" section above, type:

```
python manage.py runserver
```

## First run `setup.py` once

The first time you will need to have your YAML files ready and edit the `setup.py` to point to the absolute paths to those files on your computer or the relative paths from the code repository, like this:

```python
skillstats_yaml = 'Examples/system_stats_skills.yaml'
history_yaml = 'Examples/system_history.yaml'
```

Only run `setup.py` once to initialize your database's history rolling and roles, stats, and skills.

In another different terminal navigated to the same folder from the "Getting Set Up" section above, type:

```
python setup.py
```

It will print out a few messages about setting things up in your database.

## From then on

You can choose to create any number of characters with any amount of stat and skill points by editing these variables at the top of the `makecharacter.py` `__main__` function:

```python
if __name__ == '__main__':
    # character count to make per run
    character_count = 5

    # mean (a.k.a. average) point values
    mean_stat_points = 50
    mean_role_points = 40
    mean_other_points = 10
```

You can run `makecharacter.py` the same way every time you want more characters:

```
python makecharacter.py
```

Currently, by default, you enter `stat`, `role`, and `other` points as a mean which characters actual points are sampled from a normal distribution with 20% of the mean variance.

Now open a web browser and go to [`http://localhost:8000/cc/`](http://localhost:8000/cc/) to see all of your characters.

Enjoy!

**Credits**:

- Coded up by Eric Earl
- Thanks to my friends for giving me feedback and support along the way (especially Colin)
- Thanks to the U.S. Census for free and open name data
- Thank you Cyberpunk 2020 (R) creators for hours and hours of creativity and inspiration
- The most special thanks goes to my wife and daughter for tolerating the time I've dedicated to this project
