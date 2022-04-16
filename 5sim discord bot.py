import os, json, time, requests, discord, datetime, asyncio
from discord.utils import get
from discord.ext import commands, tasks
from datetime import datetime
global embedsms
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', case_insensitive=True, intents = intents)
bot.remove_command('help')

token = 'api-key-here'


Activation  =  False

headers = {
    
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
}

@bot.event
async def on_ready():
    print('Connected to bot: {}'.format(bot.user.name))
    print('Bot ID: {}'.format(bot.user.id))


@bot.command()
async def buy(ctx, country, operator, product):
    global embedsms, smsv
    def get_code():
        global embedsms
        r = json.loads(requests.get(f'https://5sim.net/v1/user/check/{str(dio["id"])}',headers=headers).text)
        if  len ( r [ 'sms' ]) ==  0 :
            return False
        else:
            try:
                global smsv
                for message in r['sms']:
                    smsv = message['text']
            except Exception as e:
                print(e)
                return False

            embedsms = discord.Embed(
                title = ':envelope_with_arrow: SMS received!',
                colour = discord.Color.green(),
                description = f'''
**Order ID:** {r['id']} 
**SMS:** {smsv}
**Product:** {r['product']}
**Status:** {r['status']}

Make sure you finish the order by doing `.finish (order ID)`
''')
            embedsms.timestamp = datetime.utcnow()
                    

    Activation = True
    while Activation:
        try:
            dio = requests.get(f'https://5sim.net/v1/user/buy/activation/{country}/{operator}/{product}', headers=headers)
     

            if dio.status_code == 200:
                dio = json.loads(dio.text)

                created_at = dio['created_at']
                expires = dio['expires']

                c = datetime.strptime(created_at.split('.')[0].replace('T', ' '), '%Y-%m-%d %H:%M:%S')
                e = datetime.strptime(expires.split('.')[0].replace('T', ' '), '%Y-%m-%d %H:%M:%S')
                delta = (e) - (c)
                time_in_seconds = delta.total_seconds()
                time_in_minutes = time_in_seconds / 60
                
                embed = discord.Embed(
                    title = ':white_check_mark: Success!',
                    colour = discord.Color.green(),
                    description = f'''
**Order ID:** {dio['id']}
**Country:** {dio['country']}
**Number:** {dio['phone']}
**Operator:** {dio['operator']}
**Price**: {dio['price']}
**Product:** {dio['product']}
**Expires:** {int(time_in_minutes)} mins
**Status:** {dio['status']}

Please wait for the SMS code, if you have not received it within a couple of minutes please cancel the order and try again
''')
                embed.timestamp = datetime.utcnow()
                await ctx.send(embed=embed)
                Activation = False
                get_code()
                while get_code() == False:
                    await asyncio.sleep(0.10)
                    pass
                await ctx.send(f'{ctx.author.mention}',embed=embedsms)

            else:
                embed = discord.Embed(
                    title = ':x: Error!',
                    colour = discord.Color.red(),
                    description = f'{dio.text}')
                embed.timestamp = datetime.utcnow()
                await ctx.send(embed=embed)
                return
                
        except Exception as e:
            embed = discord.Embed(
                title = ':x: Error!',
                colour = discord.Color.red(),
                description = f'{e}')
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed)
            return False
            

@buy.error
async def buy_error(ctx, error):
    raise error


@bot.command()
async def cancel(ctx, oid):
    r = requests.get(f'https://5sim.net/v1/user/cancel/{oid}', headers=headers)
    
    if r.status_code == 200:
        r = json.loads(r.text)
        embed = discord.Embed(
            title = ':no_entry: Canceled!',
            colour = discord.Color.red(),
            description = f'''
**Order ID:** {r['id']}
**Country:** {r['country']}
**Number:** {r['phone']}
**Price**: {r['price']}
**Product:** {r['product']}
**Status:** {r['status']}

Order has been successfully canceled
''')
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)
        return
    else:
        embed = discord.Embed(
            title = ':x: Error!',
            colour = discord.Color.red(),
            description = f'Order not found')
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)
        return
        

   
@cancel.error
async def cancel_error(ctx, error):
    raise error


@bot.command()
async def finish(ctx, oid):
    r = requests.get(f'https://5sim.net/v1/user/finish/{oid}', headers=headers)
    
    if r.status_code == 200:
        r = json.loads(r.text)
        embed = discord.Embed(
            title = ':white_check_mark: Finished!',
            colour = discord.Color.green(),
            description = f'''
**Order ID:** {r['id']}
**Country:** {r['country']}
**Number:** {r['phone']}
**Price**: {r['price']}
**Product:** {r['product']}
**Status:** {r['status']}
''')
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)
        return
    else:
        embed = discord.Embed(
            title = ':x: Error!',
            colour = discord.Color.red(),
            description = f'Order not found')
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)
        return
        


@finish.error
async def finish_error(ctx, error):
    raise error




@bot.command()
async def check(ctx, oid):
    r = requests.get(f'https://5sim.net/v1/user/check/{oid}', headers=headers)

    if r.status_code == 200:
        r = json.loads(r.text)
        embed = discord.Embed(
            title = f':white_check_mark: Checking order: {oid}',
            colour = discord.Color.green(),
            description = f'''
**Order ID:** {r['id']}
**Country:** {r['country']}
**Number:** {r['phone']}
**Price**: {r['price']}
**Product:** {r['product']}
**Status:** {r['status']}
''')
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)
        return
    else:
        embed = discord.Embed(
            title = ':x: Error!',
            colour = discord.Color.red(),
            description = f'Order not found')
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)
        return


@check.error
async def check_error(ctx, error):
    raise error


@bot.command()
async def balance(ctx):
    r = json.loads(requests.get(f'https://5sim.net/v1/user/profile', headers=headers).text)

    embed = discord.Embed(
        title = ':moneybag: Balance',
        description = f'''{r['balance']}''')
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title = 'All Commands',
        description = f'''
.buy (country) (operator) (product) - buys phone number
.cancel (order ID) - cancels order you have made
.finish (order ID) - finishs order after you have received phone number
.check (order ID) - checks the order's status
.balance - checks the account's balance
''')
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)

   
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord. Activity(type=discord.ActivityType.listening, name='5sim.net'))
    
    print('Connected to bot: {}'.format(bot.user.name))
    print('Bot ID: {}'.format(bot.user.id))   
    
bot.run('bot token here')
