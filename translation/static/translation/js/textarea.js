var textareas = document.querySelectorAll('textarea');

textareas.forEach(textarea => 
  textarea.addEventListener('keydown', autosize)
  )

textareas.forEach(textarea =>
  postloadautosize(textarea))
     
function autosize(){
  var el = this;
  setTimeout(function(){
    el.style.cssText = 'height:auto; padding:0';
    // for box-sizing other than "content-box" use:
    // el.style.cssText = '-moz-box-sizing:content-box';
    height = el.scrollHeight + 5;
    el.style.cssText = 'height:' + height + 'px';
  },0);
}

function postloadautosize(el){
  setTimeout(function(){
    el.style.cssText = 'height:auto; padding:0';
    el.style.cssText = 'height:' + el.scrollHeight  + 'px';
  },0);
}

// make commit
function send_commit(commit_url, csrf_token, text){
  var xhr = new XMLHttpRequest();
  xhr.open("POST", commit_url, true);
  xhr.setRequestHeader("X-CSRFToken", csrf_token); 
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(text);
}

//// textarea shortcuts

// Commit (ctrl + enter)
function make_commit(e) {
  commit_url = e.currentTarget.attributes.getNamedItem("commit-url").value  
  text = e.currentTarget.value
  status_tag = e.target.parentNode.previousElementSibling
  status_tag.innerHTML = 'Translated'
  send_commit(commit_url, csrf_token, text)
  move_below(e)
}

// Move down (ctrl + arrowdown)
function move_below(e) {
  textarea_id = e.currentTarget.id;
  next_id = "#target-" + (parseInt(textarea_id.split("-")[1]) + 1)
  next_textarea = document.querySelector(next_id)
  next_textarea.focus()
  setTimeout(function(){ next_textarea.selectionStart = next_textarea.selectionEnd = 10000; }, 0);
}

// Move up (ctrl + arrowup)
function move_up(e) {
  textarea_id = e.currentTarget.id;
  previous_id = "#target-" + (parseInt(textarea_id.split("-")[1]) - 1)
  previous_textarea = document.querySelector(previous_id)
  previous_textarea.focus()
  setTimeout(function(){ previous_textarea.selectionStart = previous_textarea.selectionEnd = 10000; }, 0);
}

function short_cuts(e) {
  // Ctrl + Enter
  if (e.ctrlKey && e.keyCode == 13) { make_commit(e) }
  // Ctrl + Downarrow
  else if (e.ctrlKey && e.keyCode == 40) { move_below(e) }
  // Ctrl + Uparrow
  else if (e.ctrlKey && e.keyCode == 38) { move_up(e) }
}
// register the handler
textareas.forEach(textarea => 
  textarea.addEventListener('keyup', short_cuts, false)
  )

