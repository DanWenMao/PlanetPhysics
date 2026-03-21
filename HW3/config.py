from obspy import UTCDateTime

# 地震参数
ORIGIN_TIME = UTCDateTime("2008-05-12T06:28:00")
EVT_LAT = 31.0
EVT_LON = 103.4
EVT_DEPTH = 10  # km

# 台站筛选
DIST_MIN = 30
DIST_MAX = 90
N_INITIAL = 50
N_FINAL = 50
NETWORKS = "IU,II,GE,IC,AK,CN"

# 时间窗（基于理论走时）
NOISE_BEFORE_P = 300
SIGNAL_AFTER_S = 600

# SNR阈值
SNR_THRESHOLD = 25 # 后期调参。此次地震震级较大，信噪比较高，可以适当调高阈值以获得更干净的记录。
NOISE_WIN = 20
SIGNAL_WIN = 20

# 数据源
CLIENT = "EARTHSCOPE"
CHANNEL = "BH?"