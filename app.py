import streamlit as st
from datetime import date, timedelta, datetime
import time
import pandas as pd
import io
import json
from streamlit_local_storage import LocalStorage
import streamlit.components.v1 as components

# ================= 1. Page Config & Custom CSS =================
st.set_page_config(page_title="My Life App", page_icon="✨", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #FFDEE9 0%, #B5FFFC 100%); }
    div[data-testid="stVerticalBlock"] > div:has(div.stContainer) {
        background-color: rgba(255, 255, 255, 0.9); border-radius: 20px; padding: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.05);
    }
    .letter-paper {
        background-color: #fffdf5; border: 1px solid #e0d6b8; border-radius: 10px; padding: 30px;
        font-family: 'Courier New', Courier, monospace; box-shadow: 5px 5px 15px rgba(0,0,0,0.1); margin-top: 20px;
    }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================= 2. 多语言字典 =================
LANG = {
    "EN": {
        "radio": "🎵 My Radio", "nav": "🎛️ Navigation", "backup": "☁️ Backup & Restore",
        "upload": "Upload Backup (.json)", "restore_success": "✅ Data Restored!",
        "download": "Download Backup", "save_file": "Save File", "lock": "🔒 Lock App",
        "nav_plan": "🏠 Daily Plan", "nav_timer": "⏱️ Focus Timer", "nav_mood": "🌸 Mood & Calendar",
        "nav_media": "🎬 Media Tracker", "nav_export": "📥 Data & Envelope",
        "plan_title": "🏠 Daily Plan", "from_yesterday": "📥 From Yesterday",
        "unfinished": "(Unfinished)", "done": "✅ Done", "postpone": "➡️ Postpone",
        "timer_title": "⏱️ Focus Timer", "timer_desc": "Track your time accurately with the stopwatch.",
        "timer_task": "📌 What are you working on?", "timer_ph": "e.g., Study Math",
        "save_record": "Save Focus Record", "minutes_ph": "Minutes focused:", "save_btn": "💾 Save Record",
        "success_log": "✅ Logged: {} for {} mins!", "error_log": "Please enter a task name above!",
        "logs_title": "📖 Today's Time Logs",
        "mood_title": "🌸 Mood & Calendar", "mood_diary": "Mood Diary", "mood_desc": "Describe your mood:",
        "record_mood": "Record Mood", "cycle": "Cycle Predictor", "last_period": "Last period start date:",
        "cycle_len": "Cycle length (days):", "next_pred": "🗓️ Next predicted: **{}**",
        "media_title": "🎬 Media Tracker", "add_title": "Title:", "add_title_ph": "e.g., Inception",
        "bookmark": "Bookmark (Optional):", "bookmark_ph": "e.g., Ep 5 / Page 100", "add_btn": "Add",
        "finished": "✅ Finished",
        "export_title": "📥 Data & Envelope", "export_btn": "Export Data to Excel",
        "download_excel": "Download Excel", "end_day": "💌 End of the Day",
        "seal_btn": "🔒 Seal Today & Put in Envelope", "sealing": "Sealing...",
        "new_day": "Start a New Day", "letter_to": "✉️ To: You ({})",
        "letter_task": "Today you completed <b>{}</b> / {} tasks.",
        "letter_time": "You focused for a total of <b>{}</b> minutes.",
        "letter_mood": "Last mood: {}", "letter_end": "—— Have a good night 🌙"
    },
    "ZH": {
        "radio": "🎵 我的电台", "nav": "🎛️ 导航菜单", "backup": "☁️ 备份与恢复",
        "upload": "上传备份文件 (.json)", "restore_success": "✅ 数据恢复成功！",
        "download": "下载备份", "save_file": "保存文件", "lock": "🔒 锁定应用",
        "nav_plan": "🏠 每日计划", "nav_timer": "⏱️ 专注时间", "nav_mood": "🌸 心情与日历",
        "nav_media": "🎬 书影音打卡", "nav_export": "📥 数据与信封",
        "plan_title": "🏠 每日计划", "from_yesterday": "📥 昨日未完成",
        "unfinished": "(未完成)", "done": "✅ 完成", "postpone": "➡️ 顺延",
        "timer_title": "⏱️ 专注时间", "timer_desc": "用秒表准确记录你的时间开销。",
        "timer_task": "📌 我正在做：", "timer_ph": "例如：复习高数",
        "save_record": "保存专注记录", "minutes_ph": "专注分钟数：", "save_btn": "💾 保存记录",
        "success_log": "✅ 已记录：{} 专注了 {} 分钟！", "error_log": "请先在上方输入任务名称！",
        "logs_title": "📖 今日时间账本",
        "mood_title": "🌸 心情与日历", "mood_diary": "心情日记", "mood_desc": "描述你的心情：",
        "record_mood": "记录心情", "cycle": "生理期预测", "last_period": "上次月经开始日期：",
        "cycle_len": "周期天数：", "next_pred": "🗓️ 预测下次：**{}**",
        "media_title": "🎬 书影音打卡", "add_title": "名称：", "add_title_ph": "例如：沙丘2",
        "bookmark": "书签进度 (可选)：", "bookmark_ph": "例如：第5集 / 第100页", "add_btn": "添加",
        "finished": "✅ 已完成",
        "export_title": "📥 数据与信封", "export_btn": "导出到 Excel",
        "download_excel": "下载 Excel", "end_day": "💌 结束今天",
        "seal_btn": "🔒 封存今天并装入信封", "sealing": "正在封存...",
        "new_day": "开启新的一天", "letter_to": "✉️ 致 {} 的你",
        "letter_task": "今天你完成了 <b>{}</b> / {} 项计划。",
        "letter_time": "你一共专注了 <b>{}</b> 分钟。",
        "letter_mood": "最后的心情：{}", "letter_end": "—— 晚安，好梦 🌙"
    }
}

