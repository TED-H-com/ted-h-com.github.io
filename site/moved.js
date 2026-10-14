/* Generated from hub.json by kit/render_hub.py. Sends a visitor of a page that
   moved to another account's GitHub Pages site there, keeping the rest of the
   path, the ?lang= choice and the #hash. */
(function () {
  var moved = {"mcp-memory-server": "https://ted-h-com.github.io"};
  var path = window.location.pathname;
  var slug = path.split("/")[1];
  if (Object.prototype.hasOwnProperty.call(moved, slug)) {
    window.location.replace(moved[slug] + path + window.location.search + window.location.hash);
  }
})();
