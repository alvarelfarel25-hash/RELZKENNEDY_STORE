// ==========================================
// RELZKENNEDY_STORE - SCRIPT.JS
// ==========================================


// ==========================================
// CROPPER.JS
// ==========================================

let cropper = null;
let croppedFile = null;

const imageInput = document.getElementById("image");
const cropContainer = document.getElementById("cropContainer");
const cropImage = document.getElementById("cropImage");
const cropButton = document.getElementById("cropButton");
const cropStatus = document.getElementById("cropStatus");
const productForm = document.getElementById("productForm");

if (
    imageInput &&
    cropContainer &&
    cropImage &&
    cropButton &&
    cropStatus &&
    productForm
) {
    imageInput.addEventListener("change", function () {

        const file = this.files[0];

        if (!file) {
            return;
        }

        if (!file.type.startsWith("image/")) {
            alert("File harus berupa gambar.");
            this.value = "";
            return;
        }

        const imageURL = URL.createObjectURL(file);

        cropImage.src = imageURL;
        cropContainer.style.display = "block";

        if (cropper) {
            cropper.destroy();
        }

        cropper = new Cropper(cropImage, {
            aspectRatio: 1,
            viewMode: 1,
            dragMode: "move",
            autoCropArea: 0.9,
            responsive: true,
            background: false
        });

        croppedFile = null;

        cropStatus.textContent =
            "Atur gambar lalu klik Gunakan Gambar.";

        cropStatus.style.color = "";
    });


    cropButton.addEventListener("click", function () {

        if (!cropper) {
            return;
        }

        const canvas = cropper.getCroppedCanvas({
            width: 800,
            height: 800
        });

        if (!canvas) {
            return;
        }

        canvas.toBlob(function (blob) {

            if (!blob) {
                return;
            }

            croppedFile = new File(
                [blob],
                "product_" + Date.now() + ".jpg",
                {
                    type: "image/jpeg"
                }
            );

            const dataTransfer = new DataTransfer();

            dataTransfer.items.add(croppedFile);

            imageInput.files = dataTransfer.files;

            cropStatus.textContent =
                "✓ Gambar siap digunakan.";

            cropStatus.style.color = "#22c55e";

            cropButton.style.display = "none";

            cropper.destroy();
            cropper = null;

        }, "image/jpeg", 0.9);
    });


    productForm.addEventListener("submit", function (event) {

        if (
            imageInput.files.length > 0 &&
            !croppedFile
        ) {
            event.preventDefault();

            cropStatus.textContent =
                "⚠️ Klik Gunakan Gambar terlebih dahulu.";

            cropStatus.style.color = "#ef4444";
        }

    });
}


// ==========================================
// CART
// ==========================================

const CART_KEY = "relzkennedy_cart";

let cart = [];


// ==========================================
// LOAD CART
// ==========================================

function loadCart() {

    try {

        const data =
            localStorage.getItem(CART_KEY);

        if (!data) {
            return [];
        }

        const parsed =
            JSON.parse(data);

        if (!Array.isArray(parsed)) {
            return [];
        }

        return parsed;

    } catch (error) {

        console.error(
            "Cart error:",
            error
        );

        return [];
    }
}


// ==========================================
// SAVE CART
// ==========================================

function saveCart() {

    localStorage.setItem(
        CART_KEY,
        JSON.stringify(cart)
    );

    updateCartCount();
}


// ==========================================
// ADD PRODUCT
// ==========================================

function addToCart(id, name, price) {

    console.log(
        "Tambah produk:",
        id,
        name,
        price
    );

    const existing =
        cart.find(
            item =>
                Number(item.id) === Number(id)
        );


    if (existing) {

        existing.quantity =
            Number(existing.quantity) + 1;

    } else {

        cart.push({
            id: Number(id),
            name: String(name),
            price: String(price),
            quantity: 1
        });
    }


    saveCart();

    updateCartCount();

    showNotification(
        "✓ " + name + " masuk keranjang"
    );
}


// ==========================================
// CART COUNT
// ==========================================

function updateCartCount() {

    const count =
        document.getElementById("cartCount");

    if (!count) {
        return;
    }


    let total = 0;

    cart.forEach(function (item) {

        total += Number(
            item.quantity || 0
        );

    });


    count.textContent = total;
}


// ==========================================
// OPEN CART
// ==========================================

function openCart() {

    const overlay =
        document.getElementById("cartOverlay");

    if (!overlay) {
        console.error(
            "cartOverlay tidak ditemukan."
        );
        return;
    }


    renderCart();


    overlay.classList.add("active");

    /*
     * Untuk CSS yang menggunakan display:flex
     */
    overlay.style.display = "flex";

    document.body.classList.add(
        "cart-open"
    );
}


// ==========================================
// CLOSE CART
// ==========================================

function closeCart() {

    const overlay =
        document.getElementById("cartOverlay");

    if (!overlay) {
        return;
    }


    overlay.classList.remove("active");

    overlay.style.display = "none";

    document.body.classList.remove(
        "cart-open"
    );
}


// ==========================================
// RENDER CART
// ==========================================

