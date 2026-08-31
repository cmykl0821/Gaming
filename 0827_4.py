import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json


# =====================================================
# 1. Streamlit 設定
# =====================================================

st.set_page_config(
    page_title="遊戲成癮程度分析",
    layout="wide"
)



st.write(
    "透過使用者輸入資料計算遊戲成癮程度"

)
def password_required():
    """只有輸入 Streamlit Secrets 中的密碼後，才允許顯示主頁。"""
    if st.session_state.get("authenticated", False):
        return True

    try:
        expected_password = str(st.secrets["APP_PASSWORD"])
    except (FileNotFoundError, KeyError):
        st.error("尚未設定登入密碼，請先在 Streamlit 平台的 Secrets 加入 APP_PASSWORD。")
        st.code('APP_PASSWORD = "請設定你的密碼"', language="toml")
        return False

    if not expected_password:
        st.error("APP_PASSWORD 不可為空白，請到 Streamlit 平台重新設定。")
        return False

    st.title("🎮 遊戲成癮程度分析")
    st.caption("請輸入密碼後進入分析主頁。")

    with st.form("login_form", clear_on_submit=True):
        entered_password = st.text_input(
            "密碼",
            type="password",
            placeholder="請輸入登入密碼",
        )
        submitted = st.form_submit_button("登入", width="stretch")

    if submitted:
        if hmac.compare_digest(entered_password, expected_password):
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("密碼錯誤，請重新輸入。")

    return False


if not password_required():
    st.stop()

if st.sidebar.button("🔒 登出", width="stretch"):
    st.session_state["authenticated"] = False
    st.rerun()


# =====================================================
# 2. 讀取 CSV
# =====================================================

try:

    df = pd.read_csv("gaming_part1_100k.csv")

    # Demo 先使用前 1000 筆
    df = df.head(1000)

except Exception as e:

    st.error("❌ CSV 讀取失敗")
    st.error(str(e))
    st.stop()


# =====================================================
# 3. 檢查必要欄位
# =====================================================

required_columns = [
    "daily_gaming_hours",
    "screen_time_total",
    "exercise_hours",
    "sleep_hours",
    "addiction_level"
]


missing_columns = [
    col
    for col in required_columns
    if col not in df.columns
]


if missing_columns:

    st.error("❌ CSV 缺少必要欄位")

    st.write("缺少欄位：")
    st.write(missing_columns)

    st.write("目前 CSV 欄位：")
    st.write(list(df.columns))

    st.stop()


# =====================================================
# 4. 保留需要的欄位
# =====================================================

df = df[
    [
        "daily_gaming_hours",
        "screen_time_total",
        "exercise_hours",
        "sleep_hours",
        "addiction_level"
    ]
].copy()


# =====================================================
# 5. 移除空值
# =====================================================

df = df.dropna()


# =====================================================
# 6. 使用者輸入
# =====================================================

st.divider()

left_col, right_col = st.columns([1, 2])


with left_col:

    st.subheader("📝 使用者輸入")

    st.write(
        "請輸入以下四項資料："
    )


    # -------------------------------------------------
    # ① 每日遊戲時間
    # -------------------------------------------------

    gaming_hours = st.number_input(
        "🎮 每日遊戲時間（小時）",
        min_value=0.0,
        max_value=24.0,
        value=3.0,
        step=0.5
    )


    # -------------------------------------------------
    # ② 每日睡眠時間
    # -------------------------------------------------

    sleep_hours = st.number_input(
        "😴 每日睡眠時間（小時）",
        min_value=0.0,
        max_value=24.0,
        value=7.0,
        step=0.5
    )


    # -------------------------------------------------
    # ③ 每日總螢幕時間
    # -------------------------------------------------

    screen_time = st.number_input(
        "📱 每日總螢幕時間（小時）",
        min_value=0.0,
        max_value=24.0,
        value=6.0,
        step=0.5
    )


    # -------------------------------------------------
    # ④ 每週運動時間
    # -------------------------------------------------

    exercise_hours = st.number_input(
        "🏃 每週運動時間（小時）",
        min_value=0.0,
        max_value=168.0,
        value=3.0,
        step=0.5
    )


# =====================================================
# 7. 使用者輸入資料對應
# =====================================================

user_values = {

    "daily_gaming_hours": gaming_hours,

    "screen_time_total": screen_time,

    "exercise_hours": exercise_hours,

    "sleep_hours": sleep_hours

}


# =====================================================
# 8. 計算各項分數
# =====================================================


# -----------------------------------------------------
# A. 遊戲時間分數
#
# 10 小時以上 = 10 分
# -----------------------------------------------------

gaming_score = (
    gaming_hours / 10
) * 10


gaming_score = max(
    0,
    min(
        10,
        gaming_score
    )
)


