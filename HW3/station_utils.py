import pandas as pd
import numpy as np
from obspy.clients.fdsn import Client
from obspy.geodetics import locations2degrees

def fetch_stations_by_distance(
    client,
    evt_lat,
    evt_lon,
    starttime,
    endtime,
    dmin,
    dmax,
    channel="BH?",
    networks="IU,II,GE,IC,AK,CN"
):
    inv = client.get_stations(
        network=networks,
        station="*",
        channel=channel,
        starttime=starttime,
        endtime=endtime,
        latitude=evt_lat,
        longitude=evt_lon,
        minradius=dmin,
        maxradius=dmax,
        level="station"
    )

    data = []

    for net in inv:
        for sta in net:
            data.append({
                "network": net.code,
                "station": sta.code,
                "lat": sta.latitude,
                "lon": sta.longitude,
                "dist": locations2degrees(evt_lat, evt_lon, sta.latitude, sta.longitude)
            })

    print(f"Stations (distance + network filter): {len(data)}")

    return pd.DataFrame(data)

def filter_stations_by_quality(client, df, config, max_workers=10):

    from concurrent.futures import ThreadPoolExecutor

    start = config.ORIGIN_TIME - 600
    end   = config.ORIGIN_TIME + 3600

    def check(row):
        try:
            # ✔ 1. 检查是否有波形（极轻量）
            '''
            st = client.get_waveforms(
                row["network"], row["station"], "*",
                config.CHANNEL, start, end,
                headonly=True
            )
            if len(st) == 0:
                return None            
            '''

            # ✔ 2. 检查是否有channel信息（代替response）
            inv = client.get_stations(
                network=row["network"],
                station=row["station"],
                starttime=start,
                endtime=end,
                level="channel"
            )

            if len(inv.get_contents()["channels"]) == 0:
                return None

            return row

        except:
            return None

    good = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(check, row) for _, row in df.iterrows()]

        for f in futures:
            r = f.result()
            if r is not None:
                good.append(r)

    print(f"Stations (quality filter): {len(good)}")

    return pd.DataFrame(good).reset_index(drop=True)

def select_uniform(df, n):
    df = df.sort_values("dist").reset_index(drop=True)
    distances = df["dist"].values
    targets = np.linspace(distances.min(), distances.max(), n)

    selected = []
    used = set()

    for t in targets:
        idx = np.argmin(np.abs(distances - t))
        while idx in used and idx < len(df)-1:
            idx += 1
        selected.append(idx)
        used.add(idx)

    return df.iloc[selected].reset_index(drop=True)