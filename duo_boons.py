import json
import itertools

gods = sorted([
    "Zeus", "Demeter", "Hermes", "Aphrodite", "Ares", "Poseidon", "Athena", "Artemis", "Dionysus"
])
duo_gods = sorted(set(gods) - {"Hermes"})

BASIC_BOON_TYPES = ["WeaponTrait", "SecondaryTrait", "RangedTrait", "RushTrait", "ShoutTrait"]

BASIC_BOONS = {
    god + t: god
    for god in gods
    for t in BASIC_BOON_TYPES
}

god_colors = {
    "Zeus": "#ffe85b",
    "Demeter": "#e4ebfe",
    "Hermes": "#9d7556",
    "Aphrodite": "#dd6ac0",
    "Ares": "#eb687a",
    "Poseidon": "#0097ce",
    "Athena": "#bbaf67",
    "Artemis": "#74c34c",
    "Dionysus": "#7d7ac5",
}

def with_opacity(col, o):
    rgb = tuple(int(col.removeprefix("#")[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba{rgb + (o,)}"


with open("trait_data.json") as f:
    traits = json.load(f)

def icon(trait):
    path = traits[trait]["icon"]
    path = path.replace("Dionysus_Artemis_01", "Dionyuss_Artemis_01") # Lol...
    if path.startswith("Boon_"):
        path = path.removeprefix("Boon_")
        if "00" in path:
            path = path.replace("00", "secondary_attack")
        else:
            path += "_Large"
    
    return f"BoonIcons/{path}.png"


no_beowulf_duos = {
    'Blizzard Shot', 'Cold Embrace', 'Crystal Clarity', 'Hunting Blades', 'Lightning Phalanx', 'Parting Shot', 'Scintillating Feast'
} 
caveats = [
    (no_beowulf_duos, "Incompatible with Aspect of Beowolf."),
    ({"Curse of Drowning"}, "Incompatible with Aspect of Hera."),
    ({"Smoldering Air"}, "Requires a non-Hades Aid boon."),
    ({"Vengeful Mood"}, "Requires a Revenge boon."),
    ({"Curse of Drowning", "Blizzard Shot", "Ice Wine"}, "Curse of Drowning, Blizzard Shot and Ice Wine are all incompatible with each other."),
    ({"Curse of Drowning", "Mirage Shot"}, "Mirage Shot and Curse of Drowning can't be combined."),
    ({"Hunting Blades", "Freezing Vortex"}, "Hunting Blades and Freezing Vortex can't be combined."),
    ({"Cold Embrace", "Crystal Clarity"}, "Cold Embrace and Crystal Clarity can't be combined."),
    ({"Parting Shot"}, "Parting Shot and Trippy Shot can't be combined."),
    ({"Lightning Rod"}, "Incompatible with Stygian Soul."),
    ({"Splitting Headache"}, "Hunter's Flare does not count towards Splitting Headache."),
]

other_boon_reqs = {
    "Cold Fusion": "Zeus Boon: Static Discharge.",
    "Curse of Nausea": "(or Curse of Vengeance)"
}

out = []
for godnr, god1 in enumerate(sorted(duo_gods)):
    out.append(f"""<table class="duotable" cellspacing="0" style="grid-area: god{godnr}; background: {with_opacity(god_colors[god1], 0.3)}">""")

    for god2 in sorted(set(duo_gods) - {god1}):

        duo_trait = next(t for t in traits.values() if set(t["gods"]) == {god1, god2})
        
        all_simple_same_god = lambda ts: all(t in BASIC_BOONS for t in ts) and len(set(BASIC_BOONS[t] for t in ts)) == 1
        simple = [all_simple_same_god(ts) for ts in duo_trait["prereq_data"]]

        out.append(f"""<tr class="godrow">""")

        for base in BASIC_BOON_TYPES:
            for i, prereq_god in enumerate([god1, god2]):
                trait = prereq_god + base

                if (
                    prereq_god == "Zeus" and duo_trait["name"] == "Cold Fusion"
                    or prereq_god == "Ares" and duo_trait["name"] == "Curse of Nausea" and not (base in ["WeaponTrait", "SecondaryTrait"])
                ):
                    out.append("<td>")
                    if prereq_god == "Zeus" and base == "WeaponTrait" or prereq_god == "Ares" and base == "RangedTrait":
                        out.append(f"""<div class="other-boon-req{i} other-{prereq_god.lower()}">{other_boon_reqs[duo_trait["name"]]}</div>""")

                    out.append(f"""<div class="boonicon{i}" style="visibility: hidden; --src: url('{icon(trait)}')"></div>""")
                    out.append("</td>")
                    continue

                if any(trait in prereq for prereq in duo_trait["prereq_data"]):
                    extra_class = "splitting-headache-cast" if duo_trait["name"] == "Splitting Headache" and base == "RangedTrait" else ""
                    out.append(f"""<td><div class="boonicon{i} {extra_class}" title="{traits[trait]["name"]}" style="--src: url('{icon(trait)}')"></div></td>""")
                else:
                    out.append(f"""<td><div class="boonicon{i} disabled" title="{traits[trait]["name"]}" style="--src: url('{icon(trait)}')"></div></td>""")
                    
        out.append(f"""<td class="aftericons"></td>""")
        out.append(f"""<td><div src="" title="{duo_trait["name"]}" class="boonicon-big"
                style="--shadowcolor: {god_colors[god2]}; --src: url('{icon(duo_trait["internal"])}');"></div></td>""")
        out.append(f"""<td style="padding-right: 4px;"></td>""")
        out.append(f"""<td class="descr" style="border-left:  4px solid {with_opacity(god_colors[god2], 0.8)};"><b>{duo_trait["name"]}</b><br>{duo_trait["short_descr"]}""")
        out.append(f"""<div class="caveats">""")
        relevant_caveats = [i for i, (ts, caveat) in enumerate(caveats) if duo_trait["name"] in ts]
        if relevant_caveats:
            out.append("" + ", ".join(f"{i + 1}" for i in relevant_caveats))
        out.append("""</div></td>""")
        # out.append(f"""<td><img src="{icon(duo_trait["internal"])}" title="{duo_trait["name"]}" class="boonicon-big" style="--shadowcolor: {god_colors[god2]};"></img></td>""")
        out.append("</tr>\n")
    out.append("</table>")



out.append("""<div class="caveat-descr">""")
for i, (ts, caveat) in enumerate(caveats):
    out.append(f"""<div><ol><li value="{i+1}"> {caveat}</li></ol></div>""")
out.append("""</div>""")


with open("docs/duo_boons.html", "w") as f:
    f.write(r"""<!DOCTYPE HTML>
<html>
<head>
<title>Hades Duo Boons</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*, *::before, *::after {
    box-sizing: border-box;
}

* {
    --icon-size: 36px;
    margin: 0;
    padding: 0;
    font-family: "Calibri", Verdana, Arial, sans-serif;
    text-rendering: optimizeLegibility;
    /* text-shadow: -0.2px -0.2px 1px #111, 0.2px -0.2px 1px #111, -0.2px 0.2px 1px #111, 0.2px 0.2px
    1px #111; */
    color: #eee;
    line-height: 1.1em;

}

.descr, .caveats, .caveat-descr, .other-boon-req0, .other-boon-req1 {
    font-size: 11px;
}

.descr {
    background: rgba(0, 0, 0, 0.5);
}

body {
    background: #333;
    color: white;
}

#header {
    grid-area: header;
    margin-left: 2em;
    font-size: 14px;
}

#maingrid {
    /*
    display: inline-flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: flex-start;
    row-gap: 1em;
    */
    width: 100%;
    padding: 0 0.5vw;
    padding-top: 0.5vw;
    display: grid;
    grid-gap: 0.5vw;
    grid-template-rows: auto;
    align-items: center;
}

@media (orientation: landscape) {
    #maingrid {
        grid-template-columns: 1fr 1fr 1fr 1fr;
        grid-template-areas:
            "header header header header"
            "god0 god1 god2 god3"
            "god4 god5 god6 god7"
            "caveats caveats caveats caveats";
    }
}

@media (orientation: portrait) {
    #maingrid {
        grid-template-columns: 1fr 1fr;
        grid-template-areas:
            "header header"
            "god0 god1"
            "god2 god3"
            "god4 god5"
            "god6 god7"
            "caveats caveats";
    }
}


.duotable {
    display: inline-block;
    padding: 4px;
}

.aftericons {
    padding-left: calc(var(--icon-size) / 2);
}


.descr {
    /* width: 126px; */
    width: 99%;
    padding: 4px;
    position: relative;
}


.caveats {
    # width: 50px;
    # height: var(--icon-size);
    # margin-left: calc(var(--icon-size) / -5 - 25px);
    # margin-top: calc(var(--icon-size) * -1 + 4px);
    # line-height: var(--icon-size);
    position: absolute;
    top: 4px;
    right: 4px;
    text-align: right;
    vertical-align: top;
    # vertical-align: middle;
    # text-align: center;
}

.caveat-descr {
    grid-area: caveats;
    display: flex;
    justify-content: space-evenly;
    align-items: flex-start;
    flex-direction: row;
}

.caveat-descr > div {
    margin-left: 2em;
}

.godrow {
    display: block;
}

.godrow + .godrow {
    margin-top: 4px;
}

.other-boon-req0 {
    position: absolute;
    height: calc(1.5 * var(--icon-size) / 2);
    line-height: calc(1.5 * var(--icon-size) / 2);
    margin-top: calc(var(--icon-size) / -2 - 2px);
    text-align: center;
    vertical-align: middle;
}

.other-boon-req1 {
    position: absolute;
    height: calc(1.5 * var(--icon-size) / 2);
    line-height: calc(1.5 * var(--icon-size) / 2);
    margin-top: 2px;
    text-align: center;
    vertical-align: middle;
}

.other-boon-req0.other-zeus {
    width: calc((var(--icon-size) + 2px) * 5.25);
}

.other-boon-req1.other-zeus {
    width: calc((var(--icon-size) + 2px) * 5.25);
    margin-left: calc(var(--icon-size) * -1 - 6px);
}

.other-boon-req0.other-ares {
    width: calc((var(--icon-size) + 2px) * 3.5);
    margin-left: -4px;
}

.other-boon-req1.other-ares {
    width: calc((var(--icon-size) + 2px) * 3.5 - 6px);
    margin-left: calc(var(--icon-size) * -0.5 - 6px);
}

.boonicon0, .boonicon1 {
    width: var(--icon-size);
    height: var(--icon-size);
    background-image: url("BoonIconFrames/booninfo.png"), var(--src);
    background-size: calc(var(--icon-size)), calc(var(--icon-size) - 10%);
    background-position: center;
    background-repeat: no-repeat;
    filter: drop-shadow(0px 0px 3px rgba(0, 0, 0, 0.25));
}

.boonicon0 {
    position: relative;
    margin-top: calc(var(--icon-size) / -2);
    margin-left: 2px;
}

.boonicon1 {
    position: absolute;
    margin-left: calc(var(--icon-size) / -2 + 1px);
    margin-top: calc(var(--icon-size) / -4 + 1px);
}

.boonicon0.disabled, .boonicon1.disabled {
    filter: grayscale(100%) opacity(15%);
}

.splitting-headache-cast {
    filter: drop-shadow(0px 0px 4px red);
}

.boonicon-big {
    width: calc(var(--icon-size) * 1.5);
    height: calc(var(--icon-size) * 1.5);
    background-image: url("BoonIconFrames/booninfo.png"), var(--src);
    background-size: calc(var(--icon-size) * 1.5), calc(var(--icon-size) * 1.5 - 10%);
    background-position: center;
    background-repeat: no-repeat;
    filter: drop-shadow(0px 0px 3px rgba(0, 0, 0, 0.25));
}

</style>
</head>

<body>
<div id="maingrid">
<div id="header">
<div><p><b>Hades Duo Boon</b> chart - made by orlp.</p></div>
<div><p>Next to each Duo boon the prerequisite Attack/Special/Cast/Dash/Aid boons are listed (in
that order, left-to-right). You need
at least one of the listed boons from both gods if you want to be offered their Duo boon.</p></div>
</div>
    """)
    f.write("".join(out))
    f.write("""
</div>
</body>
</html>
    """)
