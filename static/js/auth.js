document
  .getElementById("logout-button")
  ?.addEventListener("click", async () => {
    try {
      await fetch("/auth/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch (error) {
      console.error("Logout request failed:", error);
    }

    localStorage.removeItem("access_token");

    window.location.href = "/auth/login";
  });