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

        match_res = re.match(r"^!name-add\s+(.+?)\s*$", message.content)
        if match_res:
            session = Session()
            name = match_res[1]
            if len(name) > 100:
                await message.channel.send("Sorry, names can't be over 100 characters")
                return

            stmt = session.query(BandName).filter(BandName.name == name)
            if stmt.count() > 0:
                await message.channel.send("Sorry, name exists")
                return

            session.add(BandName(name=name, creator=message.author.name))
            session.commit()

            await message.channel.send("Name added!")
            return


    client.run(secrets["bot_token"])

class BandName(Base):
    __tablename__ = "band_names"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    creator = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

if __name__ == "__main__":
    main()