function renderCart() {

    const container =
        document.getElementById("cartItems");

    const totalElement =
        document.getElementById("cartTotal");


    if (!container) {
        return;
    }


    if (cart.length === 0) {

        container.innerHTML = `
            <div class="empty-cart">
                <div class="empty-cart-icon">🛒</div>
                <h3>Keranjang Kosong</h3>
                <p>Belum ada produk di keranjang.</p>
            </div>
        `;

        if (totalElement) {
            totalElement.textContent =
                "Rp 0";
        }

        return;
    }


    let total = 0;


    container.innerHTML =
        cart.map(function (item) {

            const price =
                parsePrice(item.price);

            const quantity =
                Number(item.quantity) || 1;

            const subtotal =
                price * quantity;

            total += subtotal;


            return `
                <div class="cart-item">

                    <div class="cart-item-info">

                        <strong>
                            ${escapeHTML(item.name)}
                        </strong>

                        <span>
                            ${escapeHTML(item.price)}
                        </span>

                    </div>

                    <div class="cart-quantity">

                        <button
                            type="button"
                            onclick="changeQuantity(${item.id}, -1)"
                        >
                            −
                        </button>

                        <span>
                            ${quantity}
                        </span>

                        <button
                            type="button"
                            onclick="changeQuantity(${item.id}, 1)"
                        >
                            +
                        </button>

                    </div>

                    <button
                        type="button"
                        class="remove-cart"
                        onclick="removeFromCart(${item.id})"
                    >
                        🗑️
                    </button>

                </div>
            `;

        }).join("");


    if (totalElement) {

        totalElement.textContent =
            "Rp " + formatNumber(total);

    }
}


// ==========================================
// CHANGE QUANTITY
// ==========================================

function changeQuantity(id, amount) {

    const item =
        cart.find(
            product =>
                Number(product.id) === Number(id)
        );


    if (!item) {
        return;
    }


    item.quantity =
        Number(item.quantity) + amount;


    if (item.quantity <= 0) {

        cart =
            cart.filter(
                product =>
                    Number(product.id) !== Number(id)
            );
    }


    saveCart();

    renderCart();
}


// ==========================================
// REMOVE PRODUCT
// ==========================================

function removeFromCart(id) {

    cart =
        cart.filter(
            item =>
                Number(item.id) !== Number(id)
        );


    saveCart();

    renderCart();
}


// ==========================================
// PRICE
// ==========================================

function parsePrice(price) {

    if (!price) {
        return 0;
    }


    let text =
        String(price)
            .toUpperCase()
            .replace(/\s/g, "");


    let multiplier = 1;


    if (text.includes("K")) {
        multiplier = 1000;
    }


    text =
        text.replace(
            /[^0-9.,]/g,
            ""
        );


    if (!text) {
        return 0;
    }


    let number;


    if (
        text.includes(".") &&
        text.includes(",")
    ) {

        number =
            parseFloat(
                text
                    .replace(/\./g, "")
                    .replace(",", ".")
            );

    } else if (text.includes(".")) {

        number =
            parseFloat(
                text.replace(/\./g, "")
            );

    } else if (text.includes(",")) {

        number =
            parseFloat(
                text.replace(",", ".")
            );

    } else {

        number =
            parseFloat(text);
    }


    if (isNaN(number)) {
        return 0;
    }


    return number * multiplier;
}


// ==========================================
// FORMAT PRICE
// ==========================================

function formatNumber(number) {

    return new Intl.NumberFormat(
        "id-ID"
    ).format(number);
}


// ==========================================
// CHECKOUT WHATSAPP
// ==========================================

function checkoutWhatsApp() {

    if (cart.length === 0) {

        alert(
            "Keranjang masih kosong."
        );

        return;
    }


    let message =
        "Halo RELZKENNEDY_STORE 👋\n\n" +
        "Saya ingin memesan:\n\n";


    let total = 0;


    cart.forEach(function (item, index) {

        const price =
            parsePrice(item.price);

        const quantity =
            Number(item.quantity) || 1;

        const subtotal =
            price * quantity;

        total += subtotal;


        message +=
            `${index + 1}. ${item.name}\n` +
            `Jumlah: ${quantity}\n` +
            `Harga: ${item.price}\n` +
            `Subtotal: Rp ${formatNumber(subtotal)}\n\n`;
    });


    message +=
        `Total: Rp ${formatNumber(total)}\n\n` +
        "Mohon info cara pembayarannya. Terima kasih.";


    const phone =
        "6282257548537";


    const url =
        "https://wa.me/" +
        phone +
        "?text=" +
        encodeURIComponent(message);


    window.open(
        url,
        "_blank"
    );
}


// ==========================================
// NOTIFICATION
// ==========================================

function showNotification(message) {

    let notification =
        document.getElementById(
            "cartNotification"
        );


    if (!notification) {

        notification =
            document.createElement("div");

        notification.id =
            "cartNotification";

        notification.className =
            "cart-notification";

        document.body.appendChild(
            notification
        );
    }


    notification.textContent =
        message;


    notification.classList.add(
        "show"
    );


    clearTimeout(
        window.notificationTimer
    );


    window.notificationTimer =
        setTimeout(function () {

            notification.classList.remove(
                "show"
            );

        }, 2000);
}


// ==========================================
// ESCAPE HTML
// ==========================================

function escapeHTML(text) {

    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// ==========================================
// START
// ==========================================

cart = loadCart();

document.addEventListener(
    "DOMContentLoaded",
    function () {

        updateCartCount();


        const overlay =
            document.getElementById(
                "cartOverlay"
            );


        if (overlay) {

            /*
             * Pastikan modal awalnya tertutup.
             */
            overlay.classList.remove(
                "active"
            );

            overlay.style.display =
                "none";
        }


        /*
         * ESC untuk menutup keranjang
         */
        document.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Escape"
                ) {
                    closeCart();
                }

            }
        );

    }
);