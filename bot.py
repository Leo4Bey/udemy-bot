import discord
from discord.ext import commands
import os
from discord import ui
from config import *
import random
import pymongo
from discord.ui import Button, View


client = pymongo.MongoClient(url)
db = client.user_data


class LeoButtonListener(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.members = True
        intents.messages = True

        super().__init__(command_prefix=commands.when_mentioned_or(prefix), intents=intents)

    async def setup_hook(self) -> None:
        self.add_view(Merrhaba())
        self.add_view(BanButton())
        self.add_view(YetkiliButton())
        self.add_view(YetkiliOnayRed())

bot = LeoButtonListener()


class YetkiliOnayRed(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Onayla", style=discord.ButtonStyle.green, custom_id="leo_yetkili_onay")
    async def yetkili_basvuru_onayla(self, interaction:discord.Interaction, button: discord.ui.Button):
        yonetici_role = interaction.guild.get_role(yonetici)
        if yonetici_role not in interaction.user.roles:
            await interaction.response.send_message("Bu butona basma yetkin yok", ephemeral=True)
        else:
            yetkili_role = interaction.guild.get_role(yetkili)
            basvuru_sonuc = interaction.guild.get_channel(basvuru_durum)
            hex = {"message_id": interaction.message.id}
            basvuru_list = db.basvuru.find(hex)
            for i in basvuru_list:
                user_id = i['user_id']
            embed = discord.Embed(
                title="Onaylandı",
                description=f"**kullanıcı ID**: ``{user_id}``\n\n**Onaylayan Yetkili**: {interaction.user.mention}\n**Yetkili ID**: ``{interaction.user.id}``",
                colour= discord.Colour.green()
            )
            await interaction.message.edit(embed=embed, view=None)
            member = interaction.guild.get_member(user_id)
            await member.add_roles(yetkili_role)
            await basvuru_sonuc.send(f"{member.mention} (``{member.id}``) başvurun {interaction.user.mention} (``{interaction.user.id}``) tarafından **onaylandı** :white_check_mark: ")
            await db.basvuru.delete_one(hex)
            await interaction.response.send_message("Başvuru başarıyla onaylandı", ephemeral=True)


    @discord.ui.button(label="Reddet", style=discord.ButtonStyle.red, custom_id="leo_yetkili_red")
    async def yetkili_basvuru_reddet(self, interaction:discord.Interaction, button: discord.ui.Button):
        yonetici_role = interaction.guild.get_role(yonetici)
        if yonetici_role not in interaction.user.roles:
            await interaction.response.send_message("Bu butona basma yetkin yok", ephemeral=True)
        else:
            basvuru_sonuc = interaction.guild.get_channel(basvuru_durum)
            hex = {"message_id": interaction.message.id}
            basvuru_list = db.basvuru.find(hex)
            for i in basvuru_list:
                user_id = i['user_id']
            embed = discord.Embed(
                title="Reddedildi",
                description=f"**kullanıcı ID**: ``{user_id}``\n\n**Reddeden Yetkili**: {interaction.user.mention}\n**Yetkili ID**: ``{interaction.user.id}``",
                colour= discord.Colour.red()
            )
            await interaction.message.edit(embed=embed, view=None)
            await basvuru_sonuc.send(f"<@{user_id}> (``{user_id}``) başvurun {interaction.user.mention} (``{interaction.user.id}``) tarafından **reddedildi**:x:")
            await db.basvuru.delete_one(hex)
            await interaction.response.send_message("Başvuru başarıyla reddedildi", ephemeral=True)

class LeoModal(ui.Modal, title="Leo4Code Başvuru Sistemi"):
    ad = ui.TextInput(label="adın",placeholder="Leo...", style=discord.TextStyle.short, min_length=3)
    soyad = ui.TextInput(label="soyadın",placeholder="demir...", style=discord.TextStyle.short, min_length=3)
    yas = ui.TextInput(label="yaşın",placeholder="25", style=discord.TextStyle.short, min_length=2, max_length=2)
    neden = ui.TextInput(label="Neden biz?",placeholder="çok süpersiniz...", style=discord.TextStyle.long, min_length=100, max_length=1000)

    async def on_submit(self, interaction: discord.Interaction):
        basvuru_log_channel = interaction.guild.get_channel(basvuru_log)
        embed = discord.Embed(
            title="Leo4Code Başvuru Sistemi",
            description=f"**Adı**: ``{self.ad}``\n**Soyadı**: ``{self.soyad}``\n**Yaşı**: ``{self.yas}``\n**Neden Biz**: ``{self.neden}``",
            colour=discord.Colour.random()
        )
        view = YetkiliOnayRed()
        message = await basvuru_log_channel.send(embed=embed, view=view)
        db.basvuru.insert_one({
            "message_id": message.id,
            "user_id": interaction.user.id,
        })
        await interaction.response.send_message(f"Başvuru başarıyla alındı sonuçları <#{basvuru_durum}> kanalından takip edebilirsin", ephemeral=True)


class Merrhaba(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Merhaba", style=discord.ButtonStyle.blurple, custom_id="leo_merhaba")
    async def merrhaba(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"Sana da merhaba {interaction.user.mention}")

class YetkiliButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Başvuru Yap", style=discord.ButtonStyle.green, custom_id="leo_yetkili_button")
    async def yetkili_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        yetkili_role = interaction.guild.get_role(yetkili)
        if yetkili_role in interaction.user.roles:
            await interaction.response.send_message("Zaten yetkilisin!", ephemeral=True)
        else:
            await interaction.response.send_modal(LeoModal())

class BanButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="İptal Et", style=discord.ButtonStyle.red, custom_id="leo_ban_iptal")
    async def ban_iptal(self, interaction:discord.Interaction, button: discord.ui.Button):
        hex = {"msg_id": interaction.message.id}
        ban_check_list = db.ban_check.find(hex)
        for i in ban_check_list:
            staff_id = i['staff_id']
        if interaction.user.id != staff_id:
            await interaction.response.send_message("Bu butona basma yetkin yok", ephemeral=True)
        else:
            embed = discord.Embed(
                title="Banlama İptal Edildi",
                description=f"Ban işlemi {interaction.user.mention} (``{interaction.user.id}``) tarafından iptal edildi",
                colour=discord.Colour.random()
            )
            await interaction.response.edit_message(embed=embed, view=None)
            await db.ban_check.delete_one(hex)
     
    @discord.ui.button(label="Onayla", style=discord.ButtonStyle.green, custom_id="leo_ban_onay")
    async def ban_onay(self, interaction:discord.Interaction, button: discord.ui.Button):
        hex = {"msg_id": interaction.message.id}
        log_channel = interaction.guild.get_channel(ban_log)
        ban_check_list = db.ban_check.find(hex)
        for i in ban_check_list:
            staff_id = i['staff_id']
            member_id = i['member_id']
            sebep = i['sebep']
        if interaction.user.id != staff_id:
            await interaction.response.send_message("Bu butona basma yetkin yok", ephemeral=True)
        else:
            embed = discord.Embed(
                title="Banlama Başarılı",
                description=f"<@{member_id}> (``{member_id}``) kullanıcısı <@{staff_id}> (``{staff_id}``) tarafından **{sebep}** sebebiyle sunucudan yasaklandı",
                colour=discord.Colour.random()
            )
            member = interaction.guild.get_member(member_id)
            await member.ban(reason=f"{sebep} | {interaction.user.global_name} ({interaction.user.id})")
            await interaction.response.edit_message(embed=embed, view=None)
            await log_channel.send(embed=embed)
            await db.ban_check.delete_one(hex)

class LeoMenu(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(dropdown())

class dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="A", value=1, description="A seçeneği"),
            discord.SelectOption(label="B", value=2, description="B seçeneği"),
            discord.SelectOption(label="C", value=3, description="C seçeneği"),
        ]
        super().__init__(placeholder="Bir şık seçiniz", options=options, min_values=1, max_values=2)

    async def callback(self, interaction: discord.Interaction):
        selected_value = int(self.values[0])
        selected_option = self.options[selected_value-1]
        label = selected_option.label
        await interaction.response.send_message(f"``{label}`` şıkkını seçtin", ephemeral=True)

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')


@bot.event
async def on_member_join(member):
    welcome_channel = bot.get_channel(1263452785962389565)
    welcome_role = member.guild.get_role(1263453415036682260)
    await welcome_channel.send(f"<@{member.id}> sunucumuza hoş geldin")
    await member.add_roles(welcome_role)

@bot.event
async def on_member_remove(member):
    babay_channel = bot.get_channel(1263452800264700027)
    await babay_channel.send(f"<@{member.id}> üyesi aramızdan ayrıldı")

@bot.event
async def on_message(msg):
    if msg.content.lower() == "sa":
        await msg.channel.send(f"Aleyküm selam hoş geldin <@{msg.author.id}>")
    await bot.process_commands(msg)

@bot.tree.command(name="modal", description="modal gönderir")
async def modal_gonder(interaction:discord.Interaction):
    await interaction.response.send_modal(LeoModal())


@bot.tree.command(name="yetkili-basvuru", description="Yetkililerin başvurması içinn butonn oluşturur")
async def yetkili_basvuru(interaction:discord.Interaction):
    yetkili_role = interaction.guild.get_role(yetkili)
    if yetkili_role not in interaction.user.roles:
        await interaction.response.send_message(f"Bu komutu kullanmak için {yetkili_role.mention} rolün esahip olmalısın", ephemeral=True)
    else:
        embed = discord.Embed(
            title="Yetkili Başvuru Sistemi",
            description="Yetkili ekibimize katılmak için aşağıdaki butona tıklayarak başvuru yapabilirsiniz.",
            colour=discord.Colour.random()
        )
        view = YetkiliButton()
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("yetkili başvuru mesajı başarıyla gönderildi", ephemeral=True)


@bot.tree.command(name="ban", description="Seçtiğiniz üyeyi sunucudan yasaklar")
async def ban(interaction:discord.Interaction, member:discord.Member, sebep:str = "Sebep belirtilmemiş"):
    ban_yetkili = interaction.guild.get_role(yetkili)
    if ban_yetkili not in interaction.user.roles:
        await interaction.response.send_message(f"Bu komutu kullanmak için {ban_yetkili.mention} yetkisine sahip olmalısın", ephemeral=True)
    else:
        if member == None:
            await interaction.response.send_message("Geçersiz kullanıcı", ephemeral=True)
        else:
            embed = discord.Embed(
                title="Banlama İşlemi Bekleniyor",
                description=f"{member.mention} (``{member.id}``) kullanıcısını ``{sebep}`` sebebinden dolayı banlamak istiyorsun işlemi onaylıyorsann **Onayla**, iptal etmek istiyorsan **İptal** butonuna basabilirsin",
                colour= discord.Colour.random()
            )
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_icon)
            view = BanButton()
            await interaction.response.send_message(embed=embed, view=view)
            msg = await interaction.original_response()
            db.ban_check.insert_one({
                "staff_id": interaction.user.id,
                "member_id": member.id,
                "msg_id": msg.id,
                "sebep": sebep
            })

