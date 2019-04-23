# FROM: https://github.com/Arthur-Milchior/anki-correct-due
# Modified version by lovac42 for Anki 2.0


# =====================================

AUTOMATIC_SCAN_ON_DB_CHECK = False

# =====================================


import anki
from anki.hooks import wrap
from aqt.qt import QAction
from aqt import mw
from aqt.utils import tooltip


NEW_CARDS_RANDOM = 0

def redue(col):

    # Save time
    if not col.db.scalar("select id from cards where type=0 and due>666000"):
        return

    #doesn't show up on small db
    tooltip(_("found cards with dues more than 666000, repositioning now."), period=3000)


    redline = col.db.scalar(
        """select max(due)+1 from cards 
        where due<=666000 and type=0""")

    if redline < 65536: #process overflows only
        query="""select id from cards where type=0 
                and due>666000 order by due,ord"""

    else: #process all
        query = "select id from cards where type=0 order by due,ord"
        redline = 0

    cids = col.db.list(query)
    col.sched.sortCards(cids, start=redline, shift=True)


    col.conf['nextPos'] = col.db.scalar(
        "select max(due)+1 from cards where type = 0") or 0

    dconfs = col.decks.dconf

    random_dconfs = [dconf for dconf in dconfs.values() if dconf["new"]['order'] == NEW_CARDS_RANDOM]
    for dconf in random_dconfs:
        col.sched.resortConf(dconf)


if AUTOMATIC_SCAN_ON_DB_CHECK:
    anki.collection._Collection.fixIntegrity = wrap(anki.collection._Collection.fixIntegrity,redue,"before")
else:
    action = QAction(mw)
    action.setText("Clean bulky dues")
    mw.form.menuTools.addAction(action)
    action.triggered.connect(lambda:redue(mw.col))

