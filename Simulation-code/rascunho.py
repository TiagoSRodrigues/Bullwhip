class animal:
    def __init__(self,object, nome):
        self.name=nome
        object.animais_da_quinta.append(self)


class quinta:
    def __init__(self):
        self.animais_da_quinta=[]
        create_animal=animal(self,"rato")

monte=quinta()
print(monte.animais_da_quinta)