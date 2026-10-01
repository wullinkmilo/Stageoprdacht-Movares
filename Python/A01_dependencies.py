import json

if __name__ == "__main__":
    dependencies = {}
    for i in list(range(58, 74)) + list(range(76, 95)) + list(range(97, 99)) \
        + list(range(109, 125)) + list(range(127, 147)) + list(range(149, 151)) \
            + list(range(158, 172)) + list(range(174, 185)) + [187] \
                + list(range(195, 199)) + [201, 204] \
                    + list(range(212, 216)) + [218, 221]:
        dependencies[i] = [i]

    # Dependencies for masonry substructure
    dependencies[221] = list(range(212, 216)) + [218, 221]
    dependencies[218] = [218, 215]

    # Dependencies for concrete substructure
    dependencies[204] = list(range(195, 199)) + [201, 204]
    dependencies[201] = [201, 198]

    # Dependencies for masonry superstructure
    dependencies[187] = list(range(158, 172)) + list(range(174, 185)) + [187]
    dependencies[183] = [183, 177, 171, 167]
    dependencies[182] = [182, 176, 170, 166]
    dependencies[181] = [181, 175, 169, 165]
    dependencies[180] = [180, 174, 168, 164]
    dependencies[179] = [179, 163]
    dependencies[178] = [178, 162]
    dependencies[177] = [177, 171]
    dependencies[176] = [176, 170]
    dependencies[175] = [175, 169]
    dependencies[174] = [174, 168]

    # Dependencies for concrete superstructure
    dependencies[150] = [150, 131, 120, 114]
    dependencies[131] = [131, 120]

    dependencies[149] = [dependency for dependency in (list(range(109, 125)) + list(range(127, 147)) + list(range(149, 151))) if dependency not in {150, 131, 120, 114}]
    dependencies[141] = [141, 135, 124, 119]
    dependencies[140] = [140, 134, 123, 118]
    dependencies[139] = [139, 133, 122, 117]
    dependencies[138] = [138, 132, 121, 116]
    dependencies[137] = [137, 115]
    dependencies[136] = [136, 113]
    dependencies[135] = [135, 124]
    dependencies[134] = [134, 123]
    dependencies[133] = [133, 122]
    dependencies[132] = [132, 121]

    # Dependencies for steel superstructure
    dependencies[98] = [98, 81, 69, 63]
    dependencies[81] = [81, 69]

    dependencies[97] = [dependency for dependency in (list(range(58, 74)) + list(range(76, 95)) + list(range(97, 99))) if dependency not in {98, 81, 69, 63}]
    dependencies[89] = [89, 85, 73, 67]
    dependencies[88] = [88, 84, 72, 66]
    dependencies[87] = [87, 83, 71, 65]
    dependencies[86] = [86, 82, 70, 64]
    dependencies[85] = [85, 73]
    dependencies[84] = [84, 72]
    dependencies[83] = [83, 71]
    dependencies[82] = [82, 70]
    dependencies[80] = [80, 68]
    dependencies[62] = [62] # Maybe needs to change t0 [62, 65, 66]

    # Save the dependencies to a JSON file
    json.dump(dependencies, open("dependencies.json", "w"), indent=4, default=int)