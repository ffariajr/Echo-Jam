chars = []
for z in range(0,7):
	chars.append(chr(z + ord("a")))
wrds1 = ["minor", "major"]
wrds2 = ["flat", "sharp"]
chrds = []
for z in chars:
	chrds.append(z)
for z in chars:
	for y in wrds1:
		chrds.append(z + " " + y)
for z in chars:
	for y in wrds2:
		chrds.append(z + " " + y)
for z in chars:
	for y in wrds1:
		for x in wrds2:
			chrds.append(z + " " + x + " " + y)
allchrds = []
for z1 in chrds:
	for z2 in chrds:
		for z3 in chrds:
			for z4 in chrds:
				for z5 in chrds:
					allchrds.append(z1 + " " + z2 + " " + z3 + " " + z4 + " " + z5)
print(allchrds)