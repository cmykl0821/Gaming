import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json

st.set_page_config(page_title="遊戲與心理健康", layout="wide")
st.title("遊戲與心理健康")

#跑馬燈
#marquee_text = "🔥 最新消息：..."

#st.html(
#    f"""
#    <marquee style="color: #FF4B4B; font-weight: bold; font-size: 18px;" 
#             scrollamount="6" 
#             direction="left">
#        {marquee_text}
#    </marquee>
#    """
#)

#8. 分隔線
st.divider()


st.divider()
st.subheader("📝 請輸入基本資料")

col_left, col_right = st.columns([1, 7])

with col_left:
    name = st.text_input("請輸入您的姓名", value="")
    age = st.number_input("請輸入年齡", min_value=0, max_value=100, value=18, step=1)
    screen_hour = st.number_input("請輸入每日螢幕使用時數",min_value=0.0, max_value=24.0,value=0.0,step=0.5)
    game_hour = st.number_input("請輸入每日遊戲時數",min_value=0.0, max_value=24.0,value=0.0,step=0.5)
    sleep_hour = st.number_input("請輸入每日睡眠時數",min_value=0.0, max_value=24.0,value=0.0,step=0.5)
    exercite_hour = st.number_input("請輸入每週運動時數",min_value=0.0, max_value=70.0,value=0.0,step=0.5)

gaming_score = (game_hour/10) * 10
sleep_score = ((8 - sleep_hour) / 4) * 10
addiction_score = (gaming_score * 0.7 + sleep_score * 0.3)
addiction_score = max( 0, min( 10, addiction_score ))

if addiction_score < 2:
    level = "低"
    color = "#4CAF50"
elif addiction_score < 4:
    level = "偏低"
    color = "#8BC34A"
elif addiction_score < 6:
    level = "中"
    color = "#FFC107"
elif addiction_score < 8:
    level = "偏高"
    color = "#FF9800"
else:
    level = "高"
    color = "#F44336"


with col_right:
    target_score = round(addiction_score, 2)

    html_gauge = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }}
            #chartdiv {{
                width: 100%;
                height: 400px;
            }}
        </style>
        <!-- amCharts v4 核心資源 -->
        <script src="https://cdn.amcharts.com/lib/4/core.js"></script>
        <script src="https://cdn.amcharts.com/lib/4/charts.js"></script>
    </head>
    <body>

        <div id="chartdiv"></div>

        <script>
        am4core.ready(function() {{

            // 建立圖表
            var chart = am4core.create("chartdiv", am4charts.GaugeChart);
            chart.innerRadius = -15;

            // 設定 0 ~ 10 分的數值軸
            var axis = chart.xAxes.push(new am4charts.ValueAxis());
            axis.min = 0;
            axis.max = 10;
            axis.strictMinMax = true;
            axis.renderer.grid.template.stroke = new am4core.InterfaceColorSet().getFor("background");
            axis.renderer.grid.template.strokeOpacity = 0.3;

            // 建立五級成癮區塊與配色
            function createRange(start, end, color) {{
                var range = axis.axisRanges.create();
                range.value = start;
                range.endValue = end;
                range.axisFill.fillOpacity = 0.9;
                range.axisFill.fill = am4core.color(color);
                range.axisFill.zIndex = -1;
            }}

            createRange(0, 2, "#4CAF50");   // 低
            createRange(2, 4, "#8BC34A");   // 偏低
            createRange(4, 6, "#FFC107");   // 中
            createRange(6, 8, "#FF9800");   // 偏高
            createRange(8, 10, "#F44336");  // 高

            // 建立指針
            var hand = chart.hands.push(new am4charts.ClockHand());
            hand.innerRadius = am4core.percent(20);
            hand.radius = am4core.percent(85);
            
            // 核心修正 1：移除預設的滑入動畫，並直接將指針固定在 0
            hand.showValue(0, 0);

            // 核心修正 2：延遲 100ms 等待 DOM 渲染完畢後，再從 0 平滑轉動至目標分數
            setTimeout(function() {{
                hand.showValue({target_score}, 1000, am4core.ease.cubicOut);
            }}, 100);

        }});
        </script>
    </body>
    </html>
    """
    components.html(html_gauge, height=420, scrolling=False)
    

# 讀取 CSV

try:
    df = pd.read_csv("gaming_part1_100k.csv")
    df = df.head(1000)
    df = df[
        [
            "daily_gaming_hours",
            "sleep_hours",
            "addiction_level"
        ]
    ].copy()

    df = df.dropna()
except Exception as e:
    st.error("❌ CSV 讀取失敗")
    st.error(str(e))
    st.stop()

chart_data = []

for _, row in df.iterrows():
    chart_data.append({
        "x": float(
            row["daily_gaming_hours"]
        ),

        "y": float(
            row["sleep_hours"]
        ),
        "value": float(
            row["addiction_level"]
        ),
        "user": False
    })

chart_data.append({
    "x": game_hour,
    "y": sleep_hour,
    "value": addiction_score,
    "user": True
})

# 泡泡圖

chart_json = json.dumps(
    chart_data,
    ensure_ascii=False
)

st.divider()

st.subheader(
    "🫧 遊戲時間 × 睡眠時間 × 成癮程度"
)

html_code = f"""
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
0～2　低
</span>

<span class="item">
<span class="dot"
style="background:#8BC34A"></span>
2～4　偏低
</span>

<span class="item">
<span class="dot"
style="background:#FFC107"></span>
4～6　中
</span>

<span class="item">
<span class="dot"
style="background:#FF9800"></span>
6～8　偏高
</span>

<span class="item">
<span class="dot"
style="background:#F44336"></span>
8～10　高
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
    // 資料
    // =========================================

    chart.data = {chart_json};

    // =========================================
    // X 軸
    // =========================================

    var xAxis = chart.xAxes.push(
        new am4charts.ValueAxis()
    );

    xAxis.title.text =
        "每日遊戲時間（小時）";

    xAxis.min = 0;

    // =========================================
    // Y 軸
    // =========================================

    var yAxis = chart.yAxes.push(
        new am4charts.ValueAxis()
    );

    yAxis.title.text =
        "睡眠時間（小時）";

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
    // Bubble
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
                    target.dataItem.dataContext.value
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
                    target.dataItem.dataContext.value
                );

            if (value < 2) {{
                return am4core.color(
                    "#4CAF50"
                );
            }}

            if (value < 4) {{
                return am4core.color(
                    "#8BC34A"
                );
            }}

            if (value < 6) {{
                return am4core.color(
                    "#FFC107"
                );
            }}

            if (value < 8) {{
                return am4core.color(
                    "#FF9800"
                );
            }}

            return am4core.color(
                "#F44336"
            );
        }}
    );

    // =========================================
    // 使用者資料黑色外框
    // =========================================

    bullet.circle.adapter.add(
        "stroke",
        function(stroke, target) {{

            var isUser =
                target.dataItem.dataContext.user;

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

    bullet.circle.adapter.add(
        "strokeWidth",
        function(width, target) {{

            var isUser =
                target.dataItem.dataContext.user;

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
        "遊戲時間：{{valueX}} 小時\\n" +
        "睡眠時間：{{valueY}} 小時\\n" +
        "成癮程度：{{value}} / 10";

    // =========================================
    // 滑鼠放大
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

# 顯示圖表
components.html(
    html_code,
    height=600
)
