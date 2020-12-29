  
function autosize(){
  var el = this;
  setTimeout(function(){
    el.style.cssText = 'height:auto; padding:0';
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

function send_commit(commit_url, csrf_token, text, e){
  const xhr = new XMLHttpRequest();

  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4) {
      update_status(xhr.response, e);
    }
  }

  xhr.open("POST", commit_url, true);
  xhr.setRequestHeader("X-CSRFToken", csrf_token);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(text);
}

function retrieve_match(search_url, seg_id) {

  var xhr = new XMLHttpRequest();

  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4) {
      update_search_result(xhr.response);
    }
  }

  xhr.open("GET", search_url, true);
  xhr.send(seg_id);
}

function update_search_result(htmlSnippet) {
  const search_result_span = document.querySelector('#search_result')
  search_result_span.innerHTML = htmlSnippet
}

function update_status(status_text, e) {
  status_tag = e.target.parentNode.previousElementSibling
  status_tag.innerHTML = status_text
}


//// textarea shortcuts ////

// Commit (ctrl + enter)
function make_commit(e) {
  commit_url = e.currentTarget.attributes.getNamedItem("commit-url").value
  text = e.currentTarget.value
  send_commit(commit_url, csrf_token, text, e)
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

// Copy found result to textarea (ctrl + t)
function copy_found_result(e) {
  found_result = doucment.querySelector('#found_target_text').value;
  e.currentTarget.value = found_result;
  setTimeout(function(){ e.currentTarget.selectionStart = e.currentTarget.selectionEnd = 10000; }, 0);
}


// Register short_cuts
function short_cuts(e) {
  // Ctrl + Enter
  if (e.ctrlKey && e.keyCode == 13) { make_commit(e) }
  // Ctrl + Downarrow
  else if (e.ctrlKey && e.keyCode == 40) { move_below(e) }
  // Ctrl + Uparrow
  else if (e.ctrlKey && e.keyCode == 38) { move_up(e) }
  // Ctrl + t
  else if (e.ctrlKey && e.keyCode == 84) { copy_found_result(e) }
}


//// register the handler ////
var textareas = document.querySelectorAll('textarea');

textareas.forEach(textarea => 
  textarea.addEventListener('keyup', short_cuts, false)
  )

textareas.forEach(textarea => 
  textarea.addEventListener('keydown', autosize)
  )

textareas.forEach(textarea =>
  postloadautosize(textarea)
  )
