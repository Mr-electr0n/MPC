import discord
from discord.ext import commands
import re
from database import collection , staff


class start(commands.Cog):
    @commands.command()
    async def start(self, ctx):
        await ctx.send('I am working fine')


    # Function to sanitize the username and create a valid channel name

    @commands.command()
    async def setup(self, ctx):
        if ctx.author != ctx.guild.owner:
            embed = discord.Embed(title="Error", description="You don't have permission to use this command.", color=0xff0000)
            await ctx.send(embed=embed)
            return

        verification_channel = discord.utils.get(ctx.guild.channels, name='verification')
        if not verification_channel:
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            
            # Sanitize the username and create a valid channel name
            channel_name = 'verification'
            
            verification_channel = await ctx.guild.create_text_channel(channel_name, overwrites=overwrites)

        embed = discord.Embed(title="React Roles", description="React to this message to get a role.", color=0x00ff00)
        embed = discord.Embed(title="Verification", description="React to this message to get verified.")
        embed.add_field(name="Client", value="React with 👤 to get the Client role and a private channel.")
        embed.add_field(name="Form", value="React with 📝 to apply for team member role via form")
        message = await verification_channel.send(embed=embed)
        await message.add_reaction("👤")
        await message.add_reaction("📝")
    @commands.command()
    async def sc(self,ctx):
        '''In this we will delete the user forms'''
        member_id = {'team_id':ctx.author.name}
        collection.find_one_and_delete(member_id)

        
        

    # @commands.Cog.listener()
    # async def on_reaction_add(self, reaction, user):
    #     if user.bot:
    #         return
    #     if str(reaction.emoji) == "👥":
    #         role = discord.utils.get(user.guild.roles, name="Team")
    #         await user.add_roles(role)
    #     elif str(reaction.emoji) == "👤":
    #         role = discord.utils.get(user.guild.roles, name="Client")
    #         await user.add_roles(role)
    #         category = discord.utils.get(user.guild.categories, name="Users")
    #         channel = await category.create_text_channel(name=user.name)

async def setup(bot):
    await bot.add_cog(start(bot))