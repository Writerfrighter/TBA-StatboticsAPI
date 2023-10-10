import TBA

list = TBA.fetchEventOprs("2023wasam")["ccwms"]
for team in list.keys():
    print("Team {} has ccwms {}.".format(team, list[team]))