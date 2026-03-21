import numpy as np
from obspy.clients.fdsn import Client
from obspy.geodetics import gps2dist_azimuth

def download_waveform(client, row, start, end, channel):
    return client.get_waveforms(
        row["network"], row["station"], "*",
        channel, start, end
    )

def compute_snr(tr, tp, noise_win, signal_win):
    data = tr.data
    sr = tr.stats.sampling_rate

    ip = int(tp * sr)

    n_noise = int(noise_win * sr)
    n_signal = int(signal_win * sr)

    noise = data[ip-n_noise : ip]
    signal = data[ip : ip+n_signal]

    noise_rms = np.sqrt(np.mean(noise**2))
    signal_rms = np.sqrt(np.mean(signal**2))

    return signal_rms / noise_rms if noise_rms != 0 else np.nan

def process_station(client, row, config, tP, tS):
    try:
        # ===============================
        # 1️⃣ 时间窗（统一参考）
        # ===============================
        start = config.ORIGIN_TIME + tP - config.NOISE_BEFORE_P
        end   = config.ORIGIN_TIME + tS + config.SIGNAL_AFTER_S

        st = download_waveform(client, row, start, end, config.CHANNEL)

        # ===============================
        # 2️⃣ 合并 + 强制统一时间轴（关键）
        # ===============================
        st.merge(method=1, fill_value=0)
        st.trim(start, end)

        # ===============================
        # 3️⃣ 检查三分量完整性
        # ===============================
        if len(st.select(component="Z")) == 0:
            raise Exception("No Z component")

        # ===============================
        # 4️⃣ 获取响应
        # ===============================
        inv = client.get_stations(
            network=row["network"],
            station=row["station"],
            location="*",
            channel=config.CHANNEL,
            starttime=start,
            endtime=end,
            level="response"
        )

        # ===============================
        # 5️⃣ 去趋势 + taper（去响应前必须）
        # ===============================
        st.detrend("demean")
        st.detrend("linear")
        st.taper(max_percentage=0.05)

        # ===============================
        # 6️⃣ 去仪器响应（稳定反卷积）
        # ===============================
        st.remove_response(
            inventory=inv,
            output="VEL",
            pre_filt=(1/180, 1/150, 4, 5)
        )

        # ===============================
        # 7️⃣ 再次保证时间一致（防止处理后微小偏差）
        # ===============================
        st.trim(start, end)

        # ===============================
        # 8️⃣ 计算 back-azimuth
        # ===============================
        _, az, baz = gps2dist_azimuth(
            config.EVT_LAT, config.EVT_LON,
            row["lat"], row["lon"]
        )

        # ===============================
        # 9️⃣ 旋转 NE → RT（自动对齐）
        # ===============================
        st.rotate("NE->RT", back_azimuth=baz)

        # ===============================
        # 🔟 提取“对齐后的”三分量（关键）
        # ===============================
        trZ = st.select(component="Z")[0]   # ✔ 已对齐
        trR = st.select(component="R")[0]
        trT = st.select(component="T")[0]

        # ===============================
        # 11️⃣ 计算 SNR（围绕 P 波）
        # ===============================
        snr = compute_snr(
            trZ,
            config.NOISE_WIN,
            config.SIGNAL_WIN,
            config.NOISE_BEFORE_P
        )

        print("Success:", row["station"], "SNR:", snr)

        # ===============================
        # 12️⃣ 返回结果
        # ===============================
        return {
            "meta": row,
            "snr": snr,
            "tP": tP,
            "tS": tS,
            "trZ": trZ.copy(),
            "trR": trR,
            "trT": trT
        }

    except Exception as e:
        print("Fail:", row["station"], e)
        return None