# -----------------------------------------------------
# B. 螢幕時間分數
#
# 12 小時以上 = 10 分
# -----------------------------------------------------

screen_score = (
    screen_time / 12
) * 10


screen_score = max(
    0,
    min(
        10,
        screen_score
    )
)


# -----------------------------------------------------
# C. 運動時間分數
#
# 0 小時 = 10 分
# 7 小時以上 = 0 分
# -----------------------------------------------------

exercise_score = (
    (7 - exercise_hours) / 7
) * 10


exercise_score = max(
    0,
    min(
        10,
        exercise_score
    )
)


# -----------------------------------------------------
# D. 睡眠時間分數
#
# 4 小時以下 = 10 分
# 8 小時以上 = 0 分
# -----------------------------------------------------

sleep_score = (
    (8 - sleep_hours) / 4
) * 10


sleep_score = max(
    0,
    min(
        10,
        sleep_score
    )
)


# =====================================================
# 9. 加權計算成癮分數
# =====================================================

# 遊戲時間：50%
# 螢幕時間：20%
# 運動時間：10%
# 睡眠時間：20%

addiction_score = (

    gaming_score * 0.50

    +

    screen_score * 0.20

    +

    exercise_score * 0.10

    +

    sleep_score * 0.20

)


# =====================================================
# 10. 限制成癮分數 0～10
# =====================================================

addiction_score = max(
    0,
    min(
        10,
        addiction_score
    )
)


# =====================================================
# 11. 五級成癮程度
# =====================================================

if addiction_score < 2:

    level = "低"

    level_color = "#4CAF50"


elif addiction_score < 4:

    level = "偏低"

    level_color = "#8BC34A"


elif addiction_score < 6:

    level = "中"

    level_color = "#FFC107"


elif addiction_score < 8:

    level = "偏高"

    level_color = "#FF9800"


else:

    level = "高"

    level_color = "#F44336"


# =====================================================
# 12. Gauge 儀表板
# =====================================================

with right_col:

    st.subheader("🎯 遊戲成癮程度")

    st.write(
        "根據使用者輸入資料計算"
    )


    html_code = f"""

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<script src="https://cdn.amcharts.com/lib/4/core.js"></script>

<script src="https://cdn.amcharts.com/lib/4/charts.js"></script>


<style>

html,
body {{

    margin: 0;

    padding: 0;

    width: 100%;

    height: 100%;

    background: transparent;

}}


#chartdiv {{

    width: 100%;

    height: 400px;

}}


#result {{

    text-align: center;

    font-family: Arial, sans-serif;

    font-size: 28px;

    font-weight: bold;

    padding: 10px;

}}

</style>

</head>


<body>


<div id="chartdiv"></div>


<div id="result">

遊戲成癮程度：

{addiction_score:.2f} / 10

<br>

<span style="color:{level_color};">

{level}

</span>

</div>


<script>

am4core.ready(function() {{


    // =========================================
    // 建立 Gauge
    // =========================================

    var chart = am4core.create(
        "chartdiv",
        am4charts.GaugeChart
    );


    // =========================================
    // 數值軸
    // =========================================

    var axis = chart.xAxes.push(
        new am4charts.ValueAxis()
    );


    axis.min = 0;

    axis.max = 10;

    axis.strictMinMax = true;


    // =========================================
    // 軸設定
    // =========================================

    axis.renderer.radius =
        am4core.percent(90);

    axis.renderer.innerRadius =
        am4core.percent(65);

    axis.renderer.line.strokeOpacity = 0;

    axis.renderer.ticks.template.length = 10;

    axis.renderer.labels.template.fontSize = 14;


    // =========================================
    // 0～2 低
    // =========================================

    var range1 =
        axis.axisRanges.create();

    range1.value = 0;

    range1.endValue = 2;

    range1.axisFill.fill =
        am4core.color("#4CAF50");

    range1.axisFill.fillOpacity = 0.8;


    // =========================================
    // 2～4 偏低
    // =========================================

    var range2 =
        axis.axisRanges.create();

    range2.value = 2;

    range2.endValue = 4;

    range2.axisFill.fill =
        am4core.color("#8BC34A");

    range2.axisFill.fillOpacity = 0.8;


    // =========================================
    // 4～6 中
    // =========================================

    var range3 =
        axis.axisRanges.create();

    range3.value = 4;

    range3.endValue = 6;

    range3.axisFill.fill =
        am4core.color("#FFC107");

    range3.axisFill.fillOpacity = 0.8;


    // =========================================
    // 6～8 偏高
    // =========================================

    var range4 =
        axis.axisRanges.create();

    range4.value = 6;

    range4.endValue = 8;

    range4.axisFill.fill =
        am4core.color("#FF9800");

    range4.axisFill.fillOpacity = 0.8;


    // =========================================
    // 8～10 高
    // =========================================

    var range5 =
        axis.axisRanges.create();

    range5.value = 8;

    range5.endValue = 10;

    range5.axisFill.fill =
        am4core.color("#F44336");

    range5.axisFill.fillOpacity = 0.8;


    // =========================================
    // 建立指針
    // =========================================

    var hand =
        chart.hands.push(
            new am4charts.ClockHand()
        );


    hand.axis = axis;

    hand.innerRadius =
        am4core.percent(20);

    hand.startWidth = 8;

    hand.pin.disabled = false;


    // =========================================
    // 指針數值
    // =========================================

    hand.value = {addiction_score};


}});

</script>


</body>

</html>

"""


    components.html(
        html_code,
        height=500
    )


