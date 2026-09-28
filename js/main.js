/* main.js — the only script the site loads globally.
   Mobile menu, scroll reveals, and click-to-load YouTube facades.
   No dependencies. Everything degrades fine without it. */
(function () {
  "use strict";

  /* ---- mobile menu ------------------------------------------------- */
  var btn = document.querySelector(".menu-btn");
  var nav = document.getElementById("nav");
  if (btn && nav) {
    btn.addEventListener("click", function () {
      var open = document.body.classList.toggle("nav-open");
      btn.setAttribute("aria-expanded", String(open));
    });
    nav.addEventListener("click", function (ev) {
      if (ev.target.tagName === "A") {
        document.body.classList.remove("nav-open");
        btn.setAttribute("aria-expanded", "false");
      }
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && document.body.classList.contains("nav-open")) {
        document.body.classList.remove("nav-open");
        btn.setAttribute("aria-expanded", "false");
        btn.focus();
      }
    });
  }

  /* ---- scroll reveals ---------------------------------------------- */
  var reveals = document.querySelectorAll(".reveal");
  if (reveals.length) {
    if (!("IntersectionObserver" in window)) {
      reveals.forEach(function (el) { el.classList.add("in"); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) {
            en.target.classList.add("in");
            io.unobserve(en.target);
          }
        });
      }, { rootMargin: "0px 0px -8% 0px" });
      reveals.forEach(function (el) { io.observe(el); });
    }
  }

  /* ---- YouTube click-to-load ---------------------------------------
     Keeps the page light: no iframe, no autoplay request, no cookie
     until somebody actually asks for the video.                        */
  function facade(btn) {
    btn.addEventListener("click", function () {
      var id = btn.getAttribute("data-video");
      if (!id) return;
      var iframe = document.createElement("iframe");
      iframe.src = "https://www.youtube-nocookie.com/embed/" +
        encodeURIComponent(id) + "?autoplay=1&rel=0";
      iframe.title = btn.getAttribute("data-title") || "Video player";
      iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; picture-in-picture";
      iframe.allowFullscreen = true;
      btn.replaceWith(iframe);
    });
  }
  document.querySelectorAll("[data-video]").forEach(facade);

  /* ---- copyright year ---------------------------------------------- */
  var y = document.getElementById("year");
  if (y) y.textContent = new Date().getFullYear();
})();
