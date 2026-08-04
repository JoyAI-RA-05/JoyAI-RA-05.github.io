document.documentElement.classList.add("js");

const revealTargets = [...document.querySelectorAll("[data-reveal]")];
const topLink = document.querySelector(".top-link");
const lightboxTriggers = [...document.querySelectorAll("[data-lightbox-src]")];
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

let lightbox;
let lightboxImage;

function revealFallback() {
  for (const target of revealTargets) {
    target.classList.add("is-visible");
  }
}

function updateTopLink() {
  topLink?.classList.toggle("is-visible", window.scrollY > 720);
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