# =====================================================
# 13. Bubble Chart
# =====================================================

st.divider()

st.subheader(
    "🫧 變數關係 × 遊戲成癮程度"
)

st.write(
    "自由選擇 X 軸與 Y 軸，"
    "觀察不同變數與遊戲成癮程度之間的關係。"
)


# =====================================================
# 14. X、Y 軸選擇
# =====================================================

available_cols = [

    "daily_gaming_hours",

    "screen_time_total",

    "exercise_hours",

    "sleep_hours"

]


column_names = {

    "daily_gaming_hours":
        "每日遊戲時間（小時）",

    "screen_time_total":
        "每日總螢幕時間（小時）",

    "exercise_hours":
        "每週運動時間（小時）",

    "sleep_hours":
        "每日睡眠時間（小時）"

}


col_x, col_y = st.columns(2)


with col_x:

    x_col = st.selectbox(

        "📌 X 軸",

        available_cols,

        index=0,

        format_func=lambda x:
            column_names[x]

    )


with col_y:

    y_col = st.selectbox(

        "📌 Y 軸",

        available_cols,

        index=3,

        format_func=lambda x:
            column_names[x]

    )


# =====================================================
# 15. 準備 Bubble Chart 資料
# =====================================================

chart_data = []


# -----------------------------------------------------
# CSV 資料
# -----------------------------------------------------

for _, row in df.iterrows():

    chart_data.append({

        "x": float(
            row[x_col]
        ),

        "y": float(
            row[y_col]
        ),

        "value": float(
            row["addiction_level"]
        ),

        "user": False

    })


# -----------------------------------------------------
# 使用者資料
# -----------------------------------------------------

chart_data.append({

    "x": float(
        user_values[x_col]
    ),

    "y": float(
        user_values[y_col]
    ),

    "value": float(
        addiction_score
    ),

    "user": True

})


chart_json = json.dumps(
    chart_data,
    ensure_ascii=False
)


# =====================================================
# 16. Bubble Chart HTML
# =====================================================