# ================= 3. 状态与本地存储 =================
localS = LocalStorage()
if "lang" not in st.session_state:
    st.session_state.lang = "EN" # 默认英文

def t(key):
    return LANG[st.session_state.lang].get(key, key)

saved_data_str = localS.getItem("my_life_app_data")
if saved_data_str and "initialized" not in st.session_state:
    try:
        saved_data = json.loads(saved_data_str)
        st.session_state.todo_data = saved_data.get("todo_data", {})
        st.session_state.task_states = saved_data.get("task_states", {})
        st.session_state.mood_data = saved_data.get("mood_data", [])
        st.session_state.media_data = saved_data.get("media_data", {})
        st.session_state.time_logs = saved_data.get("time_logs", [])
        st.session_state.initialized = True
    except:
        pass

if "todo_data" not in st.session_state:
    st.session_state.todo_data = {
        "📚 Study": ["Read 10 pages", "Finish homework"],
        "🏃‍♂️ Exercise": ["Workout", "Stretch"],
        "🏠 Life": ["Clean room"],
        "🎮 Entertainment": ["Watch TV"]
    }
    st.session_state.task_states = {}
    st.session_state.mood_data = []
    st.session_state.media_data = {"🎬 Movies": [], "📺 TV Shows": [], "📖 Books": [], "🎤 Variety": []}
    st.session_state.time_logs = []
    st.session_state.initialized = True

if "unlocked" not in st.session_state: st.session_state.unlocked = False
if "page" not in st.session_state: st.session_state.page = "plan"
if "day_ended" not in st.session_state: st.session_state.day_ended = False

def save_to_browser():
    data_to_save = {
        "todo_data": st.session_state.todo_data, "task_states": st.session_state.task_states,
        "mood_data": st.session_state.mood_data, "media_data": st.session_state.media_data,
        "time_logs": st.session_state.time_logs
    }
    try:
        localS.setItem("my_life_app_data", json.dumps(data_to_save))
    except:
        pass

# ================= 4. Unlock Page =================
if not st.session_state.unlocked:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #FF69B4; font-size: 60px;'>✨ My Life ✨</h1>", unsafe_allow_html=True)
        unlock = st.slider("👇 Swipe right to unlock 👇" if st.session_state.lang=="EN" else "👇 向右滑动解锁 👇", 0, 3, 0)
        if unlock == 3:
            st.session_state.unlocked = True
            st.rerun()
    st.stop()

# ================= 5. Sidebar =================
with st.sidebar:
    # 语言切换按钮
    lang_choice = st.radio("Language / 语言", ["EN", "ZH"], index=0 if st.session_state.lang=="EN" else 1, horizontal=True)
    st.session_state.lang = lang_choice

    st.markdown(f"<h3 style='text-align: center;'>{t('radio')}</h3>", unsafe_allow_html=True)
    audio_url = "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3" 
    st.markdown(f"""
        <audio controls loop style="width: 100%; border-radius: 10px;">
            <source src="{audio_url}" type="audio/mpeg">
        </audio>
    """, unsafe_allow_html=True)
    
    st.write("---")
    st.markdown(f"<h2 style='text-align: center;'>{t('nav')}</h2>", unsafe_allow_html=True)
    
    with st.expander(t('backup')):
        uploaded_backup = st.file_uploader(t('upload'), type=["json"])
        if uploaded_backup is not None:
            imported = json.load(uploaded_backup)
            st.session_state.todo_data = imported.get("todo_data", st.session_state.todo_data)
            st.session_state.task_states = imported.get("task_states", st.session_state.task_states)
            st.session_state.mood_data = imported.get("mood_data", st.session_state.mood_data)
            st.session_state.media_data = imported.get("media_data", st.session_state.media_data)
            st.session_state.time_logs = imported.get("time_logs", st.session_state.time_logs)
            save_to_browser()
            st.success(t('restore_success'))
            st.rerun()
        if st.button(t('download')):
            data = {"todo_data": st.session_state.todo_data, "task_states": st.session_state.task_states, "mood_data": st.session_state.mood_data, "media_data": st.session_state.media_data, "time_logs": st.session_state.time_logs}
            st.download_button(t('save_file'), data=json.dumps(data, ensure_ascii=False), file_name="MyLife_Backup.json")

    st.divider()
    if st.button(t('nav_plan'), use_container_width=True): st.session_state.page = "plan"
    if st.button(t('nav_timer'), use_container_width=True): st.session_state.page = "timer"
    if st.button(t('nav_mood'), use_container_width=True): st.session_state.page = "mood"
    if st.button(t('nav_media'), use_container_width=True): st.session_state.page = "media"
    if st.button(t('nav_export'), use_container_width=True): st.session_state.page = "export"
    st.divider()
    if st.button(t('lock'), use_container_width=True): st.session_state.unlocked = False; st.rerun()

# ================= 6. Page: Daily Plan =================
if st.session_state.page == "plan":
    st.title(t('plan_title'))
    st.caption(f"Date: {date.today().strftime('%B %d, %Y')}")
    
    if "yesterday_task" not in st.session_state:
        st.session_state.yesterday_task = "Review yesterday's notes"
    
    if st.session_state.yesterday_task:
        st.subheader(t('from_yesterday'))
        with st.container(border=True):
            c_task, c_done, c_postpone = st.columns([3, 1, 1])
            with c_task:
                st.write(f"**{st.session_state.yesterday_task}** {t('unfinished')}")
            with c_done:
                if st.button(t('done'), key="done_yesterday", use_container_width=True):
                    st.session_state.yesterday_task = ""
                    save_to_browser()
                    st.rerun()
            with c_postpone:
                if st.button(t('postpone'), key="postpone_yesterday", use_container_width=True):
                    st.session_state.todo_data["📚 Study"].append(st.session_state.yesterday_task + " (Postponed)")
                    st.session_state.yesterday_task = ""
                    save_to_browser()
                    st.rerun()
        st.divider()

    col1, col2 = st.columns(2)
    quad_keys = list(st.session_state.todo_data.keys())
    
    def render_quadrant(col, key_name):
        with col:
            st.subheader(key_name)
            with st.container(border=True):
                for task in st.session_state.todo_data[key_name]:
                    k = f"{key_name}_{task}"
                    is_done = st.checkbox(task, value=st.session_state.task_states.get(k, False), key=k, on_change=save_to_browser)
                    st.session_state.task_states[k] = is_done

    render_quadrant(col1, quad_keys[0])
    render_quadrant(col1, quad_keys[2])
    render_quadrant(col2, quad_keys[1])
    render_quadrant(col2, quad_keys[3])

