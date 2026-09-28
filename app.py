import sqlite3
from datetime import date
import streamlit as st
from PIL import Image

# =========================================================
# CẤU HÌNH TRANG
# =========================================================

st.set_page_config(
    page_title="Hotel Room Manager",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_NAME = "hotel.db"

ROOM_STATUSES = [
    "Trống",
    "Đã đặt",
    "Đang ở",
    "Đang dọn",
    "Bảo trì"
]

ROOM_TYPES = [
    "Superior",
    "Deluxe",
    "Super Deluxe",
    "Suite"
]


# =========================================================
# DATABASE OPERATIONS
# =========================================================

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT UNIQUE NOT NULL,
            room_type TEXT NOT NULL,
            floor INTEGER NOT NULL,
            price REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Trống',
            guest_name TEXT DEFAULT '',
            guest_phone TEXT DEFAULT '',
            check_in TEXT DEFAULT '',
            check_out TEXT DEFAULT '',
            note TEXT DEFAULT ''
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM rooms")
    count = cursor.fetchone()[0]

    if count == 0:
        sample_rooms = [
            ("101", "Superior", 1, 900000, "Trống"),
            ("102", "Superior", 1, 900000, "Đang ở"),
            ("103", "Deluxe", 1, 1200000, "Đã đặt"),
            ("104", "Deluxe", 1, 1200000, "Đang dọn"),
            ("201", "Superior", 2, 900000, "Trống"),
            ("202", "Super Deluxe", 2, 1500000, "Trống"),
            ("203", "Super Deluxe", 2, 1500000, "Đang ở"),
            ("204", "Suite", 2, 2200000, "Bảo trì"),
            ("301", "Superior", 3, 900000, "Trống"),
            ("302", "Deluxe", 3, 1200000, "Đã đặt"),
            ("303", "Super Deluxe", 3, 1500000, "Trống"),
            ("304", "Suite", 3, 2200000, "Trống"),
        ]

        cursor.executemany("""
            INSERT INTO rooms
            (room_number, room_type, floor, price, status)
            VALUES (?, ?, ?, ?, ?)
        """, sample_rooms)

    conn.commit()
    conn.close()


def get_rooms():
    conn = get_connection()
    rooms = conn.execute("""
        SELECT * FROM rooms
        ORDER BY CAST(room_number AS INTEGER)
    """).fetchall()
    conn.close()
    return rooms


def get_room(room_id):
    conn = get_connection()
    room = conn.execute(
        "SELECT * FROM rooms WHERE id = ?",
        (room_id,)
    ).fetchone()
    conn.close()
    return room


def add_room(room_number, room_type, floor, price, status, note):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO rooms
            (room_number, room_type, floor, price, status, note)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (room_number, room_type, floor, price, status, note))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    finally:
        conn.close()
    return success


def update_room(room_id, room_number, room_type, floor, price, status, note):
    conn = get_connection()
    try:
        conn.execute("""
            UPDATE rooms
            SET room_number = ?,
                room_type = ?,
                floor = ?,
                price = ?,
                status = ?,
                note = ?
            WHERE id = ?
        """, (room_number, room_type, floor, price, status, note, room_id))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    finally:
        conn.close()
    return success


def delete_room(room_id):
    conn = get_connection()
    conn.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
    conn.commit()
    conn.close()


def update_booking(room_id, status, guest_name, guest_phone, check_in, check_out, note):
    conn = get_connection()
    conn.execute("""
        UPDATE rooms
        SET status = ?,
            guest_name = ?,
            guest_phone = ?,
            check_in = ?,
            check_out = ?,
            note = ?
        WHERE id = ?
    """, (status, guest_name, guest_phone, check_in, check_out, note, room_id))
    conn.commit()
    conn.close()


# =========================================================
# UTILS & STYLES
# =========================================================

def format_money(value):
    return f"{value:,.0f} đ"


def status_icon(status):
    icons = {
        "Trống": "🟢",
        "Đã đặt": "🔵",
        "Đang ở": "🟠",
        "Đang dọn": "🟡",
        "Bảo trì": "🔴"
    }
    return icons.get(status, "⚪")


