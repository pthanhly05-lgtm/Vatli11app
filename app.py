import json
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from google import genai

# Cấu hình giao diện trang web
st.set_page_config(
    page_title="Vật Lí 11 - Ôn Tập Chương 1", page_icon="⚛️", layout="wide"
)

# Lấy API Key từ Secrets của Streamlit (bảo mật, học sinh không cần nhập)
api_key = st.secrets.get("GEMINI_API_KEY", "")


def generate_questions(topic, difficulty, key):
  if not key:
    st.error("Chưa cấu hình API Key trong mục Secrets của Streamlit!")
    return None

  client = genai.Client(api_key=key)
  prompt = f"""
    Bạn là chuyên gia Vật lí THPT (chương trình GDPT mới).
    Hãy tạo 3 câu hỏi trắc nghiệm khách quan 4 lựa chọn về chủ đề: "{topic}", mức độ: "{difficulty}".
    Mỗi câu hỏi phải đúng chuẩn kiến thức Vật lí 11 Chương 1: Dao động.
    Trả về định dạng JSON thuần túy (không dùng markdown code block, chỉ chuỗi JSON hợp lệ):
    [
      {{
        "question": "Nội dung câu hỏi...",
        "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
        "correct_answer": "A. ...",
        "explanation": "Lời giải chi tiết ngắn gọn..."
      }}
    ]
    """
  try:
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    )
    raw_text = response.text.strip()
    if raw_text.startswith("```json"):
      raw_text = raw_text[7:-3].strip()
    elif raw_text.startswith("```"):
      raw_text = raw_text[3:-3].strip()
    return json.loads(raw_text)
  except Exception as e:
    st.error(f"Lỗi khi sinh câu hỏi: {e}")
    return None


# Thanh điều hướng
menu = st.sidebar.radio(
    "Nội dung học tập:",
    [
        "1. Mô phỏng & Lý thuyết trực quan",
        "2. Luyện tập trắc nghiệm sinh bởi AI",
    ],
)

# ----------------- PHẦN 1: MÔ PHỎNG & LÝ THUYẾT -----------------
if menu == "1. Mô phỏng & Lý thuyết trực quan":
  st.title("⚛️ Khám Phá Trực Quan: Dao Động Điều Hòa")
  st.markdown(
      "Kéo thanh trượt để quan sát đồ thị li độ - thời gian biến đổi tương"
      " ứng:"
  )

  col1, col2 = st.columns([1, 2])
  with col1:
    st.subheader("Cài đặt thông số")
    A = st.slider("Biên độ A (cm):", 1.0, 10.0, 4.0, 0.5)
    omega = st.slider("Tần số góc ω (rad/s):", 1.0, 10.0, 2.0, 0.5)
    phi = st.slider(
        "Pha ban đầu φ (rad):", -np.pi, np.pi, 0.0, 0.1 * np.pi, format="%.2f"
    )
    st.info(f"**Phương trình dao động:**\n$$x = {A}\\cos({omega:.1f}t + {phi:.2f})\\text{{ (cm)}}$$")

  with col2:
    t = np.linspace(0, 6, 500)
    x = A * np.cos(omega * t + phi)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=t,
            y=x,
            mode="lines",
            name="Li độ x(t)",
            line=dict(color="#1f77b4", width=3),
        )
    )
    fig.update_layout(
        title="Đồ thị li độ - thời gian x(t)",
        xaxis_title="Thời gian t (s)",
        yaxis_title="Li độ x (cm)",
        yaxis=dict(range=[-11, 11]),
        template="plotly_white",
        height=380,
    )
    st.plotly_chart(fig, use_container_width=True)

  st.divider()
  st.subheader("Bản tóm tắt công thức trọng tâm")
  c1, c2, c3 = st.columns(3)
  c1.metric("Vận tốc cực đại", f"v_max = {A*omega:.1f} cm/s")
  c2.metric("Gia tốc cực đại", f"a_max = {A*(omega**2):.1f} cm/s²")
  c3.metric("Chu kì T", f"{2*np.pi/omega:.2f} s")

# ----------------- PHẦN 2: LUYỆN TẬP SINH CÂU HỎI AI -----------------
elif menu == "2. Luyện tập trắc nghiệm sinh bởi AI":
  st.title("🎯 Tự Luyện Tập Trắc Nghiệm Thông Minh")
  st.caption("AI tự động sinh các biến thể câu hỏi khác nhau theo yêu cầu.")

  col_t1, col_t2 = st.columns(2)
  with col_t1:
    topic = st.selectbox(
        "Chọn mảng kiến thức:",
        [
            "Phương trình và các đại lượng dao động điều hòa",
            "Mối liên hệ giữa li độ, vận tốc và gia tốc",
            "Động năng, thế năng và cơ năng trong dao động",
            "Dao động tắt dần, dao động cưỡng bức và cộng hưởng",
        ],
    )
  with col_t2:
    difficulty = st.selectbox(
        "Mức độ:", ["Nhận biết", "Thông hiểu", "Vận dụng"]
    )

  if st.button("Sinh bộ câu hỏi mới ✨"):
    with st.spinner("AI đang tạo đề bài..."):
      st.session_state["questions"] = generate_questions(
          topic, difficulty, api_key
      )
      st.session_state["submitted"] = False

  if "questions" in st.session_state and st.session_state["questions"]:
    questions = st.session_state["questions"]
    with st.form("quiz_form"):
      user_answers = {}
      for idx, q in enumerate(questions):
        st.markdown(f"**Câu {idx+1}: {q['question']}**")
        user_answers[idx] = st.radio(
            "Chọn đáp án:", q["options"], key=f"q_{idx}", label_visibility="collapsed"
        )
        st.write("---")
      submit = st.form_submit_button("Nộp bài & Xem giải thích")

    if submit:
      st.session_state["submitted"] = True
      score = 0
      for idx, q in enumerate(questions):
        is_correct = user_answers[idx] == q["correct_answer"]
        if is_correct:
          score += 1
          st.success(f"Câu {idx+1}: Chính xác! ✅")
        else:
          st.error(
              f"Câu {idx+1}: Chưa chính xác! ❌ Đáp án đúng:"
              f" {q['correct_answer']}"
          )
        st.info(f"💡 **Lời giải chi tiết:** {q['explanation']}")
      st.balloons()
      st.subheader(f"Điểm số của bạn: {score}/{len(questions)}")
