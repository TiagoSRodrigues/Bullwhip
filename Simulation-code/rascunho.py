import supply_chain as sc

a=sc.supply_chain()
a.add_to_supply_chain("2")

a.add_to_supply_chain("2")
a.add_to_supply_chain("4")
a.add_to_supply_chain("3")
a.add_to_supply_chain("5")



q=a.get_supply_chain()
print(q)

a.show_supply_chain()


