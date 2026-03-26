# Task
## 任务描述
- 绘制火震不同震相的射线路径，分别在有固态内核和无固态内核的情况下绘制。
- 计算以下震相在有固态内核和无固态内核时的走时差异
-- PKKP
-- P'P'r_bc（无固态内核）与P'P'r_df（有固态内核）
## 模型规定
- 无固态内核
-- 一维速度剖面：Model_Khan_1.nd
-- 地震射线
--- PKKP
--- P'P'r_ab, P'P'r_bc
    P'P'r对应rays leaving from the event towards the station along the major arc
    P'P'r_ab仅经过核的浅层。初始入射角更大，大约为110°
    P'P'r_bc经过了核的内部，在有内核的情况下，经过内核，转变为P'P'r_df。初始入射角更小，大约为80°
--- P'P'n
    P'P'n对应a ray taking off along the minor arc，初始入射角最小，大约为40°
- 有固态内核
-- 一维速度剖面：Model_Bi_1.nd
-- 地震射线
--- PKiKP
--- PKIIKP
--- PKIKKIKP
    这个震相标记为PKKP，由无固态内核的PKKP震相转化而来
--- PKIKPPKIKP
    这个震相标记为P'P'r_df，由无固态内核的P'P'r_bc震相转化而来
--- P'P'r_ab
--- P'P'n
## 可视化规定
- PKiKP，正红直线
- PKIIKP，赭红直线
- PKKP，橙色直线
- P'P'r_bc，紫色直线
- P'P'n，天蓝色直线
- P'P'r_ab，蓝色虚线
- P'P'r_df，绿色虚线
## 方法规定
使用Obspy的TauP库

