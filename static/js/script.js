function verify() {
    try {
        var password = document.forms['form']['password'].value;
        var userName = document.forms['form']['userName'].value;
        if (password == null || password == "" || userName == null || userName == "") {
            document.getElementById("error").innerHTML = "User name and password are required";
            return false;
        }

        var checkboxes = document.getElementsByName("authorities");
        var okay = false;
        var arr = [];
        for (var i = 0; i < checkboxes.length; i++) {
            if (checkboxes[i].checked) {
                okay = true;
                arr.push(checkboxes[i].value);
                // break;
            }
        }
        if (arr.length == 0) {
            document.getElementById("error").innerHTML = "You must select at least one role";
            okay = false;
        } else {
            okay = true;
        }

        var okay2 = true;
        if (arr.includes("ROLE_MANAGER") && !arr.includes("ROLE_USER")) {
            document.getElementById("error").innerHTML = "To add a manager role, you should ALSO check a user role";
            okay2 = false;
        } else {
            okay2 = true;
        }
        console.log('okay1: ' + okay + " okay2: " + okay2);
        return okay && okay2;

    } catch (err) {
        alert(err);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('ROLE_MANAGER').onclick = function () {
        var userCheckbox = document.getElementById('ROLE_USER');
        var managerCheckbox = document.getElementById('ROLE_MANAGER');

        if (!managerCheckbox.checked) {
            userCheckbox.checked = false;
        } else {
            userCheckbox.checked = true;
        }
    }
});


document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('addToCartForm');
    const modal = document.getElementById('addToCartModal');
    const quantityInput = document.getElementById('quantity');

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const quantity = quantityInput.value;
        const url = form.dataset.action;

        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new URLSearchParams({ quantity })
            });

            if (res.ok) {
                const bsModal = bootstrap.Modal.getInstance(modal);
                bsModal.hide();

                // Optional: show toast or alert
                alert("✅ Product added to cart!");
            } else {
                const text = await res.text();
                console.error(text);
                alert("❌ Failed to add to cart.");
            }
        } catch (err) {
            console.error(err);
            alert("💥 Something went wrong.");
        }
    });
});

