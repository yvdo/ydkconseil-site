/* YDK Conseil — interactions */
(function () {
  var doc = document.documentElement;
  var reduce = false; /* effets affichés pour tous les visiteurs */

  /* Menu mobile */
  var btn = document.querySelector('.menu-btn');
  var nav = document.getElementById('menu');
  if (btn && nav) {
    var close = function () { nav.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); btn.setAttribute('aria-label', 'Ouvrir le menu'); };
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
    });
    nav.addEventListener('click', function (e) { if (e.target.closest('a')) close(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
  }

  /* Apparitions au défilement */
  if (!reduce && 'IntersectionObserver' in window) {
    doc.classList.add('js');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    document.querySelectorAll('.rv, .rv-clip').forEach(function (el) { io.observe(el); });
  }

  /* Profondeur du hero à la souris */
  var hero = document.querySelector('.hero');
  if (hero && !reduce && window.matchMedia('(pointer: fine)').matches) {
    var raf = 0, mx = 0, my = 0;
    hero.addEventListener('pointermove', function (ev) {
      var r = hero.getBoundingClientRect();
      mx = (ev.clientX - r.left) / r.width - 0.5;
      my = (ev.clientY - r.top) / r.height - 0.5;
      if (!raf) raf = requestAnimationFrame(function () {
        hero.style.setProperty('--mx', mx.toFixed(3));
        hero.style.setProperty('--my', my.toFixed(3));
        raf = 0;
      });
    });
    hero.addEventListener('pointerleave', function () {
      hero.style.setProperty('--mx', '0'); hero.style.setProperty('--my', '0');
    });
  }

  /* Retour du formulaire */
  var params = new URLSearchParams(location.search);
  var msg = document.getElementById('form-status');
  if (msg && params.has('envoi')) {
    msg.hidden = false;
    msg.textContent = params.get('envoi') === 'ok'
      ? 'Merci, votre demande est bien partie. Je vous réponds sous 48 h.'
      : 'L’envoi a échoué. Écrivez-moi directement à contact@ydkconseil.com.';
  }

  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();
})();
