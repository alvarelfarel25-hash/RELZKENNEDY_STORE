from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename


# ==========================================
# APP CONFIGURATION
# ==========================================

app = Flask(__name__)

# Secret key dari Environment Variable
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "RELZKENNEDY_SECRET_KEY_2026"
)


# ==========================================
# PATH CONFIGURATION
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATABASE = os.path.join(
    BASE_DIR,
    "products.db"
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "static",
    "images"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# ==========================================
# DATABASE
# ==========================================

def get_db():
    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_db()

    cursor = conn.cursor()


    # --------------------------------------
    # Buat tabel products jika belum ada
    # --------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price TEXT NOT NULL,
            description TEXT NOT NULL,
            image TEXT,
            status TEXT NOT NULL DEFAULT 'Tersedia',
            category TEXT NOT NULL DEFAULT 'Lainnya'
        )
    """)


    # --------------------------------------
    # Cek kolom database
    # --------------------------------------

    cursor.execute(
        "PRAGMA table_info(products)"
    )

    columns = [
        row["name"]
        for row in cursor.fetchall()
    ]


    # --------------------------------------
    # Tambahkan status jika database lama
    # --------------------------------------

    if "status" not in columns:

        cursor.execute("""
            ALTER TABLE products
            ADD COLUMN status TEXT
            NOT NULL
            DEFAULT 'Tersedia'
        """)


    # --------------------------------------
    # Tambahkan category jika database lama
    # --------------------------------------

    if "category" not in columns:

        cursor.execute("""
            ALTER TABLE products
            ADD COLUMN category TEXT
            NOT NULL
            DEFAULT 'Lainnya'
        """)


    conn.commit()

    conn.close()


# Jalankan database
init_db()


# ==========================================
# ADMIN CONFIGURATION
# ==========================================

ADMIN_USERNAME = os.environ.get(
    "ADMIN_USERNAME",
    "admin"
)

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    "relz123"
)


# ==========================================
# CATEGORY CONFIGURATION
# ==========================================

ALLOWED_CATEGORIES = [
    "Aplikasi",
    "Game",
    "Akun",
    "Jasa",
    "Lainnya"
]


ALLOWED_STATUS = [
    "Tersedia",
    "Habis"
]


# ==========================================
# ADMIN LOGIN CHECK
# ==========================================

def admin_logged_in():

    return (
        session.get(
            "admin_logged_in"
        ) is True
    )


# ==========================================
# HOME / STORE
# ==========================================

@app.route("/")
def index():

    conn = get_db()

    products = conn.execute("""
        SELECT *
        FROM products
        ORDER BY id DESC
    """).fetchall()

    conn.close()


    return render_template(
        "index.html",
        products=products
    )


# ==========================================
# PRODUCT DETAIL
# ==========================================

@app.route("/product/<int:product_id>")
def product(product_id):

    conn = get_db()

    product_data = conn.execute("""
        SELECT *
        FROM products
        WHERE id = ?
    """, (product_id,)).fetchone()

    conn.close()


    if product_data is None:

        return (
            "Produk tidak ditemukan",
            404
        )


    return render_template(
        "product.html",
        product=product_data
    )


# ==========================================
# LOGIN
# ==========================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    # Kalau sudah login
    if admin_logged_in():

        return redirect(
            url_for("admin")
        )


    error = None


    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        if (
            username == ADMIN_USERNAME
            and password == ADMIN_PASSWORD
        ):

            session[
                "admin_logged_in"
            ] = True


            return redirect(
                url_for("admin")
            )


        error = (
            "Username atau password salah."
        )


    return render_template(
        "login.html",
        error=error
    )


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.pop(
        "admin_logged_in",
        None
    )


    return redirect(
        url_for("login")
    )


# ==========================================
# ADMIN PANEL
# ==========================================

@app.route(
    "/admin",
    methods=["GET", "POST"]
)
def admin():

    # --------------------------------------
    # Cek login
    # --------------------------------------

    if not admin_logged_in():

        return redirect(
            url_for("login")
        )


    # --------------------------------------
    # Tambah produk
    # --------------------------------------

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        price = request.form.get(
            "price",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        status = request.form.get(
            "status",
            "Tersedia"
        ).strip()

        category = request.form.get(
            "category",
            "Lainnya"
        ).strip()


        # ----------------------------------
        # Validasi status
        # ----------------------------------

        if status not in ALLOWED_STATUS:

            status = "Tersedia"


        # ----------------------------------
        # Validasi kategori
        # ----------------------------------

        if category not in ALLOWED_CATEGORIES:

            category = "Lainnya"


        # ----------------------------------
        # Upload gambar
        # ----------------------------------

        image_file = request.files.get(
            "image"
        )

        filename = None


        if (
            image_file
            and image_file.filename
        ):

            original_name = secure_filename(
                image_file.filename
            )


            if original_name:

                filename = original_name


                save_path = os.path.join(
                    app.config[
                        "UPLOAD_FOLDER"
                    ],
                    filename
                )


                image_file.save(
                    save_path
                )


        # ----------------------------------
        # Simpan produk ke database
        # ----------------------------------

        conn = get_db()


        conn.execute("""
            INSERT INTO products
            (
                name,
                price,
                description,
                image,
                status,
                category
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            price,
            description,
            filename,
            status,
            category
        ))


        conn.commit()

        conn.close()


        return redirect(
            url_for("admin")
        )


    # --------------------------------------
    # Ambil semua produk
    # --------------------------------------

    conn = get_db()


    products = conn.execute("""
        SELECT *
        FROM products
        ORDER BY id DESC
    """).fetchall()


    conn.close()


    return render_template(
        "admin.html",
        products=products
    )


