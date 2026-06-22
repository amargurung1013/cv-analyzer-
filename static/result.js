const shell = document.querySelector(".result-shell");

if (shell) {

    const total = parseInt(shell.dataset.total, 10) || 1;
    const dossiers = Array.from(document.querySelectorAll(".dossier"));
    const indexItems = Array.from(document.querySelectorAll(".index-item"));
    const currentLabel = document.getElementById("pager-current");
    const prevBtn = document.getElementById("pager-prev");
    const nextBtn = document.getElementById("pager-next");

    let current = 1;

    const pad = (n) => String(n).padStart(2, "0");

    const goTo = (page) => {
        if (page < 1 || page > total) return;

        current = page;

        dossiers.forEach((el) => {
            el.classList.toggle("is-active", parseInt(el.dataset.page, 10) === current);
        });

        indexItems.forEach((el) => {
            el.classList.toggle("is-active", parseInt(el.dataset.page, 10) === current);
        });

        if (currentLabel) currentLabel.textContent = pad(current);

        if (prevBtn) prevBtn.disabled = current === 1;
        if (nextBtn) nextBtn.disabled = current === total;

        const activeIndexItem = document.querySelector(".index-item.is-active");
        if (activeIndexItem) {
            activeIndexItem.scrollIntoView({ block: "nearest", behavior: "smooth" });
        }

        const stage = document.querySelector(".dossier-stage");
        if (stage) stage.scrollTo({ top: 0, behavior: "instant" in window ? "instant" : "auto" });
    };

    if (prevBtn) prevBtn.addEventListener("click", () => goTo(current - 1));
    if (nextBtn) nextBtn.addEventListener("click", () => goTo(current + 1));

    indexItems.forEach((el) => {
        el.addEventListener("click", () => goTo(parseInt(el.dataset.page, 10)));
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "ArrowRight") goTo(current + 1);
        if (event.key === "ArrowLeft") goTo(current - 1);
    });

    goTo(1);
}