# MakeRPG

MakeRPG is intended to be a system that allows anyone who can edit YAML files to make automatic characters and game systems.

# Dependencies

MakeRPG runs using Django 2.1 and Python 3.  You can install those however you like, but here is an easy way.

## Windows, Mac, or Linux

1. [Install Anaconda](https://docs.anaconda.com/anaconda/install/)
1. Open your new [Anaconda Navigator](https://docs.anaconda.com/anaconda/navigator/) and go to the Environments
1. On the right, choose "Not installed" from the drop-down menu
1. Type "django" into the "Search Packages" field
1. Click the checkbox to the left of "django" in the table
1. Click Apply in the bottom-right of the panel and it will install Django

# Getting Set Up

Getting set up can be easy too.  It involves starting the MakeRPG Django server, configuring your server admin, and starting your server.

## Steps

1. Clone this repository
1. Open your Anaconda prompt by clicking the "Play" button next to your "base (root)" environment where you installed Django in the Anaconda Navigator
1. Select the "Open Terminal" option
1. Change directory with `cd` on the terminal into the path on your computer where you cloned this repository
1. Type the following:
```
python manage.py createsuperuser
```
1. You will be prompted for your Django server admin username, email address, and password
1. Type the following three lines in sequence (type the line and then hit Enter):
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

# Making Characters

Now you are ready for the extra cool part, automatic character generation.  It is currently achieved with a Python script called `setup.py`.  You'll need to edit a few numbers in the `setup.py` script and then you'll be ready to start.

## The first run of `setup.py`

The first time you will need to have your YAML files ready and point the `setup.py` to the absolute paths to those files on your computer.  You can make sample characters at the same time if you want, but don't have to.  The important part is to only run `setup.py` once this way to initialize your database's history rolling and roles, stats, and skills.

In another different terminal navigated to the same folder from the "Getting Set Up" section above, type:

```
python setup.py
```

It will print out a few messages about setting things up in your database.

## From then on

You need to open up the `setup.py` and comment out the two lines to only run once.  You can choose to create any number of character by editing the `character_count` variable.  Now every other time you will run `setup.py` the same way:

```
python setup.py
```

Now open a web browser and go to [`http://localhost:8000/cc/`](http://localhost:8000/cc/) to see all of your characters.

Enjoy!
