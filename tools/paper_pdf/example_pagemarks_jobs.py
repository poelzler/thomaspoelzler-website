"""BEISPIEL (Oktober 2026): So wurden Original-Seitenzahlen und der einheitliche Kopfvermerk
für die selbst gesetzten PDFs erzeugt. Die Pfade unten stammen aus der damaligen Sitzung und
existieren nicht mehr; für neue PDFs nur als Vorlage für Aufrufe von pagemarks.py verwenden."""
import sys, os, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pagemarks import *

S = "/tmp/claude-0/-home-claude/d1e223b3-265f-5a5b-9c86-a8528c3ac9bd/scratchpad/"
U = "/mnt/user-data/attachments/d1e223b3-265f-5a5b-9c86-a8528c3ac9bd/"
U2 = "/root/.claude/uploads/d1e223b3-265f-5a5b-9c86-a8528c3ac9bd/"
UO = S + "pm/user_orig/"   # unveränderte Kopien der in Word gesetzten PDFs
MS = S + "ms/out/"         # mit build.py gesetzte PDFs (Kopf schon im neuen Stil)
OUT = S + "pm/out/"
ep25 = U + "bdaa1029-EP_253_full_issue_1.pdf"
ep22 = U + "fd508a8d-EP_223_full_issue.pdf"

# Kopfvermerke der Word-PDFs: Text unverändert, nur neu gesetzt
HEAD = {
    "Pölzler (2015) - Climate Change Inaction and Moral Nihilism.pdf":
        "© 2015 Taylor &amp; Francis | This is an Accepted Manuscript of an article published by Taylor &amp; Francis in <i>Ethics, Policy &amp; Environment</i> on 26 November 2015, available online: https://doi.org/10.1080/21550085.2015.1070488. | Published as: Pölzler, Thomas (2015): Climate Change Inaction and Moral Nihilism. <i>Ethics, Policy &amp; Environment</i> 18 (2), 202-214. | For the published version please contact me at thomas.poelzler@uni-graz.at.",
    "Pölzler (2015) - Moral Judgements and Emotions A Less Intimate Relationship than Recently Claimed.pdf":
        "© 2015 American Psychological Association | This article may not exactly replicate the final version published in the APA journal. It is not the copy of record. | Published as: Pölzler, Thomas (2015): Moral Judgements and Emotions: A Less Intimate Relationship than Recently Claimed. <i>Journal of Theoretical and Philosophical Psychology</i> 35 (3), 177-195. https://doi.org/10.1037/teo0000022 | For the published version please contact me at thomas.poelzler@uni-graz.at.",
    "Pölzler (2016) - Further Problems with Projectivism.pdf":
        "© 2016 The Philosophical Society of Southern Africa | This is the Accepted Manuscript of an article whose final and definitive form has been published in <i>South African Journal of Philosophy</i> on 8 March 2016, available online: https://doi.org/10.1080/02580136.2015.1128242. | Published as: Pölzler, Thomas (2016): Further Problems with Projectivism. <i>South African Journal of Philosophy</i> 35 (1), 92-102. | For the published version please contact me at thomas.poelzler@uni-graz.at.",
    "Pölzler (2016) - Wie schlüssig ist Albert Camus’ frühe Logik des Absurden.pdf":
        "© 2016 frommann-holzboog | Dies ist das vom Verlag angenommene Manuskript eines Artikels, der von frommann-holzboog publiziert wurde. | Publiziert als: Pölzler, Thomas (2016): Wie schlüssig ist Albert Camus’ frühe Logik des Absurden? <i>Allgemeine Zeitschrift für Philosophie</i> 41 (1), 59-76. https://doi.org/10.5771/0340-7969-2016-1-59 | Für die publizierte Version kontaktieren Sie mich bitte unter thomas.poelzler@uni-graz.at.",
    "Pölzler (2017) - Lastenteilung in der europäischen Asylpolitik.pdf":
        "© 2017 Grazer Universitätsverlag | Diese Fassung entspricht möglicherweise nicht exakt der publizierten Version. | Publiziert als: Pölzler, Thomas (2017): Lastenteilung in der europäischen Asylpolitik. In: Meyer, Lukas; Reiter, Barbara (Hg.): <i>Wem gehört das Klima?</i> Graz: Grazer Universitätsverlag, 21-25. | Für die publizierte Version kontaktieren Sie mich bitte unter thomas.poelzler@uni-graz.at.",
    "Pölzler (2017) - Unsere Verantwortung gegenüber Flüchtlingen.pdf":
        "© 2017 Grazer Universitätsverlag | Diese Fassung entspricht möglicherweise nicht exakt der publizierten Version. | Publiziert als: Pölzler, Thomas (2017): Unsere Verantwortung gegenüber Flüchtlingen. In: Meyer, Lukas; Reiter, Barbara (Hg.): <i>Wem gehört das Klima?</i> Graz: Grazer Universitätsverlag, 43-47. | Für die publizierte Version kontaktieren Sie mich bitte unter thomas.poelzler@uni-graz.at.",
    "Pölzler (2019) - The Effects of Morality on Acting against Climate Change.pdf":
        "© 2019 Taylor &amp; Francis | This is the final version of a chapter published by Routledge. It is not the copy of record. | Published as: Pölzler, Thomas (2019): The Effects of Morality on Acting against Climate Change. In: Garner, Richard; Joyce, Richard (eds.): <i>The End of Morality: Taking Moral Abolitionism Seriously</i>. New York: Routledge, 202-219. | For the published version please contact me at thomas.poelzler@uni-graz.at.",
    "Pölzler (2021) - Insufficient Effort Responding in Experimental Philosophy.pdf":
        "© 2021 Oxford University Press | This is the accepted version of a manuscript published by Oxford University Press. It is not the copy of record. | Published as: Pölzler, Thomas (2021): Insufficient Effort Responding in Experimental Philosophy. In: Lombrozo, Tania; Knobe, Joshua; Nichols, Shaun (eds.): <i>Oxford Studies in Experimental Philosophy, Volume 4</i>. Oxford: Oxford University Press, 214-256. https://doi.org/10.1093/oso/9780192856890.003.0009 | For the published version please contact me at thomas.poelzler@uni-graz.at.",
}

