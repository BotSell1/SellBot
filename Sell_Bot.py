import os
from dotenv import load_dotenv
import discord
from discord.ext import commands


load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_MTMzNDcxODAzNDQwMDY0MTExNQ.GU61Y0.4vNfSPgRzGosXAyg-WhZqGBURX0EhLi1GV-U8M')


intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

# Initialize the bot
bot = commands.Bot(command_prefix='!', intents=intents)
money = {}
prices = {"item_1": 5000, "item_2": 7000, "item_3": 9000}
purchased_items = {}
button_labels = {"item_1": "구매항목 1", "item_2": "구매항목 2", "item_3": "구매항목 3"}
product_texts = {"item_1": "블피 현질 50000로벅 계정", "item_2": "구매 항목 2 설명", "item_3": "구매 항목 3 설명"}
dm_texts = {"item_1": "구매항목 1을 구매했습니다.", "item_2": "구매항목 2를 구매했습니다.", "item_3": "구매항목 3을 구매했습니다."}

# MainView class
class MainView(discord.ui.View):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.green, label="구매", custom_id="buy_button"))
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.green, label="충전", custom_id="charge_button"))
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.green, label="제품", custom_id="product_button"))

# BuyView class
class BuyView(discord.ui.View):
    def __init__(self, user):
        super().__init__()
        self.user = user

        for item in prices:
            label = button_labels[item]
            disabled = user.id in purchased_items and item in purchased_items[user.id]
            self.add_item(discord.ui.Button(style=discord.ButtonStyle.green, label=label, custom_id=item, disabled=disabled))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.name == '자판기💎':
        view = MainView(message.author)
        sent_message = await message.channel.send(f'환영합니다, {message.author.mention}! 아래 버튼 중 하나를 선택하세요.', view=view)
        
        def check(m):
            return m.channel == message.channel and m.author == message.author
        
        while True:
            try:
                response = await bot.wait_for('message', check=check)
                if response:
                    break
            except Exception as e:
                break
        
        await sent_message.delete()

    await bot.process_commands(message)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    await interaction.response.defer()

    custom_id = interaction.data['custom_id']
    if custom_id == "buy_button":
        view = BuyView(interaction.user)
        await interaction.followup.send("원하시는 항목을 선택해주세요.", view=view, ephemeral=True)
    elif custom_id == "charge_button":
        await interaction.followup.send("KB국민은행 75289072720232, 티켓 후 이름과 이중창", ephemeral=True)
    elif custom_id == "product_button":
        product_text = "아래 텍스트를 확인해주세요:\n\n" + "\n".join([f"{button_labels[key]} {product_texts[key]}" for key in product_texts])
        await interaction.followup.send(product_text, ephemeral=True)
    elif custom_id in prices:
        item_id = custom_id
        price = prices[item_id]
        if interaction.user.id in money and money[interaction.user.id] >= price:
            money[interaction.user.id] -= price
            if interaction.user.id not in purchased_items:
                purchased_items[interaction.user.id] = []
            purchased_items[interaction.user.id].append(item_id)
            await interaction.user.send(dm_texts[item_id])
            view = BuyView(interaction.user)
            await interaction.followup.edit_message(message_id=interaction.message.id, content="구매 완료! 버튼이 비활성화되었습니다.", view=view)
        else:
            await interaction.followup.send("잔액이 부족합니다.", ephemeral=True)
    elif custom_id in product_texts:
        await interaction.followup.send(product_texts[custom_id], ephemeral=True)

# Ensure the 'add' command has the correct permission decorator
@bot.command()
@commands.has_permissions(administrator=True)  # 관리자 권한 확인
async def add(ctx, member: discord.Member, amount: int):
    if member.id not in money:
        money[member.id] = 0
    money[member.id] += amount
    await ctx.send(f'{member.mention}에게 {amount} 원이 추가되었습니다. 현재 잔액: {money[member.id]} 원')

@bot.command()
@commands.has_permissions(administrator=True)  # 관리자 권한 확인
async def set(ctx, item: str, price: int):
    prices[item] = price
    await ctx.send(f'{item}의 가격이 {price} 원으로 설정되었습니다.')

@bot.command()
@commands.has_permissions(administrator=True)  # 관리자 권한 확인
async def set_label(ctx, item: str, *, name: str):
    if item in button_labels:
        button_labels[item] = name.replace('{', '').replace('}', '')
        product_texts[item] = ""
        await ctx.send(f'{item}의 레이블이 "{button_labels[item]}"으로 설정되었고, 해당 항목의 기존 텍스트는 삭제되었습니다.')
    else:
        await ctx.send(f'{item}이(가) 존재하지 않습니다.')

@bot.command()
@commands.has_permissions(administrator=True)  # 관리자 권한 확인
async def set_product_text(ctx, item: str, *, text: str):
    if item in product_texts:
        product_texts[item] = text
        await ctx.send(f'{item}의 제품 설명이 "{product_texts[item]}"으로 설정되었습니다.')
    else:
        await ctx.send(f'{item}이(가) 존재하지 않습니다.')

@bot.command()
@commands.has_permissions(administrator=True)  # 관리자 권한 확인
async def reset_purchase(ctx, member: discord.Member, item: str):
    if member.id in purchased_items and item in purchased_items[member.id]:
        purchased_items[member.id].remove(item)
        await ctx.send(f'{member.mention}의 {item} 구매 항목 버튼이 재활성화되었습니다.')
    else:
        await ctx.send(f'{member.mention}은(는) {item}을(를) 구매하지 않았습니다.')

@bot.command()
@commands.has_permissions(administrator=True)  # 관리자 권한 확인
async def reset_all_purchases(ctx, item: str):
    for user_id in purchased_items:
        if item in purchased_items[user_id]:
            purchased_items[user_id].remove(item)
    await ctx.send(f'모든 사용자의 {item} 구매 항목 버튼이 재활성화되었습니다.')


