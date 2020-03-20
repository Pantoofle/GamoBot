import discord

class Table():
    def __init__(self):
        self.name = None
        self.txt_channel = None
        self.vocal_channel = None
        self.category = None
        self.open = False
        self.players = []

    async def start(self):
        await self.txt_channel.send("La table est créée : " + " ".join([p.mention for p in self.players]))
        await self.txt_channel.send("Par défaut, la visibilité est sur Fermé. Pour permettre à d'autres de rejoindre, entrez `!open`, pour refermer la table utilisez `!close`")

    async def add_player(self, user):
        self.players.append(user)
        await self.update_permissions()
        await self.txt_channel.send("Nouveau joueur en vue : " + user.mention)

    async def update_permissions(self):
        for p in self.players:
            await self.category.set_permissions(p, read_messages=True)
