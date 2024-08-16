import os
import discord
from discord.ext import commands
from keep_alive import keep_alive
keep_alive()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="%", intents=intents)

raid_mode = False
verification_channel_id = None
verification_role_id = None
anti_raid_measures_active = True

admin_role_ids = [
    1164191308970197063,  # Head Admin
    1164248097224937563,  # Senior Admin
    1164216899169681408   # Normal Admin
]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.command()
async def raidhelp(ctx):
    global raid_mode
    raid_mode = not raid_mode
    status = "activated" if raid_mode else "deactivated"
    await ctx.send(f"Raid mode is now {status}.")

@bot.command()
async def startverification(ctx):
    await ctx.send("Please provide the channel ID where you want to implement the verification system using the `%id <channel_id>` command.")

@bot.command()
async def id(ctx, channel_id: int):
    global verification_channel_id
    verification_channel_id = channel_id
    await ctx.send(f"Verification system has been set up in the channel with ID {channel_id}.")

@bot.command()
async def verificationrole(ctx, role_id: int):
    global verification_role_id
    verification_role_id = role_id
    await ctx.send(f"Verification role has been set with ID {role_id}.")

@bot.command()
async def startmeasures(ctx):
    global anti_raid_measures_active
    anti_raid_measures_active = True
    await ctx.send("Anti-raid measures have been activated.")

@bot.command()
async def stopmeasures(ctx):
    global anti_raid_measures_active
    anti_raid_measures_active = False
    await ctx.send("Anti-raid measures have been deactivated.")

@bot.event
async def on_member_join(member):
    if anti_raid_measures_active and verification_channel_id:
        channel = bot.get_channel(verification_channel_id)
        if channel:
            await channel.send(f"Welcome {member.mention}! Please introduce yourself. Due to recent raids, a verification system has been implemented. Your introduction must be reviewed by at least 2 admins before you get verified. If anyone gives you the admin role before your application is reviewed, they will be kicked or banned.")

@bot.event
async def on_member_update(before, after):
    if anti_raid_measures_active:
        # Check if the member has received an admin role
        new_roles = set(after.roles) - set(before.roles)
        for role in new_roles:
            if role.id in admin_role_ids:
                # Check if the member has the verification role
                if verification_role_id and verification_role_id not in [r.id for r in after.roles]:
                    # Ban the member who received admin without verification
                    try:
                        await after.ban(reason="Received admin role without verification.")
                        print(f"Banned {after.name}#{after.discriminator} for receiving admin without verification.")
                    except Exception as e:
                        print(f"Failed to ban {after.name}#{after.discriminator}: {e}")
                else:
                    # Kick the person who gave the admin role
                    audit_logs = await after.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update).flatten()
                    if audit_logs:
                        log_entry = audit_logs[0]
                        if log_entry.target.id == after.id and log_entry.user.id != after.id:
                            try:
                                await log_entry.user.kick(reason="Granted admin role to a member awaiting verification.")
                                print(f"Kicked {log_entry.user.name}#{log_entry.user.discriminator} for granting admin role to unverified member.")
                            except Exception as e:
                                print(f"Failed to kick {log_entry.user.name}#{log_entry.user.discriminator}: {e}")

@bot.event
async def on_invite_create(invite):
    if raid_mode:
        try:
            await invite.delete(reason="Automatic invite revoke due to raid mode.")
            print(f"Revoked invite {invite.url}")
        except Exception as e:
            print(f"Failed to revoke invite {invite.url}: {e}")

bot.run(os.getenv('DISCORD_TOKEN'))