@bot.tree.command(name="dropdown", description="dropdown menü gönderir")
async def drpdown(interaction: discord.Interaction):
    await interaction.response.send_message("seçenekler", view=LeoMenu())

@bot.tree.command(name="buton", description="buton kullanım örneği")
async def command_button(interaction: discord.Interaction):
    merhaba_button = Button(label="Merhaba", style=discord.ButtonStyle.blurple, custom_id="leo_merhaba")
    async def merhaba_button_callback(interaction:discord.Interaction):
        await interaction.response.send_message(f"sana da merhaba {interaction.user}")
    merhaba_button.callback = merhaba_button_callback
    view = View(timeout=60)
    view.add_item(merhaba_button)
    await interaction.response.send_message(content="Merhaba", view=view)

@bot.tree.command(name="embed", description="embed gönderir")
async def embed(interaction:discord.Interaction):
    pp = interaction.user.avatar
    embed = discord.Embed(
        title="Bu bir başlık",
        description="Bu bir açıklama",
        colour=discord.Colour.dark_orange()
    )
    embed.set_author(name="Leo4Code", url="https://www.youtube.com/@Leo4Code")
    embed.add_field(name="Youtube Kanalım", value="https://www.youtube.com/@Leo4Code")
    embed.add_field(name="Websitem", value="https://leo4bey.net")
    embed.set_image(url="https://cdn.discordapp.com/attachments/1253437172262899807/1273935850237067294/coding.gif?ex=66c06cb7&is=66bf1b37&hm=0bbb6a291ca90ac7cb3c47b9b9da7baaaf75ec95cabb2a5389ae4cf49732b84e&")
    embed.set_thumbnail(url=pp)
    embed.set_footer(text=f"{interaction.user.name} tarafından kullanıldı", icon_url=pp)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="merhaba-deneme", description="deneme buton gönderir")
async def merhaba_deneme(interaction:discord.Interaction):
    embed = discord.Embed(
        title="deneme",
        description="deneme",
        colour = discord.Colour.blurple()
    )
    view = Merrhaba()
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="ping", description="pong gönderir")
async def ping(interaction:discord.Interaction):
    await interaction.response.send_message("pong", ephemeral=True)

@bot.command(name="zar")
async def zar(ctx):
    rastgele_sayi = random.randint(1,6)
    await ctx.send(f"Çıkan sayı: {rastgele_sayi}")


@bot.command(name="sil")
async def sil(ctx):
    limit = 5
    await ctx.channel.purge(limit=limit)
    await ctx.channel.send(f"Son ``{limit}`` adet mesaj silindi")

@bot.event
async def on_ready():
    await load()
    try:
        synced = await bot.tree.sync()
        print(f'Entegre edilen slash komut sayısı {len(synced)}')
    except Exception as e:
        print(f'hata: {e}')
    print(f"{bot.user.name} Aktif oldu")
    await bot.change_presence(activity=discord.Streaming(name="Twitch kanalım", url="https://www.twitch.tv/foolish"))

bot.run(token)