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

// Textarea navigation and commit shortcuts

// Commit (Ctrl + Enter)
function make_commit(e, value) {
  if (e.ctrlKey && e.keyCode == 13) {
      // call your function to do the thing
      commit_url = e.currentTarget.attributes.getNamedItem("commit-url").value  
      text = e.currentTarget.value
      status_tag = e.target.parentNode.previousElementSibling
      status_tag.innerHTML = 'Translated'
      send_commit(commit_url, csrf_token, text)
  }
}
// register the handler
textareas.forEach(textarea => 
  textarea.addEventListener('keyup', make_commit, false)
  )

function send_commit(commit_url, csrf_token, text){
  var xhr = new XMLHttpRequest();
  xhr.open("POST", commit_url, true);
  xhr.setRequestHeader("X-CSRFToken", csrf_token); 
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(text);
}
