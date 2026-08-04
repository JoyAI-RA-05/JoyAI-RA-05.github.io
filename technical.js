document.documentElement.classList.add("js");

const revealTargets = [...document.querySelectorAll("[data-reveal]")];
const topLink = document.querySelector(".top-link");
const lightboxTriggers = [...document.querySelectorAll("[data-lightbox-src]")];
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const finePointer = window.matchMedia("(pointer: fine)");

let lightbox;
let lightboxImage;
let pointerAnimationFrame = 0;
let targetPointer = {
  x: window.innerWidth * 0.36,
  y: window.innerHeight * 0.24,
};
let currentPointer = { ...targetPointer };

function revealFallback() {
  for (const target of revealTargets) {
    target.classList.add("is-visible");
  }
}

function updateTopLink() {
  topLink?.classList.toggle("is-visible", window.scrollY > 720);
}

function applyPointer() {
  pointerAnimationFrame = 0;
  currentPointer.x += (targetPointer.x - currentPointer.x) * 0.18;
  currentPointer.y += (targetPointer.y - currentPointer.y) * 0.18;

  const width = Math.max(window.innerWidth, 1);
  const height = Math.max(window.innerHeight, 1);
  document.documentElement.style.setProperty("--pointer-x-px", `${currentPointer.x}px`);
  document.documentElement.style.setProperty("--pointer-y-px", `${currentPointer.y}px`);
  document.documentElement.style.setProperty("--pointer-x", `${(currentPointer.x / width) * 100}%`);
  document.documentElement.style.setProperty("--pointer-y", `${(currentPointer.y / height) * 100}%`);

  if (
    Math.abs(targetPointer.x - currentPointer.x) > 0.4 ||
    Math.abs(targetPointer.y - currentPointer.y) > 0.4
  ) {
    pointerAnimationFrame = window.requestAnimationFrame(applyPointer);
  }
}

function queuePointerUpdate(x, y) {
  targetPointer = { x, y };
  if (!pointerAnimationFrame) {
    pointerAnimationFrame = window.requestAnimationFrame(applyPointer);
  }
}

function closeLightbox() {
  lightbox?.classList.remove("is-open");
  lightboxImage?.removeAttribute("src");
  document.body.style.removeProperty("overflow");
}

function ensureLightbox() {
  if (lightbox) return;

  lightbox = document.createElement("div");
  lightbox.className = "lightbox";
  lightbox.setAttribute("role", "dialog");
  lightbox.setAttribute("aria-modal", "true");
  lightbox.setAttribute("aria-label", "Expanded image preview");

  lightboxImage = document.createElement("img");
  lightboxImage.alt = "";

  const closeButton = document.createElement("button");
  closeButton.type = "button";
  closeButton.setAttribute("aria-label", "Close expanded image preview");
  closeButton.textContent = "×";

  lightbox.append(lightboxImage, closeButton);
  document.body.append(lightbox);

  lightbox.addEventListener("click", (event) => {
    if (event.target === lightbox) closeLightbox();
  });
  closeButton.addEventListener("click", closeLightbox);
}

function openLightbox(src, alt) {
  ensureLightbox();
  lightboxImage.src = src;
  lightboxImage.alt = alt || "";
  lightbox.classList.add("is-open");
  document.body.style.overflow = "hidden";
}

if (reducedMotion.matches || !("IntersectionObserver" in window)) {
  revealFallback();
} else {
  const revealObserver = new IntersectionObserver(
    (entries, observer) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    },
    { threshold: 0.12, rootMargin: "0px 0px -6%" },
  );

  for (const target of revealTargets) {
    revealObserver.observe(target);
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

updateTopLink();
window.addEventListener("scroll", updateTopLink, { passive: true });

if (!reducedMotion.matches && finePointer.matches) {
  queuePointerUpdate(targetPointer.x, targetPointer.y);
  window.addEventListener(
    "pointermove",
    (event) => {
      if (event.pointerType === "touch") return;
      queuePointerUpdate(event.clientX, event.clientY);
    },
    { passive: true },
  );
  window.addEventListener("resize", () => {
    queuePointerUpdate(window.innerWidth * 0.36, window.innerHeight * 0.24);
  });
}
