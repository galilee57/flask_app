(() => {
    const bg = document.getElementById("bg");
    if (!bg) return;

    let ticking = false;

    const clamp = (v, min, max) => Math.max(min, Math.min(max, v));

    const update = () => {
      const y = window.scrollY || 0;

      const factor = 0.30; // intensité
      let offset = y * factor;

      // ✅ on limite pour ne jamais voir les bords
      offset = clamp(offset, -80, 80);

      bg.style.transform = `translate3d(0, ${offset}px, 0) scale(1.15)`;
      ticking = false;
    };

    const onScroll = () => {
      if (!ticking) {
        requestAnimationFrame(update);
        ticking = true;
      }
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    update();
  })();