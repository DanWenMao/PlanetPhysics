import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def plot_map(df, evt_lat, evt_lon, title, path):
    fig = plt.figure(figsize=(10, 6))

    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=100))
    ax.set_global()

    # ✔ 背景
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.LAND, alpha=0.3)
    ax.add_feature(cfeature.OCEAN, alpha=0.3)

    # ✔ 台站（三角形）
    sc = ax.scatter(
        df["lon"], df["lat"],
        c=df["dist"], cmap="viridis",
        marker="^", s=60,
        transform=ccrs.PlateCarree(),
        label="Stations"
    )

    # ✔ 震源（红色五角星）
    ax.scatter(
        evt_lon, evt_lat,
        color="red", marker="*", s=200,
        transform=ccrs.PlateCarree(),
        label="Event"
    )

    # plt.colorbar(sc, label="Distance (deg)")
    # plt.legend(markerscale=0.5, loc="lower left")
    plt.title(title)

    plt.savefig(path, dpi=300)
    plt.close()

def plot_record_section(results, comp, path, config):
    import matplotlib.pyplot as plt
    import numpy as np
    from obspy.taup import TauPyModel

    plt.figure(figsize=(10, 8))

    # ===============================
    # 1️⃣ 排序
    # ===============================
    results = sorted(results, key=lambda r: r["meta"]["dist"])

    # ===============================
    # 2️⃣ 画波形（观测数据）
    # ===============================
    for r in results:
        tr = r[comp]

        sr = tr.stats.sampling_rate
        t = np.arange(tr.stats.npts) / sr

        # 转为“真实时间”（相对发震时刻）
        t_real = t + (r["tP"] - config.NOISE_BEFORE_P)

        offset = r["meta"]["dist"]

        # 归一化
        data = tr.data / (np.max(np.abs(tr.data)) + 1e-10)

        plt.plot(t_real, data + offset, color="black", linewidth=0.6)

    # ===============================
    # 3️⃣ 理论走时曲线（iasp91）
    # ===============================
    model = TauPyModel(model="iasp91")

    dists = np.linspace(30, 90, 300)

    tP_curve, tS_curve = [], []
    tPP_curve, tSS_curve, tpP_curve = [], [], []

    for d in dists:
        # ---- P ----
        arr = model.get_travel_times(
            source_depth_in_km=config.EVT_DEPTH,
            distance_in_degree=d,
            phase_list=["P"]
        )
        tP_curve.append(arr[0].time if arr else np.nan)

        # ---- S ----
        arr = model.get_travel_times(
            source_depth_in_km=config.EVT_DEPTH,
            distance_in_degree=d,
            phase_list=["S"]
        )
        tS_curve.append(arr[0].time if arr else np.nan)

        # ---- PP ----
        arr = model.get_travel_times(
            source_depth_in_km=config.EVT_DEPTH,
            distance_in_degree=d,
            phase_list=["PP"]
        )
        tPP_curve.append(arr[0].time if arr else np.nan)

        # ---- SS ----
        arr = model.get_travel_times(
            source_depth_in_km=config.EVT_DEPTH,
            distance_in_degree=d,
            phase_list=["SS"]
        )
        tSS_curve.append(arr[0].time if arr else np.nan)

        # ---- pP ----
        arr = model.get_travel_times(
            source_depth_in_km=config.EVT_DEPTH,
            distance_in_degree=d,
            phase_list=["pP"]
        )
        tpP_curve.append(arr[0].time if arr else np.nan)


    # ===============================
    # 4️⃣ 绘制理论曲线
    # ===============================
    # 主相
    plt.plot(tP_curve, dists, "r--", linewidth=1.5, alpha=0.8, label="P")
    plt.plot(tS_curve, dists, "b--", linewidth=1.5, alpha=0.8, label="S")

    # 次级相（更细更透明）
    plt.plot(tPP_curve, dists, "r-", linewidth=0.8, alpha=0.4, label="PP")
    plt.plot(tSS_curve, dists, "b-", linewidth=0.8, alpha=0.4, label="SS")
    plt.plot(tpP_curve, dists, "m-", linewidth=0.8, alpha=0.4, label="pP")

    # ===============================
    # 5️⃣ 标注每个台站的理论到时
    # ===============================
    for r in results:
        plt.scatter(r["tP"], r["meta"]["dist"], color="red", s=15)
        plt.scatter(r["tS"], r["meta"]["dist"], color="blue", s=15)

    # ===============================
    # 6️⃣ 图形修饰
    # ===============================
    plt.xlabel("Time since origin (s)")
    plt.ylabel("Distance (deg)")
    plt.title(f"{comp} component")

    plt.legend()
    plt.grid(alpha=0.3)

    plt.savefig(path, dpi=300)
    plt.close()