# ==========================================
# EDIT PRODUCT
# ==========================================

@app.route(
    "/edit/<int:product_id>",
    methods=["GET", "POST"]
)
def edit_product(product_id):

    # --------------------------------------
    # Cek login
    # --------------------------------------

    if not admin_logged_in():

        return redirect(
            url_for("login")
        )


    conn = get_db()


    # --------------------------------------
    # Cari produk
    # --------------------------------------

    product_data = conn.execute("""
        SELECT *
        FROM products
        WHERE id = ?
    """, (product_id,)).fetchone()


    if product_data is None:

        conn.close()

        return (
            "Produk tidak ditemukan",
            404
        )


    # --------------------------------------
    # Proses update
    # --------------------------------------

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        price = request.form.get(
            "price",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        status = request.form.get(
            "status",
            "Tersedia"
        ).strip()

        category = request.form.get(
            "category",
            "Lainnya"
        ).strip()


        # ----------------------------------
        # Validasi status
        # ----------------------------------

        if status not in ALLOWED_STATUS:

            status = "Tersedia"


        # ----------------------------------
        # Validasi kategori
        # ----------------------------------

        if category not in ALLOWED_CATEGORIES:

            category = "Lainnya"


        # ----------------------------------
        # Gambar lama
        # ----------------------------------

        new_filename = product_data[
            "image"
        ]


        # ----------------------------------
        # Gambar baru
        # ----------------------------------

        image_file = request.files.get(
            "image"
        )


        if (
            image_file
            and image_file.filename
        ):

            original_name = secure_filename(
                image_file.filename
            )


            if original_name:

                new_filename = original_name


                save_path = os.path.join(
                    app.config[
                        "UPLOAD_FOLDER"
                    ],
                    new_filename
                )


                image_file.save(
                    save_path
                )


                # --------------------------
                # Hapus gambar lama
                # --------------------------

                old_image = product_data[
                    "image"
                ]


                if (
                    old_image
                    and old_image != new_filename
                ):

                    old_path = os.path.join(
                        app.config[
                            "UPLOAD_FOLDER"
                        ],
                        old_image
                    )


                    if os.path.exists(
                        old_path
                    ):

                        try:

                            os.remove(
                                old_path
                            )

                        except OSError:

                            pass


        # ----------------------------------
        # Update database
        # ----------------------------------

        conn.execute("""
            UPDATE products
            SET
                name = ?,
                price = ?,
                description = ?,
                image = ?,
                status = ?,
                category = ?
            WHERE id = ?
        """, (
            name,
            price,
            description,
            new_filename,
            status,
            category,
            product_id
        ))


        conn.commit()

        conn.close()


        return redirect(
            url_for("admin")
        )


    # --------------------------------------
    # Tampilkan halaman edit
    # --------------------------------------

    conn.close()


    return render_template(
        "edit.html",
        product=product_data
    )


# ==========================================
# DELETE PRODUCT
# ==========================================

@app.route(
    "/delete/<int:product_id>",
    methods=["POST"]
)
def delete_product(product_id):

    # --------------------------------------
    # Cek login
    # --------------------------------------

    if not admin_logged_in():

        return redirect(
            url_for("login")
        )


    conn = get_db()


    # --------------------------------------
    # Cari produk
    # --------------------------------------

    product_data = conn.execute("""
        SELECT *
        FROM products
        WHERE id = ?
    """, (product_id,)).fetchone()


    if product_data:

        image_name = product_data[
            "image"
        ]


        # ----------------------------------
        # Hapus gambar
        # ----------------------------------

        if image_name:

            image_path = os.path.join(
                app.config[
                    "UPLOAD_FOLDER"
                ],
                image_name
            )


            if os.path.exists(
                image_path
            ):

                try:

                    os.remove(
                        image_path
                    )

                except OSError:

                    pass


        # ----------------------------------
        # Hapus database
        # ----------------------------------

        conn.execute("""
            DELETE FROM products
            WHERE id = ?
        """, (product_id,))


        conn.commit()


    conn.close()


    return redirect(
        url_for("admin")
    )


# ==========================================
# RUN LOCAL
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )