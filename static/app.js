(() => {
  const token = document.body.dataset.token;
  const status = document.getElementById("status");
  const pad = document.getElementById("pad");
  const speedInput = document.getElementById("speed");
  const speedValue = document.getElementById("speed-value");

  const socket = io({ auth: { token } });
  socket.on("connect", () => {
    status.textContent = "Connected";
    status.className = "status online";
  });
  socket.on("disconnect", () => {
    status.textContent = "Disconnected";
    status.className = "status offline";
  });
  socket.on("connect_error", () => {
    status.textContent = "Connection blocked";
    status.className = "status offline";
  });

  let speed = Number(speedInput.value);
  speedInput.addEventListener("input", () => {
    speed = Number(speedInput.value);
    speedValue.textContent = `${speed.toFixed(1)}×`;
  });

  let active = new Map();
  let last = null;
  let start = null;
  let moved = false;
  let lastScrollY = null;
  let scrollRemainder = 0;

  pad.addEventListener("contextmenu", e => e.preventDefault());
  pad.addEventListener("pointerdown", e => {
    e.preventDefault();
    pad.setPointerCapture(e.pointerId);
    active.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (active.size === 1) {
      last = { x: e.clientX, y: e.clientY };
      start = { x: e.clientX, y: e.clientY, time: Date.now() };
      moved = false;
    } else if (active.size === 2) {
      lastScrollY = [...active.values()].reduce((sum, p) => sum + p.y, 0) / 2;
      last = null;
    }
  });

  pad.addEventListener("pointermove", e => {
    if (!active.has(e.pointerId)) return;
    e.preventDefault();
    const previous = active.get(e.pointerId);
    active.set(e.pointerId, { x: e.clientX, y: e.clientY });

    if (active.size >= 2) {
      const points = [...active.values()];
      const averageY = points.reduce((sum, p) => sum + p.y, 0) / points.length;
      if (lastScrollY !== null) {
        scrollRemainder += lastScrollY - averageY;
        const amount = Math.trunc(scrollRemainder / 24);
        if (amount !== 0) {
          socket.emit("scroll", { amount });
          scrollRemainder -= amount * 24;
        }
      }
      lastScrollY = averageY;
      return;
    }

    if (!last) return;
    const dx = e.clientX - last.x;
    const dy = e.clientY - last.y;
    if (Math.abs(e.clientX - start.x) + Math.abs(e.clientY - start.y) > 8) moved = true;
    socket.emit("move", { dx, dy, speed });
    last = { x: e.clientX, y: e.clientY };
  });

  function endPointer(e) {
    if (!active.has(e.pointerId)) return;
    active.delete(e.pointerId);
    if (active.size === 0) {
      const duration = start ? Date.now() - start.time : 9999;
      if (!moved && duration < 450) socket.emit("click", { button: "left" });
      last = null;
      start = null;
      lastScrollY = null;
      scrollRemainder = 0;
    } else if (active.size === 1) {
      const p = [...active.values()][0];
      last = { x: p.x, y: p.y };
      start = { x: p.x, y: p.y, time: Date.now() };
      moved = true;
      lastScrollY = null;
    }
  }
  pad.addEventListener("pointerup", endPointer);
  pad.addEventListener("pointercancel", endPointer);
  pad.addEventListener("lostpointercapture", endPointer);

  document.getElementById("left-click").addEventListener("click", () => socket.emit("click", { button: "left" }));
  document.getElementById("right-click").addEventListener("click", () => socket.emit("click", { button: "right" }));
  document.querySelectorAll("[data-key]").forEach(button => {
    button.addEventListener("click", () => socket.emit("key", { key: button.dataset.key }));
  });
})();
