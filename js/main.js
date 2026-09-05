const menuBtn = document.querySelector(".menu-btn");
menuBtn.addEventListener("click", () => {
  const open = document.body.classList.toggle("nav-open");
  menuBtn.setAttribute("aria-expanded", String(open));
});

document.querySelectorAll(".nav a").forEach((link) =>
  link.addEventListener("click", () => {
    document.body.classList.remove("nav-open");
    menuBtn.setAttribute("aria-expanded", "false");
  })
);

document.querySelectorAll(".yt-facade").forEach((facade) => {
  facade.addEventListener("click", () => {
    const id = facade.dataset.id;
    const iframe = document.createElement("iframe");
    iframe.src = `https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0`;
    iframe.title = "YouTube video player";
    iframe.allow =
      "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
    iframe.allowFullscreen = true;
    facade.replaceWith(iframe);
  });
});

const io = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("in");
        io.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.12 }
);
document.querySelectorAll(".reveal").forEach((el) => io.observe(el));

const sections = document.querySelectorAll("section[id]");
const navLinks = document.querySelectorAll('.nav a[href^="#"]');
const spy = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        navLinks.forEach((l) =>
          l.setAttribute(
            "aria-current",
            l.getAttribute("href") === `#${entry.target.id}` ? "true" : "false"
          )
        );
      }
    });
  },
  { rootMargin: "-40% 0px -55% 0px" }
);
sections.forEach((s) => spy.observe(s));

const yearEl = document.getElementById("year");
if (yearEl) yearEl.textContent = new Date().getFullYear();
