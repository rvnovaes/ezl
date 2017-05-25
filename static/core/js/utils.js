function toggle(e) {
    checkboxes = document.getElementsByName("selection");
    for (var c in checkboxes)checkboxes[c].checked = e.checked
}