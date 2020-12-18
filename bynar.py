#!/usr/bin/env python3

# Core
import os
import csv
import random
import datetime
import re

# Community
import discord
import yaml

# SQLAlchemy
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
def main():
    with open('secrets.yml') as secrets_file:
        secrets = yaml.load(secrets_file)

    engine = sqlalchemy.create_engine('sqlite:///data.sqlite', echo=True)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)

    client = discord.Client()

    @client.event
    async def on_ready():
        print(f'{client.user} has connected to Discord!')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content == "!ping":
            await message.channel.send("Pong!")

        session = Session()
        current_user = find_or_initialize_user(message.author, session)

        match_res = re.match(r"^!name-add\s+(.+?)\s*$", message.content)
        if match_res:
            name = match_res[1]
            if len(name) > 100:
                await message.channel.send("Sorry, names can't be over 100 characters")
                return

            stmt = session.query(BandName).filter(BandName.name == name)
            if stmt.count() > 0:
                await message.channel.send("Sorry, name exists")
                return

            session.add(BandName(name=name, creator=message.author.name))

            points_gained = 40
            current_user.experience_points += points_gained

            session.add(current_user)

            session.commit()

            await message.channel.send("<@{}> Your suggested name has been added! You gain {}xp! (total: {}xp)".format(current_user.discord_id, points_gained, current_user.experience_points))
            return

        if message.content == "!name-list":
            session = Session()
            await message.channel.send(", ".join(name.name for name in session.query(BandName).all()))
            return

        if message.content == "!help":
            find_or_initialize_user(message.author, session)
            await message.channel.send("<@{}> Read the code, FRIEND https://github.com/chao-mu/BynarBot".format(current_user.discord_id))
            

    client.run(secrets["bot_token"])

def find_or_initialize_user(author, session):
    stmt = session.query(User).filter(User.discord_id == author.id)
    if stmt.count() > 0:
        db_author = stmt.first()
    else:
        db_author = User(discord_id=author.id, experience_points=0)

    db_author.name = author.nick

    return db_author

class BandName(Base):
    __tablename__ = "band_names"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    creator = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    name = Column(String)
    discord_id = Column(String)
    experience_points = Column(Integer)

if __name__ == "__main__":
    main()