def status_color(status):
    colors = {
        "Trống": "#16a34a",
        "Đã đặt": "#2563eb",
        "Đang ở": "#f97316",
        "Đang dọn": "#eab308",
        "Bảo trì": "#dc2626"
    }
    return colors.get(status, "#64748b")


# Khởi tạo DB lần đầu
init_database()

# CSS Custom
st.markdown("""
<style>
.main {
    background-color: #f8fafc;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
.hotel-title {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 0;
}
.hotel-subtitle {
    color: #64748b;
    margin-top: 5px;
}
.room-card {
    padding: 18px;
    border-radius: 14px;
    background: white;
    border: 1px solid #e2e8f0;
    margin-bottom: 12px;
}
.room-number {
    font-size: 23px;
    font-weight: 700;
}
.status-badge {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    color: white;
    font-size: 13px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

st.sidebar.title("🏨 HOTEL MANAGER")
st.sidebar.caption("Hệ thống quản lý phòng khách sạn")

menu = st.sidebar.radio(
    "MENU",
    [
        "📊 Tổng quan",
        "🛏️ Quản lý phòng",
        "📅 Đặt phòng / Nhận phòng",
        "➕ Thêm phòng"
    ]
)

st.sidebar.divider()
st.sidebar.info("💡 Dữ liệu được lưu tự động trong file `hotel.db`.")


# =========================================================
# LOAD DATA & METRICS
# =========================================================

rooms = get_rooms()

total_rooms = len(rooms)
empty_rooms = sum(r["status"] == "Trống" for r in rooms)
booked_rooms = sum(r["status"] == "Đã đặt" for r in rooms)
occupied_rooms = sum(r["status"] == "Đang ở" for r in rooms)
cleaning_rooms = sum(r["status"] == "Đang dọn" for r in rooms)
maintenance_rooms = sum(r["status"] == "Bảo trì" for r in rooms)


# =========================================================
# MODULE 1: TỔNG QUAN
# =========================================================

if menu == "📊 Tổng quan":

    try:
        image = Image.open("IMG_4862.jpeg")
        st.image(image, use_container_width=True)
    except FileNotFoundError:
        st.info("💡 Tip: Đặt ảnh `IMG_4862.jpeg` cùng thư mục để hiển thị ảnh banner khách sạn.")

    st.markdown('<div class="hotel-title">🏨 Tổng quan khách sạn</div>', unsafe_allow_html=True)
    st.markdown('<div class="hotel-subtitle">Theo dõi tình trạng phòng và hoạt động lưu trú</div>', unsafe_allow_html=True)
    st.write("")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🏨 Tổng phòng", total_rooms)
    col2.metric("🟢 Phòng trống", empty_rooms)
    col3.metric("🔵 Đã đặt", booked_rooms)
    col4.metric("🟠 Đang ở", occupied_rooms)
    col5.metric("🔴 Bảo trì", maintenance_rooms)

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 Tình trạng phòng")
        chart_data = {
            "Trạng thái": ["Trống", "Đã đặt", "Đang ở", "Đang dọn", "Bảo trì"],
            "Số phòng": [empty_rooms, booked_rooms, occupied_rooms, cleaning_rooms, maintenance_rooms]
        }
        st.bar_chart(chart_data, x="Trạng thái", y="Số phòng")

    with col_right:
        st.subheader("📈 Tỷ lệ sử dụng phòng")
        usable_rooms = total_rooms - maintenance_rooms
        occupancy = (occupied_rooms / usable_rooms) if usable_rooms > 0 else 0

        st.metric("Tỷ lệ phòng đang có khách", f"{occupancy * 100:.1f}%")
        st.progress(min(occupancy, 1.0))
        st.write(f"Đang có khách: **{occupied_rooms} phòng**")
        st.write(f"Phòng có thể khai thác: **{usable_rooms} phòng**")

    st.divider()

    st.subheader("🛏️ Sơ đồ nhanh danh sách phòng")
    cols = st.columns(4)
    for index, room in enumerate(rooms):
        with cols[index % 4]:
            color = status_color(room["status"])
            st.markdown(f"""
                <div class="room-card">
                    <div class="room-number">Phòng {room["room_number"]}</div>
                    <div style="margin-top:4px;">{room["room_type"]} - Tầng {room["floor"]}</div>
                    <div style="margin-top:8px;">
                        <span class="status-badge" style="background:{color};">
                            {status_icon(room["status"])} {room["status"]}
                        </span>
                    </div>
                    <div style="margin-top:10px; color:#64748b; font-weight:600;">
                        {format_money(room["price"])} / đêm
                    </div>
                </div>
            """, unsafe_allow_html=True)


# =========================================================
# MODULE 2: QUẢN LÝ PHÒNG
# =========================================================

elif menu == "🛏️ Quản lý phòng":

    st.title("🛏️ Quản lý & Chỉnh sửa phòng")

    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input("🔍 Tìm phòng", placeholder="Nhập số phòng...")
    with col2:
        status_filter = st.selectbox("📌 Trạng thái", ["Tất cả"] + ROOM_STATUSES)
    with col3:
        type_filter = st.selectbox("🛏️ Loại phòng", ["Tất cả"] + ROOM_TYPES)

    filtered_rooms = rooms

    if search:
        filtered_rooms = [r for r in filtered_rooms if search.lower() in r["room_number"].lower()]
    if status_filter != "Tất cả":
        filtered_rooms = [r for r in filtered_rooms if r["status"] == status_filter]
    if type_filter != "Tất cả":
        filtered_rooms = [r for r in filtered_rooms if r["room_type"] == type_filter]

    st.write(f"Hiển thị **{len(filtered_rooms)}** / **{total_rooms}** phòng")
    st.divider()

    if not filtered_rooms:
        st.warning("Không tìm thấy phòng phù hợp.")

    for room in filtered_rooms:
        with st.container(border=True):
            col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])

            with col1:
                st.markdown(f"### {room['room_number']}")
            with col2:
                st.write(f"**Loại:** {room['room_type']}")
                st.write(f"**Tầng:** {room['floor']}")
            with col3:
                st.write(f"**Giá:** {format_money(room['price'])}")
            with col4:
                st.markdown(
                    f'<span class="status-badge" style="background:{status_color(room["status"])};">'
                    f'{status_icon(room["status"])} {room["status"]}</span>',
                    unsafe_allow_html=True
                )
            with col5:
                if st.button("✏️ Sửa", key=f"edit_btn_{room['id']}"):
                    st.session_state["edit_room_id"] = (
                        None if st.session_state.get("edit_room_id") == room["id"] else room["id"]
                    )

        # Form chỉnh sửa tích hợp ngay dưới card
        if st.session_state.get("edit_room_id") == room["id"]:
            st.markdown("#### ✏️ Cập nhật thông tin phòng")
            with st.form(f"edit_form_{room['id']}"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    new_number = st.text_input("Số phòng", value=room["room_number"])
                    new_type = st.selectbox(
                        "Loại phòng",
                        ROOM_TYPES,
                        index=ROOM_TYPES.index(room["room_type"]) if room["room_type"] in ROOM_TYPES else 0
                    )
                with c2:
                    new_floor = st.number_input("Tầng", min_value=1, max_value=100, value=int(room["floor"]))
                    new_price = st.number_input("Giá / đêm", min_value=0.0, value=float(room["price"]), step=100000.0)
                with c3:
                    new_status = st.selectbox(
                        "Trạng thái",
                        ROOM_STATUSES,
                        index=ROOM_STATUSES.index(room["status"]) if room["status"] in ROOM_STATUSES else 0
                    )
                    new_note = st.text_area("Ghi chú", value=room["note"] or "")

                save = st.form_submit_button("💾 Lưu thay đổi")

                if save:
                    if not new_number.strip():
                        st.error("Vui lòng nhập số phòng.")
                    else:
                        success = update_room(
                            room["id"],
                            new_number.strip(),
                            new_type,
                            new_floor,
                            new_price,
                            new_status,
                            new_note
                        )
                        if success:
                            st.success("Đã cập nhật phòng.")
                            st.session_state["edit_room_id"] = None
                            st.rerun()
                        else:
                            st.error("Số phòng đã tồn tại!")

            if st.button("🗑️ Xóa phòng này", key=f"delete_btn_{room['id']}", type="secondary"):
                delete_room(room["id"])
                st.session_state["edit_room_id"] = None
                st.success("Đã xóa phòng.")
                st.rerun()


# =========================================================
# MODULE 3: ĐẶT PHÒNG / NHẬN PHÒNG
# =========================================================

elif menu == "📅 Đặt phòng / Nhận phòng":

    st.title("📅 Đặt phòng & Quản lý check-in/out")

    if not rooms:
        st.warning("Hiện chưa có phòng nào trong cơ sở dữ liệu. Vui lòng thêm phòng mới.")
    else:
        room_options = {
            f"Phòng {r['room_number']} - {r['room_type']} ({r['status']})": r["id"]
            for r in rooms
        }

        selected_label = st.selectbox("🛏️ Chọn phòng thao tác", list(room_options.keys()))
        selected_id = room_options[selected_label]
        room = get_room(selected_id)

        st.divider()

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown(f"### Phòng {room['room_number']}")
            st.write(f"**Loại phòng:** {room['room_type']}")
            st.write(f"**Tầng:** {room['floor']}")
            st.write(f"**Giá phòng:** {format_money(room['price'])}/đêm")
            st.write(f"**Trạng thái hiện tại:** {status_icon(room['status'])} **{room['status']}**")

        with col2:
            with st.form("booking_form"):
                st.markdown("#### Thông tin lưu trú")
                guest_name = st.text_input("👤 Tên khách hàng", value=room["guest_name"] or "")
                guest_phone = st.text_input("📱 Số điện thoại", value=room["guest_phone"] or "")

                c1, c2 = st.columns(2)
                with c1:
                    default_checkin = date.fromisoformat(room["check_in"]) if room["check_in"] else date.today()
                    check_in = st.date_input("📅 Ngày nhận phòng", value=default_checkin)
                with c2:
                    default_checkout = date.fromisoformat(room["check_out"]) if room["check_out"] else date.today()
                    check_out = st.date_input("📅 Ngày trả phòng", value=default_checkout)

                new_status = st.selectbox(
                    "📌 Cập nhật trạng thái phòng",
                    ROOM_STATUSES,
                    index=ROOM_STATUSES.index(room["status"]) if room["status"] in ROOM_STATUSES else 0
                )

                note = st.text_area("📝 Ghi chú lưu trú", value=room["note"] or "")

                submit = st.form_submit_button("💾 Cập nhật lưu trú")

                if submit:
                    if check_out < check_in:
                        st.error("Ngày trả phòng không được trước ngày nhận phòng!")
                    else:
                        update_booking(
                            room["id"],
                            new_status,
                            guest_name,
                            guest_phone,
                            check_in.isoformat(),
                            check_out.isoformat(),
                            note
                        )
                        st.success("Đã cập nhật thông tin đặt phòng thành công!")
                        st.rerun()


# =========================================================
# MODULE 4: THÊM PHÒNG
# =========================================================

elif menu == "➕ Thêm phòng":

    st.title("➕ Thêm phòng mới")
    st.write("Nhập các thông tin dưới đây để tạo phòng mới vào hệ thống.")

    with st.form("add_room_form"):
        col1, col2 = st.columns(2)

        with col1:
            room_number = st.text_input("🔢 Số phòng *", placeholder="Ví dụ: 405")
            room_type = st.selectbox("🛏️ Loại phòng", ROOM_TYPES)
            floor = st.number_input("🏢 Tầng", min_value=1, max_value=100, value=1)

        with col2:
            price = st.number_input("💰 Giá phòng / đêm", min_value=0.0, value=900000.0, step=100000.0)
            status = st.selectbox("📌 Trạng thái ban đầu", ROOM_STATUSES)
            note = st.text_area("📝 Ghi chú")

        submit = st.form_submit_button("➕ Thêm phòng vào hệ thống")

        if submit:
            if not room_number.strip():
                st.error("Vui lòng nhập số phòng.")
            else:
                success = add_room(
                    room_number.strip(),
                    room_type,
                    floor,
                    price,
                    status,
                    note
                )
                if success:
                    st.success(f"Đã thêm thành công phòng {room_number}!")
                    st.rerun()
                else:
                    st.error("Số phòng này đã tồn tại trong hệ thống.")


# =========================================================
# FOOTER
# =========================================================

st.sidebar.caption("Hotel Room Manager • Streamlit App")