# ================= 7. Page: Focus Timer =================
elif st.session_state.page == "timer":
    st.title(t('timer_title'))
    st.write(t('timer_desc'))
    
    timer_task = st.text_input(t('timer_task'), placeholder=t('timer_ph'))
    
    timer_html = """
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: 20px;">
        <div id="circle" style="width: 250px; height: 250px; border-radius: 50%; background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 99%, #FECFEF 100%); display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
            <h1 id="display" style="color: white; font-size: 45px; font-family: monospace; margin: 0;">00:00:00</h1>
        </div>
        <div style="margin-top: 20px; display: flex; gap: 15px;">
            <button onclick="startTimer()" style="padding: 10px 20px; border-radius: 20px; border: none; background: #4CAF50; color: white; font-size: 16px; cursor: pointer;">▶️ Start</button>
            <button onclick="pauseTimer()" style="padding: 10px 20px; border-radius: 20px; border: none; background: #FFC107; color: white; font-size: 16px; cursor: pointer;">⏸️ Pause</button>
            <button onclick="stopTimer()" style="padding: 10px 20px; border-radius: 20px; border: none; background: #F44336; color: white; font-size: 16px; cursor: pointer;">⏹️ End</button>
        </div>
        <p id="status" style="margin-top: 15px; color: #666;">Status: Idle</p>
    </div>

    <script>
        let timer;
        let seconds = 0;
        let isRunning = false;
        
        function updateDisplay() {
            let h = Math.floor(seconds / 3600).toString().padStart(2, '0');
            let m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
            let s = (seconds % 60).toString().padStart(2, '0');
            document.getElementById('display').innerText = h + ":" + m + ":" + s;
        }
        
        function startTimer() {
            if (!isRunning) {
                isRunning = true;
                document.getElementById('status').innerText = "Status: Focusing...";
                document.getElementById('circle').style.background = "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)";
                timer = setInterval(() => {
                    seconds++;
                    updateDisplay();
                }, 1000);
            }
        }
        
        function pauseTimer() {
            if (isRunning) {
                isRunning = false;
                clearInterval(timer);
                document.getElementById('status').innerText = "Status: Paused";
                document.getElementById('circle').style.background = "linear-gradient(135deg, #e0e0e0 0%, #f5f5f5 100%)";
            }
        }
        
        function stopTimer() {
            if (seconds > 0) {
                isRunning = false;
                clearInterval(timer);
                document.getElementById('status').innerText = "Status: Finished! Save it below.";
                document.getElementById('circle').style.background = "linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%)";
            }
        }
    </script>
    """
    components.html(timer_html, height=400)
    
    st.divider()
    st.subheader(t('save_record'))
    c_save1, c_save2 = st.columns([2, 1])
    with c_save1:
        manual_min = st.number_input(t('minutes_ph'), min_value=1, max_value=600, value=25)
    with c_save2:
        st.write("")
        st.write("")
        if st.button(t('save_btn'), use_container_width=True):
            if timer_task:
                st.session_state.time_logs.append({
                    "task": timer_task,
                    "minutes": manual_min,
                    "time": datetime.now().strftime("%H:%M")
                })
                save_to_browser()
                st.success(t('success_log').format(timer_task, manual_min))
                st.rerun()
            else:
                st.error(t('error_log'))
                
    if st.session_state.time_logs:
        st.subheader(t('logs_title'))
        for log in reversed(st.session_state.time_logs):
            st.info(f"🕒 {log['time']} | **{log['task']}** | {log['minutes']} mins")

