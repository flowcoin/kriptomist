import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from importlib import reload

from coin import Coin
import util
import config
import draw

assert "KMS" in globals(), "Please first execute `run kriptomist.py` inside the IPython shell, then `run -i <this_script>`"
KMS = globals()["KMS"]

class CumSer:
    def __init__(self, kms):
        self.mcap = util.get_cumulative_series(kms, "mcap")
        self.subs = util.get_cumulative_series(kms, "subs")
        
bitcoin = CumSer([KMS[0]])
alts_2_10 = CumSer(KMS[1:10])
alts_11_100 = CumSer(KMS[10:100])


fig, ax1 = plt.subplots()
color = 'tab:red'
ax1.set_xlabel('date')
ax1.set_ylabel('market cap', color=color)
for s, label, ls in [
    (bitcoin.mcap, "bitcoin", "-"),
    (alts_2_10.mcap, "alts #2 to #10", "--"),
    (alts_11_100.mcap, "alts #11 to #100", ":"),
]:
    ax1.plot(
        [a[0] for a in s],
        [a[1] if a[1] else None for a in s],
        label=label,
        color=color,
        linestyle=ls,
    )
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
color = 'tab:blue'
ax2.set_ylabel('reddit subscribers', color=color)  # we already handled the x-label with ax1
for s, label, ls in [
    (bitcoin.subs, "bitcoin", "-"),
    (alts_2_10.subs, "alts #2 to #10", "--"),
    (alts_11_100.subs, "alts #11 to #100", ":"),
]:
    ax2.plot(
        [a[0] for a in s],
        [a[1] if a[1] > 250000 else None for a in s],
        label=label,
        color=color,
        linestyle=ls,
    )
ax2.tick_params(axis='y', labelcolor=color)

ax1.legend(loc='upper left')

if config.SIGNATURE_IN_CHART:
    draw.signaturebar(fig, config.CHART_SIGNATURE)

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()