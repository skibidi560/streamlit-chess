import streamlit as st
import chess
import random
from streamlit_chess import chess_board

# 1. Cấu hình giao diện ứng dụng
st.set_page_config(page_title="Cờ Vua AI - Nhiều Cấp Độ", page_icon="🤖", layout="centered")
st.title("👑 GAME CỜ VUA: ĐẤU VỚI MÁY (AI)")

# 2. Khởi tạo bộ nhớ lưu trữ trạng thái Game
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "ai_thinking" not in st.session_state:
    st.session_state.ai_thinking = False

# 3. Tạo thanh điều khiển ở bên cạnh (Sidebar) để chọn chế độ
st.sidebar.header("🛠️ CÀI ĐẶT TRẬN ĐẤU")
play_mode = st.sidebar.selectbox("Chế độ chơi:", ["Đấu với Máy (AI)", "2 Người chơi (PvP)"])

difficulty = "Dễ"
if play_mode == "Đấu với Máy (AI)":
    difficulty = st.sidebar.select_slider("Mức độ khó của Máy:", options=["Dễ", "Trung bình", "Khó"])
    st.sidebar.caption("💡 **Dễ:** Máy đi ngẫu nhiên. **Trung bình:** Máy biết ăn quân ngon. **Khó:** Máy tính toán trước nước đi.")

# Nút đặt lại bàn cờ mới
if st.sidebar.button("🔄 Làm mới ván cờ"):
    st.session_state.board = chess.Board()
    st.session_state.ai_thinking = False
    st.rerun()

# 4. HÀM XỬ LÝ BỘ NÃO AI (Thuật toán tìm nước đi cho Máy)
def evaluate_board(board):
    # Tính điểm bàn cờ dựa trên giá trị các quân cờ
    piece_values = {
        chess.PAWN: 10, chess.KNIGHT: 30, chess.BISHOP: 30, 
        chess.ROOK: 50, chess.QUEEN: 90, chess.KING: 900
    }
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            # Nếu là quân Trắng (Người) thì cộng điểm, quân Đen (Máy) thì trừ điểm
            val = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                score += val
            else:
                score -= val
    return score

def get_ai_move(board, level):
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None

    # MỨC ĐỘ DỄ: Máy đi ngẫu nhiên hoàn toàn
    if level == "Dễ":
        return random.choice(legal_moves)

    # MỨC ĐỘ TRUNG BÌNH: Tìm nước đi ăn được nhiều điểm nhất ngay lập tức
    elif level == "Trung bình":
        best_move = random.choice(legal_moves)
        best_score = float('inf') # Máy chọn điểm càng thấp (âm nhiều) càng tốt
        
        for move in legal_moves:
            board.push(move)
            score = evaluate_board(board)
            board.pop()
            if score < best_score:
                best_score = score
                best_move = move
        return best_move

    # MỨC ĐỘ KHÓ: Tính toán thêm 1 bước phản công của người chơi (Minimax cơ bản)
    elif level == "Khó":
        best_move = random.choice(legal_moves)
        best_score = float('inf')
        
        for move in legal_moves:
            board.push(move)
            if board.is_checkmate(): # Ưu tiên chiếu hết
                board.pop()
                return move
            
            # Giả định người chơi sẽ đi nước tốt nhất sau đó
            opponent_moves = list(board.legal_moves)
            max_opponent_score = float('-inf')
            for opp_move in opponent_moves:
                board.push(opp_move)
                opp_score = evaluate_board(board)
                board.pop()
                if opp_score > max_opponent_score:
                    max_opponent_score = opp_score
            
            board.pop()
            if max_opponent_score < best_score:
                best_score = max_opponent_score
                best_move = move
        return best_move

# 5. HIỂN THỊ BÀN CỜ VÀ LẤY NƯỚC ĐI CỦA NGƯỜI CHƠI (Quân Trắng)
st.write(f"Trạng thái: **Lượt của bạn (Quân Trắng)** | Chế độ: **{play_mode} ({difficulty})**")
move = chess_board(st.session_state.board.fen(), key="chess_game_ai")

# Nếu người chơi thực hiện nước đi
if move and not st.session_state.board.is_game_over():
    try:
        chess_move = chess.Move.from_uci(move)
        if chess_move in st.session_state.board.legal_moves:
            st.session_state.board.push(chess_move)
            
            # Nếu chọn đấu với máy và chưa kết thúc game, kích hoạt lượt của Máy (Quân Đen)
            if play_mode == "Đấu với Máy (AI)" and not st.session_state.board.is_game_over():
                with st.spinner("🤖 Máy đang tính toán nước đi..."):
                    ai_move = get_ai_move(st.session_state.board, difficulty)
                    if ai_move:
                        st.session_state.board.push(ai_move)
            
            st.rerun()
    except Exception:
        pass

# 6. HIỂN THỊ KẾT QUẢ TRẬN ĐẤU KHI KẾT THÚC
if st.session_state.board.is_game_over():
    st.markdown("---")
    st.subheader("🏁 KẾT QUẢ TRẬN ĐẤU")
    if st.session_state.board.is_checkmate():
        if st.session_state.board.turn == chess.WHITE:
            st.error("💀 Máy (Quân Đen) đã chiến thắng! Bạn đã bị chiếu kiệt.")
        else:
            st.success("🎉 Chúc mừng! Bạn đã chiếu hết và chiến thắng Máy!")
    elif st.session_state.board.is_stalemate() or st.session_state.board.is_insufficient_material():
        st.info("🤝 Trận đấu kết thúc với kết quả Hòa!")
