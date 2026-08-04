document.documentElement.classList.add("js-ready");

const revealTargets = [...document.querySelectorAll("[data-reveal]")];
const autoVideos = [...document.querySelectorAll("[data-auto-video]")];
const lightboxTriggers = [...document.querySelectorAll("[data-lightbox-src]")];
const topButton = document.querySelector(".top-button");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

function revealVisibleTargets() {
  for (const target of revealTargets) {
    if (target.classList.contains("is-visible")) continue;
    const rect = target.getBoundingClientRect();
    const entersViewport =
      rect.top < window.innerHeight * 1.12 &&
      rect.bottom > -window.innerHeight * 0.15;
    if (entersViewport) target.classList.add("is-visible");
  }
}

let revealTicking = false;

function scheduleRevealVisibleTargets() {
  if (revealTicking) return;
  revealTicking = true;
  requestAnimationFrame(() => {
    revealTicking = false;
    revealVisibleTargets();
  });
}

function markVideoReady(video) {
  if (video.classList.contains("hero-video")) {
    video.classList.add("is-ready");
  }
}

let lightbox;
let lightboxImage;

function closeLightbox() {
  lightbox?.classList.remove("is-open");
  lightboxImage?.removeAttribute("src");
  document.body.style.removeProperty("overflow");
}

function ensureLightbox() {
  if (lightbox) return lightbox;

  lightbox = document.createElement("div");
  lightbox.className = "figure-lightbox";
  lightbox.setAttribute("role", "dialog");
  lightbox.setAttribute("aria-modal", "true");
  lightbox.setAttribute("aria-label", "Expanded figure preview");

  lightboxImage = document.createElement("img");
  lightboxImage.alt = "";

  const closeButton = document.createElement("button");
  closeButton.className = "figure-lightbox-close";
  closeButton.type = "button";
  closeButton.setAttribute("aria-label", "Close expanded figure preview");
  closeButton.textContent = "×";

  lightbox.append(lightboxImage, closeButton);
  document.body.append(lightbox);

  lightbox.addEventListener("click", (event) => {
    if (event.target === lightbox) closeLightbox();
  });
  closeButton.addEventListener("click", closeLightbox);

  return lightbox;
}

function openLightbox(src, alt) {
  ensureLightbox();
  lightboxImage.src = src;
  lightboxImage.alt = alt || "";
  document.body.style.overflow = "hidden";
  lightbox.classList.add("is-open");
}

for (const video of autoVideos) {
  if (video.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA) {
    markVideoReady(video);
  } else {
    video.addEventListener("loadeddata", () => markVideoReady(video), {
      once: true,
    });
  }
}

for (const trigger of lightboxTriggers) {
  trigger.addEventListener("click", () => {
    openLightbox(trigger.dataset.lightboxSrc, trigger.dataset.lightboxAlt);
  });
}

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeLightbox();
});

if (reducedMotion.matches || !("IntersectionObserver" in window)) {
  for (const target of revealTargets) target.classList.add("is-visible");
  for (const video of autoVideos) video.pause();
} else {
  const revealObserver = new IntersectionObserver(
    (entries, observer) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    },
    { threshold: 0.14, rootMargin: "0px 0px -6%" },
  );

  for (const target of revealTargets) revealObserver.observe(target);

  const videoObserver = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        const video = entry.target;
        if (entry.isIntersecting) {
          video.play().catch(() => {});
        } else {
          video.pause();
        }
      }
    },
    { threshold: 0.28 },
  );

  for (const video of autoVideos) videoObserver.observe(video);

  window.addEventListener("load", revealVisibleTargets, { once: true });
  window.addEventListener("hashchange", scheduleRevealVisibleTargets);
  window.addEventListener("scroll", scheduleRevealVisibleTargets, { passive: true });
  window.setTimeout(revealVisibleTargets, 900);
}

function updateTopButton() {
  topButton?.classList.toggle("is-visible", window.scrollY > 640);
}

updateTopButton();
window.addEventListener("scroll", updateTopButton, { passive: true });
