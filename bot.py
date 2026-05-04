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
if not ctx.message.attachments:
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
    mensaje = f"✅ {ctx.author.mention} registró {valor} APM 🔥\n"

if 150 <= valor <= 180:
    mensaje += "😮‍💨 Uff... necesitas trabajo por hacer."
elif 181 <= valor <= 250:
    mensaje += "🔥 Seguí así, aún queda camino."
elif 251 <= valor <= 349:
    mensaje += "🚀 Solo un poco más!"
elif 350 <= valor <= 399:
    mensaje += "💪 Estás en óptimas condiciones!"
elif valor >= 400:
    mensaje += "🥷 Manos asiáticas detectadas."
else:
    mensaje += "🌱 Empezando el camino, seguí metiéndole."

mensaje += "\n\n📅 Daily registrado. Volvé mañana para seguir subiendo en el ranking."

msg = await ctx.send(mensaje)

await msg.add_reaction("🔥")
await msg.add_reaction("🥸")
await msg.add_reaction("❓")


@bot.command()
async def dkey(ctx, valor: int):
    if not ctx.message.attachments:
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
    mensaje = f"✅ {ctx.author.mention} registró {valor} KeyReaction ⚡\n"

if valor >= 500:
    mensaje += "💀 Tienes cosas en común con mi tatarabuelo."
elif 450 <= valor <= 499:
    mensaje += "🔥 Vas por el buen camino invocador."
elif 400 <= valor <= 449:
    mensaje += "💪 Gracias por tu esfuerzo, sigue así."
elif 351 <= valor <= 399:
    mensaje += "🐱 Humano o felino?"
elif 200 <= valor <= 350:
    mensaje += "⚠️ No me gustaría tradear habilidades contigo."
else:
    mensaje += "🌱 Seguís en desarrollo, no aflojes."

mensaje += "\n\n📅 Daily registrado. Volvé mañana para seguir subiendo en el ranking."

msg = await ctx.send(mensaje)

await msg.add_reaction("🔥")
await msg.add_reaction("🥸")
await msg.add_reaction("❓")


    @bot.command()
async def daim(ctx, nivel: int, porcentaje: int):
    if not ctx.message.attachments:
        await ctx.send("❌ Tenés que subir una captura.")
        return

    if nivel < 1 or nivel > 10:
        await ctx.send("❌ Nivel inválido (1 a 10).")
        return

    if porcentaje < 0 or porcentaje > 100:
        await ctx.send("❌ Porcentaje inválido (0 a 100).")
        return

    data = cargar()
    user = str(ctx.author.id)
    asegurar_usuario(data, user)

    if not puede_enviar(data, user, "aim"):
        await ctx.send("❌ Ya enviaste Aim hoy.")
        return

    data[user]["aim"]["puntos"] += porcentaje
    data[user]["aim"]["ultimo_envio"] = hoy()

    if porcentaje > data[user]["aim"]["record"]:
        data[user]["aim"]["record"] = porcentaje

    guardar(data)

    mensaje = f"✅ {ctx.author.mention} registró Nivel {nivel} - {porcentaje}% 🎯\n"

    if 1 <= nivel <= 5:
        if porcentaje <= 90:
            mensaje += "😮‍💨 Sigue esforzándote."
        else:
            mensaje += "🔥 Sube al siguiente nivel!"

    elif 6 <= nivel <= 9:
        if porcentaje <= 80:
            mensaje += "💪 Puede que estés un tiempo en esta categoría, no te desanimes!"
        else:
            mensaje += "🚀 Sube al siguiente nivel!"

    elif nivel == 10:
        if porcentaje <= 80:
            mensaje += "⏳ Estás en la habitación del tiempo, no dejes de intentarlo."
        else:
            mensaje += "💀 Un verdadero jugador profesional!"

    mensaje += "\n\n📅 Daily registrado. Volvé mañana para seguir subiendo en el ranking."

    msg = await ctx.send(mensaje)

    await msg.add_reaction("🔥")
    await msg.add_reaction("🥸")
    await msg.add_reaction("❓")


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
