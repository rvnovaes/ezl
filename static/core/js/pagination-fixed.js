$(document).ready(function () {
    var container = document.querySelector('.pagination-fixed'),
        w = window,
        d = document,
        e = d.documentElement,
        g = d.getElementsByTagName('body')[0],
        x = w.innerWidth || e.clientWidth || g.clientWidth,
        y = w.innerHeight || e.clientHeight || g.clientHeight;
    container.style.left = (x / 2) - (container.clientWidth / 2) + 'px';
});

