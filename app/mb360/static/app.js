/* Mother & Baby 360 v1.0.0: what makes the server-rendered pages feel like one mobile app. Every page still works without it. */
(function () {
  var NAV = "mb360-nav";
  function store(k, v) { try { if (v === undefined) return sessionStorage.getItem(k); sessionStorage.setItem(k, v); } catch (e) { return null; } }

  /* Screen transitions: back = pop, tab = fade, everything else = push */
  document.addEventListener("click", function (e) {
    var a = e.target.closest("a");
    if (!a) return;
    store(NAV, a.hasAttribute("data-back") ? "pop" : a.classList.contains("tab") ? "tab" : "push");
    var from = document.referrer.indexOf(location.origin) === 0 ? new URL(document.referrer).pathname : null;
    if (a.dataset.back === "auto" && from && from !== location.pathname && history.length > 1) {
      e.preventDefault();
      history.back();
    }
  });
  window.addEventListener("pagereveal", function (e) {
    if (e.viewTransition) {
      document.documentElement.dataset.nav = store(NAV) || "tab";
      var done = function () { delete document.documentElement.dataset.nav; };
      e.viewTransition.finished.then(done, done);
    }
  });

  function ready(fn) { if (document.readyState !== "loading") fn(); else document.addEventListener("DOMContentLoaded", fn); }

  function toast(text) {
    var old = document.querySelector(".toast.js");
    if (old) old.remove();
    var t = document.createElement("div");
    t.className = "toast js";
    t.setAttribute("role", "status");
    t.textContent = text;
    document.querySelector(".scr").appendChild(t);
    setTimeout(function () { t.remove(); }, 3200);
  }

  ready(function () {
    var body = document.querySelector(".scr .body");

    /* The scroll position comes back when the mother returns to a screen */
    var key = "mb360-scroll:" + location.pathname + location.search;
    if (body && store(NAV) === "pop" && store(key)) body.scrollTop = +store(key);
    window.addEventListener("pagehide", function () { if (body) store(key, body.scrollTop); });

    /* Forms: one tap, one submit. The button keeps its name/value in the request. */
    document.querySelectorAll("form").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        store(NAV, form.method.toLowerCase() === "get" ? "tab" : "push");
        var btn = e.submitter;
        if (form.method.toLowerCase() === "post" && btn && btn.classList.contains("btn")) {
          if (form.dataset.sent) { e.preventDefault(); return; }
          form.dataset.sent = "1";
          btn.classList.add("busy");
        }
      });
    });
    window.addEventListener("pageshow", function () {
      document.querySelectorAll("form[data-sent]").forEach(function (f) { delete f.dataset.sent; });
      document.querySelectorAll(".busy").forEach(function (b) { b.classList.remove("busy"); });
    });

    /* S-083 "Close app": FR-021 clears what the sub-app kept on the device */
    var closing = document.querySelector("[data-close-form]");
    if (closing) closing.addEventListener("submit", function () {
      try { Object.keys(sessionStorage).forEach(function (k) { if (k.indexOf("mb360") === 0) sessionStorage.removeItem(k); }); } catch (e) {}
    });

    /* Hotline: the number is pending from the hospital (BOT Q8), so no dialler opens on an invented number */
    document.addEventListener("click", function (e) {
      var h = e.target.closest("[data-hotline-pending]");
      if (h) { e.preventDefault(); toast(h.dataset.hotlinePending); }
    });

    /* Symptoms: "No symptoms" excludes the others; the free text only with "Other" */
    var symptoms = document.querySelectorAll('input[name="symptoms"]');
    var otherRow = document.querySelector("[data-other-row]");
    function syncOther() {
      if (!otherRow) return;
      var other = document.querySelector('input[name="symptoms"][value="Other"]');
      var on = other && other.checked;
      otherRow.hidden = !on && !otherRow.querySelector(".err");
      if (!on) { var i = otherRow.querySelector("input"); if (i && !otherRow.querySelector(".err")) i.value = ""; }
    }
    symptoms.forEach(function (box) {
      box.addEventListener("change", function () {
        if (box.checked) symptoms.forEach(function (x) {
          if (x !== box && (box.value === "No symptoms" || x.value === "No symptoms")) x.checked = false;
        });
        syncOther();
      });
    });
    syncOther();

    /* Live hint on the report form: rules come from THRESHOLD_RULE through the page; the server decides on submit */
    var live = document.querySelector("[data-live-rules]");
    if (live) {
      var rules = JSON.parse(live.dataset.liveRules);
      var box = live.querySelector("[data-threshold-card]");
      var check = function () {
        var f = function (n) { var el = live.querySelector('[name="' + n + '"]'); return el ? el.value : ""; };
        var above = null;
        if (rules.systolic !== undefined && f("systolic") && f("diastolic")) above = +f("systolic") >= rules.systolic || +f("diastolic") >= rules.diastolic;
        if (rules.above && f("level")) above = rules.above.indexOf(f("level")) >= 0;
        if (f("glucose_context") && f("value") && rules[f("glucose_context")] !== undefined) above = +f("value") >= rules[f("glucose_context")];
        if (!box) return;
        box.dataset.state = above === null ? "idle" : above ? "above" : "normal";
      };
      live.addEventListener("input", check);
      check();
    }

    /* Glucose timing: threshold text follows the choice */
    document.querySelectorAll("[data-reload-on-change]").forEach(function (el) {
      el.addEventListener("change", function () { location.href = el.dataset.reloadOnChange + encodeURIComponent(el.value); });
    });

    /* Mood: tap again to clear */
    document.querySelectorAll('input[name="mood"]').forEach(function (r) {
      r.addEventListener("click", function () {
        if (r.dataset.was === "1") { r.checked = false; r.dataset.was = ""; return; }
        document.querySelectorAll('input[name="mood"]').forEach(function (x) { x.dataset.was = ""; });
        r.dataset.was = "1";
      });
    });

    /* Diary photos: previews and the limit of the form */
    var photos = document.querySelector("[data-photos]");
    if (photos) {
      var list = document.querySelector("[data-photo-list]");
      photos.addEventListener("change", function () {
        list.querySelectorAll("img").forEach(function (i) { i.remove(); });
        Array.prototype.slice.call(photos.files, 0, 5).forEach(function (file) {
          var img = document.createElement("img");
          img.src = URL.createObjectURL(file);
          img.className = "ph-prev";
          img.alt = "";
          list.prepend(img);
        });
      });
    }

    /* Tap a picture to see it full screen */
    var zoom = document.createElement("div");
    zoom.className = "zoom";
    zoom.hidden = true;
    zoom.innerHTML = "<img alt=''>";
    zoom.addEventListener("click", function () { zoom.hidden = true; });
    document.querySelector(".scr").appendChild(zoom);
    document.addEventListener("click", function (e) {
      var img = e.target.closest("[data-zoom]");
      if (!img) return;
      zoom.firstChild.src = img.currentSrc || img.src;
      zoom.firstChild.alt = img.alt;
      zoom.hidden = false;
    });

    /* Timeline: swipe between weeks */
    var swipe = document.querySelector("[data-swipe]");
    if (swipe) {
      var x0 = null;
      swipe.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
      swipe.addEventListener("touchend", function (e) {
        if (x0 === null) return;
        var dx = e.changedTouches[0].clientX - x0;
        var to = document.querySelector(dx > 0 ? "[data-week-prev]" : "[data-week-next]");
        if (Math.abs(dx) > 70 && to) to.click();
        x0 = null;
      });
    }

    /* Chat: newest message in view; the question appears at once while the answer is on its way */
    var chat = document.querySelector("[data-chat]");
    if (chat) {
      var toEnd = function () {
        var last = chat.querySelector(".me:last-of-type, .bot:not(.typing):last-of-type, .card:last-of-type");
        var items = chat.querySelectorAll(".me, .bot:not(.typing), .card");
        if (items.length) items[items.length - 1].scrollIntoView({ block: "end" });
        chat.scrollTop = chat.scrollHeight;
      };
      toEnd();
      window.addEventListener("load", toEnd);
      setTimeout(toEnd, 120);
      var form = document.querySelector("[data-composer]");
      var send = function (text) {
        var q = document.createElement("p");
        q.className = "me";
        q.textContent = text;
        var typing = document.getElementById("typing");
        chat.insertBefore(q, typing);
        typing.style.display = "flex";
        chat.scrollTop = chat.scrollHeight;
      };
      form.addEventListener("submit", function () {
        var input = form.querySelector("input[name=text]");
        if (input.value.trim()) send(input.value.trim());
      });
      document.querySelectorAll("[data-suggest]").forEach(function (b) {
        b.addEventListener("click", function () {
          form.querySelector("input[name=text]").value = b.dataset.suggest;
          form.requestSubmit();
        });
      });
    }

    /* D-27: the date control keeps the phone's picker but always shows dd/mm/yyyy */
    function two(n) { return (n < 10 ? "0" : "") + n; }
    document.querySelectorAll('input[type="date"], input[type="datetime-local"]').forEach(function (input) {
      var wrap = document.createElement("span");
      wrap.className = "dt-wrap";
      var show = document.createElement("span");
      show.className = "dt-show";
      show.setAttribute("aria-hidden", "true");
      input.parentNode.insertBefore(wrap, input);
      wrap.appendChild(input);
      wrap.appendChild(show);
      input.classList.add("dt-masked");
      var paint = function () {
        var m = /^(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}:\d{2}))?/.exec(input.value);
        if (!m) { show.textContent = input.placeholder || "dd/mm/yyyy"; show.classList.add("empty"); return; }
        show.classList.remove("empty");
        var d = input.hasAttribute("data-short") ? m[3] + "/" + m[2] : m[3] + "/" + m[2] + "/" + m[1];
        show.textContent = m[4] ? d + " · " + m[4] : d;
      };
      input.addEventListener("input", paint);
      input.addEventListener("change", paint);
      paint();
      if (input.showPicker) wrap.addEventListener("click", function () { try { input.showPicker(); } catch (e) { input.focus(); } });
    });

    /* Installable app, offline notice */
    if ("serviceWorker" in navigator && document.documentElement.dataset.sw) navigator.serviceWorker.register("/sw.js");
  });
})();
