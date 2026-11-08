"use strict";

(() => {
  // Keep this repository in sync with GITHUB_REPO in verseflow.py.
  const REPO = "rajm012/VerseFlow";
  const BASE = `https://github.com/${REPO}`;
  const themeButton = document.getElementById("theme-toggle");
  const themeIcon = document.getElementById("theme-icon");

  function setTheme(theme) {
    const light = theme === "light";
    document.documentElement.dataset.theme = light ? "light" : "dark";
    themeButton.setAttribute(
      "aria-label",
      `Switch to ${light ? "dark" : "light"} theme`,
    );
    themeIcon.setAttribute("href", light ? "#i-moon" : "#i-sun");
    document.querySelector('meta[name="theme-color"]').content = light
      ? "#f2f7fb"
      : "#080f1a";
    try {
      localStorage.setItem("verseflow-theme", light ? "light" : "dark");
    } catch {
      /* Storage is optional. */
    }
  }
  try {
    setTheme(localStorage.getItem("verseflow-theme") || "dark");
  } catch {
    setTheme("dark");
  }
  themeButton.addEventListener("click", () =>
    setTheme(
      document.documentElement.dataset.theme === "dark" ? "light" : "dark",
    ),
  );

  function enableTabKeys(buttons, activate) {
    buttons.forEach((button, index) => {
      button.addEventListener("keydown", (event) => {
        let next;
        if (event.key === "ArrowRight") next = (index + 1) % buttons.length;
        if (event.key === "ArrowLeft")
          next = (index - 1 + buttons.length) % buttons.length;
        if (event.key === "Home") next = 0;
        if (event.key === "End") next = buttons.length - 1;
        if (next === undefined) return;
        event.preventDefault();
        activate(buttons[next]);
        buttons[next].focus();
      });
    });
  }

  const preview = document.getElementById("lyric-preview");
  const modeButtons = [...document.querySelectorAll("[data-mode]")];
  const styleCards = [...document.querySelectorAll("[data-style-choice]")];
  const stack = document.getElementById("stack-display");
  const focus = document.getElementById("focus-display");
  const canvas = document.getElementById("constellation-display");
  const ctx = canvas.getContext("2d");
  const progress = document.getElementById("demo-progress");
  const play = document.getElementById("play-toggle");
  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");
  const demoLines = [
    "let the night feel like home",
    "a little light in every word",
    "we move wherever the music goes",
  ];
  const lineDuration = 4000;
  const demoDuration = lineDuration * demoLines.length;
  let elapsed = 1800;
  let playing = !reducedMotion.matches;
  let visible = true;
  let mode = "Stack";
  let frameId = null;
  let lastFrame = null;
  let lastPaint = 0;
  let renderedLine = -1;

  function selectMode(button) {
    mode = button.dataset.mode;
    preview.dataset.style = mode;
    preview.setAttribute("aria-labelledby", button.id);
    modeButtons.forEach((tab) => {
      const selected = tab === button;
      tab.setAttribute("aria-selected", String(selected));
      tab.tabIndex = selected ? 0 : -1;
    });
    styleCards.forEach((card) => {
      const selected = card.dataset.styleChoice === mode;
      card.classList.toggle("is-selected", selected);
      card.setAttribute("aria-pressed", String(selected));
    });
    stack.hidden = mode !== "Stack";
    focus.hidden = mode !== "Focus";
    canvas.hidden = mode !== "Constellation";
    render();
  }
  modeButtons.forEach((button) =>
    button.addEventListener("click", () => selectMode(button)),
  );
  enableTabKeys(modeButtons, selectMode);
  styleCards.forEach((card) =>
    card.addEventListener("click", () => {
      selectMode(
        modeButtons.find(
          (button) => button.dataset.mode === card.dataset.styleChoice,
        ),
      );
      document
        .getElementById("experience")
        .scrollIntoView({
          behavior: reducedMotion.matches ? "instant" : "smooth",
          block: "center",
        });
    }),
  );

  function drawStar(x, y, radius, color) {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(x, y - radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.quadraticCurveTo(x, y, x, y + radius);
    ctx.quadraticCurveTo(x, y, x - radius, y);
    ctx.quadraticCurveTo(x, y, x, y - radius);
    ctx.fill();
  }

  function drawConstellation(words, active) {
    if (!ctx) return;
    const bounds = canvas.getBoundingClientRect();
    if (!bounds.width || !bounds.height) return;
    const ratio = Math.min(devicePixelRatio || 1, 2);
    const width = bounds.width;
    const height = bounds.height;
    if (
      canvas.width !== Math.round(width * ratio) ||
      canvas.height !== Math.round(height * ratio)
    ) {
      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(height * ratio);
    }
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.clearRect(0, 0, width, height);
    const points = [
      [0.14, 0.57],
      [0.28, 0.3],
      [0.42, 0.66],
      [0.57, 0.34],
      [0.71, 0.6],
      [0.85, 0.32],
    ];
    const fontSize = Math.max(11, Math.min(22, width / 35));
    points.forEach(([x, y], index) => {
      if (index > 0) {
        const previous = points[index - 1];
        ctx.beginPath();
        ctx.moveTo(previous[0] * width, previous[1] * height);
        ctx.lineTo(x * width, y * height);
        ctx.strokeStyle =
          index <= active ? "rgba(125,217,242,.45)" : "rgba(125,217,242,.14)";
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    });
    points.forEach(([x, y], index) => {
      const px = x * width;
      const py = y * height;
      const current = index === active;
      const sung = index <= active;
      if (current) {
        const glow = ctx.createRadialGradient(px, py, 0, px, py, 52);
        glow.addColorStop(0, "rgba(125,217,242,.18)");
        glow.addColorStop(1, "rgba(125,217,242,0)");
        ctx.fillStyle = glow;
        ctx.fillRect(px - 52, py - 52, 104, 104);
        ctx.beginPath();
        ctx.arc(px, py, 14, 0, Math.PI * 2);
        ctx.strokeStyle = "rgba(176,239,211,.4)";
        ctx.stroke();
      }
      drawStar(px, py, current ? 9 : 5, sung ? "#b0efd3" : "#557987");
      ctx.font = `${current ? 600 : 400} ${current ? fontSize + 2 : fontSize}px Sora, sans-serif`;
      ctx.textAlign = "center";
      ctx.fillStyle = current ? "#e6fcf8" : sung ? "#a4dcd9" : "#68899b";
      ctx.fillText(words[index], px, py + (index % 2 ? -24 : 34));
    });
  }

  function render() {
    const lineIndex = Math.min(
      demoLines.length - 1,
      Math.floor(elapsed / lineDuration),
    );
    const words = demoLines[lineIndex].split(" ");
    const active = Math.min(
      words.length - 1,
      Math.floor(((elapsed % lineDuration) / lineDuration) * words.length),
    );
    if (renderedLine !== lineIndex) {
      document.getElementById("previous-line").textContent =
        demoLines[(lineIndex + demoLines.length - 1) % demoLines.length];
      document.getElementById("next-line").textContent =
        demoLines[(lineIndex + 1) % demoLines.length];
      ["stack-line", "focus-line"].forEach((id) => {
        const line = document.getElementById(id);
        line.replaceChildren(
          ...words.flatMap((word, index) => {
            const span = document.createElement("span");
            span.textContent = word;
            return index ? [document.createTextNode(" "), span] : [span];
          }),
        );
      });
      renderedLine = lineIndex;
    }
    ["stack-line", "focus-line"].forEach((id) => {
      document
        .getElementById(id)
        .querySelectorAll("span")
        .forEach((span, index) => {
          span.classList.toggle("is-sung", index <= active);
          span.classList.toggle("is-current", index === active);
        });
    });
    progress.value = Math.floor(elapsed);
    progress.style.setProperty(
      "--progress",
      `${(elapsed / demoDuration) * 100}%`,
    );
    const seconds = Math.floor(elapsed / 1000);
    document.getElementById("demo-time").textContent =
      `0:${String(seconds).padStart(2, "0")} / 0:12`;
    progress.setAttribute("aria-valuetext", `${seconds} seconds of 12`);
    if (mode === "Constellation") drawConstellation(words, active);
  }

  function frame(time) {
    if (lastFrame !== null)
      elapsed = (elapsed + Math.min(time - lastFrame, 200)) % demoDuration;
    lastFrame = time;
    if (time - lastPaint > 65) {
      render();
      lastPaint = time;
    }
    frameId = requestAnimationFrame(frame);
  }
  function syncAnimation() {
    if (frameId !== null) cancelAnimationFrame(frameId);
    frameId = null;
    lastFrame = null;
    if (playing && visible && !document.hidden)
      frameId = requestAnimationFrame(frame);
  }
  function syncPlayButton() {
    play.setAttribute(
      "aria-label",
      `${playing ? "Pause" : "Play"} lyric preview`,
    );
    document
      .getElementById("play-icon")
      .setAttribute("href", playing ? "#i-pause" : "#i-play");
  }
  play.addEventListener("click", () => {
    playing = !playing;
    syncPlayButton();
    syncAnimation();
  });
  progress.addEventListener("input", () => {
    elapsed = Math.min(Number(progress.value), demoDuration - 1);
    render();
  });
  document.addEventListener("visibilitychange", syncAnimation);
  if ("IntersectionObserver" in window) {
    new IntersectionObserver((entries) => {
      visible = entries[0].isIntersecting;
      syncAnimation();
    }).observe(preview);
  }
  if ("ResizeObserver" in window) new ResizeObserver(render).observe(preview);
  else window.addEventListener("resize", render);
  reducedMotion.addEventListener("change", () => {
    if (reducedMotion.matches) {
      playing = false;
      syncPlayButton();
      syncAnimation();
    }
  });
  document.fonts.ready.then(render);
  syncPlayButton();
  render();
  syncAnimation();

  const installTabs = [...document.querySelectorAll("[data-install]")];
  function selectInstall(button) {
    installTabs.forEach((tab) => {
      const selected = tab === button;
      tab.setAttribute("aria-selected", String(selected));
      tab.tabIndex = selected ? 0 : -1;
      document.getElementById(`${tab.dataset.install}-install`).hidden =
        !selected;
    });
  }
  installTabs.forEach((button) =>
    button.addEventListener("click", () => selectInstall(button)),
  );
  enableTabKeys(installTabs, selectInstall);

  let copyTimer;
  document
    .getElementById("copy-install")
    .addEventListener("click", async () => {
      const code = document.getElementById("install-commands");
      const status = document.getElementById("copy-status");
      try {
        if (!navigator.clipboard) throw new Error("Clipboard unavailable");
        await navigator.clipboard.writeText(code.textContent.trim());
        document.getElementById("copy-label").textContent = "Copied";
        document.getElementById("copy-icon").setAttribute("href", "#i-check");
        status.textContent = "Installation commands copied to your clipboard.";
        clearTimeout(copyTimer);
        copyTimer = setTimeout(() => {
          document.getElementById("copy-label").textContent = "Copy";
          document.getElementById("copy-icon").setAttribute("href", "#i-copy");
        }, 2500);
      } catch {
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(code);
        selection.removeAllRanges();
        selection.addRange(range);
        status.textContent =
          "Commands selected. Press Ctrl+C or use your browser copy command.";
        document.getElementById("copy-label").textContent = "Selected";
      }
    });

  const architecture = document.getElementById("architecture");
  let release = null;
  let releaseFailed = false;
  function matchingArchive(arch) {
    return (Array.isArray(release?.assets) ? release.assets : []).find(
      (asset) => {
        if (
          !new RegExp(`^VerseFlow-linux-${arch}-.+\\.tar\\.gz$`, "i").test(
            asset.name || "",
          )
        )
          return false;
        try {
          const url = new URL(asset.browser_download_url);
          return (
            url.protocol === "https:" &&
            url.hostname === "github.com" &&
            url.pathname.startsWith(`/${REPO}/releases/download/`)
          );
        } catch {
          return false;
        }
      },
    );
  }
  function updateDownload() {
    const arch = architecture.value;
    const asset = matchingArchive(arch);
    const portable = document.getElementById("portable-download");
    const portableStatus = document.getElementById("portable-status");
    if (asset) {
      document.querySelectorAll("[data-download]").forEach((link) => {
        link.href = asset.browser_download_url;
      });
      document.querySelectorAll("[data-download-label]").forEach((label) => {
        label.textContent = "Download for Linux";
      });
      portable.href = asset.browser_download_url;
      portable.replaceChildren(
        document.createTextNode(`Download ${arch} archive`),
      );
      const version = String(release.tag_name || "").replace(/^v/, "");
      const size = Number.isFinite(asset.size)
        ? ` · ${(asset.size / 1048576).toFixed(1)} MB`
        : "";
      document.getElementById("release-info").textContent =
        `Version ${version} · Linux ${arch}${size} · Free & open source`;
      portableStatus.textContent = `Version ${version}${size}. Build compatibility depends on the release's build distribution.`;
    } else {
      document.querySelectorAll("[data-download]").forEach((link) => {
        link.href = "#install";
      });
      document.querySelectorAll("[data-download-label]").forEach((label) => {
        label.textContent = "Get VerseFlow";
      });
      portable.href = `${BASE}/releases`;
      portable.textContent = "View Linux releases";
      document.getElementById("release-info").textContent =
        "Source install available · Free & open source";
      portableStatus.textContent = releaseFailed
        ? "Release lookup is unavailable. Browse GitHub Releases, or use the source installation tab."
        : `No ${arch} archive is published in the latest release. Use the source tab, or browse all releases.`;
    }
  }
  architecture.addEventListener("change", updateDownload);
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 7000);
  fetch(`https://api.github.com/repos/${REPO}/releases/latest`, {
    signal: controller.signal,
    headers: { Accept: "application/vnd.github+json" },
  })
    .then((response) => {
      if (response.status === 404) return null;
      if (!response.ok) throw new Error("Release request failed");
      return response.json();
    })
    .then((data) => {
      release = data;
      updateDownload();
    })
    .catch(() => {
      releaseFailed = true;
      updateDownload();
    })
    .finally(() => clearTimeout(timeout));
})();
