/* Aggregate engagement only: no names, email addresses or saved listening positions. */
(function () {
  'use strict';
  if (!['qualiapartners.com.au', 'www.qualiapartners.com.au'].includes(location.hostname)) return;
  var sent = new Set();
  function once(name) {
    if (sent.has(name) || typeof window.plausible !== 'function') return;
    try {
      window.plausible(name);
      sent.add(name);
    } catch (_) { /* Analytics must never interrupt navigation or playback. */ }
  }

  document.addEventListener('click', function (event) {
    var link = event.target.closest && event.target.closest('a[href]');
    if (!link) return;
    if (link.protocol === 'mailto:' || link.protocol === 'tel:') once('Contact click');
  });

  var audio = document.getElementById('book-audio');
  if (!audio) return;
  audio.addEventListener('playing', function () { once('Audiobook start'); });
  function progress() {
    // played contains the actual media ranges played, excluding seek jumps.
    // Overlapping/replayed ranges do not inflate listening milestones.
    var seconds = 0;
    for (var i = 0; i < audio.played.length; i++) {
      seconds += audio.played.end(i) - audio.played.start(i);
    }
    if (seconds >= 300) once('Audiobook 5 minutes');
    if (seconds >= 900) once('Audiobook 15 minutes');
  }
  audio.addEventListener('timeupdate', progress);
  audio.addEventListener('pause', progress);
  audio.addEventListener('ended', progress);
})();
