document.documentElement.classList.add("js-ready");

const revealTargets = [...document.querySelectorAll("[data-reveal]")];
const autoVideos = [...document.querySelectorAll("[data-auto-video]")];
const topButton = document.querySelector(".top-button");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

function markVideoReady(video) {
  if (video.classList.contains("hero-video")) {
    video.classList.add("is-ready");
  }
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
}

function updateTopButton() {
  topButton?.classList.toggle("is-visible", window.scrollY > 640);
}

updateTopButton();
window.addEventListener("scroll", updateTopButton, { passive: true });
