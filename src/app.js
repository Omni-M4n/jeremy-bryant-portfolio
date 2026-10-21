/* Small progressive enhancements; the document and both diagrams work without JS. */
(() => {
  "use strict";

  for (const printButton of document.querySelectorAll("button[data-print]")) {
    printButton.addEventListener("click", () => window.print());
  }

  const header = document.querySelector(".site-header");
  const menuButton = header?.querySelector(".nav-toggle");
  const menuId = menuButton?.getAttribute("aria-controls");
  const menu = (menuId && document.getElementById(menuId)) || header?.querySelector(".site-nav");

  if (header && menuButton && menu) {
    const setMenu = (open, restoreFocus = false) => {
      header.classList.toggle("mobile-menu-open", open);
      menuButton.setAttribute("aria-expanded", String(open));
      menuButton.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
      if (restoreFocus) menuButton.focus();
    };
    setMenu(false);
    menuButton.addEventListener("click", () => {
      setMenu(menuButton.getAttribute("aria-expanded") !== "true");
    });
    menu.addEventListener("click", (event) => {
      if (event.target instanceof Element && event.target.closest("a")) setMenu(false);
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && menuButton.getAttribute("aria-expanded") === "true") {
        setMenu(false, true);
      }
    });
    document.addEventListener("click", (event) => {
      if (event.target instanceof Node && !header.contains(event.target)) setMenu(false);
    });
    const wideScreen = window.matchMedia("(min-width: 561px)");
    wideScreen.addEventListener?.("change", (event) => { if (event.matches) setMenu(false); });
    // Only activate the collapsed mobile layout once its control is connected.
    document.documentElement.classList.add("has-js");
  }

  const viewButtons = [...document.querySelectorAll("button[data-view]")];
  const groups = new Map();
  for (const button of viewButtons) {
    let group = button.closest("[data-diagram]") || button.closest(".diagram-view");
    if (!group) {
      group = button.parentElement;
      while (group && !group.querySelector("[data-panel]")) group = group.parentElement;
    }
    if (group) {
      if (!groups.has(group)) groups.set(group, []);
      groups.get(group).push(button);
    }
  }

  let groupIndex = 0;
  for (const [group, buttons] of groups) {
    groupIndex += 1;
    const panels = [...group.querySelectorAll("[data-panel]")];
    const validViews = new Set(panels.map((panel) => panel.dataset.panel));
    const validButtons = buttons.filter((button) => validViews.has(button.dataset.view));
    if (validButtons.length < 2) continue;
    const controlledViews = new Set(validButtons.map((button) => button.dataset.view));
    const controlledPanels = panels.filter((panel) => controlledViews.has(panel.dataset.panel));

    for (const [index, panel] of controlledPanels.entries()) {
      if (!panel.id) panel.id = `diagram-${groupIndex}-panel-${index + 1}`;
      const matchingButton = validButtons.find((button) => button.dataset.view === panel.dataset.panel);
      if (matchingButton) {
        const ids = controlledPanels.filter((item) => item.dataset.panel === matchingButton.dataset.view).map((item) => {
          if (!item.id) item.id = `diagram-${groupIndex}-panel-${controlledPanels.indexOf(item) + 1}`;
          return item.id;
        });
        matchingButton.setAttribute("aria-controls", ids.join(" "));
      }
    }

    const selectView = (view) => {
      if (!controlledViews.has(view)) return;
      for (const button of validButtons) {
        button.setAttribute("aria-pressed", String(button.dataset.view === view));
      }
      for (const panel of controlledPanels) panel.hidden = panel.dataset.panel !== view;
      group.dataset.activeView = view;
    };
    for (const button of validButtons) {
      button.addEventListener("click", () => selectView(button.dataset.view));
    }
    const initial = validButtons.find((button) => button.getAttribute("aria-pressed") === "true") || validButtons[0];
    selectView(initial.dataset.view);
  }

  // The active section is a reading aid. Content visibility never depends on it.
  const tocLinks = [...document.querySelectorAll(".case-toc a[href^='#']")];
  const sections = tocLinks.map((link) => {
    const id = link.getAttribute("href")?.slice(1);
    return { link, section: id ? document.getElementById(id) : null };
  }).filter((entry) => entry.section);
  if (sections.length && "IntersectionObserver" in window) {
    const visible = new Set();
    const setActive = (section) => {
      for (const entry of sections) {
        if (entry.section === section) entry.link.setAttribute("aria-current", "location");
        else entry.link.removeAttribute("aria-current");
      }
    };
    const observer = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) visible.add(entry.target);
        else visible.delete(entry.target);
      }
      const firstVisible = sections.find((entry) => visible.has(entry.section));
      if (firstVisible) setActive(firstVisible.section);
    }, { rootMargin: "-8% 0px -56% 0px", threshold: 0 });
    for (const entry of sections) {
      observer.observe(entry.section);
      entry.link.addEventListener("click", () => setActive(entry.section));
    }
  }

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const depthAllowed = window.matchMedia("(min-width: 821px) and (hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference)");
  const heroArt = document.querySelector(".hero-art");
  const progress = document.createElement("div");
  const progressBar = document.createElement("span");
  progress.className = "reading-progress";
  progress.setAttribute("aria-hidden", "true");
  progress.append(progressBar);
  document.body.append(progress);

  let pointerX = 0;
  let pointerY = 0;
  let currentX = 0;
  let currentY = 0;
  let frame = 0;
  const maintenanceLink = heroArt?.querySelector(".lab-link-maintenance");
  const recoveryLink = heroArt?.querySelector(".lab-link-recovery");
  const clamp = (value, lower, upper) => Math.min(upper, Math.max(lower, value));
  const alignLabLinks = (x, y) => {
    // These match the independent SVG layer factors, keeping each wire attached.
    const nodeX = x * -.2;
    const nodeY = y * -.12;
    const tvX = x * .38;
    const tvY = y * .32;
    const elbowY = 251 + (nodeY + tvY) / 2;
    maintenanceLink?.setAttribute("d", `M${179 + nodeX} ${223 + nodeY}V${elbowY}H${270 + tvX}V${276 + tvY}`);
    recoveryLink?.setAttribute("d", `M${661 + nodeX} ${223 + nodeY}V${elbowY}H${570 + tvX}V${276 + tvY}`);
  };
  const renderMotion = () => {
    frame = 0;
    const scrollRange = document.documentElement.scrollHeight - window.innerHeight;
    const fraction = scrollRange > 0 ? clamp(window.scrollY / scrollRange, 0, 1) : 0;
    // CSSOM property writes are compatible with the site's self-only stylesheet policy.
    progressBar.style.transform = `scaleX(${fraction})`;
    if (heroArt && depthAllowed.matches) {
      const artBounds = heroArt.getBoundingClientRect();
      if (artBounds.bottom > -80 && artBounds.top < window.innerHeight + 80) {
        const depthY = clamp(-window.scrollY * .065, -30, 0);
        const targetY = depthY + pointerY;
        currentX += (pointerX - currentX) * .16;
        currentY += (targetY - currentY) * .16;
        heroArt.style.setProperty("--hero-x", `${currentX.toFixed(3)}px`);
        heroArt.style.setProperty("--hero-y", `${currentY.toFixed(3)}px`);
        alignLabLinks(currentX, currentY);
        if (Math.abs(pointerX - currentX) > .025 || Math.abs(targetY - currentY) > .025) {
          frame = window.requestAnimationFrame(renderMotion);
        }
      }
    }
  };
  const requestMotionFrame = () => {
    if (!frame) frame = window.requestAnimationFrame(renderMotion);
  };

  if (heroArt) {
    const plane = document.createElement("div");
    plane.className = "hero-depth-plane";
    plane.setAttribute("aria-hidden", "true");
    heroArt.prepend(plane);
    heroArt.classList.add("motion-depth");
    heroArt.addEventListener("pointermove", (event) => {
      if (!depthAllowed.matches || event.pointerType === "touch") return;
      const bounds = heroArt.getBoundingClientRect();
      pointerX = clamp(((event.clientX - bounds.left) / bounds.width - .5) * 12, -6, 6);
      pointerY = clamp(((event.clientY - bounds.top) / bounds.height - .5) * 10, -5, 5);
      requestMotionFrame();
    }, { passive: true });
    heroArt.addEventListener("pointerleave", () => {
      pointerX = 0;
      pointerY = 0;
      requestMotionFrame();
    }, { passive: true });
  }

  if (!reducedMotion.matches && "IntersectionObserver" in window) {
    const revealObserver = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add("reveal-visible");
          entry.target.classList.remove("motion-waiting");
          revealObserver.unobserve(entry.target);
        }
      }
    }, { rootMargin: "0px 0px -5% 0px", threshold: .04 });
    document.documentElement.classList.add("motion-enabled");
    const candidates = document.querySelectorAll(".section-heading, .project-grid, .about-grid, .writing-item, .contact-panel, .case-section");
    for (const element of candidates) {
      const bounds = element.getBoundingClientRect();
      element.classList.add("reveal");
      if (bounds.top >= window.innerHeight * .95) {
        revealObserver.observe(element);
        element.classList.add("motion-waiting");
      } else {
        element.classList.add("reveal-visible");
      }
    }
    reducedMotion.addEventListener?.("change", (event) => {
      if (!event.matches) return;
      for (const element of document.querySelectorAll(".motion-waiting")) {
        element.classList.remove("motion-waiting");
        element.classList.add("reveal-visible");
      }
      revealObserver.disconnect();
    });
  }

  depthAllowed.addEventListener?.("change", () => {
    pointerX = 0;
    pointerY = 0;
    currentX = 0;
    currentY = 0;
    heroArt?.style.removeProperty("--hero-x");
    heroArt?.style.removeProperty("--hero-y");
    alignLabLinks(0, 0);
    requestMotionFrame();
  });
  window.addEventListener("scroll", requestMotionFrame, { passive: true });
  window.addEventListener("resize", requestMotionFrame, { passive: true });
  window.addEventListener("load", requestMotionFrame, { once: true });
  window.addEventListener("beforeprint", () => alignLabLinks(0, 0));
  window.addEventListener("afterprint", () => {
    alignLabLinks(depthAllowed.matches ? currentX : 0, depthAllowed.matches ? currentY : 0);
    requestMotionFrame();
  });
  requestMotionFrame();
})();