jobs = [
    dict(name="Pölzler (2019) - Review of Robin Attfield’s Environmental Ethics A Very Short Introduction.pdf", lang="en", first=507,
         A=lambda: anchors(U + "0127c0d6-10.3197096327119x15576762300749.pdf", [(2, 508), (3, 509)], top=70)),
    dict(name="Pölzler (2015) - Climate Change Inaction and Moral Nihilism.pdf", lang="en", first=202,
         A=lambda: anchors(U + "76a4af9e-10.108021550085.2015.1070488.pdf", [(i, 200 + i) for i in range(3, 15)], top=80)),
    dict(name="Pölzler (2015) - Moral Judgements and Emotions A Less Intimate Relationship than Recently Claimed.pdf", lang="en", first=177,
         A=lambda: anchors(U + "1285db8c-2015-33469-001.pdf", [(i, 176 + i) for i in range(2, 20)], top=65, col=True,
                           skip=r"(This (article|document) is (intended|copyrighted)|.*personal use of the individual)")),
    dict(name="Pölzler (2016) - Further Problems with Projectivism.pdf", lang="en", first=92,
         A=lambda: anchors(U + "18ffdb44-10.108002580136.2015.1128242.pdf", [(i, 90 + i) for i in range(3, 13)], top=50)),
    dict(name="Pölzler (2019) - How to Determine whether Evolution Debunks Moral Realism.pdf", lang="en", first=35,
         A=lambda: anchors(U + "49bd5819-10.1515_jwiet-2018-230104.pdf", [(i, 34 + i) for i in range(2, 27)], top=45)),
    dict(name="Pölzler (2023) - The Explanatory Redundancy Challenge to Moral Properties.pdf", lang="en", first=104,
         A=lambda: anchors(U2 + "805d9bdb-Chapter6_Poelzler_-_tp_1.pdf", [(i, 103 + i) for i in range(2, 22)], top=85)),
    dict(name="Pölzler (2020) - Psychologische Forschung zum moralischen Realismus und ihre metaethischen Implikationen.pdf", lang="de", first=423,
         A=lambda: anchors(U2 + "c0fe15d3-29892_01_Empirische_Ethik_1_Lauf_14_0_1.pdf",
                           [((212 + (n - 422) // 2) if n % 2 == 0 else (212 + (n - 423) // 2), n, 0 if n % 2 == 0 else 1) for n in range(424, 455)],
                           top=40, bottom=470, spread=True)),
    dict(name="Pölzler (2016) - Wie schlüssig ist Albert Camus’ frühe Logik des Absurden.pdf", lang="de", first=59,
         A=lambda: anchors(U + "5827f2ee-Poelzler.pdf", [(i, 58 + i) for i in range(2, 19)], top=80)),
    dict(name="Pölzler (2019) - The Effects of Morality on Acting against Climate Change.pdf", lang="en", first=202,
         A=lambda: anchors(U + "97d3a6c9-Richard_Garner_Editor_Richard_Joyce_Editor_z-lib.org.pdf", [(i, i - 25) for i in range(228, 245)], top=55)),
    dict(name="Pölzler (2021) - Insufficient Effort Responding in Experimental Philosophy.pdf", lang="en", first=214,
         A=lambda: anchors(U + "681f6746-dabfd9dcafc5bce41ffdf9e9c1680f16.pdf", [(i, i - 7) for i in range(222, 264)], top=55)),
    dict(name="Pölzler (2018) - Review of Kieran Setiya’s Midlife A Philosophical Guide.pdf", lang="en", first=575,
         A=lambda: anchors(ep25, [(218, 576), (219, 577), (220, 578), (221, 579)], top=80)),
    dict(name="Pölzler (2015) - Review of Erik J. Wielenberg’s Robust Ethics The Metaphysics and Epistemology of Godless Normative Realism.pdf", lang="en", first=509,
         A=lambda: anchors(ep22, [(141, 510), (142, 511), (143, 512), (144, 513)], top=80)),
    dict(name="Pölzler (2019) - Review of Iddo Landau’s Finding Meaning in an Imperfect World.pdf", lang="en", first=435, approx=True,
         A=lambda: [(436, "oneself. Finally, it can also result from conceited and narcissistic attitudes"),
                    (437, "Landau argues that compared to pleasure, we may not be more sensitive"),
                    (438, "These worries should not distract from the fact, however, that Landau")]),
    dict(name="Meyer et al (2017) - Introduction to the Special Issue on Legitimate Expectations.pdf", lang="en", first=173,
         A=lambda: anchors(U + "e05f5e25-10.1515_mopp-2017-0045.pdf", [(2, 174), (3, 175)], top=50)),
    dict(name="Pölzler (2023) - Basic Needs.pdf", lang="en", first=221, approx=True,
         A=lambda: [tuple(x) for x in json.load(open(S + "pm/bn_anchors.json"))]),
    # ohne Original: nur Kopfvermerk
    dict(name="Pölzler (2017) - Lastenteilung in der europäischen Asylpolitik.pdf", lang="de"),
    dict(name="Pölzler (2017) - Unsere Verantwortung gegenüber Flüchtlingen.pdf", lang="de"),
    dict(name="Pölzler (2023) - Review of Joel Marks’s Reason and Ethics The Case Against Objective Value.pdf", lang="en"),
    dict(name="Pölzler (2016) - Art in the Face of the Absurd.pdf", lang="en"),
    dict(name="Pölzler (2015) - Moral Disagreement, Anti-Realism, and the Worry about Overgeneralization.pdf", lang="en"),
]

os.makedirs(OUT, exist_ok=True)
only = sys.argv[1:]
for j in jobs:
    if only and not any(o in j["name"] for o in only):
        continue
    word = j["name"] in HEAD
    src = (UO if word else MS) + j["name"]
    doc = pymupdf.open(src)
    has_marks = "A" in j
    if word:
        restyle_header(doc, HEAD[j["name"]], NOTICE[(j["lang"], j.get("approx", False))] if has_marks else None)
        tmp = OUT + "_tmp.pdf"; doc.save(tmp); doc = pymupdf.open(tmp)
    print("=====", j["name"][:75])
    if not has_marks:
        doc.save(OUT + j["name"], garbage=3, deflate=True); continue
    A = j["A"]()
    res = locate(doc, A, title_label=j["first"])
    for (label, info, how), a in zip(res, [(j["first"], "TITLE")] + A):
        if how.startswith(("exact", "title")):
            continue
        where = "p%d y%.0f" % (info[0] + 1, info[1][1]) if info else "-"
        print("  %s %-12s %-10s | %s" % (label, how[:12], where, a[1][:60].replace("\n", " ")))
    stamp(doc, OUT + j["name"], res, j["lang"], approx=j.get("approx", False), notice=False)
