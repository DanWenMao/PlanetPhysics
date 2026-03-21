import pandas as pd
from obspy.clients.fdsn import Client

import config
from station_utils import *
from taup_utils import compute_travel_times
from waveform_utils import process_station
from plot_utils import *

client = Client(config.CLIENT)

# ===============================
# 1. 获取台站
# ===============================
df = fetch_stations_by_distance(
    client,
    config.EVT_LAT,
    config.EVT_LON,
    config.ORIGIN_TIME - 3600,
    config.ORIGIN_TIME + 3600,
    config.DIST_MIN,
    config.DIST_MAX,
    config.CHANNEL,
    config.NETWORKS
)

# ===============================
# 2. 数据质量筛选
# ===============================
# df = filter_stations_by_quality(client, df, config)

# ===============================
# 3. 均匀选100台站
# ===============================
# df100 = select_uniform(df, config.N_INITIAL)

plot_map(df, config.EVT_LAT, config.EVT_LON,
         "Initial Stations", "output/map.pdf")

# df100.to_csv("output/stations_100.csv", index=False)

# ===============================
# 4. 计算走时
# ===============================
df["tP"], df["tS"] = zip(*df.apply(
    lambda r: compute_travel_times(r["dist"], config.EVT_DEPTH),
    axis=1
))

df.to_csv("output/stations.csv", index=False)

# ===============================
# 5. 下载波形 + SNR筛选
# ===============================
results = []
rows = []

for _, row in df.iterrows():
    r = process_station(client, row, config, row["tP"], row["tS"])
    if r is not None:
        results.append(r)

for r in results:
    meta = r["meta"]
    rows.append({
        "station": meta["station"],
        "network": meta["network"],
        "lat": meta["lat"],
        "lon": meta["lon"],
        "dist": meta["dist"],
        "tP": r["tP"],
        "tS": r["tS"],
        "snr": r["snr"]
    })

pd.DataFrame(rows).to_csv("output/stations_SNR.csv", index=False)

results = [r for r in results if r["snr"] >= config.SNR_THRESHOLD]
results = sorted(results, key=lambda r: r["snr"], reverse=True)[:config.N_FINAL]

# ===============================
# 6. 最终台站
# ===============================
final_df = pd.DataFrame([r["meta"] for r in results])

plot_map(final_df, config.EVT_LAT, config.EVT_LON,
         "Final Stations", "output/map_final.pdf")

# ===============================
# 7. record section
# ===============================
plot_record_section(results, "trZ", "output/Z.pdf", config)
plot_record_section(results, "trR", "output/R.pdf", config)
plot_record_section(results, "trT", "output/T.pdf", config)

print("Pipeline DONE")