(function () {
  const compassDataEl = document.getElementById("compass-data");
  const compass = document.getElementById("era-compass");

  if (!compassDataEl || !compass) return;

  const data = JSON.parse(compassDataEl.textContent);
  let pendingYear = null;
  let transitioning = false;

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function applyCompassData(d) {
    if (!d) return;

    const yearEl = compass.querySelector(".compass-year");
    if (yearEl) yearEl.textContent = d.year;

    const framingEl = compass.querySelector(".compass-framing");
    if (framingEl) {
      if (d.framing) {
        framingEl.textContent = d.framing;
        framingEl.hidden = false;
      } else {
        framingEl.hidden = true;
      }
    }

    const intensityEl = compass.querySelector(".compass-intensity");
    if (intensityEl) {
      if (d.intensity && d.intensity.length > 0) {
        intensityEl.innerHTML = d.intensity
          .map(
            (item) =>
              `<div class="compass-category">` +
              `<span class="compass-cat-name">${escapeHtml(item.category)}</span>` +
              `<span class="compass-cat-bar" style="--cat-color: ${escapeHtml(item.color)}; --cat-count: ${item.count};"></span>` +
              `</div>`
          )
          .join("");
        intensityEl.hidden = false;
      } else {
        intensityEl.hidden = true;
      }
    }

    const linkEl = compass.querySelector(".compass-newsletter-link");
    if (linkEl) {
      if (d.newsletter && d.newsletter.url) {
        linkEl.href = d.newsletter.url;
        linkEl.textContent = (d.newsletter.title || "Newsletter") + " →";
        linkEl.hidden = false;
      } else {
        linkEl.hidden = true;
      }
    }
  }

  function updateCompass(d) {
    if (!d) return;
    pendingYear = d;

    if (transitioning) return; // will flush on transitionend
    transitioning = true;

    compass.classList.add("switching");

    function onFadeOut(e) {
      if (e.propertyName !== "opacity") return;
      compass.removeEventListener("transitionend", onFadeOut);

      applyCompassData(pendingYear);
      pendingYear = null;

      compass.classList.remove("switching");

      compass.addEventListener("transitionend", function onFadeIn(e2) {
        if (e2.propertyName !== "opacity") return;
        compass.removeEventListener("transitionend", onFadeIn);
        transitioning = false;
      });
    }

    compass.addEventListener("transitionend", onFadeOut);
  }

  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          updateCompass(data[entry.target.dataset.year]);
        }
      }
    },
    { rootMargin: "-15% 0px -80% 0px" }
  );

  document.querySelectorAll(".year-section").forEach((el) => observer.observe(el));
})();
