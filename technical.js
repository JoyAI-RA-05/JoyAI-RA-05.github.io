document.documentElement.classList.add("js");

const revealTargets = [...document.querySelectorAll("[data-reveal]")];
const topLink = document.querySelector(".top-link");
const lightboxTriggers = [...document.querySelectorAll("[data-lightbox-src]")];
const g1TaskButtons = [...document.querySelectorAll("[data-g1-task]")];
const g1TaskRail = document.querySelector(".g1-task-rail");
const g1PreviewVideos = [...document.querySelectorAll(".g1-task-card video")];
const g1FeaturedVideo = document.querySelector("#g1-featured-video");
const g1FeaturedKicker = document.querySelector("#g1-featured-kicker");
const g1FeaturedTitle = document.querySelector("#g1-featured-title");
const g1FeaturedDescription = document.querySelector("#g1-featured-description");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const finePointer = window.matchMedia("(pointer: fine)");

let lightbox;
let lightboxImage;
let pointerAnimationFrame = 0;
let g1AutoScrollTimer = 0;
let g1AutoScrollDirection = 1;
let g1AutoScrollPaused = false;
let g1AutoScrollResumeAt = 0;
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

function selectG1Task(button) {
  if (!button || !g1FeaturedVideo) return;

  for (const taskButton of g1TaskButtons) {
    const selected = taskButton === button;
    taskButton.classList.toggle("is-active", selected);
    taskButton.setAttribute("aria-selected", String(selected));
  }

  g1FeaturedVideo.pause();
  g1FeaturedVideo.poster = button.dataset.poster || "";
  g1FeaturedVideo.src = button.dataset.video || "";
  g1FeaturedVideo.load();

  if (g1FeaturedKicker) g1FeaturedKicker.textContent = button.dataset.kicker || "";
  if (g1FeaturedTitle) g1FeaturedTitle.textContent = button.dataset.title || "";
  if (g1FeaturedDescription) {
    g1FeaturedDescription.textContent = button.dataset.description || "";
  }

  const playAttempt = g1FeaturedVideo.play();
  playAttempt?.catch(() => {});
}

function scrollG1Tasks(direction) {
  if (!g1TaskRail) return;
  g1AutoScrollDirection = direction;
  g1AutoScrollResumeAt = window.performance.now() + 2600;
  g1TaskRail.scrollBy({
    left: direction * Math.max(g1TaskRail.clientWidth * 0.72, 280),
    behavior: reducedMotion.matches ? "auto" : "smooth",
  });
}

function autoScrollG1Tasks() {
  const timestamp = window.performance.now();
  if (
    !g1TaskRail ||
    g1AutoScrollPaused ||
    timestamp < g1AutoScrollResumeAt ||
    document.visibilityState !== "visible"
  ) {
    return;
  }

  const maxScroll = g1TaskRail.scrollWidth - g1TaskRail.clientWidth;
  if (maxScroll <= 1) return;

  g1TaskRail.scrollLeft += g1AutoScrollDirection * 1.1;
  if (g1TaskRail.scrollLeft >= maxScroll - 0.5) {
    g1TaskRail.scrollLeft = maxScroll;
    g1AutoScrollDirection = -1;
  } else if (g1TaskRail.scrollLeft <= 0.5) {
    g1TaskRail.scrollLeft = 0;
    g1AutoScrollDirection = 1;
  }
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

for (const button of g1TaskButtons) {
  button.addEventListener("click", () => selectG1Task(button));
  button.addEventListener("keydown", (event) => {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
    event.preventDefault();
    const index = g1TaskButtons.indexOf(button);
    const offset = event.key === "ArrowRight" ? 1 : -1;
    const nextButton = g1TaskButtons[(index + offset + g1TaskButtons.length) % g1TaskButtons.length];
    selectG1Task(nextButton);
    nextButton.focus();
    nextButton.scrollIntoView({ behavior: reducedMotion.matches ? "auto" : "smooth", block: "nearest", inline: "center" });
  });
}

document.querySelector("[data-g1-prev]")?.addEventListener("click", () => scrollG1Tasks(-1));
document.querySelector("[data-g1-next]")?.addEventListener("click", () => scrollG1Tasks(1));

if (g1TaskRail && !reducedMotion.matches) {
  g1TaskRail.addEventListener("mouseenter", () => {
    g1AutoScrollPaused = true;
  });
  g1TaskRail.addEventListener("mouseleave", () => {
    g1AutoScrollPaused = false;
    g1AutoScrollResumeAt = window.performance.now() + 900;
  });
  g1TaskRail.addEventListener("focusin", () => {
    g1AutoScrollPaused = true;
  });
  g1TaskRail.addEventListener("focusout", (event) => {
    if (g1TaskRail.contains(event.relatedTarget)) return;
    g1AutoScrollPaused = false;
    g1AutoScrollResumeAt = window.performance.now() + 900;
  });
  g1TaskRail.addEventListener("pointerdown", () => {
    g1AutoScrollPaused = true;
  });
  window.addEventListener("pointerup", () => {
    g1AutoScrollPaused = false;
    g1AutoScrollResumeAt = window.performance.now() + 2200;
  });

  g1AutoScrollTimer = window.setInterval(autoScrollG1Tasks, 30);
}

if ("IntersectionObserver" in window) {
  const previewObserver = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        const video = entry.target;
        if (entry.isIntersecting) {
          video.play()?.catch(() => {});
        } else {
          video.pause();
        }
      }
    },
    { threshold: 0.2 },
  );

  for (const video of g1PreviewVideos) previewObserver.observe(video);
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
