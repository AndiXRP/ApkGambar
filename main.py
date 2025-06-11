from browser import document, html, timer

# --- Ambil elemen dari DOM ---
canvas = document["canvas"]
ctx = canvas.getContext("2d")

mode_select = document["mode"]
color_picker = document["color"]
undo_btn = document["undo-btn"]
redo_btn = document["redo-btn"]

# --- Variabel untuk state (status) ---
start_x = start_y = None
undo_stack = []
redo_stack = []

# --- Fungsi untuk Undo/Redo ---

def save_state():
    """Menyimpan state kanvas saat ini ke undo_stack."""
    global redo_stack
    # Hapus riwayat redo karena ada aksi baru
    redo_stack = []
    update_buttons()
    
    image_data = ctx.getImageData(0, 0, canvas.width, canvas.height)
    undo_stack.append(image_data)
    update_buttons()

def undo(evt):
    """Mengembalikan state kanvas sebelumnya."""
    if len(undo_stack) > 1:
        # Pindahkan state saat ini ke redo_stack
        current_state = undo_stack.pop()
        redo_stack.append(current_state)
        
        # Ambil state sebelumnya dan gambar ulang kanvas
        previous_state = undo_stack[-1]
        ctx.putImageData(previous_state, 0, 0)
        update_buttons()

def redo(evt):
    """Mengembalikan state kanvas yang sudah di-undo."""
    if len(redo_stack) > 0:
        # Ambil state dari redo_stack dan gambar ulang
        state_to_restore = redo_stack.pop()
        ctx.putImageData(state_to_restore, 0, 0)
        
        # Kembalikan state tersebut ke undo_stack
        undo_stack.append(state_to_restore)
        update_buttons()

def update_buttons():
    """Mengaktifkan/menonaktifkan tombol undo/redo."""
    undo_btn.disabled = len(undo_stack) <= 1
    redo_btn.disabled = len(redo_stack) == 0

# --- Fungsi Menggambar ---

def start_drawing(evt):
    """Memulai proses menggambar."""
    global start_x, start_y

    mode = mode_select.value
    rect = canvas.getBoundingClientRect()
    x = evt.offsetX
    y = evt.offsetY

    if mode == "dot":
        color = color_picker.value
        ctx.fillStyle = color
        ctx.beginPath()
        ctx.arc(x, y, 3, 0, 2 * 3.1415)
        ctx.fill()
        # Simpan state setelah menggambar titik
        save_state()
    else:
        # Hanya simpan koordinat awal untuk bentuk lain
        start_x = x
        start_y = y

def finish_drawing(evt):
    """Menyelesaikan proses menggambar (untuk garis, persegi, dll.)."""
    global start_x, start_y

    if start_x is None or start_y is None:
        return

    color = color_picker.value
    mode = mode_select.value
    x = evt.offsetX
    y = evt.offsetY

    ctx.strokeStyle = color
    ctx.lineWidth = 2 # Sedikit lebih tebal agar terlihat jelas
    
    # Mulai path baru
    ctx.beginPath()

    if mode == "line":
        ctx.moveTo(start_x, start_y)
        ctx.lineTo(x, y)
    elif mode == "rect":
        ctx.rect(start_x, start_y, x - start_x, y - start_y)
    elif mode == "circle":
        radius = ((x - start_x) ** 2 + (y - start_y) ** 2) ** 0.5
        ctx.arc(start_x, start_y, radius, 0, 2 * 3.1415)
    elif mode == "ellipse":
        ctx.ellipse(
            (start_x + x) / 2,
            (start_y + y) / 2,
            abs(x - start_x) / 2,
            abs(y - start_y) / 2,
            0, 0, 2 * 3.1415
        )
    
    ctx.stroke()

    # Reset koordinat awal
    start_x = start_y = None
    
    # Simpan state setelah bentuk selesai digambar
    save_state()

# --- Ikat (Bind) event ke fungsi ---
canvas.bind("mousedown", start_drawing)
canvas.bind("mouseup", finish_drawing)
undo_btn.bind("click", undo)
redo_btn.bind("click", redo)

# --- Inisialisasi Aplikasi ---
# Simpan state awal (kanvas kosong)
save_state()