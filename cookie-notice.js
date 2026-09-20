/* EU cookie / privacy notice — DSM Communications, 2026-09-20.
 *
 * Written for these sites rather than pulled from a CDN, for two reasons:
 * every site runs `script-src 'self'`, so a third-party consent tool would be
 * blocked outright; and loading a consent banner from someone else's server
 * hands the visitor's IP to that server before they have consented to
 * anything, which is the very problem the banner exists to solve.
 *
 * What it is actually for. None of these sites set a tracking cookie, and
 * there is no analytics or advertising pixel on any of them. The one thing
 * that does leave the EU is Google Fonts: a <link> to fonts.googleapis.com
 * hands the visitor's IP address to Google in the US on page load. A Munich
 * court found that unlawful without consent in 2022 (LG München I,
 * 3 O 17493/20). So this banner is not decoration - it HOLDS THOSE FONTS BACK
 * until the visitor agrees, and the page renders in its own fallback stack
 * until then.
 *
 * To gate a resource, write the tag with data-consent-href instead of href:
 *     <link rel="stylesheet" data-consent-href="https://fonts.googleapis.com/...">
 * Nothing loads until consent is given; on "Accept" the href is set and the
 * browser fetches it normally.
 *
 * The choice is kept in localStorage, not a cookie. It is first-party, never
 * leaves the browser, and storing "this person said no" is strictly necessary
 * to honour the refusal - so it needs no consent of its own.
 *
 * Refuse is a real, equal button, not a hidden link: under EDPB guidance
 * refusing must be as easy as accepting, and a banner offering only "OK" is
 * not valid consent.
 */
(function () {
  "use strict";

  var KEY = "dsm-cookie-choice";      // "accepted" | "rejected"
  var POLICY = "/privacy.html";

  function choice() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function remember(v) {
    try { localStorage.setItem(KEY, v); } catch (e) { /* private mode - ask again */ }
  }

  /* Load anything held back until consent. Safe to call twice. */
  function release() {
    var held = document.querySelectorAll("[data-consent-href]");
    for (var i = 0; i < held.length; i++) {
      var el = held[i];
      var url = el.getAttribute("data-consent-href");
      if (!url) continue;
      el.removeAttribute("data-consent-href");
      el.setAttribute("href", url);
    }
  }

  function dismiss(bar) {
    if (bar.parentNode) bar.parentNode.removeChild(bar);
  }

  function build() {
    var bar = document.createElement("div");
    bar.className = "dsm-cookie";
    bar.setAttribute("role", "dialog");
    bar.setAttribute("aria-live", "polite");
    bar.setAttribute("aria-label", "Privacy notice");

    // Deliberately specific wording. "This site uses cookies" would be untrue
    // here, and a notice that misdescribes what happens is not informed consent.
    var text = document.createElement("p");
    text.className = "dsm-cookie-text";
    text.appendChild(document.createTextNode(
      "This site uses no tracking cookies and no analytics. We would like to load " +
      "web fonts from Google, which shares your IP address with Google. You can " +
      "refuse and the site works normally. "));
    var link = document.createElement("a");
    link.setAttribute("href", POLICY);
    link.textContent = "Privacy policy";
    text.appendChild(link);
    text.appendChild(document.createTextNode("."));

    var btns = document.createElement("div");
    btns.className = "dsm-cookie-btns";

    var no = document.createElement("button");
    no.type = "button";
    no.className = "dsm-cookie-btn dsm-cookie-no";
    no.textContent = "Refuse";
    no.addEventListener("click", function () { remember("rejected"); dismiss(bar); });

    var yes = document.createElement("button");
    yes.type = "button";
    yes.className = "dsm-cookie-btn dsm-cookie-yes";
    yes.textContent = "Accept";
    yes.addEventListener("click", function () { remember("accepted"); release(); dismiss(bar); });

    btns.appendChild(no);          // refuse first: equal weight, reached first by keyboard
    btns.appendChild(yes);
    bar.appendChild(text);
    bar.appendChild(btns);
    document.body.appendChild(bar);
    no.focus();
  }

  function start() {
    var c = choice();
    if (c === "accepted") { release(); return; }   // already agreed - just load
    if (c === "rejected") { return; }              // already refused - stay held back
    build();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