# ================= 8. Page: Mood & Calendar =================
elif st.session_state.page == "mood":
    st.title(t('mood_title'))
    c1, c2 = st.columns(2)
    with c1:
        st.subheader(t('mood_diary'))
        mood_text = st.text_area(t('mood_desc'))
        if st.button(t('record_mood'), type="primary") and mood_text:
            text_lower = mood_text.lower()
            if any(w in text_lower for w in ["happy", "good", "great", "开心", "高兴"]): mood, emoji = "😆 Happy", "😆"
            elif any(w in text_lower for w in ["sad", "tired", "emo", "难过", "累"]): mood, emoji = "😭 Sad", "😭"
            else: mood, emoji = "😶 Calm", "😶"
            st.session_state.mood_data.append({"date": date.today().strftime("%Y-%m-%d"), "text": mood_text, "mood": mood})
            save_to_browser()
            st.markdown(f"<h1 style='text-align: center; font-size: 120px;'>{emoji}</h1>", unsafe_allow_html=True)
    with c2:
        st.subheader(t('cycle'))
        last_period = st.date_input(t('last_period'), date.today() - timedelta(days=14))
        cycle_len = st.number_input(t('cycle_len'), 20, 40, 28)
        next_period = last_period + timedelta(days=cycle_len)
        st.success(t('next_pred').format(next_period.strftime('%Y-%m-%d')))

# ================= 9. Page: Media Tracker =================
elif st.session_state.page == "media":
    st.title(t('media_title'))
    
    with st.container(border=True):
        c_add1, c_add2, c_add3 = st.columns([2, 2, 1])
        with c_add1:
            media_type = st.selectbox("Category:", list(st.session_state.media_data.keys()))
            new_media = st.text_input(t('add_title'), placeholder=t('add_title_ph'))
        with c_add2:
            bookmark_note = st.text_input(t('bookmark'), placeholder=t('bookmark_ph'))
        with c_add3:
            st.write("") 
            st.write("") 
            if st.button(t('add_btn'), use_container_width=True) and new_media:
                note = f" ({bookmark_note})" if bookmark_note else ""
                st.session_state.media_data[media_type].append(new_media + note)
                save_to_browser()
                st.rerun()
    
    cols = st.columns(2)
    for i, (m_type, items) in enumerate(st.session_state.media_data.items()):
        with cols[i % 2]:
            st.subheader(m_type)
            with st.container(border=True):
                for item in items:
                    k = f"media_{m_type}_{item}"
                    is_done = st.checkbox(item, value=st.session_state.task_states.get(k, False), key=k, on_change=save_to_browser)
                    st.session_state.task_states[k] = is_done
                    if is_done:
                        st.markdown(f"~~{item}~~ {t('finished')}")

# ================= 10. Page: Export & Envelope =================
elif st.session_state.page == "export":
    st.title(t('export_title'))
    
    if st.button(t('export_btn')):
        task_data = [{"Type": "Task", "Date": date.today(), "Content": t, "Status": "Done" if st.session_state.task_states.get(f"{c}_{t}") else "Pending"} for c, ts in st.session_state.todo_data.items() for t in ts]
        mood_records = [{"Type": "Mood", "Date": r["date"], "Content": r["text"], "Status": r["mood"]} for r in st.session_state.mood_data]
        time_records = [{"Type": "Time", "Date": date.today(), "Content": l["task"], "Status": f"{l['minutes']} mins"} for l in st.session_state.time_logs]
        df = pd.DataFrame(task_data + mood_records + time_records)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='MyLife')
        st.download_button(t('download_excel'), data=buffer.getvalue(), file_name="MyLife.xlsx")
    
    st.divider()
    st.subheader(t('end_day'))
    if not st.session_state.day_ended:
        if st.button(t('seal_btn'), type="primary"):
            with st.spinner(t('sealing')):
                time.sleep(1.5)
                st.session_state.day_ended = True
                st.balloons()
                st.rerun()
    else:
        total_tasks = sum(len(ts) for ts in st.session_state.todo_data.values())
        done_tasks = sum(1 for k, v in st.session_state.task_states.items() if v)
        total_time = sum(l["minutes"] for l in st.session_state.time_logs)
        
        st.markdown(f"""
        <div class="letter-paper">
            <h3 style="text-align: center; color: #8b7355;">{t('letter_to').format(date.today().strftime('%Y-%m-%d'))}</h3>
            <p>{t('letter_task').format(done_tasks, total_tasks)}</p>
            <p>{t('letter_time').format(total_time)}</p>
            <p>{t('letter_mood').format(st.session_state.mood_data[-1]['text'] if st.session_state.mood_data else 'None')}</p>
            <br>
            <p style="text-align: right;">{t('letter_end')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(t('new_day')):
            st.session_state.day_ended = False
            st.session_state.page = "plan"
            st.rerun()