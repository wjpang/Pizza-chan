import disnake


class EmbedMaker:
    """Creates a disnake embed"""

    def __init__(self, title, url, description, color, name, picture):
        self.embed = disnake.Embed(title=title, url=url, description=description, color=color)
        self.embed = self.embed.set_author(name=name)
        if "http" in picture:
            self.embed = self.embed.set_thumbnail(url=picture)
        else:
            self.embed = self.embed.set_thumbnail(file=disnake.File(picture))
