document.getElementById("sandwich-menu").addEventListener("click", () => {
    document.getElementById("nav-drawer").classList.toggle("open");
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        const sidebar = document.querySelector('.nav-drawer');
        sidebar.classList.remove('open');
    }
});

document.addEventListener('click', (event) => {
    const sidebar = document.querySelector('.nav-drawer');
    const btnAbrir = document.querySelector('.sandwich-menu');

    if (!sidebar.contains(event.target) && !btnAbrir.contains(event.target)) {
        sidebar.classList.remove('open');
    }
});