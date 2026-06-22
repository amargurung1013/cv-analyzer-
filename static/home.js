/* ---------- Scroll / load reveal ---------- */

const revealEls = document.querySelectorAll(".reveal");
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (revealEls.length) {

    if (prefersReducedMotion) {
        revealEls.forEach((el) => el.classList.add("is-visible"));
    } else {
        const revealObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("is-visible");
                        revealObserver.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.15 }
        );

        revealEls.forEach((el) => revealObserver.observe(el));
    }
}

/* ---------- Particle field ---------- */

const canvas = document.getElementById("particle-field");

if (canvas && !prefersReducedMotion) {

    const ctx = canvas.getContext("2d");
    let particles = [];
    let width = 0;
    let height = 0;
    let animationId = null;

    const DENSITY = 14000; // px^2 per particle, lower = more particles
    const MAX_SPEED = 0.18;
    const LINK_DISTANCE = 120;

    const resize = () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;

        const count = Math.min(90, Math.floor((width * height) / DENSITY));

        particles = Array.from({ length: count }, () => ({
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - 0.5) * MAX_SPEED,
            vy: (Math.random() - 0.5) * MAX_SPEED,
            r: Math.random() * 1.2 + 0.4,
        }));
    };

    const step = () => {
        ctx.clearRect(0, 0, width, height);

        for (const p of particles) {
            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0 || p.x > width) p.vx *= -1;
            if (p.y < 0 || p.y > height) p.vy *= -1;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = "rgba(245, 245, 243, 0.55)";
            ctx.fill();
        }

        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const a = particles[i];
                const b = particles[j];
                const dx = a.x - b.x;
                const dy = a.y - b.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < LINK_DISTANCE) {
                    const opacity = (1 - dist / LINK_DISTANCE) * 0.12;
                    ctx.beginPath();
                    ctx.moveTo(a.x, a.y);
                    ctx.lineTo(b.x, b.y);
                    ctx.strokeStyle = `rgba(245, 245, 243, ${opacity})`;
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            }
        }

        animationId = requestAnimationFrame(step);
    };

    resize();
    step();

    let resizeTimer = null;
    window.addEventListener("resize", () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(resize, 200);
    });

    document.addEventListener("visibilitychange", () => {
        if (document.hidden) {
            if (animationId) cancelAnimationFrame(animationId);
        } else {
            animationId = requestAnimationFrame(step);
        }
    });
}