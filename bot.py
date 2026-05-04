import discord
from discord.ext import commands
import json
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ---------------- DATOS ---------------- #

def cargar():
    try:
        with open("datos.json", "r") as f:
            return json.load(f)
    except:
        with open("datos.json", "w") as f:
            json.dump({}, f)
        return {}


# ---------------- COMANDOS ---------------- #

@bot.command()
async def dapm(ctx, valor: int):
    if len(ctx.message.attachments) == 0:
        await ctx.send("❌ Tenés que subir una captura.")
        return

    data = cargar()
    user = str(ctx.author.id)
    asegurar_usuario(data, user)

    if not puede_enviar(data, user, "apm"):
        await ctx.send("❌ Ya enviaste tu APM hoy.")
        return

    data[user]["apm"]["puntos"] += valor
    data[user]["apm"]["ultimo_envio"] = hoy()

    if valor > data[user]["apm"]["record"]:
        data[user]["apm"]["record"] = valor

    guardar(data)
    await ctx.send(f"✅ {ctx.author.mention} registró {valor} APM 🔥")


@bot.command()
async def dkey(ctx, valor: int):
    if len(ctx.message.attachments) == 0:
        await ctx.send("❌ Tenés que subir una captura.")
        return

    data = cargar()
    user = str(ctx.author.id)
    asegurar_usuario(data, user)

    if not puede_enviar(data, user, "key"):
        await ctx.send("❌ Ya enviaste KeyReaction hoy.")
        return

    data[user]["key"]["puntos"] += valor
    data[user]["key"]["ultimo_envio"] = hoy()

    if valor > data[user]["key"]["record"]:
        data[user]["key"]["record"] = valor

    guardar(data)
    await ctx.send(f"✅ {ctx.author.mention} registró {valor} KeyReaction ⚡")


@bot.command()
async def daim(ctx, valor: int):
    if len(ctx.message.attachments) == 0:
        await ctx.send("❌ Tenés que subir una captura que validé tu información.")
        return

    data = cargar()
    user = str(ctx.author.id)
    asegurar_usuario(data, user)

    if not puede_enviar(data, user, "aim"):
        await ctx.send("❌ Ya enviaste Aim hoy.")
        return

    data[user]["aim"]["puntos"] += valor
    data[user]["aim"]["ultimo_envio"] = hoy()

    if valor > data[user]["aim"]["record"]:
        data[user]["aim"]["record"] = valor

    guardar(data)
    await ctx.send(f"✅ {ctx.author.mention} registró {valor} Aim 🎯")


# ---------------- RANKINGS ---------------- #

@bot.command()
async def ranking(ctx, tipo):
    data = cargar()

    if tipo not in ["apm", "key", "aim"]:
        await ctx.send("Usá: !ranking apm / key / aim")
        return

    ranking_ordenado = sorted(
        data.items(),
        key=lambda x: x[1][tipo]["puntos"],
        reverse=True
    )

    mensaje = f"🏆 Ranking {tipo.upper()}\n\n"

    for i, (user_id, stats) in enumerate(ranking_ordenado[:10], start=1):
        usuario = await bot.fetch_user(int(user_id))
        puntos = stats[tipo]["puntos"]
        record = stats[tipo]["record"]

        mensaje += f"{i}. {usuario.name} | {puntos} pts | récord {record}\n"

    await ctx.send(mensaje)


# ---------------- PERFIL ---------------- #

@bot.command()
async def me(ctx):
    data = cargar()
    user = str(ctx.author.id)

    if user not in data:
        await ctx.send("❌ Aún no tenés datos.")
        return

    def posicion(tipo):
        ranking = sorted(
            data.items(),
            key=lambda x: x[1][tipo]["puntos"],
            reverse=True
        )
        for i, (uid, _) in enumerate(ranking, start=1):
            if uid == user:
                return i
        return "?"

    def estado(tipo):
        return "✅" if data[user][tipo]["ultimo_envio"] == hoy() else "❌"

    apm = data[user]["apm"]
    key = data[user]["key"]
    aim = data[user]["aim"]

    mensaje = f"""
📊 {ctx.author.name}

🔥 APM
Puesto: {posicion("apm")}
Puntos: {apm["puntos"]}
Récord: {apm["record"]}
Hoy: {estado("apm")}

⚡ KEY
Puesto: {posicion("key")}
Puntos: {key["puntos"]}
Récord: {key["record"]}
Hoy: {estado("key")}

🎯 AIM
Puesto: {posicion("aim")}
Puntos: {aim["puntos"]}
Récord: {aim["record"]}
Hoy: {estado("aim")}
"""

    await ctx.send(mensaje)


# ---------------- TOP GLOBAL ---------------- #

@bot.command()
async def top(ctx):
    data = cargar()

    ranking_global = sorted(
        data.items(),
        key=lambda x: (
            x[1]["apm"]["puntos"] +
            x[1]["key"]["puntos"] +
            x[1]["aim"]["puntos"]
        ),
        reverse=True
    )

    mensaje = "🏆 TOP GLOBAL\n\n"

    for i, (user_id, stats) in enumerate(ranking_global[:10], start=1):
        usuario = await bot.fetch_user(int(user_id))
        total = (
            stats["apm"]["puntos"] +
            stats["key"]["puntos"] +
            stats["aim"]["puntos"]
        )

        mensaje += f"{i}. {usuario.name} | {total} pts\n"

    await ctx.send(mensaje)


# ---------------- BOT ---------------- #

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")


import os
bot.run(os.getenv("TOKEN"))