bubble_html = f"""

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<script src="https://cdn.amcharts.com/lib/4/core.js"></script>

<script src="https://cdn.amcharts.com/lib/4/charts.js"></script>

<script src="https://cdn.amcharts.com/lib/4/themes/animated.js"></script>


<style>

#chartdiv {{

    width: 100%;

    height: 500px;

}}


#legend {{

    text-align: center;

    font-family: Arial;

    font-size: 15px;

    padding: 10px;

}}


.item {{

    display: inline-block;

    margin: 5px 12px;

}}


.dot {{

    width: 14px;

    height: 14px;

    border-radius: 50%;

    display: inline-block;

    margin-right: 5px;

}}

</style>

</head>


<body>


<div id="chartdiv"></div>


<div id="legend">


<span class="item">

<span class="dot"
style="background:#4CAF50"></span>

0～2 低

</span>


<span class="item">

<span class="dot"
style="background:#8BC34A"></span>

2～4 偏低

</span>


<span class="item">

<span class="dot"
style="background:#FFC107"></span>

4～6 中

</span>


<span class="item">

<span class="dot"
style="background:#FF9800"></span>

6～8 偏高

</span>


<span class="item">

<span class="dot"
style="background:#F44336"></span>

8～10 高

</span>


</div>


<script>

am4core.ready(function() {{


    // =========================================
    // 建立圖表
    // =========================================

    var chart = am4core.create(
        "chartdiv",
        am4charts.XYChart
    );


    // =========================================
    // 載入資料
    // =========================================

    chart.data = {chart_json};


    // =========================================
    // X 軸
    // =========================================

    var xAxis = chart.xAxes.push(
        new am4charts.ValueAxis()
    );


    xAxis.title.text =
        "{column_names[x_col]}";


    xAxis.min = 0;


    // =========================================
    // Y 軸
    // =========================================

    var yAxis = chart.yAxes.push(
        new am4charts.ValueAxis()
    );


    yAxis.title.text =
        "{column_names[y_col]}";


    yAxis.min = 0;


    // =========================================
    // Bubble Series
    // =========================================

    var series = chart.series.push(
        new am4charts.LineSeries()
    );


    series.dataFields.valueX = "x";

    series.dataFields.valueY = "y";


    // 不畫線

    series.strokeOpacity = 0;


    // =========================================
    // 建立泡泡
    // =========================================

    var bullet = series.bullets.push(
        new am4charts.CircleBullet()
    );


    // =========================================
    // 泡泡大小
    // =========================================

    bullet.circle.adapter.add(

        "radius",

        function(radius, target) {{

            var value =
                Number(
                    target.dataItem
                    .dataContext
                    .value
                );


            return 5 + value * 2;

        }}

    );


    // =========================================
    // 泡泡顏色
    // =========================================

    bullet.circle.adapter.add(

        "fill",

        function(fill, target) {{

            var value =
                Number(
                    target.dataItem
                    .dataContext
                    .value
                );


            if (value < 2) {{

                return am4core.color(
                    "#4CAF50"
                );

            }}


            else if (value < 4) {{

                return am4core.color(
                    "#8BC34A"
                );

            }}


            else if (value < 6) {{

                return am4core.color(
                    "#FFC107"
                );

            }}


            else if (value < 8) {{

                return am4core.color(
                    "#FF9800"
                );

            }}


            else {{

                return am4core.color(
                    "#F44336"
                );

            }}

        }}

    );


    // =========================================
    // 使用者資料黑色外框
    // =========================================

    bullet.circle.adapter.add(

        "stroke",

        function(stroke, target) {{

            var isUser =
                target.dataItem
                .dataContext
                .user;


            if (isUser) {{

                return am4core.color(
                    "#000000"
                );

            }}


            return am4core.color(
                "#FFFFFF"
            );

        }}

    );


    // =========================================
    // 使用者資料外框粗細
    // =========================================

    bullet.circle.adapter.add(

        "strokeWidth",

        function(width, target) {{

            var isUser =
                target.dataItem
                .dataContext
                .user;


            if (isUser) {{

                return 4;

            }}


            return 1;

        }}

    );


    // =========================================
    // Tooltip
    // =========================================

    bullet.tooltipText =

        "{column_names[x_col]}：{{valueX}}" +
        "\\n" +
        "{column_names[y_col]}：{{valueY}}" +
        "\\n" +
        "遊戲成癮程度：{{value}} / 10";


    // =========================================
    // Hover
    // =========================================

    var hover =
        bullet.circle.states.create(
            "hover"
        );


    hover.properties.scale = 1.5;


    // =========================================
    // Zoom
    // =========================================

    chart.cursor =
        new am4charts.XYCursor();


    chart.cursor.behavior =
        "zoomXY";


    // =========================================
    // Scrollbar
    // =========================================

    chart.scrollbarX =
        new am4core.Scrollbar();


    chart.scrollbarY =
        new am4core.Scrollbar();


}});

</script>


</body>

</html>

"""


# =====================================================
# 17. 顯示 Bubble Chart
# =====================================================

components.html(

    bubble_html,

    height=600

)


# =====================================================
# 18. 圖表說明
# =====================================================

st.info(

    f"目前 X 軸：{column_names[x_col]} ｜ "
    f"Y 軸：{column_names[y_col]} ｜ "
    "泡泡大小與顏色代表遊戲成癮程度，"
    "黑色外框代表目前使用者資料。"

)

# =====================================================
# 使用者分析結果
# =====================================================

st.divider()

st.subheader("📊 使用者分析結果")

# 第一排：四項輸入資料
result1, result2, result3, result4 = st.columns(4)

with result1:
    st.metric(
        "🎮 每日遊戲時間",
        f"{gaming_hours:.1f} 小時"
    )

with result2:
    st.metric(
        "😴 平均睡眠時間",
        f"{sleep_hours:.1f} 小時"
    )

with result3:
    st.metric(
        "📱 每日總螢幕時間",
        f"{screen_time:.1f} 小時"
    )

with result4:
    st.metric(
        "🏃 每週運動時間",
        f"{exercise_hours:.1f} 小時"
    )


# =====================================================
# 第二排：成癮分數與等級
# =====================================================

st.markdown("<br>", unsafe_allow_html=True)

score_col, level_col = st.columns(2)


with score_col:

    st.metric(
        "🎯 成癮程度分數",
        f"{addiction_score:.2f} / 10"
    )


with level_col:

    st.markdown(
        f"""
        <div style="
            background-color:{level_color};
            color:white;
            padding:12px;
            border-radius:10px;
            text-align:center;
            font-size:24px;
            font-weight:bold;
        ">
            遊戲成癮程度：{level}
        </div>
        """,
        unsafe_allow_html=True
    )
