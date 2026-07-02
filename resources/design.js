(() => {
  const stars = document.querySelector("[data-github-stars]");

  if (stars && window.fetch) {
    fetch("https://api.github.com/repos/Jianghanxiao/PhysTwin", {
      headers: { Accept: "application/vnd.github+json" }
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`GitHub request failed with ${response.status}`);
        }

        return response.json();
      })
      .then((repository) => {
        if (!Number.isFinite(repository.stargazers_count)) {
          return;
        }

        const formatted = new Intl.NumberFormat("en-US").format(repository.stargazers_count);
        stars.textContent = `${formatted} stars`;
        stars.title = "Live GitHub star count";
      })
      .catch(() => {
        // The stable fallback remains visible when GitHub is offline or rate-limited.
      });
  }

  if (!("IntersectionObserver" in window)) {
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      const video = entry.target;

      if (!entry.isIntersecting && !video.paused) {
        video.dataset.resumeOnView = "true";
        video.pause();
      } else if (entry.isIntersecting && video.dataset.resumeOnView === "true") {
        delete video.dataset.resumeOnView;
        video.play().catch(() => {
          // Browsers can still decline autoplay; controls remain available.
        });
      }
    });
  }, {
    rootMargin: "180px 0px",
    threshold: 0.01
  });

  document.querySelectorAll("video[autoplay]").forEach((video) => observer.observe(video));
})();
