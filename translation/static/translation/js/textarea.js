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
    // for box-sizing other than "content-box" use:
    // el.style.cssText = '-moz-box-sizing:content-box';
    console.log(el.scrollHeight)
    el.style.cssText = 'height:' + el.scrollHeight  + 'px';
  },0);
}