import discord
from discord.ext import commands
import Settings
import tracemalloc
import os
import hashlib
from database import collection , staff

logger = Settings.logging.getLogger("bot")

intents = discord.Intents.all()
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    
    #This is to fetch the commands file and load it on server
    for cmd_file in Settings.CMDS_DIR.glob('*.py'):
        if cmd_file.name != "__init__.py":
            await bot.load_extension(f'Cmds.{cmd_file.name[:-3]}')

@bot.event
async def on_guild_join(guild):
    default_channel = guild.system_channel
    if default_channel is None:
        default_channel = guild.welcome_channel
    if default_channel is not None:
        await default_channel.send("Hello, I have joined this server!")



@bot.event
async def on_raw_reaction_add(payload):
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    if member == bot.user:
        return

    if payload.emoji.name == '👤':
        client_role = discord.utils.get(guild.roles, name=f'client - {member.id}')
        if not client_role:
            client_role = await guild.create_role(name=f'client - {member.id}')

        await member.add_roles(client_role)

        clients_category = discord.utils.get(guild.categories, name='Clients')
        if not clients_category:
            clients_category = await guild.create_category(name='Clients')

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            member: discord.PermissionOverwrite(read_messages=True),
            client_role: discord.PermissionOverwrite(read_messages=True)
        }
        team_manager_role = discord.utils.get(guild.roles, name='Account Manager')
        sale_manager_role = discord.utils.get(guild.roles, name='Sales Manager')
        media_manager_role = discord.utils.get(guild.roles, name='Media Buyer')
        if team_manager_role:
            overwrites[team_manager_role] = discord.PermissionOverwrite(read_messages=True)

        if sale_manager_role:
            overwrites[sale_manager_role] = discord.PermissionOverwrite(read_messages=True)

        if media_manager_role:
            overwrites[media_manager_role] = discord.PermissionOverwrite(read_messages=True)

        channel_name = f'{member.name}'
        channel = await clients_category.create_text_channel(channel_name, overwrites=overwrites)

        member_data = {
            '_id': member.id,
            member.name : channel.id
        }
        try:
            collection.insert_one(member_data)

        except:
            pass


    elif payload.emoji.name == '📝':    
            
                embed = discord.Embed(title="***Form***", description="*Reply to this form giving the following details in a singal message:*", color = 0x00ff00)
                embed.add_field(name="Name", value="Your full name.", inline=False)
                embed.add_field(name="Email", value="Your email address.", inline=False)
                embed.add_field(name="Code", value="Your code.", inline=False)
                await member.send(embed=embed)


@bot.event
async def on_raw_reaction_remove(payload):
    guild = bot.get_guild(payload.guild_id)
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)

    # Check if the reaction is on a message sent by the bot
    if message.author != bot.user:
        return

    member = guild.get_member(payload.user_id)

    # Check if the reaction emoji is '👤'
    if payload.emoji.name == '👤':
        role_name = f'client - {member.id}'
        role = discord.utils.get(guild.roles, name=role_name)

        # If the corresponding role exists, remove it 
        if role:
            await member.remove_roles(role)
            await role.delete()
            data_set = collection.find_one({'_id': member.id})
            # Generate the modified channel name to match the username
            channel_name = data_set[member.name]

            # Attempt to find the private text channel with the modified name
            private_channel = discord.utils.get(guild.text_channels, id=channel_name)

            if private_channel:
                # Remove the client's permissions to view the channel
                await private_channel.delete()
                collection.delete_one({'_id':member.id})






@bot.listen('on_message')
async def on_message(message):
    user = collection.find_one({'team_id' : message.author.name})
    if user is not None:
        if message.author == bot.user or not isinstance(message.channel, discord.DMChannel):
            return
        else:
            await message.author.send('You can only try it once')
    else:
        if message.author == bot.user or not isinstance(message.channel, discord.DMChannel):
            return
        for guild in bot.guilds:
            member = guild.get_member(message.author.id)
            if member:
                form_channel = discord.utils.get(guild.channels, name='form')
                if not form_channel:
                    overwrites = {
                        guild.default_role: discord.PermissionOverwrite(send_messages=False),
                        guild.owner: discord.PermissionOverwrite(send_messages=True),
                        bot.user: discord.PermissionOverwrite(send_messages=True)
                    }
                    form_channel = await guild.create_text_channel('form', overwrites=overwrites)
                embed = discord.Embed(title=f"Form from {message.author}", description=message.content)
                await form_channel.send(embed=embed)
                data = collection.find_one({'_id':1})
                user_info = {
                    'team_id': message.author.name,
                    str(message.author.name) : int(message.author.id)
                }
                collection.insert_one(user_info)
    await bot.process_commands(message)

tracemalloc.start()


bot.run(Settings.Discord_api , root_logger=True)    