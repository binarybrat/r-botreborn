from custom_embeds import *
from rbotreborn import bot

"""

testing commands for things

"""


@bot.command(pass_context=True)
async def test_images(ctx, url: str):
    await bot.delete_message(ctx.message)
    embed = RedditPostEmbed()
    embed.create_embed(title="This is a test post for testing images from the link you provided",
                       image=url)
    await bot.say(embed=embed.get_embed())
