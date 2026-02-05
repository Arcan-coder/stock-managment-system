const loginForm = document.getElementById("loginForm");
const loginOverlay = document.getElementById("loginOverlay");

if (loginForm) {
  loginForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (loginOverlay) {
      loginOverlay.classList.add("show");
    }
    setTimeout(() => {
      window.location.href = "/dashboard.html";
    }, 1400);
  });
}
